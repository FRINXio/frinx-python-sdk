from frinx.common.conductor_enums import WorkflowStatus
from frinx.common.type_aliases import ListStr
from frinx.common.workflow.service import ServiceWorkflowsImpl
from frinx.common.workflow.task import TerminateTask
from frinx.common.workflow.task import TerminateTaskInputParameters
from frinx.common.workflow.workflow import FrontendWFInputFieldType
from frinx.common.workflow.workflow import WorkflowImpl
from frinx.common.workflow.workflow import WorkflowInputField
from frinx.common.workflow.task import SimpleTask
from frinx.common.workflow.task import SimpleTaskInputParameters
from frinx.common.workflow.task import DecisionTask
from frinx.common.workflow.task import DecisionTaskInputParameters
from frinx.common.workflow.task import DynamicForkTask
from frinx.common.workflow.task import DynamicForkTaskInputParameters
from frinx.common.workflow.task import JoinTask
from frinx.workers.wf_input_handlers.wf_input_handlers_service import WFInputHandlersService


# TODO: refactor
class DynamicForkWFService(ServiceWorkflowsImpl):

    class DynamicFork(WorkflowImpl):
        name: str = 'Dynamic_fork'
        description: str = 'A dynamic fork + join task with input validation'
        version: int = 1
        labels: ListStr = ['BASICS', 'UTILS']
        
        class WorkflowInput(WorkflowImpl.WorkflowInput):
            dynamic_tasks: WorkflowInputField = WorkflowInputField(
                name='dynamic_tasks',
                description='Tasks or sub-workflows running in parallel.',
                type=FrontendWFInputFieldType.TEXTAREA,
                frontend_default_value=None
            )

            expected_name: WorkflowInputField = WorkflowInputField(
                name='expectedName',
                description='Expected name of sub-tasks or sub-workflows.',
                type=FrontendWFInputFieldType.STRING,
                frontend_default_value=None
            )

            expected_type: WorkflowInputField = WorkflowInputField(
                name='expectedType',
                description='Expected type of sub-tasks or sub-workflows.',
                type=FrontendWFInputFieldType.STRING,
                frontend_default_value=None
            )

            dynamic_tasks_input: WorkflowInputField = WorkflowInputField(
                name='dynamic_tasks_input',
                description='Inputs to sub-tasks or sub-workflows.',
                type=FrontendWFInputFieldType.TEXTAREA,
                frontend_default_value=None
            )

        class WorkflowOutput(WorkflowImpl.WorkflowOutput):
            status: WorkflowStatus

        def workflow_builder(self, workflow_inputs: WorkflowInput) -> None:
            # NOTE: becouse output object wrapper in conductor frontend a.k.a. 'result' (Object)
            # can't be returned like origin type, validation do worker instead of lambda-task
            # e.g. Array always returns like Object

            validation = SimpleTask(
                name=WFInputHandlersService.ForkJoinWFInputHandler,
                task_reference_name='validation',
                input_parameters=SimpleTaskInputParameters(
                    dynamic_tasks=workflow_inputs.dynamic_tasks.wf_input,
                    expected_name=workflow_inputs.expected_name.wf_input,
                    expected_type=workflow_inputs.expected_type.wf_input,
                    dynamic_tasks_input=workflow_inputs.dynamic_tasks_input.wf_input
                )
            )

            termination = TerminateTask(
                name='terminateTask',
                task_reference_name='termination',
                input_parameters=TerminateTaskInputParameters(
                    termination_status=WorkflowStatus.FAILED,
                    termination_reason=validation.output_ref('errors'),
                    workflow_output={'output': validation.output_ref('errors')}
                )
            )

            dynamic_fork = DynamicForkTask(
                name='dynamicForkTask',
                task_reference_name='dynamic_fork',
                dynamic_fork_tasks_param='dynamic_tasks',
                dynamic_fork_tasks_input_param_name='dynamic_tasks_input',
                input_parameters=DynamicForkTaskInputParameters(
                    dynamic_tasks=validation.output_ref('result.dynamic_tasks'),
                    dynamic_tasks_input=validation.output_ref('result.dynamic_tasks_input')
                )
            )

            join = JoinTask(
                name='joinTask',
                task_reference_name='join'
            )

            def _js_case_expression() -> str:
                return """
                $.errors ? 'termination' : 'default'
                """

            decision = DecisionTask(
                name='decisionTask',
                task_reference_name='decision',
                default_case=[
                    dynamic_fork,
                    join,
                ],
                decision_cases={
                    'termination': [termination]
                },
                case_expression=_js_case_expression(),
                input_parameters=DecisionTaskInputParameters(
                    errors=validation.output_ref('errors')
                )
            )

            self.tasks = [
                validation,
                decision,
            ]
