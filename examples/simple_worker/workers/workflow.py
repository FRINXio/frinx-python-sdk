from frinx.common.conductor_enums import TimeoutPolicy
from frinx.common.type_aliases import ListStr
from frinx.common.workflow.task import SimpleTask
from frinx.common.workflow.task import SimpleTaskInputParameters
from frinx.common.workflow.workflow import FrontendWFInputFieldType
from frinx.common.workflow.workflow import WorkflowImpl
from frinx.common.workflow.workflow import WorkflowInputField

from .simple_worker import Echo


class TestWorkflow(WorkflowImpl):
    name: str = 'Simple_workflow'
    version: int = 1
    description: str = 'Simple workflow'
    labels: ListStr = ['TEST']
    timeout_seconds: int = 60 * 5
    timeout_policy: TimeoutPolicy = TimeoutPolicy.TIME_OUT_WORKFLOW

    class WorkflowInput(WorkflowImpl.WorkflowInput):
        text: WorkflowInputField = WorkflowInputField(
            name='text',
            frontend_default_value='Hello world',
            description='Custom string',
            type=FrontendWFInputFieldType.STRING,
        )

    class WorkflowOutput(WorkflowImpl.WorkflowOutput):
        text: str

    def workflow_builder(self, workflow_inputs: WorkflowInput) -> None:

        echo_task = SimpleTask(
            name=Echo,
            task_reference_name='echo',
            input_parameters=SimpleTaskInputParameters(
                input=workflow_inputs.text.wf_input
            )
        )

        self.tasks.append(echo_task)

        self.output_parameters = self.WorkflowOutput(
            text=echo_task.output_ref()
        ).dict()
