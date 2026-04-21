from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from openapi_test_tool.generator.testcase_model import TestCaseCategory, TestCaseType


class BuiltRequest(BaseModel):
    __test__ = False
    """Normalized HTTP request ready to be sent by the API runner."""

    method: str
    url: str
    path: str
    path_params: dict[str, Any] = Field(default_factory=dict)
    query_params: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, Any] = Field(default_factory=dict)
    json_body: Any | None = None


class RawExecutionResponse(BaseModel):
    __test__ = False
    """Raw transport-level result returned by the API runner."""

    actual_status_code: int | None = None
    response_headers: dict[str, Any] = Field(default_factory=dict)
    response_body: Any | None = None
    response_time_ms: float | None = None
    execution_error: str | None = None


class ResponseValidationResult(BaseModel):
    __test__ = False
    """Validation result for one executed test case."""

    status_code_valid: bool
    schema_validation_applied: bool = False
    schema_validation_passed: bool | None = None
    validation_errors: list[str] = Field(default_factory=list)
    passed: bool = False


class TestExecutionResult(BaseModel):
    __test__ = False
    """Final execution result for one generated test case."""

    test_id: str
    name: str
    method: str
    path: str
    final_url: str
    category: TestCaseCategory
    test_type: TestCaseType
    expected_status_codes: list[int] = Field(default_factory=list)
    actual_status_code: int | None = None
    passed: bool = False
    response_time_ms: float | None = None
    response_headers: dict[str, Any] = Field(default_factory=dict)
    response_body: Any | None = None
    validation_errors: list[str] = Field(default_factory=list)
    execution_error: str | None = None
    source_operation_id: str | None = None


class TestExecutionSummary(BaseModel):
    __test__ = False
    """Summary for one end-to-end execution run."""

    total_count: int
    passed_count: int
    failed_count: int
    valid_passed_count: int
    invalid_passed_count: int
    results: list[TestExecutionResult] = Field(default_factory=list)
