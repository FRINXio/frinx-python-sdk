import json
from json import JSONDecodeError
from typing import Any
from typing import Optional

import requests
from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError
from pydantic import validator
from pydantic.networks import AnyHttpUrl
from requests.exceptions import RequestException

from frinx.services.http_service.enums import HTTPMethod
from frinx.services.http_service.exceptions import InvalidJSONError

TERMINAL_ERROR = -1


class HTTPInput(BaseModel):

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    method: HTTPMethod = Field(...)
    url: AnyHttpUrl = Field(..., alias='uri')
    headers: dict[str, str] = Field(default={})
    data: dict[str, Any] | list[Any] | str | None = Field(default=None, alias='body')
    params: dict[str, str] = Field(default={}, alias='query_string_parameters')
    cookies: dict[str, str] | None = Field(default=None)
    # TODO: validate if float is positive and less than 5 min
    timeout: float | tuple[float, float] | None = Field(default=None)

    @classmethod
    @validator('data')
    def encode_decode(cls, data: dict[str, Any] | list[Any] | str | None) -> Optional[
    dict[str, Any] | list[Any] | str | None]:
        if data:
            try:
               json.dumps(json.loads(data)) if isinstance(data, str) else json.dumps(data)
            except JSONDecodeError as err:
                raise InvalidJSONError(err.args)
        return data


class HTTPOutput(BaseModel):

    class Config:
        min_anystr_length = 1

    code: int
    data: dict[str, Any]
    errors: list[str]
    logs: Optional[list[str]] | Optional[str] | None = None
    url: Optional[str] | None = None


def http_task(http_input: HTTPInput | dict[str, Any]) -> HTTPOutput:
    if isinstance(http_input, dict):
        try:
            http_input = HTTPInput(**http_input)
        except ValidationError as err:
            return HTTPOutput(code=TERMINAL_ERROR, data={}, errors=[json.dumps(e) for e in err.errors()])

    try:
        response = requests.request(**http_input.dict())
    except RequestException as err:
        return HTTPOutput(code=TERMINAL_ERROR, data={}, errors=[str(err)])

    return HTTPOutput(
        logs=f'< {http_input.method} {response.url} | status: {response.status_code} {response.reason} >',
        errors=[response.reason] if not response.ok else [],
        code=response.status_code,
        url=response.url,
        data={'data': response.text}
    )
