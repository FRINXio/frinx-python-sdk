import logging
import os

from frinx.client.v2.frinx_conductor_wrapper import FrinxConductorWrapper
from frinx.common.logging.config import LoggerConfig


def register_tasks(conductor_client: FrinxConductorWrapper) -> None:
    logging.info('Register tasks')
    from workers.test_worker import TestWorkers
    TestWorkers().register(conductor_client=conductor_client)


def register_workflows() -> None:
    logging.info('Register workflows')
    from workers.test_workflow import TestWorkflows
    TestWorkflows().register(overwrite=True)


def main() -> None:

    LoggerConfig().setup_logging()

    from frinx.common.telemetry.metrics import Metrics
    from frinx.common.telemetry.metrics import MetricsSettings

    Metrics(settings=MetricsSettings(metrics_enabled=True))

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
