from frinx.common.conductor_enums import WorkflowStatus
from frinx.common.type_aliases import ListStr
from frinx.common.workflow.task import SimpleTask
from frinx.common.workflow.task import SimpleTaskInputParameters
from frinx.common.workflow.task import TaskType
from frinx.common.workflow.workflow import FrontendWFInputFieldType
from frinx.common.workflow.workflow import WorkflowImpl
from frinx.common.workflow.workflow import WorkflowInputField
from frinx.workers.http_workers.http_workers import HTTPWorkersService

SLACK_WEBHOOK_ID_DEFAULT = 'T05ECRXU1B7/B05FA6EUAKA/8EPw07KLIxOUAhojfg2Fx7DH'
MESSAGE_TEXT_DEFAULT = 'Hello Slack!'

Worker = HTTPWorkersService.GenericHTTPWorker


class PostToSlack(WorkflowImpl):
    name: str = 'Post_to_Slack'
    version: int = 1
    description: str = 'Post a message to your favorite Slack channel'
    restartable: bool = True
    labels: ListStr = ['SLACK']

    class WorkflowInput(WorkflowImpl.WorkflowInput):
        slack_webhook_id: WorkflowInputField = WorkflowInputField(
            name='slack_webhook_id',
            description='The Slack webhook ID that you want to send this message to',
            frontend_default_value=SLACK_WEBHOOK_ID_DEFAULT,
            type=FrontendWFInputFieldType.STRING
        )
        message_text: WorkflowInputField = WorkflowInputField(
            name='message_text',
            description='The message that you want to send to Slack',
            frontend_default_value=MESSAGE_TEXT_DEFAULT,
            type=FrontendWFInputFieldType.TEXTAREA
        )

    class WorkflowOutput(WorkflowImpl.WorkflowOutput):
        status: WorkflowStatus

    def workflow_builder(self, workflow_inputs: WorkflowInput) -> None:
        worker_input = SimpleTaskInputParameters(
            uri=f'https://hooks.slack.com/services/{workflow_inputs.slack_webhook_id.wf_input}',
            body={'text': workflow_inputs.message_text.wf_input},
            method='POST'
        )

        self.tasks.append(
            SimpleTask(
                task_reference_name=Worker().task_def.name,
                input_parameters=worker_input,
                type=TaskType.SIMPLE,
                name=Worker
            )
        )
