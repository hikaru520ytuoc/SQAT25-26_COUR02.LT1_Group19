import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openapi_test_tool.executor.execution_model import TestExecutionResult, TestExecutionSummary  # noqa: E402
from openapi_test_tool.generator import TestCaseCategory, TestCaseType, generate_test_suite  # noqa: E402
from openapi_test_tool.parser import extract_spec_summary, load_openapi_spec  # noqa: E402
from openapi_test_tool.reporter import (  # noqa: E402
    build_html_report,
    build_json_report,
    build_markdown_report,
    build_report_context,
    write_report_files,
)


def _build_report_context():
    spec_path = PROJECT_ROOT / "samples" / "sample_openapi.yaml"
    spec = load_openapi_spec(spec_path)
    spec_summary = extract_spec_summary(spec)
    test_suite = generate_test_suite(spec_summary)

    results = [
        TestExecutionResult(
            test_id="TC-001",
            name="GET /users/{userId} - valid case",
            method="GET",
            path="/users/{userId}",
            final_url="http://localhost:8000/users/10",
            category=TestCaseCategory.VALID,
            test_type=TestCaseType.VALID_CASE,
            expected_status_codes=[200],
            actual_status_code=200,
            passed=True,
            response_time_ms=12.5,
            response_headers={"Content-Type": "application/json"},
            response_body={
                "id": 10,
                "username": "alice",
                "email": "alice@example.com",
                "age": 25,
                "role": "member",
            },
            validation_errors=[],
            execution_error=None,
            source_operation_id="getUserById",
        ),
        TestExecutionResult(
            test_id="TC-002",
            name="POST /users - invalid enum",
            method="POST",
            path="/users",
            final_url="http://localhost:8000/users",
            category=TestCaseCategory.INVALID,
            test_type=TestCaseType.INVALID_ENUM,
            expected_status_codes=[422],
            actual_status_code=400,
            passed=False,
            response_time_ms=8.0,
            response_headers={"Content-Type": "application/json"},
            response_body={"message": "invalid role"},
            validation_errors=["Status code 400 is not in expected list [422]."],
            execution_error=None,
            source_operation_id="createUser",
        ),
    ]

    execution_summary = TestExecutionSummary(
        total_count=2,
        passed_count=1,
        failed_count=1,
        valid_passed_count=1,
        invalid_passed_count=0,
        results=results,
    )

    return build_report_context(
        spec_file=str(spec_path),
        base_url="http://localhost:8000",
        spec_summary=spec_summary,
        test_suite_summary=test_suite,
        execution_summary=execution_summary,
        generated_at="2026-04-21T12:00:00",
    )


def test_json_reporter_builds_expected_structure():
    context = _build_report_context()

    payload = build_json_report(context)

    assert payload["tool"]["name"] == "OpenAPI Test Tool"
    assert payload["spec"]["title"] == "Sample User API"
    assert payload["summary"]["passed_count"] == 1
    assert len(payload["results"]) == 2


def test_markdown_reporter_generates_markdown_content():
    context = _build_report_context()

    markdown = build_markdown_report(context)

    assert markdown.startswith("# OpenAPI Test Tool Execution Report")
    assert "## Execution Summary" in markdown
    assert "TC-002" in markdown
    assert "Failed Cases" in markdown


def test_html_reporter_renders_html():
    context = _build_report_context()

    html = build_html_report(context)

    assert "<html" in html.lower()
    assert "OpenAPI Test Tool Execution Report" in html
    assert "TC-001" in html
    assert "status-fail" in html


def test_report_writer_writes_files(tmp_path):
    context = _build_report_context()

    report_files = write_report_files(context, tmp_path, timestamp="20260421_120000")

    assert report_files["json"].exists()
    assert report_files["markdown"].exists()
    assert report_files["html"].exists()

    json_payload = json.loads(report_files["json"].read_text(encoding="utf-8"))
    assert json_payload["summary"]["failed_count"] == 1
    assert "Execution Summary" in report_files["markdown"].read_text(encoding="utf-8")
    assert "<table>" in report_files["html"].read_text(encoding="utf-8")
