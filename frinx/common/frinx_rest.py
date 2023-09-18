import os
from types import MappingProxyType
from typing import Any

# RBAC CONFIGURATION
X_TENANT_ID = os.getenv('X_TENANT_ID', 'frinx')
X_FROM = os.getenv('X_FROM', 'fm-base-workers')
X_AUTH_USER_GROUP = os.getenv('X_AUTH_USER_GROUP', 'network-admin')

# SET SERVICES URL VARIABLES
UNICONFIG_URL_BASE = os.getenv('UNICONFIG_URL_BASE', 'http://uniconfig:8181/rests')
CONDUCTOR_URL_BASE = os.getenv('CONDUCTOR_URL_BASE', 'http://workflow-proxy:8088/proxy/api')
INVENTORY_URL_BASE = os.getenv('INVENTORY_URL_BASE', 'http://inventory:8000/graphql')
INFLUXDB_URL_BASE = os.getenv('INFLUXDB_URL_BASE', 'http://influxdb:8086')
RESOURCE_MANAGER_URL_BASE = os.getenv('RESOURCE_MANAGER_URL_BASE', 'http://resource-manager:8884/query')
SCHELLAR_URL_BASE = os.getenv('SCHELLAR_URL_BASE', 'http://schellar:3000/query')
KRAKEND_URL_BASE = os.getenv('KRAKEND_URL_BASE', 'http://krakend:8080')
UNICONFIG_ZONE_URL_TEMPLATE = os.getenv('UNICONFIG_ZONE_URL_TEMPLATE', 'http://{uc}:8181/rests')

# URL HEADERS
UNICONFIG_HEADERS = MappingProxyType({'Content-Type': 'application/json'})
UNICONFIG_REQUEST_PARAMS: MappingProxyType[str, Any] = MappingProxyType({})

CONDUCTOR_HEADERS = MappingProxyType(
    {
        'Content-Type': 'application/json',
        'x-tenant-id': X_TENANT_ID,
        'from': X_FROM,
        'x-auth-user-groups': X_AUTH_USER_GROUP
    }
)

INVENTORY_HEADERS = MappingProxyType(
    {
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Keep-Alive': 'timeout=5',
        'x-tenant-id': X_TENANT_ID,
    }
)

SCHELLAR_HEADERS = MappingProxyType({
    'Content-Type': 'application/json',
    'Accept': 'application/json',
})

ADDITIONAL_UNICONFIG_REQUEST_PARAMS = MappingProxyType(
    {
        'verify': False,
        'headers': UNICONFIG_HEADERS
    }
)
