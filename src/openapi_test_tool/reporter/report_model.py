from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from openapi_test_tool import __version__
from openapi_test_tool.executor.execution_model import TestExecutionResult, TestExecutionSummary
from openapi_test_tool.generator.testcase_model import TestSuiteSummary
from openapi_test_tool.parser.models import OpenAPISpecSummary


class ReportSummary(BaseModel):
    """Aggregated report metrics rendered in JSON/Markdown/HTML outputs."""

    generated_at: str
    base_url: str
    total_test_cases: int
    generated_valid_count: int
    generated_invalid_count: int
    passed_count: int
    failed_count: int
    valid_passed_count: int
    invalid_passed_count: int


class ReportContext(BaseModel):
    """Complete immutable context required to render all report formats."""

    tool_name: str = "OpenAPI Test Tool"
    tool_version: str = __version__
    spec_file: str
    base_url: str
    summary: ReportSummary
    spec_summary: OpenAPISpecSummary
    test_suite_summary: TestSuiteSummary
    execution_summary: TestExecutionSummary
    detailed_results: list[TestExecutionResult] = Field(default_factory=list)

    def to_serializable_dict(self) -> dict[str, Any]:
        return {
            "tool": {
                "name": self.tool_name,
                "version": self.tool_version,
            },
            "spec": {
                "file": self.spec_file,
                "openapi_version": self.spec_summary.openapi_version,
                "title": self.spec_summary.title,
                "version": self.spec_summary.version,
                "path_count": self.spec_summary.path_count,
                "operation_count": self.spec_summary.operation_count,
            },
            "execution": {
                "generated_at": self.summary.generated_at,
                "base_url": self.base_url,
                "timeout_related_failures": sum(1 for result in self.detailed_results if result.execution_error),
            },
            "summary": {
                "total_test_cases": self.summary.total_test_cases,
                "generated_valid_count": self.summary.generated_valid_count,
                "generated_invalid_count": self.summary.generated_invalid_count,
                "passed_count": self.summary.passed_count,
                "failed_count": self.summary.failed_count,
                "valid_passed_count": self.summary.valid_passed_count,
                "invalid_passed_count": self.summary.invalid_passed_count,
            },
            "results": [result.model_dump(mode="json") for result in self.detailed_results],
        }


def build_report_context(
    *,
    spec_file: str,
    base_url: str,
    spec_summary: OpenAPISpecSummary,
    test_suite_summary: TestSuiteSummary,
    execution_summary: TestExecutionSummary,
    generated_at: str | None = None,
) -> ReportContext:
    timestamp = generated_at or datetime.now().isoformat(timespec="seconds")
    summary = ReportSummary(
        generated_at=timestamp,
        base_url=base_url,
        total_test_cases=execution_summary.total_count,
        generated_valid_count=test_suite_summary.valid_count,
        generated_invalid_count=test_suite_summary.invalid_count,
        passed_count=execution_summary.passed_count,
        failed_count=execution_summary.failed_count,
        valid_passed_count=execution_summary.valid_passed_count,
        invalid_passed_count=execution_summary.invalid_passed_count,
    )
    return ReportContext(
        spec_file=spec_file,
        base_url=base_url,
        summary=summary,
        spec_summary=spec_summary,
        test_suite_summary=test_suite_summary,
        execution_summary=execution_summary,
        detailed_results=execution_summary.results,
    )
