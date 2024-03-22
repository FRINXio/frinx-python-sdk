from __future__ import annotations

import logging
import time
import traceback
from abc import abstractmethod
from functools import reduce
from json import JSONDecodeError
from json import loads as json_loads
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeAlias
from typing import Union

from pydantic import ValidationError

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

if TYPE_CHECKING:
    from frinx.client.v2.frinx_conductor_wrapper import FrinxConductorWrapper


logger = logging.getLogger(__name__)
metrics = Metrics()

RawTaskIO: TypeAlias = dict[str, Any]
TaskExecLog: TypeAlias = str


class WorkerImpl:
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

        # TODO maybe exist better way how to handle this case
        for attr_name, attr_value in self.__class__.__dict__.items():
            if (not attr_name.startswith('__')
                    and not callable(attr_value)
                    and not isinstance(attr_value, classmethod)
                    and not isinstance(attr_value, staticmethod)):
                self.__setattr__(attr_name, attr_value)

    def _param_parser(self) -> Any:
        params = {}
        for param in self.WorkerDefinition.model_fields.values():
            params[param.alias] = param.default
            if param.alias == 'inputKeys':
                values = []
                for key, field in self.WorkerInput.model_fields.items():
                    values.append(field.alias or key)
                if values:
                    params[param.alias] = values
            if param.alias == 'outputKeys':
                values = []
                for key, field in self.WorkerOutput.model_fields.items():
                    values.append(field.alias or key)
                if values:
                    params[param.alias] = values

        # Create Description in JSON format
        params['description'] = jsonify_description(
            params['description'], params['labels'], params['rbac']
        )

        params.pop('labels')
        params.pop('rbac')

        return params

    def _task_definition_builder(
            self, task_def_template: type[BaseTaskdef] | type[DefaultTaskDefinition] | None = None
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
        self._validate()

        params = self._param_parser()

        for k, v in self.WorkerInput.model_fields.items():
            if v.annotation == ListStr \
                    or v.annotation == DictAny \
                    or v.annotation == dict \
                    or v.annotation == DictStr:
                pass

        if task_def_template is None:
            task_def_template = DefaultTaskDefinition.model_fields.items()  # type: ignore
        else:
            task_def_template = task_def_template.model_fields.items()  # type: ignore

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
        logger.info('%s', self.task_def.name)
        logger.debug('Worker definition: %s', self.task_def.model_dump(by_alias=True, exclude_none=True))
        conductor_client.register(task_blueprint=self)

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

    def exception_response_handler(self, error: Exception, **kwargs: Any) -> TaskResult[WorkerOutput]:

        error_name: str = error.__class__.__name__
        execution_properties: TaskExecutionProperties = kwargs.get('execution_properties', TaskExecutionProperties())

        task_result: TaskResult[Any] = TaskResult(
            status=TaskResultStatus.FAILED,
            logs=[TaskExecLog(f'{error_name}: {error}')]
        )

        match error:
            case ValidationError():
                formatted_error: DictAny = self._validate_exception_format(error)
                task_result.logs = [TaskExecLog(f'{error_name}: {formatted_error}')]

                if execution_properties.pass_worker_input_exception_to_task_output:
                    task_result.output = self._parse_exception_output_path_to_dict(
                        dot_path={
                            execution_properties.worker_input_exception_task_output_path: formatted_error
                        }
                    )

        logger.error('%s error occurred: %s \n%s', error_name, error, str(traceback.format_exc()))
        return task_result

    def execute_wrapper(self, task: RawTaskIO) -> Any:
        """Wrap the execution of the worker logic.

        This internal method wraps the execution of the worker logic, handling the task type
        and reporting any errors or exceptions that may occur during execution.

        Args:
            task (RawTaskIO): The raw task data from the conductor.

        Returns:
            Any: The task result produced by the worker's execution.
        """
        execution_properties = self.ExecutionProperties()
        task_type = str(task.get('taskType'))
        increment_task_poll(metrics, task_type)

        try:
            logger.debug('Executing task %s:', task)
            task_result: RawTaskIO = self._execute_func(task, execution_properties)
            logger.debug('Task result %s:', task_result)
            return task_result
        except Exception as error:
            increment_task_execution_error(metrics, task_type, error)
            increment_uncaught_exception(metrics, task_type)
            return self.exception_response_handler(
                error=error,
                execution_properties=execution_properties
            ).model_dump()

    def _execute_func(self, task: RawTaskIO, execution_properties: ExecutionProperties) -> RawTaskIO:
        """Execute the worker logic and handle error reporting.

        This internal method executes the worker logic, transforming the input data as needed,
        measuring execution time, and handling errors and exceptions.

        Args:
            task (RawTaskIO): The raw task data from the conductor.

        Returns:
            RawTaskIO: The raw task data representing the task result.
        """
        input_data: DictAny = task['inputData']

        if execution_properties.exclude_empty_inputs:
            logger.debug('Worker input data before removing empty elements: %s:', input_data)
            input_data = remove_empty_elements_from_root_dict(task['inputData'])
            logger.debug('Worker input data after removing empty elements: %s:', input_data)

        if execution_properties.transform_string_to_json_valid:
            logger.debug('Worker input data before json serialization: %s:', input_data)
            input_data = self._transform_input_data_to_json(input_data)
            logger.debug('Worker input data after json serialization: %s:', input_data)

        try:
            worker_input = self.WorkerInput.model_validate(input_data)
            worker_input._task_id = task.get('taskId', None)
            worker_input._workflow_instance_id = task.get('workflowInstanceId', None)
            worker_input._workflow_type = task.get('workflowType', None)
        except ValidationError as error:
            raise error

        if not metrics.settings.metrics_enabled:
            return self.execute(worker_input).model_dump()

        start_time = time.time()
        task_result: RawTaskIO = self.execute(worker_input).model_dump()
        finish_time = time.time()
        record_task_execute_time(metrics, str(task.get('taskType')), finish_time - start_time)
        return task_result

    def _transform_input_data_to_json(self, input_data: DictAny) -> DictAny:
        """Transform input data to JSON format.

        This internal method transforms input data value to JSON format for specific fields in the
        worker input model.

        Args:
            input_data (DictAny): The input data dictionary.

        Returns:
            DictAny: The transformed input data dictionary.
        """
        for k, v in self.WorkerInput.model_fields.items():
            if v.annotation in (
                list, ListStr, dict, DictStr, DictAny, Union[DictStr, None],
                Union[ListStr, None], Union[DictAny, None],
                Union[list, None], Union[dict, None]
            ):
                if type(input_data.get(k)) == str:
                    try:
                        input_data[k] = json_loads(str(input_data.get(k)))
                    except JSONDecodeError as e:
                        raise Exception(f'Worker input {k} is invalid JSON, {e}')
        return input_data

    def _validate(self) -> None:
        """Validate the WorkerInput and WorkerOutput subclasses.

        This method checks that the WorkerInput and WorkerOutput classes are subclasses of TaskInput
        and TaskOutput, respectively. If not, it raises a TypeError.

        Returns:
            None
        """
        if not issubclass(self.WorkerInput, TaskInput):
            error_msg = (
                "Expecting task input model to be a subclass of "
                f"'{TaskInput.__qualname__}', not '{self.WorkerInput.__qualname__}'"
            )
            logger.error(error_msg)
            raise TypeError(error_msg)

        if not issubclass(self.WorkerOutput, TaskOutput):
            error_msg = (
                "Expecting task output model to be a subclass of "
                f"'{TaskOutput.__qualname__}', not '{self.WorkerOutput.__qualname__}'"
            )
            logger.error(error_msg)
            raise TypeError(error_msg)

    def _validate_exception_format(self, error: ValidationError) -> DictAny:
        """Converts a pydantic.ValidationError loc tuple to a dictionary representing the path or value.

        Args:
            error (ValidationError): An instance of pydantic.ValidationError.

        Returns:
            Dict[str, Dict[str, Union[str, int]]]: Formatted information about the error.
        """

        formatted_error = {}

        def _loc_to_dot_sep(loc: tuple[Union[str, int], ...]) -> str:
            path: str = ''
            for i, x in enumerate(loc):
                if isinstance(x, str):
                    if i > 0:
                        path += '.'
                    path += x
                elif isinstance(x, int):
                    path += f'[{x}]'
                else:
                    raise TypeError('Unexpected type')
            return path

        for err in error.errors():
            formatted_error[str(_loc_to_dot_sep(err['loc']))] = dict(
                type=err.get('type', 'Unknown'),
                message=err.get('msg', '')
            )
        return formatted_error

    @staticmethod
    def _parse_exception_output_path_to_dict(dot_path: DictAny) -> DictAny:
        """Parse a dictionary with keys in dot notation and convert it into a nested dictionary.

        Args:
            dot_path (DictAny): A dictionary with keys in dot notation.

        Returns:
            DictAny: A nested dictionary representing the parsed structure.

        Example:
            >>> input_dict = {'a.b.c': 42, 'x.y': 'hello'}
            >>> WorkerImpl._parse_exception_output_path_to_dict(input_dict)
            {'a': {'b': {'c': 42}}, 'x': {'y': 'hello'}}
        """
        output: DictAny = {}
        for key, value in dot_path.items():
            path = key.split('.')
            target = reduce(lambda d, k: d.setdefault(k, {}), path[:-1], output)
            target[path[-1]] = value
        return output
