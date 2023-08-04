import logging
import time
from abc import ABC
from abc import abstractmethod
from json import JSONDecodeError
from json import loads as json_loads
from typing import Any
from typing import TypeAlias

from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from frinx.client.frinx_conductor_wrapper import FrinxConductorWrapper
from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.telemetry.common import increment_task_execution_error
from frinx.common.telemetry.common import increment_task_poll
from frinx.common.telemetry.common import increment_uncaught_exception
from frinx.common.telemetry.common import record_task_execute_time
from frinx.common.telemetry.metrics import Metrics
from frinx.common.type_aliases import DictAny
from frinx.common.util import jsonify_description
from frinx.common.util import remove_empty_elements_from_root_dict
from frinx.common.util import snake_to_camel_case
from frinx.common.worker.task_def import BaseTaskdef
from frinx.common.worker.task_def import DefaultTaskDefinition
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskExecutionProperties
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult

logger = logging.getLogger(__name__)
metrics = Metrics()

RawTaskIO: TypeAlias = dict[str, Any]
TaskExecLog: TypeAlias = str


class Config:
    arbitrary_types_allowed = True
    alias_generator = snake_to_camel_case
    allow_population_by_field_name = True


@dataclass(config=Config)
class WorkerImpl(ABC):
    task_def: TaskDefinition
    task_def_template: type[BaseTaskdef] | type[DefaultTaskDefinition] | None

    class ExecutionProperties(TaskExecutionProperties):
        ...

    class WorkerDefinition(TaskDefinition):
        ...

    class WorkerInput(TaskInput):
        ...

    class WorkerOutput(TaskOutput):
        ...

    def __init__(
            self, task_def_template: type[BaseTaskdef] | type[DefaultTaskDefinition] | None = None
    ) -> None:
        self.task_def_template = task_def_template
        self.task_def = self.task_definition_builder(self.task_def_template)

    @classmethod
    def task_definition_builder(
            cls, task_def_template: type[BaseTaskdef] | type[DefaultTaskDefinition] | None = None
    ) -> TaskDefinition:
        cls.validate()

        params = {}
        for param in cls.WorkerDefinition.__fields__.values():
            params[param.alias] = param.default
            if param.alias == 'inputKeys':
                params[param.alias] = [field.alias for field in cls.WorkerInput.__fields__.values()]
            if param.alias == 'outputKeys':
                params[param.alias] = [
                    field.alias for field in cls.WorkerOutput.__fields__.values()
                ]

        # Create Description in JSON format
        params['description'] = jsonify_description(
            params['description'], params['labels'], params['rbac']
        )

        params.pop('labels')
        params.pop('rbac')

        if task_def_template is None:
            task_def_template = DefaultTaskDefinition.__fields__.items()  # type: ignore
        else:
            task_def_template = task_def_template.__fields__.items()  # type: ignore

        # Transform dict to TaskDefinition object use default values in necessary
        task_def = TaskDefinition(**params)

        for key, value in task_def_template:  # type: ignore
            if value.default is not None and task_def.__getattribute__(key) is None:
                task_def.__setattr__(key, value.default)

        return task_def

    def register(self, conductor_client: FrinxConductorWrapper) -> None:
        conductor_client.register(
            task_type=self.task_def.name,
            task_definition=self.task_def.dict(by_alias=True, exclude_none=True),
            exec_function=self._execute_wrapper,
        )

    @abstractmethod
    def execute(self, worker_input: Any) -> TaskResult[Any]:
        # worker_input parameter has to be of type any, otherwise all other subclasses of WorkerImpl would
        # violate Liskov substitution principle.
        # https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        pass

    @classmethod
    def _execute_wrapper(cls, task: RawTaskIO) -> Any:
        task_type = str(task.get('taskType'))
        increment_task_poll(metrics, task_type)
        try:
            logger.debug('Executing task %s:', task)
            task_result: RawTaskIO = cls._execute_func(task)
            logger.debug('Task result %s:', task_result)
            return task_result
        except Exception as error:
            increment_task_execution_error(metrics, task_type, error)
            increment_uncaught_exception(metrics, task_type)
            logger.error('Validation error occurred: %s', error)
            return TaskResult(status=TaskResultStatus.FAILED, logs=[TaskExecLog(str(error))]).dict()

    @classmethod
    def _execute_func(cls, task: RawTaskIO) -> RawTaskIO:

        input_data: DictAny = task['inputData']
        execution_properties = cls.ExecutionProperties()

        if execution_properties.exclude_empty_inputs:
            logger.debug('Worker input data before removing empty elements: %s:', input_data)
            input_data = remove_empty_elements_from_root_dict(task['inputData'])
            logger.debug('Worker input data after removing empty elements: %s:', input_data)

        if execution_properties.transform_string_to_json_valid:
            logger.debug('Worker input data before json serialization: %s:', input_data)
            input_data = cls._transform_input_data_to_json(input_data)
            logger.debug('Worker input data after json serialization: %s:', input_data)

        try:
            worker_input = cls.WorkerInput.parse_obj(input_data)
        except ValidationError as error:
            logger.error('Validation error occurred: %s', error)
            raise error

        if not metrics.settings.metrics_enabled:
            return cls.execute(cls, worker_input).dict()  # type: ignore[arg-type]

        start_time = time.time()
        task_result: RawTaskIO = cls.execute(cls, worker_input).dict()  # type: ignore[arg-type]
        finish_time = time.time()
        record_task_execute_time(metrics, str(task.get('taskType')), finish_time - start_time)
        return task_result

    @classmethod
    def _transform_input_data_to_json(cls, input_data: DictAny) -> DictAny:
        for k, v in cls.WorkerInput.__fields__.items():
            if v.outer_type_ == list[str] or v.outer_type_ == DictAny:
                if type(input_data.get(k)) == str:
                    try:
                        input_data[k] = json_loads(str(input_data.get(k)))
                    except JSONDecodeError as e:
                        raise Exception(f'Worker input {k} is invalid JSON, {e}')
        return input_data

    @classmethod
    def validate(cls) -> None:
        if not issubclass(cls.WorkerInput, TaskInput):
            error_msg = (
                "Expecting task input model to be a subclass of "
                f"'{TaskInput.__qualname__}', not '{cls.WorkerInput.__qualname__}'"
            )
            logger.error(error_msg)
            raise TypeError(error_msg)

        if not issubclass(cls.WorkerOutput, TaskOutput):
            error_msg = (
                "Expecting task output model to be a subclass of "
                f"'{TaskOutput.__qualname__}', not '{cls.WorkerOutput.__qualname__}'"
            )
            logger.error(error_msg)
            raise TypeError(error_msg)
