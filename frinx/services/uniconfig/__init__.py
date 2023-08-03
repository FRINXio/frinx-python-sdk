# generated by datamodel-codegen:
#   filename:  uniconfigV3.yaml

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel

from .cli.unit.generic import configcoverage
from .cli.unit.generic import execute
from .cli.unit.generic import executeandexpect
from .cli.unit.generic import executeandread
from .cli.unit.generic import executeandreaduntil
from .connection.manager import changeadminstate
from .connection.manager import checkinstallednodes
from .connection.manager import dryrunmountnode
from .connection.manager import dryrununmountnode
from .connection.manager import getinstallednodes
from .connection.manager import installmultiplenodes
from .connection.manager import installnode
from .connection.manager import mountnode
from .connection.manager import uninstallmultiplenodes
from .connection.manager import uninstallnode
from .connection.manager import unmountnode
from .crypto import changeencryptionstatus
from .data.change.events import createdatachangesubscription
from .data.change.events import deletedatachangesubscription
from .data.change.events import showsubscriptiondata
from .device.discovery import discover
from .dryrun.manager import dryruncommit
from .journal import clearjournal
from .journal import readjournal
from .logging import disabledefaultdevicelogging
from .logging import disabledevicelogging
from .logging import disablelogging
from .logging import enabledefaultdevicelogging
from .logging import enabledevicelogging
from .logging import enablelogging
from .logging import setglobalhiddentypes
from .netconf.keystore import addkeystoreentry
from .netconf.keystore import addprivatekey
from .netconf.keystore import addtrustedcertificate
from .netconf.keystore import removekeystoreentry
from .netconf.keystore import removeprivatekey
from .netconf.keystore import removetrustedcertificate
from .notifications import createsubscription
from .restconf.logging import sethiddenhttpheaders
from .restconf.logging import sethiddenhttpmethods
from .schema.resources import registerrepository
from .snapshot.manager import createsnapshot
from .snapshot.manager import deletesnapshot
from .snapshot.manager import replaceconfigwithsnapshot
from .subtree.manager import bulkedit
from .subtree.manager import calculatesubtreediff
from .subtree.manager import calculatesubtreegitlikediff
from .subtree.manager import copymanytoone
from .subtree.manager import copyonetomany
from .subtree.manager import copyonetoone
from .template.manager import applytemplate
from .template.manager import createmultipletemplates
from .template.manager import gettemplateinfo
from .template.manager import gettemplatenodes
from .template.manager import upgradetemplate
from .transaction.log import revertchanges
from .uniconfig.manager import calculatediff
from .uniconfig.manager import calculategitlikediff
from .uniconfig.manager import checkedcommit
from .uniconfig.manager import commit
from .uniconfig.manager import compareconfig
from .uniconfig.manager import health
from .uniconfig.manager import isinsync
from .uniconfig.manager import replaceconfigwithoperational
from .uniconfig.manager import syncfromnetwork
from .uniconfig.manager import synctonetwork
from .uniconfig.manager import validate
from .uniconfig.query import queryconfig


class OperationsReadJournalPostRequest(BaseModel):
    pass

    class Config:
        allow_population_by_field_name = True


class OperationsClearJournalPostRequest(BaseModel):
    pass

    class Config:
        allow_population_by_field_name = True


class OperationsGetTemplateNodesPostRequest(BaseModel):
    pass

    class Config:
        allow_population_by_field_name = True


class Content(Enum):
    nonconfig = 'nonconfig'
    config = 'config'
    all = 'all'


class OperationsCreateTransactionPostRequest(BaseModel):
    pass

    class Config:
        allow_population_by_field_name = True


class OperationsHealthPostRequest(BaseModel):
    pass

    class Config:
        allow_population_by_field_name = True


class OperationsCloseTransactionPostRequest(BaseModel):
    pass

    class Config:
        allow_population_by_field_name = True


class OperationsConfigCoveragePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[configcoverage.Input] = None


class OperationsConfigCoveragePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[configcoverage.Output] = None


class OperationsExecutePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[execute.Input] = None


class OperationsExecutePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[execute.Output] = None


class OperationsExecuteAndExpectPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[executeandexpect.Input] = None


class OperationsExecuteAndExpectPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[executeandexpect.Output] = None


class OperationsExecuteAndReadPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[executeandread.Input] = None


class OperationsExecuteAndReadPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[executeandread.Output] = None


class OperationsExecuteAndReadUntilPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[executeandreaduntil.Input] = None


class OperationsExecuteAndReadUntilPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[executeandreaduntil.Output] = None


class OperationsGetInstalledNodesPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[getinstallednodes.Output] = None


class OperationsCheckInstalledNodesPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[checkinstallednodes.Input] = None


class OperationsCheckInstalledNodesPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[checkinstallednodes.Output] = None


class OperationsChangeEncryptionStatusPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[changeencryptionstatus.Input] = None


class OperationsChangeEncryptionStatusPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[changeencryptionstatus.Output] = None


class OperationsShowSubscriptionDataPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[showsubscriptiondata.Input] = None


class OperationsDeleteDataChangeSubscriptionPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[deletedatachangesubscription.Input] = None


class OperationsCreateDataChangeSubscriptionPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[createdatachangesubscription.Output] = None


class OperationsDiscoverPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[discover.Input] = None


class OperationsDiscoverPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[discover.Output] = None


class OperationsDryrunCommitPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[dryruncommit.Input] = None


class OperationsReadJournalPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[readjournal.Output] = None


class OperationsClearJournalPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[clearjournal.Output] = None


class OperationsEnableDefaultDeviceLoggingPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[enabledefaultdevicelogging.Input] = None


class OperationsDisableLoggingPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[disablelogging.Input] = None


class OperationsSetGlobalHiddenTypesPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[setglobalhiddentypes.Input] = None


class OperationsDisableDeviceLoggingPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[disabledevicelogging.Input] = None


class OperationsDisableDefaultDeviceLoggingPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[disabledefaultdevicelogging.Input] = None


class OperationsEnableDeviceLoggingPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[enabledevicelogging.Input] = None


class OperationsEnableLoggingPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[enablelogging.Input] = None


class OperationsAddTrustedCertificatePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[addtrustedcertificate.Input] = None


class OperationsRemoveKeystoreEntryPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[removekeystoreentry.Input] = None


class OperationsAddKeystoreEntryPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[addkeystoreentry.Input] = None


class OperationsRemoveTrustedCertificatePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[removetrustedcertificate.Input] = None


class OperationsAddPrivateKeyPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[addprivatekey.Input] = None


class OperationsRemovePrivateKeyPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[removeprivatekey.Input] = None


class OperationsCreateSubscriptionPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[createsubscription.Input] = None


class OperationsSetHiddenHttpHeadersPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[sethiddenhttpheaders.Input] = None


class OperationsRegisterRepositoryPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[registerrepository.Input] = None


class OperationsDeleteSnapshotPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[deletesnapshot.Input] = None


class OperationsCreateSnapshotPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[createsnapshot.Input] = None


class OperationsReplaceConfigWithSnapshotPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[replaceconfigwithsnapshot.Input] = None


class OperationsCalculateSubtreeDiffPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[calculatesubtreediff.Output] = None


class OperationsCalculateSubtreeGitLikeDiffPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[calculatesubtreegitlikediff.Output] = None


class OperationsApplyTemplatePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[applytemplate.Input] = None


class OperationsUpgradeTemplatePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[upgradetemplate.Input] = None


class OperationsGetTemplateInfoPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[gettemplateinfo.Input] = None


class OperationsGetTemplateInfoPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[gettemplateinfo.Output] = None


class OperationsGetTemplateNodesPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[gettemplatenodes.Output] = None


class OperationsRevertChangesPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[revertchanges.Input] = None


class OperationsSyncToNetworkPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[synctonetwork.Input] = None


class OperationsHealthPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[health.Output] = None


class OperationsReplaceConfigWithOperationalPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[replaceconfigwithoperational.Input] = None


class OperationsValidatePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[validate.Input] = None


class OperationsCommitPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[commit.Input] = None


class OperationsCheckedCommitPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[checkedcommit.Input] = None


class OperationsCompareConfigPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[compareconfig.Input] = None


class OperationsCalculateDiffPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[calculatediff.Input] = None


class OperationsSyncFromNetworkPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[syncfromnetwork.Input] = None


class OperationsCalculateGitLikeDiffPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[calculategitlikediff.Input] = None


class OperationsIsInSyncPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[isinsync.Input] = None


class OperationsQueryConfigPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[queryconfig.Input] = None


class OperationsQueryConfigPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[queryconfig.Output] = None


class OperationsUninstallNodePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[uninstallnode.Input] = None


class OperationsUninstallNodePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[uninstallnode.Output] = None


class OperationsUninstallMultipleNodesPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[uninstallmultiplenodes.Input] = None


class OperationsUninstallMultipleNodesPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[uninstallmultiplenodes.Output] = None


class OperationsGetInstalledNodesPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[getinstallednodes.Input] = None


class OperationsInstallNodePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[installnode.Input] = None


class OperationsInstallNodePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[installnode.Output] = None


class OperationsChangeAdminStatePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[changeadminstate.Input] = None


class OperationsChangeAdminStatePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[changeadminstate.Output] = None


class OperationsUnmountNodePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[unmountnode.Input] = None


class OperationsUnmountNodePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[unmountnode.Output] = None


class OperationsDryrunUnmountNodePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[dryrununmountnode.Input] = None


class OperationsDryrunUnmountNodePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[dryrununmountnode.Output] = None


class OperationsMountNodePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[mountnode.Input] = None


class OperationsMountNodePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[mountnode.Output] = None


class OperationsInstallMultipleNodesPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[installmultiplenodes.Input] = None


class OperationsInstallMultipleNodesPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[installmultiplenodes.Output] = None


class OperationsDryrunMountNodePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[dryrunmountnode.Input] = None


class OperationsDryrunMountNodePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[dryrunmountnode.Output] = None


class OperationsShowSubscriptionDataPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[showsubscriptiondata.Output] = None


class OperationsCreateDataChangeSubscriptionPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[createdatachangesubscription.Input] = None


class OperationsDryrunCommitPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[dryruncommit.Output] = None


class OperationsEnableDefaultDeviceLoggingPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[enabledefaultdevicelogging.Output] = None


class OperationsDisableLoggingPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[disablelogging.Output] = None


class OperationsSetGlobalHiddenTypesPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[setglobalhiddentypes.Output] = None


class OperationsDisableDeviceLoggingPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[disabledevicelogging.Output] = None


class OperationsDisableDefaultDeviceLoggingPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[disabledefaultdevicelogging.Output] = None


class OperationsEnableDeviceLoggingPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[enabledevicelogging.Output] = None


class OperationsEnableLoggingPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[enablelogging.Output] = None


class OperationsSetHiddenHttpHeadersPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[sethiddenhttpheaders.Output] = None


class OperationsSetHiddenHttpMethodsPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[sethiddenhttpmethods.Input] = None


class OperationsSetHiddenHttpMethodsPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[sethiddenhttpmethods.Output] = None


class OperationsRegisterRepositoryPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[registerrepository.Output] = None


class OperationsDeleteSnapshotPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[deletesnapshot.Output] = None


class OperationsCreateSnapshotPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[createsnapshot.Output] = None


class OperationsReplaceConfigWithSnapshotPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[replaceconfigwithsnapshot.Output] = None


class OperationsCopyOneToOnePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[copyonetoone.Input] = None


class OperationsCopyOneToOnePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[copyonetoone.Output] = None


class OperationsCopyOneToManyPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[copyonetomany.Input] = None


class OperationsCopyOneToManyPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[copyonetomany.Output] = None


class OperationsCalculateSubtreeDiffPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[calculatesubtreediff.Input] = None


class OperationsCopyManyToOnePostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[copymanytoone.Input] = None


class OperationsCopyManyToOnePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[copymanytoone.Output] = None


class OperationsCalculateSubtreeGitLikeDiffPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[calculatesubtreegitlikediff.Input] = None


class OperationsBulkEditPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[bulkedit.Input] = None


class OperationsBulkEditPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[bulkedit.Output] = None


class OperationsApplyTemplatePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[applytemplate.Output] = None


class OperationsCreateMultipleTemplatesPostRequest(BaseModel):
    class Config:
        allow_population_by_field_name = True

    input: Optional[createmultipletemplates.Input] = None


class OperationsCreateMultipleTemplatesPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[createmultipletemplates.Output] = None


class OperationsRevertChangesPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[revertchanges.Output] = None


class OperationsSyncToNetworkPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[synctonetwork.Output] = None


class OperationsReplaceConfigWithOperationalPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[replaceconfigwithoperational.Output] = None


class OperationsValidatePostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[validate.Output] = None


class OperationsCommitPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[commit.Output] = None


class OperationsCheckedCommitPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[checkedcommit.Output] = None


class OperationsCompareConfigPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[compareconfig.Output] = None


class OperationsCalculateDiffPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[calculatediff.Output] = None


class OperationsSyncFromNetworkPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[syncfromnetwork.Output] = None


class OperationsCalculateGitLikeDiffPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[calculategitlikediff.Output] = None


class OperationsIsInSyncPostResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True

    output: Optional[isinsync.Output] = None
