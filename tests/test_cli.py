import sys
from pathlib import Path

from typer.testing import CliRunner

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openapi_test_tool.cli import app  # noqa: E402
from openapi_test_tool.executor.execution_model import TestExecutionResult, TestExecutionSummary  # noqa: E402
from openapi_test_tool.generator import TestCaseCategory, TestCaseType  # noqa: E402

runner = CliRunner()



def test_cli_parse_generate_and_execute_success(monkeypatch, tmp_path):
    spec_path = PROJECT_ROOT / "samples" / "sample_openapi.yaml"
    output_dir = tmp_path / "reports"

    fake_summary = TestExecutionSummary(
        total_count=2,
        passed_count=1,
        failed_count=1,
        valid_passed_count=1,
        invalid_passed_count=0,
        results=[
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
                response_time_ms=10.0,
                response_headers={"Content-Type": "application/json"},
                response_body={"id": 10},
                validation_errors=[],
                execution_error=None,
                source_operation_id="getUserById",
            )
        ],
    )

    monkeypatch.setattr("openapi_test_tool.cli.execute_test_suite", lambda **kwargs: fake_summary)

    result = runner.invoke(
        app,
        [
            "--spec",
            str(spec_path),
            "--base-url",
            "http://localhost:8000",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert output_dir.exists()
    assert "OpenAPI parsing completed successfully." in result.stdout
    assert "Generated Test Case Summary" in result.stdout
    assert "Execution Summary" in result.stdout
    assert "Generated Report Files" in result.stdout
    assert "Test execution and report generation completed successfully." in result.stdout
    assert len(list(output_dir.glob("report_*.json"))) == 1
    assert len(list(output_dir.glob("report_*.md"))) == 1
    assert len(list(output_dir.glob("report_*.html"))) == 1
