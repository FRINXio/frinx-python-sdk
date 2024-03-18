#
#  Copyright 2017 Netflix, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import json
import socket
from typing import Any
from typing import TypeAlias

import requests

hostname = socket.gethostname()

RawJsonIO: TypeAlias = dict[str, Any]
RawHeaders: TypeAlias = dict[str, Any] | None


class BaseClient:
    print_url = False
    headers: dict[str, Any] = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def __init__(self, base_url: str, base_resource: str, headers: RawHeaders = None) -> None:
        self.base_url = base_url
        self.base_resource = base_resource
        if headers is not None:
            self.headers = self.merge_two_dicts(self.headers, headers)

    def get(self, res_path: str, query_params: Any | None = None) -> Any:
        the_url = f'{self.base_url}/{res_path}'
        resp = requests.get(the_url, params=query_params, headers=self.headers)
        self.__check_for_success(resp)
        if resp.content == b'':
            return None
        else:
            return resp.json()

    def post(
            self, res_path: str, query_params: dict[str, Any] | None,
            body: RawJsonIO | None = None, headers: RawHeaders = None
    ) -> Any:
        the_url = f'{self.base_url}/{res_path}'
        the_header = self.headers
        if headers is not None:
            the_header = self.merge_two_dicts(self.headers, headers)
        if body is not None:
            json_body = json.dumps(body, ensure_ascii=False).encode('utf8')
            resp = requests.post(the_url, params=query_params, data=json_body, headers=the_header)
        else:
            resp = requests.post(the_url, params=query_params, headers=the_header)

        self.__check_for_success(resp)
        return self.__return(resp, the_header)

    def put(
            self, res_path: str, query_params: dict[str, Any] | None = None,
            body: RawJsonIO | None = None, headers: RawHeaders = None
    ) -> Any:
        the_url = f'{self.base_url}/{res_path}'
        the_header = self.headers
        if headers is not None:
            the_header = self.merge_two_dicts(self.headers, headers)

        if body is not None:
            json_body = json.dumps(body, ensure_ascii=False).encode('utf8')
            resp = requests.put(the_url, params=query_params, data=json_body, headers=the_header)
        else:
            resp = requests.put(the_url, params=query_params, headers=the_header)

        self.__print(resp)
        return self.__return(resp, the_header)

    def delete(self, res_path: str, query_params: Any) -> Any:
        the_url = f'{self.base_url}/{res_path}'
        resp = requests.delete(the_url, params=query_params, headers=self.headers)
        self.__print(resp)
        return self.__check_for_success(resp)

    def make_url(self, urlformat: str | None = None, *argv: Any) -> Any:
        url = self.base_resource + '/'
        if urlformat:
            url += urlformat.format(*argv)
        return url

    @staticmethod
    def make_params(**kwargs: Any) -> dict[str, Any] | None:
        return dict((k, v) for k, v in kwargs.items() if v is not None) or None

    @staticmethod
    def merge_two_dicts(x: dict[str, Any], y: dict[str, Any]) -> dict[str, Any]:
        z = x.copy()
        z.update(y)
        return z

    def __print(self, resp: requests.Response) -> None:
        if self.print_url:
            print(resp.url)

    @staticmethod
    def __return(resp: requests.Response, header: dict[str, Any]) -> Any:
        retval = ''
        if len(resp.text) > 0:
            if header['Accept'] == 'text/plain':
                retval = resp.text
            elif header['Accept'] == 'application/json':
                retval = resp.json()
            else:
                retval = resp.text
        return retval

    @staticmethod
    def __check_for_success(resp: requests.Response) -> Any:
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            print('ERROR: ' + resp.text)
            raise


class MetadataClient(BaseClient):
    BASE_RESOURCE = 'metadata'

    def __init__(self, base_url: str, headers: RawHeaders = None) -> None:
        BaseClient.__init__(self, base_url, self.BASE_RESOURCE, headers)

    def get_workflow_def(self, wf_name: str, version: int | None = None) -> Any:
        url = self.make_url('workflow/{}', wf_name)
        return self.get(url, self.make_params(version=version))

    def create_workflow_def(self, wfd_obj: RawJsonIO) -> Any:
        url = self.make_url('workflow')
        return self.post(url, None, wfd_obj)

    def update_workflow_defs(self, list_of_wfd_obj: RawJsonIO) -> Any:
        url = self.make_url('workflow')
        return self.put(url, None, list_of_wfd_obj)

    def get_all_workflow_defs(self) -> Any:
        url = self.make_url('workflow')
        return self.get(url)

    def unregister_workflow_def(self, wf_name: str, version: int ) -> None:
        url = self.make_url(f'workflow/{wf_name}/{version}')
        self.delete(url, None)

    def get_task_def(self, td_name: str) -> Any:
        url = self.make_url('taskdefs/{}', td_name)
        return self.get(url)

    def register_task_defs(self, list_of_task_def_obj: RawJsonIO) -> Any:
        url = self.make_url('taskdefs')
        return self.post(url, None, list_of_task_def_obj)

    def update_task_def(self, task_def_obj: RawJsonIO) -> Any:
        url = self.make_url('taskdefs')
        self.put(url, None, task_def_obj)

    def unregister_task_def(self, td_name: str, reason: str | None = None) -> None:
        url = self.make_url('taskdefs/{}', td_name)
        self.delete(url, self.make_params(reason=reason))

    def get_all_task_defs(self) -> Any:
        url = self.make_url('taskdefs')
        return self.get(url)


class TaskClient(BaseClient):
    BASE_RESOURCE = 'tasks'
    EXTERNAL_INPUT_KEY = 'externalInputPayloadStoragePath'

    def __init__(self, base_url: str, headers: RawHeaders = None) -> None:
        BaseClient.__init__(self, base_url, self.BASE_RESOURCE, headers)

    def get_task(self, task_id: str) -> Any:
        url = self.make_url('{}', task_id)
        return self.get(url)

    def update_task(self, task_obj: dict[str, Any]) -> Any:
        url = self.make_url('')
        headers = {'Accept': 'text/plain'}
        self.post(url, None, task_obj, headers)

    def poll_for_task(self, task_type: str, worker_id: str, domain: str | None = None) -> Any:
        url = self.make_url('poll/{}', task_type)
        params = {'workerid': worker_id}
        if domain is not None:
            params['domain'] = domain

        try:
            return self.get(url, params)
        except Exception as err:
            print('Error while polling ' + str(err))
            return None

    def poll_for_batch(
            self, task_type: str, count: int, timeout: int, worker_id: str, domain: str | None = None
    ) -> Any:
        url = self.make_url('poll/batch/{}', task_type)
        params = {'workerid': worker_id, 'count': count, 'timeout': timeout}

        if domain is not None:
            params['domain'] = domain

        try:
            return self.get(url, params)
        except Exception as err:
            print('Error while polling ' + str(err))
            return None

    def get_tasks_in_queue(self, task_name: str) -> Any:
        url = self.make_url('queue/{}', task_name)
        return self.get(url)

    def get_task_queue_size(self, task_type: str) -> Any:
        url = self.make_url('queue/size')
        params = {'taskType': task_type}
        return self.get(url, params)

    def get_task_input_external_payload_location(self, path: str) -> Any:
        url = self.make_url('externalstoragelocation')
        params = {'path': path, 'operation': 'READ', 'payloadType': 'TASK_INPUT'}
        return self.get(url, params)


class WorkflowClient(BaseClient):
    BASE_RESOURCE = 'workflow'

    def __init__(self, base_url: str, headers: dict[str, Any] | None = None):
        BaseClient.__init__(self, base_url, self.BASE_RESOURCE, headers)

    def get_workflow(self, wf_id: str, include_tasks: bool = True) -> Any:
        url = self.make_url('{}', wf_id)
        params = {'includeTasks': include_tasks}
        return self.get(url, params)

    def get_running_workflows(
            self, wf_name: str, version: int | None = None, start_time: int | None = None, end_time: int | None = None
    ) -> Any:
        url = self.make_url('running/{}', wf_name)
        params = {'version': version, 'startTime': start_time, 'endTime': end_time}
        return self.get(url, params)

    def start_workflow(
            self, wf_name: str, input_json: RawJsonIO, version: int | None = None, correlation_id: str | None = None
    ) -> Any:
        url = self.make_url('{}', wf_name)
        params = {'version': version, 'correlationId': correlation_id}
        headers = {'Accept': 'text/plain'}
        return self.post(url, params, input_json, headers)

    def terminate_workflow(self, wf_id: str, reason: str | None = None) -> None:
        url = self.make_url('{}', wf_id)
        params = {'reason': reason}
        self.delete(url, params)

    def remove_workflow(self, wf_id: str, archive_workflow: bool = True) -> None:
        url = self.make_url('{}/remove', wf_id)
        self.delete(url, self.make_params(archiveWorkflow=archive_workflow))

    def pause_workflow(self, wf_id: str) -> Any:
        url = self.make_url('{}/pause', wf_id)
        return self.put(url)

    def resume_workflow(self, wf_id: str) -> Any:
        url = self.make_url('{}/resume', wf_id)
        return self.put(url, )

    def skip_task_from_workflow(self, wf_id: str, task_ref_name: str, skip_task_request: dict[str, Any]) -> Any:
        url = self.make_url('{}/skiptask/{}', wf_id, task_ref_name)
        self.put(url, None, skip_task_request)

    def rerun_workflow(self, wf_id: str, body: dict[str, Any]) -> Any:
        url = self.make_url('{}/rerun', wf_id)
        return self.post(url, None, body)

    def restart_workflow(self, wf_id: str, use_latest_definitions: bool = False) -> Any:
        url = self.make_url('{}/restart', wf_id)
        params = {'useLatestDefinitions': use_latest_definitions}
        self.post(url, params, None)


class EventServicesClient(BaseClient):
    BASE_RESOURCE = 'event'

    def __init__(self, base_url: str, headers: RawHeaders = None) -> None:
        BaseClient.__init__(self, base_url, self.BASE_RESOURCE, headers)

    def get_event_handler_def(self, event: str, active_only: bool = True) -> Any:
        url = self.make_url('{}', event)
        params = {'activeOnly': active_only}
        return self.get(url, params)

    def get_event_handler_defs(self) -> Any:
        url = self.make_url()
        return self.get(url)

    def create_event_handler_def(self, eh_obj: RawJsonIO) -> Any:
        url = self.make_url()
        return self.post(url, None, eh_obj)

    def update_event_handler_def(self, eh_obj: RawJsonIO) -> None:
        url = self.make_url()
        self.put(url, None, eh_obj)

    def remove_event_handler(self, eh_name: str) -> None:
        url = self.make_url('{}', eh_name)
        self.delete(url, {})

    def get_event_handler_queues(self) -> Any:
        url = self.make_url('queues')
        return self.get(url)

    def get_event_handler_queues_providers(self) -> Any:
        url = self.make_url('queues/providers')
        return self.get(url)


class WFClientMgr:
    def __init__(self, server_url: str = 'http://localhost:8080/api/', headers: dict[str, Any] | None = None) -> None:
        self.workflow_client = WorkflowClient(server_url, headers)
        self.task_client = TaskClient(server_url, headers)
        self.metadata_client = MetadataClient(server_url, headers)
