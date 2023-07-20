from frinx.common.workflow.task import SimpleTask
from frinx.common.workflow.task import SimpleTaskInputParameters
from frinx.common.workflow.task import TaskType
from frinx.workers.http_workers.http_workers import Http
from frinx.workflows.http_workflows.generic import HTTPWorkflowService


class PostToSlack(HTTPWorkflowService.GenericRequest):
#||=====================================================================================||
    name: str = 'Post_to_Slack'
    version: int = 1
    description: str = 'Post a message to your favorite Slack channel'
    restartable: bool = True
    labels: list[str] = ['SLACK', 'HTTP']
    schema_version: int = 2
    workflow_status_listener_enabled: bool = False

    def workflow_builder(self, workflow_inputs: HTTPWorkflowService.GenericRequest.WorkflowInput) -> None:
    #|-----------------------------------------------------------------------------------|
        http_request = { 
            'body': {'text': '${workflow.input.body}'},
            'method': 'POST',
            'uri': 'https://hooks.slack.com/services/${workflow.input.uri}'
        }

        self.tasks.append(
            SimpleTask(
                name=Http.HttpTask,
                type=TaskType.HTTP,
                input_parameters=SimpleTaskInputParameters(http_request=http_request),
                task_reference_name='Generic http task'
            )
        )
