import asyncio
import json
import logging
import statistics
import time
from datetime import timedelta
from timeit import default_timer as timer
from typing import Any
from typing import Optional

import aiohttp
import pytest
from conftest import COLLECT_STATS_FOLDER
from conftest import CONDUCTOR_HEADERS
from conftest import CONDUCTOR_URL_BASE
from conftest import exec_wf
from conftest import get_wf_execution

LOGGER = logging.getLogger(__name__)

CONDUCTOR_WF_EXEC_RQ: dict[str, Any] = {
    'name': 'Test_workflow',
    'input': {
        'num_paragraphs': 10,
        'num_sentences': 10,
        'num_words': 10,
        'sleep_time': 0
    }
}

CONDUCTOR_WF_EXEC_RQ_FORK: dict[str, Any] = {
    'name': 'Test_fork_workflow',
    'input': {
        'fork_count': 10,
        'num_paragraphs': 10,
        'num_sentences': 10,
        'num_words': 10,
        'sleep_time': 0,
    },
}

CONDUCTOR_WF_EXEC_RQ_EXTERNAL_STORAGE: dict[str, Any] = {
    'name': 'Test_workflow',
    # ~ 700kB
    'input': {
        'num_paragraphs': 100,
        'num_sentences': 100,
        'num_words': 10,
        'sleep_time': 0
    },
}


async def get_running_wf_ids(session: aiohttp.ClientSession, wf_type: str = 'Test_workflow') -> bytes:
    url = CONDUCTOR_URL_BASE + 'workflow/running/' + wf_type
    async with session.get(url, headers=CONDUCTOR_HEADERS) as response:
        return await response.read()


async def get_external_payload(session: aiohttp.ClientSession, external_id: str) -> Any:
    url = CONDUCTOR_URL_BASE + 'workflow/externalstoragelocation'
    params = {'path': external_id, 'operation': 'READ', 'payloadType': 'WORKFLOW_OUTPUT'}
    async with session.get(url, headers=CONDUCTOR_HEADERS, params=params) as r_future:
        # intermediate response
        raw = await r_future.read()
        parsed = json.loads(raw.decode('utf-8'))
        content_uri = parsed['uri']
        async with session.get(
            content_uri, headers=CONDUCTOR_HEADERS, params=params
        ) as r_future_inner:
            # actual content response
            raw_inner = await r_future_inner.read()
            return json.loads(raw_inner.decode('utf-8'))


async def get_last_wf_output(executed_ids: list[str], session: aiohttp.ClientSession) -> Any:
    last_wf_id = executed_ids[-1]
    return await get_wf_output(last_wf_id, session)


async def get_wf_output(last_wf_id: str, session: aiohttp.ClientSession) -> Any:
    wf_execution = await get_wf_execution(session, last_wf_id)
    if 'externalOutputPayloadStoragePath' in wf_execution:
        return await get_external_payload(session, wf_execution['externalOutputPayloadStoragePath'])
    return wf_execution.get('output', {})


async def collect_stats(session: aiohttp.ClientSession, wf_ids: Optional[list[str]] = None) -> dict[str, Any]:
    durations = []
    failed = 0

    if wf_ids:
        for wf_id in wf_ids:
            wf = await get_wf_execution(session, wf_id)
            wf_duration_ms = wf['endTime'] - wf['startTime']
            wf_status = wf['status']
            match wf_status:
                case 'COMPLETED':
                    pass
                case 'FAILED':
                    failed = failed + 1
                case _:
                    LOGGER.warning('Unexpected status for workflow %s: %s', wf_id, wf_status)

            durations.append(wf_duration_ms)

    duration_quantiles = [round(q, 1) for q in statistics.quantiles(durations, n=10)]
    q = 0
    duration_quantiles_dict = {}
    for quantile in duration_quantiles:
        q = q + 10
        duration_quantiles_dict[f'quantile{q}_duration_seconds'] = quantile / 1000

    return duration_quantiles_dict | {
        'median_duration_seconds': timedelta(milliseconds=statistics.median(durations)).seconds,
        'average_duration_seconds': timedelta(milliseconds=statistics.mean(durations)).seconds,
        'max_duration_seconds': timedelta(milliseconds=max(durations)).seconds,
        'min_duration_seconds': timedelta(milliseconds=min(durations)).seconds,
        'failed_workflows': failed,
    }


def parse_running_wf_ids(running_wfs: bytes) -> tuple[list[str], int]:
    running_wfs_no_brackets = running_wfs.decode('utf-8')[1:-1]
    if not running_wfs_no_brackets:
        return [], 0
    running_wfs_ids = running_wfs_no_brackets.split(',')
    running_wfs_len = len(running_wfs_ids)
    return running_wfs_ids, running_wfs_len


@pytest.mark.asyncio
async def test_performance_simple_wf(timestamp: Optional[float] = None, context: str = 'simple') -> dict[str, Any]:
    collect_stats_filename = str(COLLECT_STATS_FOLDER) + 'conductor_system_tests.json'

    executions = 1000
    sleep = 15
    sampling_rate = 10

    if timestamp is None:
        timestamp = time.time()

    async with aiohttp.ClientSession() as session:
        start = timer()
        LOGGER.info('Executing %s workflows', executions)

        wf_exec_futures = [
            asyncio.ensure_future(exec_wf(session, CONDUCTOR_WF_EXEC_RQ, i))
            for i in range(executions)
        ]

        LOGGER.debug(
            'Waiting for %s workflow executions to return response',
            executions
        )
        executed_ids = await asyncio.gather(*wf_exec_futures)
        LOGGER.debug('All workflow executions received')
        end = timer()
        logging.info(
            'Took %s to submit all %s executions',
            timedelta(seconds=end - start),
            executions
        )

        while True:
            running_wfs = await get_running_wf_ids(session)
            running_wfs_ids, running_wfs_len = parse_running_wf_ids(running_wfs)

            if running_wfs_len == 0:
                break

            logging.info('Still running: %s workflows', running_wfs_len)
            time.sleep(sleep)

        end = timer()

        stats = await collect_stats(
            session,
            list(executed_ids[0::sampling_rate])
        )

        wfs_per_minute = (
            executions / timedelta(seconds=end - start).seconds
        ) * 60

        stats.update({'wfs_per_minute': wfs_per_minute})
        LOGGER.info('Execution stats: %s', stats)

        last_wf_output = await get_last_wf_output(list(executed_ids), session)
        LOGGER.debug('Last workflow output: %s', last_wf_output)
        LOGGER.info('Workflow payload size: %s bytes', last_wf_output.get('bytes', -1))

        assert stats['failed_workflows'] == 0

        if COLLECT_STATS_FOLDER:
            this_function_name = 'test_performance_simple_wf'
            if context == 'simple':
                this_function_name = 'test_performance_simple_wf'
            elif 'batch' in context:
                this_function_name = 'test_performance_simple_wf_long'
                stats.update({'batch': int(context.replace('batch', ''))})
            with open(collect_stats_filename) as openfile:
                json_object = json.load(openfile)
            stats.update({'timestamp': 1000 * timestamp})
            if this_function_name not in json_object:
                json_object.update({this_function_name: []})
            json_object[this_function_name].append(stats)
            with open(collect_stats_filename, 'w') as outfile:
                outfile.write(json.dumps(json_object, indent=4))
        return stats


@pytest.mark.asyncio
async def test_performance_simple_wf_long() -> None:
    batches = 10
    all_stats = []

    for i in range(0, batches):
        LOGGER.info('Executing batch: %s', i)
        stats = await test_performance_simple_wf(time.time(), f'batch{i:02}')
        all_stats.append(stats)

    for stat in all_stats:
        LOGGER.info('Stats: %s', stat)


@pytest.mark.asyncio
async def test_performance_fork() -> None:
    collect_stats_filename = str(COLLECT_STATS_FOLDER) + 'conductor_system_tests.json'

    executions = 10
    forks = 100
    sleep = 15
    sampling_rate = 1
    subwf_output_item_len = 3

    timestamp = time.time()

    async with aiohttp.ClientSession() as session:
        start = timer()
        LOGGER.info(
            'Executing %s workflows * %s child/forked workflows',
            executions,
            forks
        )

        CONDUCTOR_WF_EXEC_RQ_FORK['input']['fork_count'] = forks
        wf_exec_futures = [
            asyncio.ensure_future(exec_wf(session, CONDUCTOR_WF_EXEC_RQ_FORK, i))
            for i in range(executions)
        ]
        executed_ids = await asyncio.gather(*wf_exec_futures)

        while True:
            running_wfs = await get_running_wf_ids(session)
            _, running_wfs_len = parse_running_wf_ids(running_wfs)
            running_wfs_main = await get_running_wf_ids(session, 'Test_fork_workflow')
            _, running_wfs_len_main = parse_running_wf_ids(running_wfs_main)

            running_wfs_len = running_wfs_len + running_wfs_len_main

            if running_wfs_len == 0:
                break

            logging.info('Still running: %s workflows', running_wfs_len)
            time.sleep(sleep)

        end = timer()

        stats = await collect_stats(session, list(executed_ids[0::sampling_rate]))

        wfs_per_minute = (
            forks * executions
            / timedelta(seconds=end - start).seconds
        ) * 60

        stats.update(
            {'wfs_per_minute': wfs_per_minute}
        )

        LOGGER.info('Execution stats: %s', stats)

        assert stats['failed_workflows'] == 0

        if COLLECT_STATS_FOLDER:
            this_function_name = 'test_performance_fork'  # Note: possible to use inspect.currentframe().f_code.co_name
            with open(collect_stats_filename) as openfile:
                json_object = json.load(openfile)
            stats.update({'timestamp': 1000 * timestamp})
            if this_function_name not in json_object:
                json_object.update({this_function_name: []})
            json_object[this_function_name].append(stats)
            with open(collect_stats_filename, 'w') as outfile:
                outfile.write(json.dumps(json_object, indent=4))

        last_wf_output = await get_last_wf_output(list(executed_ids), session)
        LOGGER.debug('Last workflow output: %s', last_wf_output)
        LOGGER.info(
            'Workflow payload size: %s bytes', len(json.dumps(last_wf_output).encode('utf-8'))
        )

        # There was a race condition in conductor causing missing outputs in joins DEP-328
        LOGGER.info('Asserting all outputs collected correctly in join')
        for parent_id in executed_ids:
            wf_output = await get_wf_output(parent_id, session)
            assert len(wf_output.items()) == forks, (
                'Workflow %s missing output from child in join' % parent_id
            )
            for output_key in wf_output:
                subwf_output = wf_output[output_key]
                assert (
                    len(subwf_output.items()) == subwf_output_item_len
                ), 'Workflow {} missing all outputs from child {} in join: {}'.format(
                    parent_id,
                    output_key,
                    subwf_output,
                )


@pytest.mark.asyncio
async def test_performance_simple_wf_external_storage() -> None:
    collect_stats_filename = str(COLLECT_STATS_FOLDER) + 'conductor_system_tests.json'

    executions = 200
    sleep = 15
    sampling_rate = 10

    timestamp = time.time()

    async with aiohttp.ClientSession() as session:

        start = timer()
        LOGGER.info('Executing %s workflows', executions)
        wf_exec_futures = [
            asyncio.ensure_future(exec_wf(session, CONDUCTOR_WF_EXEC_RQ_EXTERNAL_STORAGE, i))
            for i in range(executions)
        ]
        executed_ids = await asyncio.gather(*wf_exec_futures)
        end = timer()
        logging.info('Executed %s workflows', len(executed_ids))
        logging.info(
            'Took %s to submit all %s executions', timedelta(seconds=end - start),
            executions
        )

        while True:
            running_wfs = await get_running_wf_ids(session)
            running_wfs_ids, running_wfs_len = parse_running_wf_ids(running_wfs)

            if running_wfs_len == 0:
                break

            logging.info('Still running: %s workflows', running_wfs_len)
            time.sleep(sleep)

        end = timer()
        stats = await collect_stats(
            session,
            list(executed_ids[0::sampling_rate]))

        stats.update({
                'wfs_per_minute': (
                    executions / timedelta(seconds=end - start).seconds
                ) * 60
            }
        )
        LOGGER.info('Execution stats: %s', stats)
        last_wf_output = await get_last_wf_output(list(executed_ids), session)
        LOGGER.debug('Last workflow output: %s', last_wf_output)
        LOGGER.info('Workflow payload size: %s bytes', last_wf_output.get('bytes', -1))

        assert stats['failed_workflows'] == 0

        if COLLECT_STATS_FOLDER:
            this_function_name = 'test_performance_simple_wf_external_storage'
            with open(collect_stats_filename) as openfile:
                json_object = json.load(openfile)
            stats.update({'timestamp': 1000 * timestamp})
            if this_function_name not in json_object:
                json_object.update({this_function_name: []})
            json_object[this_function_name].append(stats)
            with open(collect_stats_filename, 'w') as outfile:
                outfile.write(json.dumps(json_object, indent=4))
