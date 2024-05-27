import copy
from typing import Any
from typing import cast

from pydantic import Field
from pydantic import ValidationError
from pytest import raises

from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.frinx_rest import X_FROM
from frinx.common.type_aliases import DictAny
from frinx.common.type_aliases import ListAny
from frinx.common.worker.task_def import DefaultTaskDefinition
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.worker import WorkerImpl
from tests.unit_tests.conftest import MockExecuteExcludePropertyFalse
from tests.unit_tests.conftest import MockExecuteProperties
from tests.unit_tests.conftest import MockExecuteTransformPropertyFalse


class TestTaskGenerator:
    def test_create_task_def(self) -> None:
        class HttpTask(WorkerImpl):
            class WorkerDefinition(TaskDefinition):
                name: str = 'HTTP_task'
                description: str = 'Generic http task'
                labels: ListAny = ['BASIC', 'HTTP']
                timeout_seconds: int = 360
                response_timeout_seconds: int = 360
                execution_name_space: str = 'execution_namespace'
                retry_count: int = 10
                concurrent_exec_limit: int = 5

            class WorkerInput(TaskInput):
                http_request: str | dict[str, Any] | None

            class WorkerOutput(TaskOutput):
                response: Any
                body: Any
                status_code: int = Field(..., alias='statusCode')
                cookies: dict[str, Any]

            def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
                return TaskResult(status=TaskResultStatus.COMPLETED)

        test_task = HttpTask(task_def_template=DefaultTaskDefinition).task_def.model_dump(
            exclude_none=True
        )

        test_mock = {
            'name': 'HTTP_task',
            'description': '{"description": "Generic http task", "labels": ["BASIC", "HTTP"]}',
            'retry_count': 10,
            'timeout_seconds': 360,
            'input_keys': ['http_request'],
            'output_keys': ['response', 'body', 'statusCode', 'cookies'],
            'timeout_policy': 'ALERT_ONLY',
            'retry_logic': 'FIXED',
            'retry_delay_seconds': 0,
            'response_timeout_seconds': 360,
            'concurrent_exec_limit': 5,
            'rate_limit_per_frequency': 0,
            'rate_limit_frequency_in_seconds': 5,
            'execution_name_space': 'execution_namespace',
            'owner_email': 'fm-base-workers',
        }

        assert test_mock == test_task

    def test_create_task_def_with_custom_default(self) -> None:
        class HttpTask(WorkerImpl):
            class WorkerDefinition(TaskDefinition):
                name: str = 'HTTP_task'
                description: str = 'Generic http task'
                labels: ListAny = ['BASIC', 'HTTP']
                timeout_seconds: int = 360
                response_timeout_seconds: int = 360

            class WorkerInput(TaskInput):
                http_request: str | dict[str, Any] | None

            class WorkerOutput(TaskOutput):
                response: Any
                body: Any
                status_code: int = Field(..., alias='statusCode')
                cookies: dict[str, Any]

            def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
                return TaskResult(status=TaskResultStatus.COMPLETED)

        class DefaultCustomTaskDefinition(DefaultTaskDefinition):
            limit_to_thread_count: int = 10

        test_task = HttpTask(task_def_template=DefaultCustomTaskDefinition).task_def.model_dump(
            exclude_none=True
        )
        test_mock = {
            'name': 'HTTP_task',
            'description': '{"description": "Generic http task", "labels": ["BASIC", "HTTP"]}',
            'retry_count': 0,
            'timeout_seconds': 360,
            'input_keys': ['http_request'],
            'output_keys': ['response', 'body', 'statusCode', 'cookies'],
            'timeout_policy': 'ALERT_ONLY',
            'retry_logic': 'FIXED',
            'retry_delay_seconds': 0,
            'response_timeout_seconds': 360,
            'rate_limit_per_frequency': 0,
            'rate_limit_frequency_in_seconds': 5,
            'owner_email': X_FROM,
            'limit_to_thread_count': 10,
        }

        assert test_mock == test_task

    def test_execute_properties_default(self) -> None:

        task = MockExecuteProperties()
        execution_properties = cast(WorkerImpl.ExecutionProperties, task.ExecutionProperties())

        response: DictAny = DictAny({
            'response': {
                'string_list': ['a', 'b', 'c'],
                'and_dict': {'a': 'a', 'b': {'c': 'c'}},
                'required_string': 'a',
                'optional_string': None
            }
        })

        result = task._execute_func(
            task=copy.deepcopy(task.TEST_WORKER_INPUTS),
            execution_properties=execution_properties
        )
        assert result.get('output') == response

    def test_execute_properties_exclude_empty_strings_disabled(self) -> None:
        task = MockExecuteExcludePropertyFalse()
        execution_properties = cast(WorkerImpl.ExecutionProperties, task.ExecutionProperties())

        response: DictAny = DictAny({
            'response': {
                'string_list': ['a', 'b', 'c'],
                'and_dict': {'a': 'a', 'b': {'c': 'c'}},
                'required_string': 'a',
                'optional_string': ''
            }
        })

        result = task._execute_func(
            task=copy.deepcopy(task.TEST_WORKER_INPUTS),
            execution_properties=execution_properties
        )
        assert result.get('output') == response

    def test_execute_properties_transform_string_to_json_valid_disabled(self) -> None:
        task = MockExecuteTransformPropertyFalse()
        execution_properties = cast(WorkerImpl.ExecutionProperties, task.ExecutionProperties())

        test_worker_inputs: DictAny = DictAny({
            'inputData': {
                'string_list': ['a', 'b', 'c'],
                'and_dict': {'a': 'a', 'b': {'c': 'c'}},
                'required_string': 'a',
                'optional_string': ''
            }
        })

        response: DictAny = DictAny({
            'response': {
                'string_list': ['a', 'b', 'c'],
                'and_dict': {'a': 'a', 'b': {'c': 'c'}},
                'required_string': 'a',
                'optional_string': None
            }
        })

        result = task._execute_func(
            task=copy.deepcopy(test_worker_inputs),
            execution_properties=execution_properties
        )
        assert result.get('output') == response

    def test_execute_properties_transform_string_to_json_valid_disabled_exception(self) -> None:

        task = MockExecuteTransformPropertyFalse()
        execution_properties = cast(WorkerImpl.ExecutionProperties, task.ExecutionProperties())
        task.ExecutionProperties.model_fields['transform_string_to_json_valid'].default = False

        with raises(ValidationError):
            task._execute_func(
                task=copy.deepcopy(task.TEST_WORKER_INPUTS),
                execution_properties=execution_properties
            )

    def test_execute_handle(self) -> None:

        worker_input_dict: DictAny = dict(
            inputData=dict(
            )
        )

        expected_result = {'output': {'error': {'error_name': 'ValidationError',
                                                'error_info':
                                                    {
                                                        'string_list':
                                                            {'type': 'missing', 'message': 'Field required'},
                                                        'and_dict':
                                                            {'type': 'missing', 'message': 'Field required'},
                                                        'required_string':
                                                            {'type': 'missing', 'message': 'Field required'}
                                                    }
                                                }
                                      }
                           }

        worker = MockExecuteProperties()
        result = worker.execute_wrapper(task=worker_input_dict)
        assert result.get('output') == expected_result
