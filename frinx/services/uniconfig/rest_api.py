from __future__ import annotations

from typing import Any
from typing import Optional

from . import OperationsCloseTransactionPostRequest
from . import OperationsCommitPostRequest
from . import OperationsCommitPostResponse
from . import OperationsCreateSnapshotPostRequest
from . import OperationsCreateSnapshotPostResponse
from . import OperationsCreateTransactionPostRequest
from . import OperationsDeleteSnapshotPostRequest
from . import OperationsDeleteSnapshotPostResponse
from . import OperationsDiscoverPostRequest
from . import OperationsDiscoverPostResponse
from . import OperationsDryrunCommitPostRequest
from . import OperationsDryrunCommitPostResponse
from . import OperationsInstallMultipleNodesPostRequest
from . import OperationsInstallMultipleNodesPostResponse
from . import OperationsInstallNodePostRequest
from . import OperationsInstallNodePostResponse
from . import OperationsReplaceConfigWithOperationalPostRequest
from . import OperationsReplaceConfigWithOperationalPostResponse
from . import OperationsReplaceConfigWithSnapshotPostRequest
from . import OperationsReplaceConfigWithSnapshotPostResponse
from . import OperationsSyncFromNetworkPostRequest
from . import OperationsSyncFromNetworkPostResponse
from . import OperationsUninstallMultipleNodesPostRequest
from . import OperationsUninstallMultipleNodesPostResponse
from . import OperationsUninstallNodePostRequest
from . import OperationsUninstallNodePostResponse


class UniconfigRest:
    uri: str
    method: str
    request: Optional[Any]  # TODO use better type hint
    response: Optional[Any]  # TODO use better type hint


class Discover(UniconfigRest):
    uri = '/operations/discover'
    method = 'POST'
    request = OperationsDiscoverPostRequest
    response = OperationsDiscoverPostResponse


class CreateTransaction(UniconfigRest):
    uri = '/operations/create-transaction'
    method = 'POST'
    request = OperationsCreateTransactionPostRequest
    response = None


class CloseTransaction(UniconfigRest):
    uri = '/operations/close-transaction'
    method = 'POST'
    request = OperationsCloseTransactionPostRequest
    response = None


class CommitTransaction(UniconfigRest):
    uri = '/operations/commit'
    method = 'POST'
    request = OperationsCommitPostRequest
    response = OperationsCommitPostResponse


class SyncFromNetwork(UniconfigRest):
    uri = '/operations/sync-from-network'
    method = 'POST'
    request = OperationsSyncFromNetworkPostRequest
    response = OperationsSyncFromNetworkPostResponse


class ReplaceConfigWithOperational(UniconfigRest):
    uri = '/operations/replace-config-with-operational'
    method = 'POST'
    request = OperationsReplaceConfigWithOperationalPostRequest
    response = OperationsReplaceConfigWithOperationalPostResponse


class DryrunCommit(UniconfigRest):
    uri = '/operations/dryrun-commit'
    method = 'POST'
    request = OperationsDryrunCommitPostRequest
    response = OperationsDryrunCommitPostResponse


class CreateSnapshot(UniconfigRest):
    uri = '/operations/create-snapshot'
    method = 'POST'
    request = OperationsCreateSnapshotPostRequest
    response = OperationsCreateSnapshotPostResponse


class DeleteSnapshot(UniconfigRest):
    uri = '/operations/delete-snapshot'
    method = 'POST'
    request = OperationsDeleteSnapshotPostRequest
    response = OperationsDeleteSnapshotPostResponse


class ReplaceConfigWithSnapshot(UniconfigRest):
    uri = '/operations/replace-config-with-snapshot'
    method = 'POST'
    request = OperationsReplaceConfigWithSnapshotPostRequest
    response = OperationsReplaceConfigWithSnapshotPostResponse


class InstallNode(UniconfigRest):
    uri = '/operations/install-node'
    method = 'POST'
    request = OperationsInstallNodePostRequest
    response = OperationsInstallNodePostResponse


class InstallMultipleNodes(UniconfigRest):
    uri = '/operations/install-multiple-nodes'
    method = 'POST'
    request = OperationsInstallMultipleNodesPostRequest
    response = OperationsInstallMultipleNodesPostResponse


class UninstallNode(UniconfigRest):
    uri = '/operations/uninstall-node'
    method = 'POST'
    request = OperationsUninstallNodePostRequest
    response = OperationsUninstallNodePostResponse


class UninstallMultipleNodes(UniconfigRest):
    uri = '/operations/uninstall-multiple-nodes'
    method = 'POST'
    request = OperationsUninstallMultipleNodesPostRequest
    response = OperationsUninstallMultipleNodesPostResponse
