import json
import logging
import os

import requests

from frinx.common.frinx_rest import CONDUCTOR_HEADERS
from frinx.common.frinx_rest import CONDUCTOR_URL_BASE

logger = logging.getLogger(__name__)

workflow_import_url = CONDUCTOR_URL_BASE + '/metadata/workflow'


def register_workflow(workflow: str, overwrite: bool = False) -> None:
    if not isinstance(workflow, str):
        raise Exception('bad input')

    try:
        data = json.loads(workflow)
        workflow_name = data['name']
        method = 'POST'

        match overwrite:
            case True:
                method = 'PUT'
                data = [data]

        response = requests.request(
            url=workflow_import_url,
            method=method,
            data=json.dumps(data),
            headers=CONDUCTOR_HEADERS,
            timeout=60,
        )

        logger.info('%s: Response status code - %s', workflow_name, response.status_code)
        logger.debug(json.dumps(data))

        if not response.ok:
            logger.warning(
                '%s: Import of workflow failed. Ignoring the workflow. Response content: %s',
                workflow_name,
                response.content,
            )
    except Exception as err:
        logger.error(f'Error while registering workflow: {err}')
        raise err


def import_workflows(path: str) -> None:
    if os.path.isdir(path):
        logger.info('Importing workflows from folder %s', path)
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith('.json'):
                    try:
                        logger.info('Importing workflow %s', entry.name)
                        with open(entry) as payload_file:
                            # api expects array in payload
                            payload = []
                            payload_json = json.load(payload_file)
                            payload.append(payload_json)
                            response = requests.put(
                                workflow_import_url,
                                data=json.dumps(payload),
                                headers=CONDUCTOR_HEADERS,
                                timeout=60,
                            )
                            logger.info('Response status code - %s', response.status_code)
                            if response.status_code != requests.codes.no_content:
                                logger.warning(
                                    'Import of workflow %s failed. '
                                    'Ignoring the workflow. Response content: %s',
                                    entry.name,
                                    response.content,
                                )
                    except Exception as err:
                        logger.error(f'Error while registering workflow {entry.name}, {err}')
                        raise err
                elif entry.is_dir():
                    import_workflows(entry.path)
                else:
                    logger.warning('Ignoring, unknown type %s', entry)
    else:
        logger.error('Path to workflows %s is not a directory.', path)
