from typing import Generic
from typing import TypeVar

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.util import snake_to_camel_case
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
    logs: list[str] | str = Field(default=[])

    class Config:
        validate_assignment = True
        alias_generator = snake_to_camel_case
        allow_population_by_field_name = True

    @validator('logs', always=True)
    def validate_logs(cls, logs: str | list[str]) -> list[str]:
        match logs:
            case list():
                return logs
            case str():
                return [logs]
