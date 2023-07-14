
from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.frinx_rest import UNICONFIG_URL_BASE
from frinx.common.type_aliases import DictAny
from frinx.common.worker.service import ServiceWorkersImpl
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.worker import WorkerImpl
from frinx.services.uniconfig.uniconfig_manager import close_transaction
from frinx.services.uniconfig.uniconfig_manager import commit_transaction
from frinx.services.uniconfig.uniconfig_manager import create_transaction
from frinx.services.uniconfig.uniconfig_manager import replace_config_with_operational
from frinx.services.uniconfig.uniconfig_manager import sync_from_network


class UniconfigManager(ServiceWorkersImpl):
    class CreateTransaction(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Create_transaction_RPC'
            description: str = 'Create Uniconfig transaction'

        class WorkerInput(TaskInput):
            transaction_timeout: int | None = None
            use_dedicated_session: bool = False
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            transaction_id: str
            uniconfig_server_id: str | None

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            response = create_transaction(
                transaction_timeout=worker_input.transaction_timeout,
                use_dedicated_session=worker_input.use_dedicated_session,
                uniconfig_url_base=worker_input.uniconfig_url_base
            )
            cookies: DictAny = response.cookies.get_dict()  # type: ignore
            transaction_id: str = cookies['UNICONFIGTXID']
            uniconfig_server_id: str | None = cookies.get('uniconfig_server_id')
            return TaskResult(
                status=TaskResultStatus.COMPLETED,
                output=self.WorkerOutput(transaction_id=transaction_id, uniconfig_server_id=uniconfig_server_id)
            )

    class CloseTransaction(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Close_transaction_RPC'
            description: str = 'Close Uniconfig transaction'

        class WorkerInput(TaskInput):
            transaction_id: str
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        def execute(self, worker_input: WorkerInput) -> TaskResult[None]:
            close_transaction(transaction_id=worker_input.transaction_id)
            return TaskResult(status=TaskResultStatus.COMPLETED)

    class CommitTransaction(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Commit_transaction_RPC'
            description: str = 'Commit Uniconfig transaction'

        class WorkerInput(TaskInput):
            transaction_id: str
            confirmed_commit: bool = False
            validate_commit: bool = True
            uniconfig_server_id: str | None = None
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            response = commit_transaction(
                transaction_id=worker_input.transaction_id,
                uniconfig_server_id=worker_input.uniconfig_server_id,
                confirmed_commit=worker_input.confirmed_commit,
                validate_commit=worker_input.validate_commit,
                uniconfig_url_base=worker_input.uniconfig_url_base
            )

            return TaskResult(status=TaskResultStatus.COMPLETED, output=self.WorkerOutput(output=response.json()))

    class ReplaceConfigWithOperational(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Replace_config_with_operational_RPC'
            description: str = 'Replace Uniconfig CONFIG datastore with OPER datastore'

        class WorkerInput(TaskInput):
            node_ids: list[str]
            transaction_id: str
            uniconfig_server_id: str | None = None
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            response = replace_config_with_operational(
                node_ids=worker_input.node_ids,
                transaction_id=worker_input.transaction_id,
                uniconfig_server_id=worker_input.uniconfig_server_id,
                uniconfig_url_base=worker_input.uniconfig_url_base
            )
            return TaskResult(status=TaskResultStatus.COMPLETED, output=self.WorkerOutput(output=response.json()))

    class SyncFromNetwork(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Sync_from_network_RPC'
            description: str = 'Synchronize configuration from network and the UniConfig nodes'

        class WorkerInput(TaskInput):
            node_ids: list[str]
            transaction_id: str
            uniconfig_server_id: str | None = None
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            response = sync_from_network(
                node_ids=worker_input.node_ids,
                transaction_id=worker_input.transaction_id,
                uniconfig_server_id=worker_input.uniconfig_server_id,
                uniconfig_url_base=worker_input.uniconfig_url_base
            )
            return TaskResult(status=TaskResultStatus.COMPLETED, output=self.WorkerOutput(output=response.json()))
