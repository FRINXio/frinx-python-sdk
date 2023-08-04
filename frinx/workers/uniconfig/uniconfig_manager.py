from typing import Optional

import requests

from frinx.common.frinx_rest import UNICONFIG_HEADERS
from frinx.common.frinx_rest import UNICONFIG_URL_BASE
from frinx.common.type_aliases import DictAny
from frinx.common.worker.service import ServiceWorkersImpl
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskExecutionProperties
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.worker import WorkerImpl
from frinx.services.uniconfig.utils import class_to_json
from frinx.services.uniconfig.utils import uniconfig_zone_to_cookie
from frinx.workers.uniconfig import handle_response


class UniconfigManager(ServiceWorkersImpl):
    class CreateTransaction(WorkerImpl):

        from frinx.services.uniconfig.rest_api import CreateTransaction as UniconfigApi

        class ExecutionProperties(TaskExecutionProperties):
            exclude_empty_inputs: bool = True
            transform_string_to_json_valid: bool = True

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
            if self.UniconfigApi.request is None:
                raise Exception(f'Failed to create request {self.UniconfigApi.request}')

            response = requests.request(
                url=worker_input.uniconfig_url_base + self.UniconfigApi.uri,
                method=self.UniconfigApi.method,
                data=class_to_json(self.UniconfigApi.request()),
                headers=dict(UNICONFIG_HEADERS)
            )

            return handle_response(
                response,
                self.WorkerOutput(
                    transaction_id=response.cookies['UNICONFIGTXID'],
                    uniconfig_server_id=response.cookies['uniconfig_server_id']
                )
            )

    class CloseTransaction(WorkerImpl):
        from frinx.services.uniconfig.rest_api import CloseTransaction as UniconfigApi

        class ExecutionProperties(TaskExecutionProperties):
            exclude_empty_inputs: bool = True
            transform_string_to_json_valid: bool = True

        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Close_transaction_RPC'
            description: str = 'Close Uniconfig transaction'

        class WorkerInput(TaskInput):
            transaction_id: Optional[str]
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        def execute(self, worker_input: WorkerInput) -> TaskResult[None]:
            if self.UniconfigApi.request is None:
                raise Exception(f'Failed to create request {self.UniconfigApi.request}')

            response = requests.request(
                url=worker_input.uniconfig_url_base + self.UniconfigApi.uri,
                method=self.UniconfigApi.method,
                data=class_to_json(
                    self.UniconfigApi.request(
                    )
                ),
                cookies=uniconfig_zone_to_cookie(
                    transaction_id=worker_input.transaction_id
                ),
                headers=dict(UNICONFIG_HEADERS)
            )
            return handle_response(response)

    class CommitTransaction(WorkerImpl):
        from frinx.services.uniconfig.rest_api import CommitTransaction as UniconfigApi
        from frinx.services.uniconfig.uniconfig.manager.commit import Input as CommitInput

        class ExecutionProperties(TaskExecutionProperties):
            exclude_empty_inputs: bool = True
            transform_string_to_json_valid: bool = True

        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Commit_transaction_RPC'
            description: str = 'Commit Uniconfig transaction'

        class WorkerInput(TaskInput):
            confirmed_commit: bool = False
            validate_commit: bool = True
            rollback: bool | None = None
            skip_unreachable_nodes: bool | None = None
            transaction_id: Optional[str]
            uniconfig_server_id: str | None = None
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            if self.UniconfigApi.request is None:
                raise Exception(f'Failed to create request {self.UniconfigApi.request}')

            response = requests.request(
                url=worker_input.uniconfig_url_base + self.UniconfigApi.uri,
                method=self.UniconfigApi.method,
                data=class_to_json(
                    self.UniconfigApi.request(
                        input=self.CommitInput(
                            do_confirmed_commit=worker_input.confirmed_commit,
                            do_validate=worker_input.validate_commit,
                            do_rollback=worker_input.rollback,
                            skip_unreachable_nodes=worker_input.skip_unreachable_nodes,
                        )
                    )
                ),
                cookies=uniconfig_zone_to_cookie(
                    uniconfig_server_id=worker_input.uniconfig_server_id,
                    transaction_id=worker_input.transaction_id
                ),
                headers=dict(UNICONFIG_HEADERS)
            )

            return handle_response(response, self.WorkerOutput(output=response.json()))

    class ReplaceConfigWithOperational(WorkerImpl):
        from frinx.services.uniconfig.rest_api import ReplaceConfigWithOperational as UniconfigApi
        from frinx.services.uniconfig.uniconfig.manager.replaceconfigwithoperational import Input
        from frinx.services.uniconfig.uniconfig.manager.replaceconfigwithoperational import TargetNodes

        class ExecutionProperties(TaskExecutionProperties):
            exclude_empty_inputs: bool = True
            transform_string_to_json_valid: bool = True

        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_Replace_config_with_operational_RPC'
            description: str = 'Replace Uniconfig CONFIG datastore with operational datastore'

        class WorkerInput(TaskInput):
            node_ids: list[str]
            transaction_id: str
            uniconfig_server_id: str | None = None
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            if self.UniconfigApi.request is None:
                raise Exception(f'Failed to create request {self.UniconfigApi.request}')

            response = requests.request(
                url=worker_input.uniconfig_url_base + self.UniconfigApi.uri,
                method=self.UniconfigApi.method,
                data=class_to_json(
                    self.UniconfigApi.request(
                        input=self.Input(
                            target_nodes=self.TargetNodes(node=worker_input.node_ids),
                        )
                    )
                ),
                cookies=uniconfig_zone_to_cookie(
                    uniconfig_server_id=worker_input.uniconfig_server_id,
                    transaction_id=worker_input.transaction_id
                ),
                headers=dict(UNICONFIG_HEADERS)
            )

            return handle_response(response, self.WorkerOutput(output=response.json()))

    class SyncFromNetwork(WorkerImpl):
        from frinx.services.uniconfig.rest_api import SyncFromNetwork as UniconfigApi
        from frinx.services.uniconfig.uniconfig.manager.syncfromnetwork import Input
        from frinx.services.uniconfig.uniconfig.manager.syncfromnetwork import TargetNodes

        class ExecutionProperties(TaskExecutionProperties):
            exclude_empty_inputs: bool = True
            transform_string_to_json_valid: bool = True

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
            if self.UniconfigApi.request is None:
                raise Exception(f'Failed to create request {self.UniconfigApi.request}')

            response = requests.request(
                url=worker_input.uniconfig_url_base + self.UniconfigApi.uri,
                method=self.UniconfigApi.method,
                data=class_to_json(
                    self.UniconfigApi.request(
                        input=self.Input(
                            target_nodes=self.TargetNodes(node=worker_input.node_ids),
                        )
                    )
                ),
                cookies=uniconfig_zone_to_cookie(
                    uniconfig_server_id=worker_input.uniconfig_server_id,
                    transaction_id=worker_input.transaction_id
                ),
                headers=dict(UNICONFIG_HEADERS)
            )

            return handle_response(response, self.WorkerOutput(output=response.json()))

    class DryRunCommit(WorkerImpl):
        from frinx.services.uniconfig.dryrun.manager.dryruncommit import Input
        from frinx.services.uniconfig.dryrun.manager.dryruncommit import TargetNodes
        from frinx.services.uniconfig.rest_api import DryrunCommit as UniconfigApi

        class ExecutionProperties(TaskExecutionProperties):
            exclude_empty_inputs: bool = True
            transform_string_to_json_valid: bool = True

        class WorkerDefinition(TaskDefinition):
            name: str = 'UNICONFIG_dryrun_commit'
            description: str = 'Dryrun Commit uniconfig'

        class WorkerInput(TaskInput):
            do_rollback: Optional[bool] = False
            node: list[str]
            transaction_id: Optional[str]
            uniconfig_server_id: str | None = None
            uniconfig_url_base: str = UNICONFIG_URL_BASE

        class WorkerOutput(TaskOutput):
            output: DictAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            if self.UniconfigApi.request is None:
                raise Exception(f'Failed to create request {self.UniconfigApi.request}')

            response = requests.request(
                url=worker_input.uniconfig_url_base + self.UniconfigApi.uri,
                method=self.UniconfigApi.method,
                data=class_to_json(
                    self.UniconfigApi.request(
                        input=self.Input(
                            do_rollback=worker_input.do_rollback,
                            target_nodes=self.TargetNodes(
                                node=worker_input.node
                            )
                        )
                    )
                ),
                cookies=uniconfig_zone_to_cookie(
                    uniconfig_server_id=worker_input.uniconfig_server_id,
                    transaction_id=worker_input.transaction_id
                ),
                headers=dict(UNICONFIG_HEADERS)
            )

            return handle_response(response, self.WorkerOutput(output=response.json()))
