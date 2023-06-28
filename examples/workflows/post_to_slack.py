import requests

from typing import Any

from frinx.common.type_aliases import ListAny
from frinx.common.workflow.workflow import WorkflowImpl
from frinx.common.workflow.workflow import WorkflowInputField
from frinx.common.workflow.workflow import FrontendWFInputFieldType
from frinx.common.workflow.task import SimpleTaskInputParameters
from frinx.common.workflow.task import SimpleTask
from frinx.common.workflow.task import TaskType
from frinx.common.worker.worker import WorkerImpl
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.conductor_enums import WorkflowStatus
from frinx.common.conductor_enums import TaskResultStatus


# TODO: add http task and worker from old repo and refactore


class HTTPWorker(WorkerImpl):
#||=====================================================================================||

    class WorkerDefinition(TaskDefinition):
    #||=================================================================================||
        name: str = 'http_get_generic'
        description: str = 'http_post_generic_ref_6EHC'
        labels: ListAny = ['HTTP']
        timeout_seconds: int = 60
        response_timeout_seconds: int = 60
    
    class WorkerInput(TaskInput):
    #||=================================================================================||
        http_request: dict[str, Any]

    class WorkerOutput(TaskOutput):
    #||=================================================================================||
        http_response: dict[str, Any]

    def execute(self, worker_input: WorkerInput) -> TaskResult:
    #|-----------------------------------------------------------------------------------|
        response: requests.Response = requests.request(**worker_input.http_request)
        return TaskResult(status=TaskResultStatus.COMPLETED, output=response)


class PostToSlack(WorkflowImpl):
#||=====================================================================================||
    name: str = 'Post_to_Slack'
    version: int = 1
    description: str = 'Post a message to your favorite Slack channel'
    restartable: bool = True
    labels: list[str] = ['SLACK', 'HTTP']
    schema_version: int = 2
    workflow_status_listener_enabled: bool = False

    class WorkflowInput(WorkflowImpl.WorkflowInput):
    #||=================================================================================||
        slack_webhook_id: WorkflowInputField = WorkflowInputField(
            name='slack_webhook_id',
            description='The Slack webhook ID that you want to send this message to',
            frontend_default_value='T05ECRXU1B7/B05FA6EUAKA/8EPw07KLIxOUAhojfg2Fx7DH',
            type=FrontendWFInputFieldType.STRING
        )
        message_text: WorkflowInputField = WorkflowInputField(
            name='message_text',
            description='The message that you want to send to Slack',
            frontend_default_value='Hello Slack! First workflow test.',
            type=FrontendWFInputFieldType.STRING
        )

    class WorkflowOutput(WorkflowImpl.WorkflowOutput):
    #||=================================================================================||
        status: WorkflowStatus

    def workflow_builder(self, workflow_inputs: WorkflowInput) -> None:
    #|-----------------------------------------------------------------------------------|
        http_request = { 
            'body': {'text': '${workflow.input.message_text}'},
            'connectionTimeOut': '3600',
            'contentType': 'application/json',
            'method': 'POST',
            'readTimeOut': '3600',
            'uri': 'https://hooks.slack.com/services/${workflow.input.slack_webhook_id}'
        }

        self.tasks.append(
            SimpleTask(
                name=HTTPWorker,
                type=TaskType.HTTP,
                input_parameters=SimpleTaskInputParameters(http_request=http_request),
                task_reference_name='http_post_generic_ref_6EHC'
            )
        )
