import requests

from frinx.common.conductor_enums import ContentType
from frinx.common.type_aliases import DictAny
from frinx.common.util import is_json_valid
from frinx.common.util import is_xml_valid
from frinx.common.worker.task_def import TaskInput


class IncompatibleFormError(TypeError):
    def __init__(self) -> None:
        self.msg = 'Request body format is incompatible with Content-Type header!'
        super().__init__(self.msg)


# TODO: clean up type-hints about parameters and required method and uri
def http_task(http_input: DictAny | TaskInput) -> requests.Response:
    # TODO: complete ORM mechanism to connect http_input and requests APIs
    if isinstance(http_input, TaskInput):
        http_input = http_input.dict(by_alias=True)

    # TODO: find out better way, perhaps merging dicts via logical condiction
    kwargs = {
        'params': http_input.get('params', None),
        'data': http_input.get('data', None),
        'json': http_input.get('json', None),
        'headers': http_input.get('headers', {}),
        'cookies': http_input.get('colkies', None),
        'files': http_input.get('files', None),
        'auth': http_input.get('auth', None),
        'timeout': http_input.get('timeout', None),
        'allow_redirects': http_input.get('allow_redirects', None),
        'proxies': http_input.get('proxies', None),
        'verify': http_input.get('verify', None),
        'stream': http_input.get('stream', None),
        'cert': http_input.get('cert', None),
    }

    match http_input.get('body', None):
        case dict() | list():
            kwargs['json'] = http_input['body']
        case str():
            kwargs['data'] = http_input['body']

    match (http_input.get('connectTimeout', None), http_input.get('readTimeout', None)):
        case int(), int():
            kwargs['timeout'] = (http_input['connectTimeout'], http_input['readTimeout'])
        case int(), None:
            kwargs['timeout'] = http_input['connectTimeout']

    if http_input.get('contentType', None):
        kwargs['headers']['Content-Type'] = http_input['contentType']
        # TODO: complete body validation by contentType
        match http_input['contentType']:
            case ContentType.APPLICATION_JSON:
                if not is_json_valid(http_input['body']):
                    raise IncompatibleFormError()
            case ContentType.APPLICATION_XML:
                if not is_xml_valid(http_input['body']):
                    raise IncompatibleFormError()
            case ContentType.APPLICATION_X_WWW_FORM_URLENCODED:
                ...
            case ContentType.MULTIPART_FROM_DATA:
                ...
            case ContentType.TEXT_CSV:
                ...
            case ContentType.TEXT_PLAIN:
                ...
            case ContentType.TEXT_XML:
                if not is_xml_valid(http_input['body']):
                    raise IncompatibleFormError()

    if http_input.get('accept', None):
        kwargs['headers']['Accept'] = http_input['accept']

    
    return requests.request(http_input['method'], http_input['uri'] or http_input['url'], **kwargs)
