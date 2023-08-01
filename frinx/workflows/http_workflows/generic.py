from frinx.common.type_aliases import ListAny
from frinx.common.workflow.service import ServiceWorkflowsImpl
from frinx.common.workflow.task import SimpleTask
from frinx.common.workflow.task import SimpleTaskInputParameters
from frinx.common.workflow.workflow import FrontendWFInputFieldType
from frinx.common.workflow.workflow import WorkflowImpl
from frinx.common.workflow.workflow import WorkflowInputField
from frinx.workers.http_workers.http_workers import HTTPWorkersService


class HTTPWorkflowService(ServiceWorkflowsImpl):

    class GenericRequest(WorkflowImpl):
        name: str = 'Http_request'
        version: int = 1
        description: str = 'Simple HTTP request'
        labels: ListAny = ['HTTP'] 

        class WorkflowInput(WorkflowImpl.WorkflowInput):
            uri: WorkflowInputField = WorkflowInputField(
                name='uri',
                frontend_default_value='',
                description='Request url',
                type=FrontendWFInputFieldType.STRING,
            )

            content_type: WorkflowInputField = WorkflowInputField(
                name='contentType',
                frontend_default_value='application/json',
                description='Request contentType header',
                type=FrontendWFInputFieldType.STRING,
            )

            method: WorkflowInputField = WorkflowInputField(
                name='method',
                frontend_default_value='GET',
                description='Request method',
                # TODO: options = enum HTTPMethod instead of strings
                options=['GET', 'PUT', 'POST', 'DELETE', 'PATCH'],
                type=FrontendWFInputFieldType.SELECT,
            )

            headers: WorkflowInputField = WorkflowInputField(
                name='headers',
                frontend_default_value={},
                description='Request headers',
                type=FrontendWFInputFieldType.TEXTAREA,
            )

            body: WorkflowInputField = WorkflowInputField(
                name='body',
                frontend_default_value={},
                description='Request body',
                type=FrontendWFInputFieldType.TEXTAREA,
            )

            timeout: WorkflowInputField = WorkflowInputField(
                name='timeout',
                frontend_default_value=360,
                description='Request timeout',
                type=FrontendWFInputFieldType.INT,
            )

        class WorkflowOutput(WorkflowImpl.WorkflowOutput):
            # TODO: should return HTTPOutput or just partial like data ?
            data: str

        def workflow_builder(self, workflow_inputs: WorkflowInput) -> None:
            http_request = {
                'uri': workflow_inputs.uri.wf_input,
                'contentType': workflow_inputs.content_type.wf_input,
                'method': workflow_inputs.method.wf_input,
                'headers': workflow_inputs.headers.wf_input,
                'body': workflow_inputs.body.wf_input,
            }

            self.tasks.append(
                SimpleTask(
                    name=HTTPWorkersService.GenericHTTPWorker,
                    task_reference_name='http_task',
                    input_parameters=SimpleTaskInputParameters(http_request=http_request),
                )
            )
