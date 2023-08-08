from collections import defaultdict

import requests

from frinx.common.worker.task_def import TaskInput


def http_task(http_input: TaskInput) -> requests.Response:
    input = defaultdict(lambda: None, http_input.dict(by_alias=True))
    headers, timeout, json, data, auth = input['headers'] or {}, None, None, None, None

    if input['basicAuth']:
        auth = input['basicAuth']['username'], input['basicAuth']['password']

    if input['contentType']:
        headers['Content-Type'] = input['contentType']

    match input['connectTimeout'], input['readTimeout']:
        case float(), float():
            timeout = input['connectTimeout'], input['readTimeout']
        case float(), None:
            timeout = input['connectTimeout']

    match input['body']:
        case dict() | list():
            json = input['body']
        case str():
            data = input['body']
    
    return requests.request(
        method=input['method'],
        url=input['uri'] or input['url'],
        headers=headers,
        timeout=timeout or input['timeout'],
        data=data or input['data'],
        json=json or input['json'],
        cookies=input['cookies'],
        auth=auth or input['auth']
    )
