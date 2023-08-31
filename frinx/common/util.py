import json
from typing import Any

from requests import JSONDecodeError
from requests import Response

from frinx.common.type_aliases import DictAny


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
    """Returns camelCase version of provided snake_case string."""
    if not string:
        return ''

    words = string.split('_')
    return words[0].lower() + ''.join(n.capitalize() for n in words[1:])


def snake_to_kebab_case(string: str) -> str:
    """Returns kebab-case version of provided snake_case string."""
    if not string:
        return ''

    return string.replace('_', '-')


def normalize_base_url(url: str) -> str:
    return url.removesuffix('/')


def remove_empty_elements_from_root_dict(any_dict: DictAny) -> DictAny:
    """
    Removes empty elements (None, empty dictionaries, or empty lists) from a dictionary root.

    Args:
        any_dict (Dict[str, Any]): The input dictionary to be processed.

    Returns:
        Dict[str, Any]: A new dictionary with empty elements removed.
    """
    return dict((k, v) for k, v in any_dict.items() if v)


def remove_empty_elements_from_dict(any_dict: DictAny) -> Any:
    """
    Recursively removes empty elements (None, empty dictionaries, or empty lists) from a dictionary.

    Args:
        any_dict (Dict[str, Any]): The input dictionary to be processed.

    Returns:
        Dict[str, Any]: A new dictionary with empty elements removed.
    """
    def recursive_cleanup(d: DictAny) -> Any:
        cleaned = {}
        for k, v in d.items():
            match v:
                case dict():
                    cleaned[k] = recursive_cleanup(v)
                case list():
                    cleaned[k] = [item for item in v if item]
                case _:
                    if v:
                        cleaned[k] = v
        return cleaned
    return recursive_cleanup(any_dict)


def parse_response(response: Response) -> Any:
    try:
        return response.json()
    except JSONDecodeError:
        return response.text
