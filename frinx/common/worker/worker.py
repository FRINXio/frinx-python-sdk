import logging
import time
from abc import ABC
from abc import abstractmethod
from json import JSONDecodeError
from json import loads as json_loads
from typing import Any
from typing import TypeAlias

from pydantic import ValidationError

from frinx.client.frinx_conductor_wrapper import FrinxConductorWrapper
from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.telemetry.common import increment_task_execution_error
from frinx.common.telemetry.common import increment_task_poll
from frinx.common.telemetry.common import increment_uncaught_exception
from frinx.common.telemetry.common import record_task_execute_time
from frinx.common.telemetry.metrics import Metrics
from frinx.common.type_aliases import DictAny
from frinx.common.type_aliases import DictStr
from frinx.common.type_aliases import ListStr
from frinx.common.util import jsonify_description
from frinx.common.util import remove_empty_elements_from_root_dict
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


class WorkerImpl(ABC):
    """Abstract base class representing a worker implementation.

    This class serves as the base class for all worker implementations that handle
    tasks in a Frinx Conductor workflow. Subclasses must implement the `execute` method.

    Attributes:
        task_def (TaskDefinition): The task definition associated with the worker.
        task_def_template (type[BaseTaskdef] | type[DefaultTaskDefinition] | None): The template
            task definition used to build the task_def.
    """
    task_def: TaskDefinition
    task_def_template: type[BaseTaskdef] | type[DefaultTaskDefinition] | None

    class ExecutionProperties(TaskExecutionProperties):
        """Execution properties for the worker.

        This class defines the execution properties for the worker. It serves as a configuration
        for how the worker should handle task execution.

        Attributes:
            ...  # The specific execution properties are defined elsewhere.
        """

    class WorkerDefinition(TaskDefinition):
        """Definition of the worker.

        This class defines the task definition for the worker. It contains the configuration
        details and metadata associated with the worker's tasks.

        Attributes:
            ...  # The specific worker definition attributes are defined elsewhere.
        """

    class WorkerInput(TaskInput):
        """Input model for the worker.

        This class defines the input model for the worker. It specifies the expected input data
        format for the worker's tasks.

        Attributes:
            ...  # The specific worker input model attributes are defined elsewhere.
        """
    class WorkerOutput(TaskOutput):
        """Output model for the worker.

        This class defines the output model for the worker. It specifies the format of the output
        data produced by the worker's tasks.

        Attributes:
            ...  # The specific worker output model attributes are defined elsewhere.
        """

    def __init__(
            self, task_def_template: type[BaseTaskdef] | type[DefaultTaskDefinition] | None = None
    ) -> None:
        self.task_def_template = task_def_template
        self.task_def = self._task_definition_builder(self.task_def_template)

    @classmethod
    def _task_definition_builder(
            cls, task_def_template: type[BaseTaskdef] | type[DefaultTaskDefinition] | None = None
    ) -> TaskDefinition:
        """Build the task definition for the worker.

        This method constructs the task definition for the worker based on the worker's
        WorkerDefinition, WorkerInput, and WorkerOutput attributes.

        Args:
            task_def_template (type[BaseTaskdef] | type[DefaultTaskDefinition] | None, optional):
                An optional template task definition. Defaults to None.

        Returns:
            TaskDefinition: The task definition for the worker.
        """
        cls._validate()

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
        """Register the worker with the conductor client.

        This method registers the worker with the specified FrinxConductorWrapper. It provides the
        task type, task definition, and an execution wrapper to handle task execution.

        Args:
            conductor_client (FrinxConductorWrapper): The FrinxConductorWrapper instance to register
                the worker with.

        Returns:
            None
        """
        conductor_client.register(
            task_type=self.task_def.name,
            task_definition=self.task_def.dict(by_alias=True, exclude_none=True),
            exec_function=self._execute_wrapper,
        )

    @abstractmethod
    def execute(self, worker_input: Any) -> TaskResult[Any]:
        """Execute the worker logic.

        This abstract method should be implemented by subclasses to define the specific logic
        for the worker. It takes a worker_input parameter, which is of type Any to allow
        implementation flexibility for subclasses.

        Args:
            worker_input (Any): The input data for the worker.

        Returns:
            TaskResult[Any]: The task result produced by the worker's execution.
        """
        # worker_input parameter has to be of type any, otherwise all other subclasses of WorkerImpl would
        # violate Liskov substitution principle.
        # https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        pass

    @classmethod
    def _execute_wrapper(cls, task: RawTaskIO) -> Any:
        """Wrap the execution of the worker logic.

        This internal method wraps the execution of the worker logic, handling the task type
        and reporting any errors or exceptions that may occur during execution.

        Args:
            task (RawTaskIO): The raw task data from the conductor.

        Returns:
            Any: The task result produced by the worker's execution.
        """
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
        """Execute the worker logic and handle error reporting.

        This internal method executes the worker logic, transforming the input data as needed,
        measuring execution time, and handling errors and exceptions.

        Args:
            task (RawTaskIO): The raw task data from the conductor.

        Returns:
            RawTaskIO: The raw task data representing the task result.
        """
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
        """Transform input data to JSON format.

        This internal method transforms input data value to JSON format for specific fields in the
        worker input model.

        Args:
            input_data (DictAny): The input data dictionary.

        Returns:
            DictAny: The transformed input data dictionary.
        """
        for k, v in cls.WorkerInput.__fields__.items():
            if v.outer_type_ == ListStr \
                    or v.outer_type_ == DictAny \
                    or v.outer_type_ == dict \
                    or v.outer_type_ == DictStr:
                if type(input_data.get(k)) == str:
                    try:
                        input_data[k] = json_loads(str(input_data.get(k)))
                    except JSONDecodeError as e:
                        raise Exception(f'Worker input {k} is invalid JSON, {e}')
        return input_data

    @classmethod
    def _validate(cls) -> None:
        """Validate the WorkerInput and WorkerOutput subclasses.

        This method checks that the WorkerInput and WorkerOutput classes are subclasses of TaskInput
        and TaskOutput, respectively. If not, it raises a TypeError.

        Returns:
            None
        """
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
