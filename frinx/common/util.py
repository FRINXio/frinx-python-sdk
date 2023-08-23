import json
from typing import Any

from pydantic import BaseModel
from pydantic import ValidationError
from requests import JSONDecodeError
from requests import Response

from frinx.common.type_aliases import DictAny
from frinx.common.type_aliases import DictStr
from frinx.common.type_aliases import ListAny
from frinx.common.type_aliases import ListStr


def jsonify_description(
    description: str, labels: list[str] | None = None, rbac: list[str] | None = None
) -> str:
    """Returns description in format of stringified JSON.
    >>> jsonify_description("Hello world")
    '{"description": "Hello world"}'
    >>> jsonify_description("Hello world", labels=["A", "B"])
    '{"description": "Hello world", "labels": ["A", "B"]}'
    >>> jsonify_description("Hello world", labels=["A", "B"], rbac=["C", "D"])
    '{"description": "Hello world", "labels": ["A", "B"], "rbac": ["C", "D"]}'
    """
    desc_representation: dict[str, Any] = {'description': description}
    if labels:
        desc_representation['labels'] = labels
    if rbac:
        desc_representation['rbac'] = rbac
    output = json.dumps(desc_representation)
    return output


def snake_to_camel_case(string: str) -> str:
    """Returns camelCase version of provided snake_case StrictString."""
    if not string:
        return ''

    words = string.split('_')
    result = words[0].lower() + ''.join(n.capitalize() for n in words[1:])
    return result


def normalize_base_url(url: str) -> str:
    return url.removesuffix('/')


def remove_empty_elements_from_dict(any_dict: DictAny) -> DictAny:
    return dict((k, v) for k, v in any_dict.items() if v)


def parse_response(response: Response) -> DictAny | ListAny | str:
    try:
        return response.json()  # type: ignore[no-any-return]
    except JSONDecodeError:
        return response.text


def json_parse(errors: ListStr | None = None, **kwargs: str) -> tuple[ListAny | DictAny | None, ListStr]:
    """
    Parse json, returns object and errors list as tuple. 

    args:
        - errors: (optional), list of error messages, default is empty list
    kwargs:
        - <object_name>=<string>: name of json-object and json-formatted-string (optional,
            but neccessary for functionality)
            e.g.: ip_addresses='["127.0.0.1", "127.0.0.2]', this approach enables to format to error
            messages this way: 'Object `ip_addresses`: (Not JSON valid. ... .)'
    returns:
        parsed-json-object, errors-list
    """
    def _format_err_msg(obj: str, msg: str) -> str:
        return f'Object `{obj}`: ({msg})'
    
    json_string, object_name = next(iter(kwargs.values())), next(iter(kwargs.keys()))
    errors = [] if errors is None else errors

    if not len(json_string):
        errors.append(_format_err_msg(object_name, 'Cannot parse empty string.'))
        return None, errors
    try:
        return json.loads(json_string), errors
    except json.JSONDecodeError as e:
        errors.append(_format_err_msg(object_name, f'Not JSON valid. {e.args[0]}.'))
        return None, errors


def validate_structure(obj: DictAny, model: type[BaseModel], *, idx: int | None = None, 
properties: DictStr = {}, errors: ListStr | None = None) -> list[str]:
    """
    Validate structure of object based on pydantic model, return errors if occures.

    args:
        obj: (required), python object (parsed json) to compare with pydantic model
        model: (required), pydantic model to use as structure template for obj
    kwargs:
        idx: (optional), index represents position of nested object in list, used in _format_err_msg
        properties: (optional), dictionary of model properties and expected values of properties,
            enables value checking of obj
        errors: (optional), list of error messages, default is empty list
    returns:
        errors-list
    """

    def _format_err_msg(prop: str, obj: str, msg: str) -> str:
        return f'Property `{prop}` of `{obj}{{}}`, ({msg})'.format(f'[{idx}]' if idx or idx == 0 else '')
    
    errors = [] if errors is None else errors
    try:
        model.parse_obj(obj)
    except ValidationError as validation_err:
         # TODO: how to handle strict and extra ?
         # maybe skip and print in log as WARNING (extra)
         # NOTE: try to use pydantic strict types if needed, v1 doesn't support BaseConfig.strict
        for err in validation_err.errors():
            errors.append(_format_err_msg(str(err['loc'][0]), model.__class__.__name__, err['msg']))

    for key, value in properties.items():
        if obj.get(key, None) != value:
            errors.append(
                _format_err_msg(key, model.__class__.__name__, f'expected value `{value}`, get `{obj[key]}`')
            )
    return errors
