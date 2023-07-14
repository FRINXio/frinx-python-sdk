
from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.frinx_rest import UNICONFIG_URL_BASE
from frinx.common.type_aliases import DictAny
from frinx.common.worker.service import ServiceWorkersImpl
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.worker import WorkerImpl
from frinx.services.uniconfig.snapshot_manager import create_snapshot
from frinx.services.uniconfig.snapshot_manager import delete_snapshot
from frinx.services.uniconfig.snapshot_manager import replace_config_with_snapshot


class SnapshotManager(ServiceWorkersImpl):
    class CreateSnapshot(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Create_snapshot_RPC'
            description: str = 'Create Uniconfig snapshot'

        class WorkerInput(TaskInput):
            node_ids: list[str]
            snapshot_name: str
            transaction_id: str
            uniconfig_server_id: str | None = None
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            response = create_snapshot(
                node_ids=worker_input.node_ids,
                snapshot_name=worker_input.snapshot_name,
                transaction_id=worker_input.transaction_id,
                uniconfig_server_id=worker_input.uniconfig_server_id,
                uniconfig_url_base=worker_input.uniconfig_url_base
            )
            return TaskResult(status=TaskResultStatus.COMPLETED, output=self.WorkerOutput(output=response.json()))

    class DeleteSnapshot(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Delete_snapshot_RPC'
            description: str = 'Delete Uniconfig snapshot'

        class WorkerInput(TaskInput):
            snapshot_name: str
            transaction_id: str
            uniconfig_server_id: str | None = None
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            response = delete_snapshot(
                snapshot_name=worker_input.snapshot_name,
                transaction_id=worker_input.transaction_id,
                uniconfig_server_id=worker_input.uniconfig_server_id,
                uniconfig_url_base=worker_input.uniconfig_url_base
            )
            return TaskResult(status=TaskResultStatus.COMPLETED, output=self.WorkerOutput(output=response.json()))

    class ReplaceConfigWithSnapshot(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Replace_config_with_snapshot_RPC'
            description: str = 'Replace Uniconfig CONFIG datastore with a snapshot'

        class WorkerInput(TaskInput):
            snapshot_name: str
            node_ids: list[str]
            transaction_id: str
            uniconfig_server_id: str | None = None
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            response = replace_config_with_snapshot(
                snapshot_name=worker_input.snapshot_name,
                node_ids=worker_input.node_ids,
                transaction_id=worker_input.transaction_id,
                uniconfig_server_id=worker_input.uniconfig_server_id,
                uniconfig_url_base=worker_input.uniconfig_url_base
            )
            return TaskResult(status=TaskResultStatus.COMPLETED, output=self.WorkerOutput(output=response.json()))
