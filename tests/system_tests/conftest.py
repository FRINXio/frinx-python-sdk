import json
import logging
from typing import Any
from typing import Optional

import aiohttp
import pytest

from frinx.common.frinx_rest import CONDUCTOR_HEADERS
from frinx.common.frinx_rest import CONDUCTOR_URL_BASE

LOGGER = logging.getLogger(__name__)


CONDUCTOR_WF_EXEC_RQ: dict[str, Any] = {
    'name': 'Test_workflow',
    'input': {'num_paragraphs': 10, 'num_sentences': 10, 'num_words': 10, 'sleep_time': 0},
}


async def exec_wf(session: aiohttp.ClientSession, wf_rq: Optional[dict[str, Any]] = None, index: int = 0) -> str:
    if wf_rq is None:
        wf_rq = CONDUCTOR_WF_EXEC_RQ

    url = CONDUCTOR_URL_BASE + 'workflow'
    LOGGER.debug('Executing workflow %s', index)
    async with session.post(url, data=json.dumps(wf_rq), headers=CONDUCTOR_HEADERS) as r_future:
        response = await r_future.read()
        r_future.raise_for_status()
        return response.decode('utf-8')


async def get_wf_execution(session: aiohttp.ClientSession, wf_id: str) -> Any:
    url = CONDUCTOR_URL_BASE + 'workflow/' + wf_id + '?includeTasks=true'
    async with session.get(url, headers=CONDUCTOR_HEADERS) as r_future:
        response = await r_future.read()
        r_future.raise_for_status()
        return json.loads(response)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        '--collect-stats-folder',
        action='store',
        metavar='ga_workflows_collected_data',
        required=False,
        help='in context of github workflow updates the files in the repo ga_workflows_collected_data',
    )


@pytest.fixture(autouse=True)
def collect_stats_folder(pytestconfig: pytest.Config) -> None:
    pytest.COLLECT_STATS_FOLDER = pytestconfig.getoption('--collect-stats-folder')
