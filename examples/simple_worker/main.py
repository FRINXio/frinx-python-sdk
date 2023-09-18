import logging
import os

from frinx.client.frinx_conductor_wrapper import FrinxConductorWrapper
from frinx.common.logging import logging_common
from frinx.common.logging.logging_common import LoggerConfig
from frinx.common.logging.logging_common import Root


def register_tasks(conductor_client: FrinxConductorWrapper) -> None:
    logging.info('Register tasks')
    from workers.simple_worker import Echo
    Echo().register(conductor_client=conductor_client)


def register_workflows() -> None:
    logging.info('Register workflows')
    from workers.workflow import TestWorkflow
    TestWorkflow().register(overwrite=True)


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
        polling_interval=float(os.environ.get('CONDUCTOR_POLL_INTERVAL', 0.1)),
        max_thread_count=int(os.environ.get('CONDUCTOR_THREAD_COUNT', 50)),
        headers=dict(CONDUCTOR_HEADERS),
    )

    register_tasks(conductor_client)
    register_workflows()
    conductor_client.start_workers()


if __name__ == '__main__':
    main()
