from __future__ import annotations

from typing import Any
from typing import Optional
from typing import TypeAlias

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from frinx.common.type_aliases import DictAny
from frinx.common.util import snake_to_camel_case

WorkflowTask: TypeAlias = dict[str, str]
TaskDef: TypeAlias = dict[str, str]


class Task(BaseModel):
    input_data: DictAny = Field(default={})
    workflow_task: Any = Field(default=None)
    task_definition: Any = Field(default=None)

    task_type: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    reference_task_name: Optional[str] = Field(default=None)
    retry_count: Optional[int] = Field(default=None)
    seq: Optional[int] = Field(default=None)
    correlation_id: Optional[str] = Field(default=None)
    poll_count: Optional[int] = Field(default=None)
    task_def_name: Optional[str] = Field(default=None)
    scheduled_time: Optional[int] = Field(default=None)
    start_time: Optional[int] = Field(default=None)
    end_time: Optional[int] = Field(default=None)
    update_time: Optional[int] = Field(default=None)
    start_delay_in_seconds: Optional[int] = Field(default=None)
    retried_task_id: Optional[str] = Field(default=None)
    retried: Optional[bool] = Field(default=None)
    executed: Optional[bool] = Field(default=None)
    callback_from_worker: Optional[bool] = Field(default=None)
    response_timeout_seconds: Optional[int] = Field(default=None)
    workflow_instance_id: Optional[str] = Field(default=None)
    workflow_type: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)
    reason_for_incompletion: Optional[str] = Field(default=None)
    callback_after_seconds: Optional[int] = Field(default=None)
    worker_id: Optional[str] = Field(default=None)
    output_data: Optional[dict[str, Any]] = Field(default=None)
    domain: Optional[str] = Field(default=None)
    rate_limit_per_frequency: Optional[int] = Field(default=None)
    rate_limit_frequency_in_seconds: Optional[int] = Field(default=None)
    external_input_payload_storage_path: Optional[str] = Field(default=None)
    external_output_payload_storage_path: Optional[str] = Field(default=None)
    workflow_priority: Optional[int] = Field(default=None)
    execution_name_space: Optional[str] = Field(default=None)
    isolation_group_id: Optional[str] = Field(default=None)
    iteration: Optional[int] = Field(default=None)
    sub_workflow_id: Optional[str] = Field(default=None)
    subworkflow_changed: Optional[bool] = Field(default=None)
    loop_over_task: Optional[bool] = Field(default=None)
    queue_wait_time: Optional[int] = Field(default=None)

    model_config = ConfigDict(
        frozen=False,
        extra='forbid',
        validate_assignment=True,
        alias_generator=snake_to_camel_case,
        populate_by_name=True
    )
