from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TestCaseCategory(str, Enum):
    """High-level classification of generated test cases."""

    __test__ = False

    VALID = "valid"
    INVALID = "invalid"


class TestCaseType(str, Enum):
    """Supported generated test case types for the MVP generator."""

    __test__ = False

    VALID_CASE = "valid_case"
    MISSING_REQUIRED_PARAMETER = "missing_required_parameter"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    WRONG_DATA_TYPE = "wrong_data_type"
    INVALID_ENUM = "invalid_enum"
    EMPTY_VALUE = "empty_value"
    BOUNDARY_VALUE = "boundary_value"


class GeneratedTestCase(BaseModel):
    """Reusable test case model for later execution stages."""

    test_id: str
    name: str
    description: str
    endpoint_path: str
    method: str
    path_params: dict[str, Any] = Field(default_factory=dict)
    query_params: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, Any] = Field(default_factory=dict)
    request_body: Any | None = None
    expected_status_codes: list[int] = Field(default_factory=list)
    category: TestCaseCategory
    test_type: TestCaseType
    source_operation_id: str | None = None
    source_summary: str | None = None
    source_metadata: dict[str, Any] = Field(default_factory=dict)


class TestSuiteSummary(BaseModel):
    """Summary wrapper returned by the top-level test case generator."""

    total_count: int
    valid_count: int
    invalid_count: int
    test_cases: list[GeneratedTestCase] = Field(default_factory=list)
