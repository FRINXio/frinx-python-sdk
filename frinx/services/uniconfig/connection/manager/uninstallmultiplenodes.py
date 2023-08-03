# generated by datamodel-codegen:
#   filename:  uniconfigV3.yaml

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from ...frinx import types
from . import ConnectionType


class Node(BaseModel):
    class Config:
        allow_population_by_field_name = True

    node_id: str = Field(..., alias='node-id')
    """
    Node identifier of CLI/NETCONF node.
    """
    connection_type: Optional[ConnectionType] = Field(None, alias='connection-type')


class Input(BaseModel):
    class Config:
        allow_population_by_field_name = True

    nodes: Optional[list[Node]] = None


class NodeResult(BaseModel):
    class Config:
        allow_population_by_field_name = True

    node_id: str = Field(..., alias='node-id')
    """
    Node identifier of CLI/NETCONF node.
    """
    error_message: Optional[str] = Field(None, alias='error-message')
    """
    Message that described occurred error during invocation of operation on a specific node.
    """
    status: types.OperationResultType


class Output(BaseModel):
    class Config:
        allow_population_by_field_name = True

    error_message: Optional[str] = Field(None, alias='error-message')
    """
    Error message that describe overall problem.
    """
    node_results: Optional[list[NodeResult]] = Field(None, alias='node-results')
    overall_status: types.OperationResultType = Field(..., alias='overall-status')
