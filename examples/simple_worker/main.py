import logging
import os

from frinx.client.frinx_conductor_wrapper import FrinxConductorWrapper
from frinx.common.logging import logging_common
from frinx.common.logging.logging_common import LoggerConfig
from frinx.common.logging.logging_common import Root


def register_tasks(conductor_client: FrinxConductorWrapper) -> None:
    from frinx.workers.schellar.schellar_worker import Schellar
    from frinx.workers.test.test_worker import TestWorker
    from frinx.workers.uniconfig.cli_network_topology import CliNetworkTopology
    from frinx.workers.uniconfig.connection_manager import ConnectionManager
    from frinx.workers.uniconfig.snapshot_manager import SnapshotManager
    from frinx.workers.uniconfig.uniconfig_manager import UniconfigManager

    UniconfigManager().register(conductor_client)
    ConnectionManager().register(conductor_client)
    CliNetworkTopology().register(conductor_client)
    SnapshotManager().register(conductor_client)
    TestWorker().register(conductor_client)
    Schellar().register(conductor_client)


def register_workflows() -> None:
    logging.info('Register workflows')

    from frinx.workflows.schellar.schellar_workflows import SchellarWorkflows
    from frinx.workflows.test.test import TestForkWorkflow
    from frinx.workflows.test.test import TestWorkflow

    TestWorkflow().register(overwrite=True)
    TestForkWorkflow().register(overwrite=True)
    SchellarWorkflows().register(overwrite=True)


def main() -> None:

    logging_common.configure_logging(
        LoggerConfig(
            root=Root(
                level=os.environ.get('LOG_LEVEL', 'INFO').upper(),
                handlers=['console']
            )
        )
    )

    from frinx.common.telemetry.metrics import Metrics
    from frinx.common.telemetry.metrics import MetricsSettings

    Metrics(settings=MetricsSettings(metrics_enabled=True))

    from frinx.client.frinx_conductor_wrapper import FrinxConductorWrapper
    from frinx.common.frinx_rest import CONDUCTOR_HEADERS
    from frinx.common.frinx_rest import CONDUCTOR_URL_BASE

    conductor_client = FrinxConductorWrapper(
        server_url=CONDUCTOR_URL_BASE,
        polling_interval=0.1,
        max_thread_count=50,
        headers=CONDUCTOR_HEADERS.__dict__,
    )

    register_tasks(conductor_client)
    register_workflows()
    conductor_client.start_workers()


if __name__ == '__main__':
    main()
