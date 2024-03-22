# This Conductor client solves problem with shared memory between threads.
# Instead of registering task execution wrapper address is registered whole task Class WorkerImpl as a blueprint
# and during execution is from this blueprint created isolated object.
# This worker is compatible with SDK only

import copy
import json
import logging
import socket
import sys
import threading
import time
import traceback
import uuid
from collections import defaultdict
from dataclasses import dataclass
from threading import Thread
from typing import Any
from typing import TypeAlias

import requests

from frinx.client.v2.conductor import WFClientMgr
from frinx.common.worker.worker import WorkerImpl

logger = logging.getLogger(__name__)
hostname = socket.gethostname()
RawTaskIO: TypeAlias = dict[str, Any]


@dataclass
class RegisteredWorkerTask:
    task_type: str
    task_blueprint: WorkerImpl


@dataclass
class NextWorkerTask:
    task_type: str
    task_blueprint: WorkerImpl
    poll_uuid: uuid.UUID | None


class TaskSource:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.task_types: RawTaskIO = {}
        self.task_types_list: list[str] = []

        self.actual_uuid: uuid.UUID | None = None
        self.filtered_queue: dict[str, Any] = {}
        self.actual_task_types_running: dict[str, Any] = defaultdict(int)
        self.last_task_position: int = 0

    def register_task_type(self, task_type: str, task_blueprint: WorkerImpl) -> None:
        self.task_types[task_type] = RegisteredWorkerTask(task_type, task_blueprint)
        self.task_types_list = list(self.task_types)

    def handle_tasks(self, queue: dict[str, int]) -> None:
        with self.lock:
            self.actual_uuid = uuid.uuid4()
            self.filtered_queue = {
                key: value
                for key, value in queue.items()
                if key in self.task_types.keys() and value > 0
            }

    def round_robin_task_types(self) -> str:
        task_type = self.task_types_list[self.last_task_position]
        self.last_task_position += 1
        if self.last_task_position == len(self.task_types):
            self.last_task_position = 0
        return task_type

    def get_next_task(self, last_task_type: str | None) -> NextWorkerTask | None:

        with self.lock:
            if last_task_type:
                self.actual_task_types_running[last_task_type] -= 1

            if len(self.filtered_queue) == 0:
                return None

            task_type = ''
            while task_type not in self.filtered_queue:
                task_type = self.round_robin_task_types()

            self.actual_task_types_running[task_type] += 1

            registered_task: RegisteredWorkerTask = self.task_types[task_type]

            self.filtered_queue[task_type] -= 1
            if self.filtered_queue[task_type] <= 0:
                self.filtered_queue.pop(task_type, None)

            next_worker = NextWorkerTask(
                task_type=task_type,
                task_blueprint=registered_task.task_blueprint,
                poll_uuid=self.actual_uuid
            )
            return next_worker

    def task_not_found_anymore(self, task_not_found: NextWorkerTask) -> None:
        if self.actual_uuid == task_not_found.poll_uuid:
            with self.lock:
                if task_not_found.task_type is not None:
                    self.filtered_queue.pop(task_not_found.task_type, None)


class FrinxConductorWrapper:
    def __init__(
        self, server_url: str, max_thread_count: int, polling_interval: float = 0.1,
            worker_id: str | None = None, headers: dict[str, Any] | None = None
    ) -> None:
        # Synchronizes access to self.queues by producer thread (in read_queue) and consumer threads (in tasks_in_queue)
        self.lock = threading.Lock()
        self.queues: dict[Any, Any] = {}
        self.conductor_task_url = server_url + '/metadata/taskdefs'
        self.headers = headers
        self.consumer_worker_count = max_thread_count
        self.task_source = TaskSource()
        self.polling_interval = polling_interval
        wfc_mgr = WFClientMgr(server_url, headers=headers)
        self.task_client = wfc_mgr.task_client
        self.worker_id = worker_id or hostname

    def start_workers(self) -> None:
        for i in range(self.consumer_worker_count):
            thread = Thread(target=self.consume_task)
            thread.daemon = True
            thread.start()

        logger.info('Starting a queue polling')
        fail_count = 0
        max_fail_count = 10
        while True:
            try:
                time.sleep(float(self.polling_interval))
                queues_temp = self.task_client.get_tasks_in_queue('all')
                self.task_source.handle_tasks(queues_temp)
                fail_count = 0
            except Exception:
                logger.error(f'Unable to read a queue info after {fail_count} attempts', exc_info=True)
                self.task_source.handle_tasks({})
                fail_count = +1
                if fail_count > max_fail_count:
                    sys.exit(1)

    # Consume_task is executing tasks in the queue. The tasks are selected by round-robin from all task types.
    # If there is no task for processing, the thread is in sleeping for a defined interval.
    def consume_task(self) -> None:
        last_task_type = None
        while True:
            next_task = self.task_source.get_next_task(last_task_type)

            last_task_type = None

            if not next_task:
                time.sleep(float(self.polling_interval))
                continue

            last_task_type = next_task.task_type

            polled_task = self.task_client.poll_for_task(next_task.task_type, self.worker_id)

            if polled_task is None:
                self.task_source.task_not_found_anymore(next_task)
                continue

            logger.info(
                'Polled for a task %s of type %s', polled_task['taskId'], next_task.task_type
            )

            # Check if task input is externalized and if so, download the input
            polled_task = self.replace_external_payload_input(polled_task)
            if polled_task is None:
                # Error replacing external payload
                continue

            self.execute(polled_task, copy.deepcopy(next_task.task_blueprint))

    def replace_external_payload_input(self, task: RawTaskIO) -> RawTaskIO | None:
        # No external payload placeholder present, just return original task
        if self.task_client.EXTERNAL_INPUT_KEY not in task:
            return task

        location = {}
        try:
            # Get the exact uri from conductor where the payload is stored
            location = self.task_client.get_task_input_external_payload_location(
                task[self.task_client.EXTERNAL_INPUT_KEY]
            )
            if location is None:
                location = {}

            if 'uri' not in location:
                raise Exception('Unexpected output for external payload location: %s' % location)

            # Replace placeholder with real output
            task.pop(self.task_client.EXTERNAL_INPUT_KEY)
            task['inputData'] = requests.get(
                location['uri'], headers=self.task_client.headers
            ).json()
            return task

        except Exception:
            logger.error(
                'Unable to download external task input: %s for path: %s',
                task['taskId'],
                location,
                exc_info=True,
            )
            self.handle_task_exception(task)
            return None

    def register(self, task_blueprint: WorkerImpl) -> None:
        task_definition: dict[str, Any] = task_blueprint.task_def.model_dump(by_alias=True, exclude_none=True)
        task_type: str = task_blueprint.task_def.name
        logger.debug(f'Registering a task of type {task_type} with definition {task_definition}')

        try:
            requests.post(self.conductor_task_url, data=json.dumps([task_definition]), headers=self.headers)
        except Exception:
            logger.error('Unable to register a task', exc_info=True)

        self.task_source.register_task_type(task_type, task_blueprint)

    def execute(self, task: RawTaskIO, task_blueprint: WorkerImpl) -> None:
        try:
            logger.info('Executing a task %s', task['taskId'])
            resp = task_blueprint.execute_wrapper(task)

            if resp is None:
                error_msg = 'Task execution function MUST return a response as a dict with status and output fields'
                raise Exception(error_msg)

            task['status'] = resp['status']
            task['outputData'] = resp.get('output', {})
            task['logs'] = resp.get('logs', [])

            logger.debug('Executing a task %s, response: %s', task['taskId'], resp)
            logger.debug('Executing a task %s, task body: %s', task['taskId'], task)
            self.task_client.update_task(task)
        except Exception:
            self.handle_task_exception(task)

    def handle_task_exception(self, task: RawTaskIO) -> None:
        logger.error('Unable to execute a task %s', task['taskId'], exc_info=True)
        error_info = traceback.format_exc().split('\n')[:-1]
        task['status'] = 'FAILED'
        task['outputData'] = {
            'Error while executing task': task.get('taskType', ''),
            'traceback': error_info,
        }
        task['logs'] = ['Logs: %s' % traceback.format_exc()]
        try:
            self.task_client.update_task(task)
        except Exception:
            logger.error(
                'Unable to update a task %s, it may have timed out', task['taskId'], exc_info=True
            )
