from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ParameterLocation = Literal["path", "query", "header"]


class ApiParameter(BaseModel):
    """Normalized parameter definition extracted from an OpenAPI operation."""

    name: str
    location: ParameterLocation = Field(alias="in")
    required: bool = False
    description: str | None = None
    schema_data: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "populate_by_name": True,
    }


class RequestBodySpec(BaseModel):
    """Subset of request body metadata needed for future test generation."""

    required: bool = False
    content_type: str = "application/json"
    schema_data: dict[str, Any] | None = None


class ResponseSpec(BaseModel):
    """Subset of response metadata needed for validation and test generation."""

    status_code: str
    description: str | None = None
    content_type: str | None = None
    schema_data: dict[str, Any] | None = None


class EndpointSpec(BaseModel):
    """Normalized operation extracted from the OpenAPI document."""

    path: str
    method: str
    summary: str | None = None
    operation_id: str | None = Field(default=None, alias="operationId")
    parameters: list[ApiParameter] = Field(default_factory=list)
    request_body: RequestBodySpec | None = None
    responses: list[ResponseSpec] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
    }


class OpenAPISpecSummary(BaseModel):
    """High-level summary of the parsed spec for CLI reporting and later stages."""

    openapi_version: str
    title: str | None = None
    version: str | None = None
    path_count: int
    operation_count: int
    endpoints: list[EndpointSpec] = Field(default_factory=list)
