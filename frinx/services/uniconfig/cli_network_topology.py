import json

import requests

from frinx.common.frinx_rest import CLI_EXECUTE_AND_READ_URL
from frinx.common.frinx_rest import CLI_EXECUTE_URL
from frinx.common.frinx_rest import UNICONFIG_HEADERS
from frinx.common.frinx_rest import UNICONFIG_URL_BASE
from frinx.common.util import normalize_base_url


def execute_and_read(
    node_id: str,
    command: str,
    transaction_id: str,
    uniconfig_server_id: str | None = None,
    wait_for_output: int = 0,
    uniconfig_url_base: str | None = None
) -> requests.Response:
    """
    Execute command and read output.
    https://docs.frinx.io/frinx-uniconfig/user-guide/network-management-protocols/uniconfig_cli/#rpc-execute-and-read
    Args:
        node_id: Target node.
        command: Command to be executed.
        transaction_id: Transaction ID generated by Uniconfig.
        uniconfig_server_id: Uniconfig server id is used by load balancer to forward request to the correct Uniconfig
         node. It is required when using multi node deployment of Uniconfig.
        wait_for_output: Execute next command after n seconds after previous one.
        uniconfig_url_base: Override default Uniconfig url.

    Returns:
        Http response.
    """
    base_url = UNICONFIG_URL_BASE
    if uniconfig_url_base is not None:
        base_url = uniconfig_url_base

    url = normalize_base_url(base_url) + CLI_EXECUTE_AND_READ_URL.format(node_id)
    response = requests.post(
        url,
        data=json.dumps(
            {
                'input': {
                    'command': command,
                    'wait-for-output-timer': wait_for_output
                }
            }
        ),
        cookies={'UNICONFIGTXID': transaction_id, 'uniconfig_server_id': uniconfig_server_id},
        headers=UNICONFIG_HEADERS
    )

    response.raise_for_status()
    return response


def execute(
    node_id: str,
    command: str,
    transaction_id: str,
    uniconfig_server_id: str | None = None,
    uniconfig_url_base: str | None = None
) -> requests.Response:
    """
    Execute command.
    https://docs.frinx.io/frinx-uniconfig/user-guide/network-management-protocols/uniconfig_cli/#rpc-execute
    Args:
        node_id: Target node.
        command: Command to be executed.
        transaction_id: Transaction ID generated by Uniconfig.
        uniconfig_server_id: Uniconfig server id is used by load balancer to forward request to the correct Uniconfig
         node. It is required when using multi node deployment of Uniconfig.
        uniconfig_url_base: Override default Uniconfig url.

    Returns:
        Http response.
    """
    base_url = UNICONFIG_URL_BASE
    if uniconfig_url_base is not None:
        base_url = uniconfig_url_base

    url = normalize_base_url(base_url) + CLI_EXECUTE_URL.format(node_id)
    response = requests.post(
        url,
        data=json.dumps(
            {
                'input': {
                    'command': command
                }
            }
        ),
        cookies={'UNICONFIGTXID': transaction_id, 'uniconfig_server_id': uniconfig_server_id},
        headers=UNICONFIG_HEADERS
    )

    response.raise_for_status()
    return response