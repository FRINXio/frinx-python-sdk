import logging
import os

from frinx.common.logging import logging_common
from frinx.common.logging.logging_common import LoggerConfig
from frinx.common.logging.logging_common import Root


def debug_local():
    os.environ['UNICONFIG_URL_BASE'] = 'http://localhost/api/uniconfig'
    os.environ['CONDUCTOR_URL_BASE'] = os.environ.get('CONDUCTOR_URL_BASE', 'http://127.0.0.1:8088/proxy/api')
    os.environ['SCHELLAR_URL_BASE'] = os.environ.get('SCHELLAR_URL_BASE', 'http://127.0.0.1:3001/query')
    os.environ['INVENTORY_URL_BASE'] = 'http://localhost/api/inventory'
    os.environ['INFLUXDB_URL_BASE'] = 'http://localhost:8086'
    os.environ['RESOURCE_MANAGER_URL_BASE'] = 'http://localhost/api/resource'


def register_tasks(conductor_client):
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


def register_workflows():
    logging.info('Register workflows')

    from frinx.workflows.schellar.schellar_workflows import SchellarWorkflows
    from frinx.workflows.test.test import TestForkWorkflow
    from frinx.workflows.test.test import TestWorkflow

    TestWorkflow().register(overwrite=True)
    TestForkWorkflow().register(overwrite=True)
    SchellarWorkflows().register(overwrite=True)


def query_api():
    from frinx.common.graphql.client import GraphqlClient
    from frinx.common.graphql.graphql_types import schema_request
    from frinx.common.graphql.schema_converter import GraphqlJsonParser

    client = GraphqlClient(endpoint='http://127.0.0.1:3001/query')
    import frinx.services.schellar.model
    response = client.execute(schema_request)
    schema = GraphqlJsonParser(input_json=response)
    schema.export(frinx.services.schellar.model.__file__)


def main():

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
    debug_local()

    from frinx.client.frinx_conductor_wrapper import FrinxConductorWrapper
    from frinx.common.frinx_rest import CONDUCTOR_HEADERS
    from frinx.common.frinx_rest import CONDUCTOR_URL_BASE

    conductor_client = FrinxConductorWrapper(
        server_url=CONDUCTOR_URL_BASE,
        polling_interval=0.1,
        max_thread_count=50,
        headers=CONDUCTOR_HEADERS,
    )

    register_tasks(conductor_client)
    register_workflows()
    conductor_client.start_workers()


if __name__ == '__main__':
    main()
