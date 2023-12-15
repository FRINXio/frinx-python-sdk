import typing
from typing import Generic
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator

from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.worker.task_def import TaskOutput

T = TypeVar('T')


class Registry(Generic[T]):
    def __init__(self) -> None:
        self._store: dict[str, T] = {}

    def set_item(self, k: str, v: T) -> None:
        self._store[k] = v

    def get_item(self, k: str) -> T:
        return self._store[k]


TO = TypeVar('TO', bound=TaskOutput | None)


class TaskResult(BaseModel, Generic[TO]):
    status: TaskResultStatus
    output: TO | None = None
    logs: typing.Union[list[str], str] = Field(default=[])

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True
        # alias_generator=snake_to_camel_case,
    )

    @field_validator('logs', mode='before')
    def validate_logs(cls, logs: str | list[str]) -> list[str]:
        match logs:
            case list():
                return logs
            case str():
                return [logs]
