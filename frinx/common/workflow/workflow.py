from __future__ import annotations

import json
from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Any
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator

from frinx.common.conductor_enums import TimeoutPolicy
from frinx.common.import_workflows import register_workflow
from frinx.common.type_aliases import ListAny
from frinx.common.util import jsonify_description
from frinx.common.util import snake_to_camel_case
from frinx.common.workflow.task import WorkflowTaskImpl


class FrontendWFInputFieldType(str, Enum):
    TOGGLE = 'toggle'
    SELECT = 'select'
    STRING = 'string'
    INT = 'int'
    TEXTAREA = 'textarea'
    LIST = 'list'
    JSON = 'json'
    MULTISELECT = 'multiselect'


class WorkflowInputField(BaseModel):
    name: str
    frontend_default_value: Any = ''
    description: str = ''
    options: Optional[ListAny] = None
    type: Any
    frontend_type: FrontendWFInputFieldType | None = None
    wf_input: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        extra='forbid',
        str_min_length=1,
        use_enum_values=True,
        populate_by_name=True,
    )

    def __init__(self, **values: Any) -> None:
        if not isinstance(values['name'], str):
            raise ValueError('Invalid type of input for name property')
        values['wf_input'] = f"${{workflow.input.{values['name']}}}"
        super().__init__(**values)


class WorkflowImpl(BaseModel, ABC):
    class WorkflowInput(BaseModel):

        model_config = ConfigDict(
            frozen=True,
            extra='allow',
            validate_default=True
        )

        def __init__(self, **values: Any):
            super().__init__(**values)

    class WorkflowOutput(BaseModel):
        model_config = ConfigDict(
            frozen=True,
            extra='forbid',
            validate_default=True
        )

    name: str
    version: int

    # LABELS, RBAC, DESCRIPTION, INPUT VALUES
    description: str
    labels: list[str] | None = Field(default=None)
    rbac: list[str] | None = Field(default=None)

    # PREDEFINED
    restartable: bool = Field(default=False)
    output_parameters: Union[WorkflowOutput, dict[str, object]] = Field(default={})
    input_parameters: list[WorkflowInputField | str] = Field(default=[])
    tasks: list[WorkflowTaskImpl] = Field(default=[])
    timeout_policy: TimeoutPolicy = Field(default=TimeoutPolicy.TIME_OUT_WORKFLOW)
    timeout_seconds: int = Field(default=60)

    owner_app: Optional[str] = Field(default=None)
    create_time: Optional[int] = Field(default=None)
    update_time: Optional[int] = Field(default=None)
    created_by: Optional[str] = Field(default=None)
    updated_by: Optional[str] = Field(default=None)
    failure_workflow: Optional[str] = Field(default=None)
    schema_version: Optional[int] = Field(default=None)
    workflow_status_listener_enabled: Optional[bool] = Field(default=None)
    owner_email: Optional[str] = Field(default=None)
    variables: Optional[dict[str, Any]] = Field(default=None)
    input_template: dict[str, Any] = Field(default={})

    @field_validator('output_parameters', mode='before')
    def output_param(cls, data: BaseModel | dict[str, object]) -> dict[str, object]:
        if isinstance(data, BaseModel):
            return data.model_dump(exclude_none=True)
        return data

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.description_builder()
        self.workflow_builder(self.input_builder())

    def input_builder(self) -> WorkflowInput:
        workflow_inputs = self.WorkflowInput()
        self.input_parameters = []
        for wf_input in workflow_inputs:
            self.input_parameters.append(
                json.dumps(
                    {
                        wf_input[1].name: {
                            'value': wf_input[1].frontend_default_value,
                            'description': wf_input[1].description,
                            'type': wf_input[1].type,
                            'options': wf_input[1].options,
                        }
                    }
                )
            )
            self.input_template[wf_input[1].name] = wf_input[1].frontend_default_value
        return workflow_inputs

    def description_builder(self) -> None:
        self.description = jsonify_description(self.description, self.labels, self.rbac)

    @classmethod
    def register(cls, overwrite: bool = False) -> None:
        register_workflow(cls().model_dump_json(by_alias=True, exclude_none=True), overwrite)

    @abstractmethod
    def workflow_builder(self, workflow_inputs: Any) -> None:
        # TODO: workflow_inputs needs to be a reference to WorkflowInput child in it's namespace
        # error: Argument 1 of "workflow_builder" is incompatible with supertype "WorkflowImpl";
        # supertype defines the argument type as "WorkflowInput"
        # NOTE: This violates the Liskov substitution principle
        # NOTE: See https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        # https://discuss.python.org/t/a-way-to-typehint-a-return-type-in-parent-based-on-return-type-of-a-child/17020
        pass

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        alias_generator=snake_to_camel_case,
        populate_by_name=True
    )
