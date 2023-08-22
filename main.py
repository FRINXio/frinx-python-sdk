import os

os.environ['UNICONFIG_URL_BASE'] = 'http://localhost/api/uniconfig'
os.environ['CONDUCTOR_URL_BASE'] = 'http://127.0.0.1:8088/proxy/api'
os.environ['INVENTORY_URL_BASE'] = 'http://localhost/api/inventory'
os.environ['INFLUXDB_URL_BASE'] = 'http://localhost:8086'
os.environ['RESOURCE_MANAGER_URL_BASE'] = 'http://localhost/api/resource'

import logging

from frinx.workers.http_workers.http_workers import HTTPWorkersService
from frinx.workers.utils_workers.utils_service import UtilsService
from frinx.workflows.http_workflows.http_workflows_service import HTTPWorkflowService
from frinx.workflows.dynamic_fork.dynamic_fork_workflows_service import DynamicForkWFService
from frinx.common.logging import logging_common
from frinx.common.logging.logging_common import LoggerConfig
from frinx.common.logging.logging_common import Root
from frinx.client.frinx_conductor_wrapper import FrinxConductorWrapper
from frinx.common.frinx_rest import CONDUCTOR_URL_BASE
from frinx.common.frinx_rest import CONDUCTOR_HEADERS


def register_tasks(conductor_client):
    logging.info('Register HTTP workers')
    HTTPWorkersService().register(conductor_client)
    logging.info('Register UTILS workers')
    UtilsService().register(conductor_client)


def register_workflows():
    logging.info('Register HTTP workflows')
    HTTPWorkflowService().register(overwrite=True)
    logging.info('Register UTIL workflows')
    DynamicForkWFService().register(overwrite=True)


def main():
    logging_common.configure_logging(
        LoggerConfig(root=Root(level=os.environ.get('LOG_LEVEL', 'INFO').upper(), handlers=['console']))
    )
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
