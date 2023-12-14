from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import PrivateAttr

from frinx.common.conductor_enums import RetryLogic
from frinx.common.conductor_enums import TimeoutPolicy
from frinx.common.frinx_rest import X_FROM
from frinx.common.type_aliases import DictAny
from frinx.common.type_aliases import ListAny
from frinx.common.type_aliases import ListStr
from frinx.common.util import snake_to_camel_case


class TaskInput(BaseModel):

    _task_id: Optional[str] = PrivateAttr(None)
    _workflow_instance_id: Optional[str] = PrivateAttr(None)
    _workflow_type: Optional[str] = PrivateAttr(None)

    model_config = ConfigDict(
        frozen=False,
        extra='ignore',
        validate_assignment=True,
        validate_default=True,
        arbitrary_types_allowed=True,
        populate_by_name=False
    )


class TaskOutput(BaseModel):

    model_config = ConfigDict(
        frozen=False,
        extra='allow',
    )


class BaseTaskdef(BaseModel):
    name: Optional[str]
    description: Optional[str]
    owner_app: Optional[str] = Field(default=None)
    create_time: Optional[int] = Field(default=None)
    update_time: Optional[int] = Field(default=None)
    created_by: Optional[str] = Field(default=None)
    updated_by: Optional[str] = Field(default=None)
    retry_count: Optional[int] = Field(default=None)
    timeout_seconds: Optional[int] = Field(default=None)
    input_keys: Optional[ListStr] = Field(default=None)
    output_keys: Optional[ListStr] = Field(default=None)
    timeout_policy: Optional[TimeoutPolicy] = Field(default=None)
    retry_logic: Optional[RetryLogic] = Field(default=None)
    retry_delay_seconds: Optional[int] = Field(default=None)
    response_timeout_seconds: Optional[int] = Field(default=None)
    concurrent_exec_limit: Optional[int] = Field(default=None)
    input_template: Optional[DictAny] = Field(default=None)
    rate_limit_per_frequency: Optional[int] = Field(default=None)
    rate_limit_frequency_in_seconds: Optional[int] = Field(default=None)
    isolation_group_id: Optional[str] = Field(default=None)
    execution_name_space: Optional[str] = Field(default=None)
    owner_email: Optional[str] = Field(default=None)
    poll_timeout_seconds: Optional[int] = Field(default=None)
    backoff_scale_factor: Optional[int] = Field(default=None)
    limit_to_thread_count: Optional[int] = Field(default=None)

    model_config = ConfigDict(
        frozen=True,
        extra='ignore',
        validate_assignment=True,
        alias_generator=snake_to_camel_case,
        populate_by_name=True,
        use_enum_values=True
    )


class TaskDefinition(BaseTaskdef):
    name: str
    description: str
    labels: Optional[ListAny] = Field(default=None)
    rbac: Optional[ListAny] = Field(default=None)

    model_config = ConfigDict(
        frozen=False,
        extra='ignore',
    )


class DefaultTaskDefinition(BaseTaskdef):
    retry_count: int = 0
    timeout_policy: TimeoutPolicy = TimeoutPolicy.ALERT_ONLY
    timeout_seconds: int = 60
    retry_logic: RetryLogic = RetryLogic.FIXED
    retry_delay_seconds: int = 0
    response_timeout_seconds: int = 59
    rate_limit_per_frequency: int = 0
    rate_limit_frequency_in_seconds: int = 5
    owner_email: str = X_FROM


class ConductorWorkerError(Exception):
    """Base error of Conductor worker."""


class InvalidTaskInputError(ConductorWorkerError):
    """Error due to invalid input of (simple) task."""


class FailedTaskError(ConductorWorkerError):
    """Exception causing task to fail with provided message instead of full traceback."""

    def __init__(self, error_msg: str) -> None:
        self.error_msg = error_msg


class TaskExecutionProperties(BaseModel):
    exclude_empty_inputs: bool = False
    transform_string_to_json_valid: bool = False
    pass_worker_input_exception_to_task_output: bool = False
    worker_input_exception_task_output_path: str = 'result.error'

    model_config = ConfigDict(
        frozen=True,
        extra='ignore',
        validate_default=True,
        arbitrary_types_allowed=False,
        populate_by_name=False
    )
