from typing import Literal

from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.frinx_rest import UNICONFIG_URL_BASE
from frinx.common.type_aliases import DictAny
from frinx.common.worker.service import ServiceWorkersImpl
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.worker import WorkerImpl
from frinx.services.uniconfig.connection_manager import install_node
from frinx.services.uniconfig.connection_manager import uninstall_node


class ConnectionManager(ServiceWorkersImpl):
    class InstallNode(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Install_node_RPC'
            description: str = 'Install node to Uniconfig'

        class WorkerInput(TaskInput):
            node_id: str
            connection_type: Literal['netconf', 'cli']
            install_params: DictAny
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            response = install_node(
                node_id=worker_input.node_id,
                connection_type=worker_input.connection_type,
                install_params=worker_input.install_params,
                uniconfig_url_base=worker_input.uniconfig_url_base
            )
            return TaskResult(status=TaskResultStatus.COMPLETED, output=self.WorkerOutput(output=response.json()))

    class UninstallNode(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Uninstall_node_RPC'
            description: str = 'Uninstall node from Uniconfig'

        class WorkerInput(TaskInput):
            node_id: str
            connection_type: Literal['netconf', 'cli']
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            response = uninstall_node(
                node_id=worker_input.node_id,
                connection_type=worker_input.connection_type,
                uniconfig_url_base=worker_input.uniconfig_url_base
            )
            return TaskResult(status=TaskResultStatus.COMPLETED, output=self.WorkerOutput(output=response.json()))
