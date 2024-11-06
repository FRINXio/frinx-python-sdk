import asyncio
import json
import logging
import time as sleep_time
from typing import Any

import aiohttp
import pytest
from conftest import CONDUCTOR_HEADERS
from conftest import CONDUCTOR_URL_BASE
from conftest import exec_wf
from conftest import get_wf_execution

LOGGER = logging.getLogger(__name__)

CONDUCTOR_WF_EXEC_RQ_FORK: dict[str, Any] = {
    'name': 'Test_fork_workflow',
    'input': {
        'fork_count': 5,
        'num_paragraphs': 1,
        'num_sentences': 1,
        'num_words': 1,
        'sleep_time': 0,
    },
}


async def get_wf_path(session: aiohttp.ClientSession, wf_id: str) -> Any:
    url = CONDUCTOR_URL_BASE + 'workflow/path/' + wf_id
    async with session.get(url, headers=CONDUCTOR_HEADERS) as r_future:
        response = await r_future.read()
        r_future.raise_for_status()
        return json.loads(response)


async def get_wf_family(session: aiohttp.ClientSession, wf_id: str, summary: bool = True) -> Any:
    url = CONDUCTOR_URL_BASE + 'workflow/family/' + wf_id + '?summaryOnly=' + str(summary).lower()
    async with session.get(url, headers=CONDUCTOR_HEADERS) as r_future:
        response = await r_future.read()
        r_future.raise_for_status()
        return json.loads(response)


async def wait_for_completion(sleep_seconds: int, executed_id: str, session: aiohttp.ClientSession) -> None:
    iterations = 10

    for i in range(iterations):
        wf_execution = await get_wf_execution(session, executed_id)
        if wf_execution['status'] == 'COMPLETED':
            break
        elif i is (iterations - 1):
            LOGGER.error('Workflow not completed. Execution: %s', wf_execution)
            raise Exception(
                'Workflow not completed in {} seconds. Current status: {}'.format(
                    iterations * sleep_seconds, wf_execution['status']
                )
            )
        sleep_time.sleep(sleep_seconds)


@pytest.mark.asyncio
async def test_path_and_family_apis() -> None:
    sleep = 8

    async with aiohttp.ClientSession() as session:
        executed_id = await asyncio.ensure_future(exec_wf(session, CONDUCTOR_WF_EXEC_RQ_FORK, 0))
        await wait_for_completion(sleep, executed_id, session)

        # Root WF, path is of length 1
        path = await get_wf_path(session, executed_id)
        assert [executed_id] == path
        # Root WF, family is all forks + root with all parameters
        family = await get_wf_family(session, executed_id, False)
        assert len(family) == CONDUCTOR_WF_EXEC_RQ_FORK['input']['fork_count'] + 1

        # Find any child workflow
        child_wf = next(filter(lambda wf: wf['workflowName'] == 'Test_workflow', family))
        child_id = child_wf['workflowId']

        # Child WF, path is of length 2
        path = await get_wf_path(session, child_id)
        assert [executed_id, child_id] == path
        # Child WF, family is just the child returned as summary only
        family = await get_wf_family(session, child_id, True)
        assert len(family) == 1
        # This was summary only, workflowInput should be null
        assert not family[0].get('input', None)
