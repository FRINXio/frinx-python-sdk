from typing import Optional

from pydantic import SerializeAsAny

from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.type_aliases import DictAny
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskExecutionProperties
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.worker import WorkerImpl
from frinx.common.workflow.workflow import FrontendWFInputFieldType
from frinx.common.workflow.workflow import WorkflowImpl
from frinx.common.workflow.workflow import WorkflowInputField

TEST_WORKER_INPUTS_COMMON: DictAny = DictAny({
    'inputData': {
        'string_list': '["a", "b", "c"]',
        'and_dict': '{"a": "a", "b": {"c": "c"}}',
        'required_string': 'a',
        'optional_string': ''
    }
})


class MockWorker(WorkerImpl):

    class WorkerDefinition(TaskDefinition):
        name: str = 'MockWorker'
        description: str = 'Helper class used in tests.'

    class WorkerInput(TaskInput):
        ...

    class WorkerOutput(TaskOutput):
        ...

    def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
        return TaskResult(status=TaskResultStatus.COMPLETED)


class MockWorkflow(WorkflowImpl):
    name: str = 'MockWorkflow'
    version: int = 1
    description: str = 'Helper class used in tests.'

    class WorkflowInput(WorkflowImpl.WorkflowInput):
        device_name: WorkflowInputField = WorkflowInputField(
            name='device_name',
            type=FrontendWFInputFieldType.STRING,
        )

        zone: WorkflowInputField = WorkflowInputField(
            name='zone',
            type=FrontendWFInputFieldType.STRING,
        )

    class WorkflowOutput(WorkflowImpl.WorkflowOutput):
        ...

    def workflow_builder(self, workflow_inputs: WorkflowInput) -> None:
        ...


class MockExecuteProperties(WorkerImpl):

    TEST_WORKER_INPUTS: DictAny = TEST_WORKER_INPUTS_COMMON

    class ExecutionProperties(TaskExecutionProperties):
        exclude_empty_inputs: bool = True
        transform_string_to_json_valid: bool = True
        pass_worker_input_exception_to_task_output: bool = True
        worker_input_exception_task_output_path: str = 'output.error'

    class WorkerDefinition(TaskDefinition):
        name: str = 'EXECUTION_PROPERTIES_task'
        description: str = 'Mock worker to test execution properties'

    class WorkerInput(TaskInput):
        string_list: list[str]
        and_dict: DictAny
        required_string: str
        optional_string: Optional[str] = None

    class WorkerOutput(TaskOutput):
        response: SerializeAsAny[TaskInput]

    def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
        return TaskResult(
            status=TaskResultStatus.COMPLETED,
            output=self.WorkerOutput(response=worker_input)
        )


class MockExecuteExcludePropertyFalse(WorkerImpl):

    TEST_WORKER_INPUTS: DictAny = TEST_WORKER_INPUTS_COMMON

    class ExecutionProperties(TaskExecutionProperties):
        exclude_empty_inputs: bool = False
        transform_string_to_json_valid: bool = True

    class WorkerDefinition(TaskDefinition):
        name: str = 'EXECUTION_PROPERTIES_task'
        description: str = 'Mock worker to test execution properties'

    class WorkerInput(TaskInput):
        string_list: list[str]
        and_dict: DictAny
        required_string: str
        optional_string: Optional[str] = None

    class WorkerOutput(TaskOutput):
        response: SerializeAsAny[TaskInput]

    def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
        return TaskResult(
            status=TaskResultStatus.COMPLETED,
            output=self.WorkerOutput(response=worker_input)
        )


class MockExecuteTransformPropertyFalse(WorkerImpl):

    TEST_WORKER_INPUTS: DictAny = TEST_WORKER_INPUTS_COMMON

    class ExecutionProperties(TaskExecutionProperties):
        exclude_empty_inputs: bool = True
        transform_string_to_json_valid: bool = False

    class WorkerDefinition(TaskDefinition):
        name: str = 'EXECUTION_PROPERTIES_task'
        description: str = 'Mock worker to test execution properties'

    class WorkerInput(TaskInput):
        string_list: list[str]
        and_dict: DictAny
        required_string: str
        optional_string: Optional[str] = None

    class WorkerOutput(TaskOutput):
        response: SerializeAsAny[TaskInput]

    def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
        return TaskResult(
            status=TaskResultStatus.COMPLETED,
            output=self.WorkerOutput(response=worker_input)
        )
