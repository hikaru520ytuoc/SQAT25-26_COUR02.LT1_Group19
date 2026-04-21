import sys
from pathlib import Path
from types import SimpleNamespace

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openapi_test_tool.executor import build_request, execute_test_suite, validate_execution_result  # noqa: E402
from openapi_test_tool.executor.execution_model import TestExecutionSummary  # noqa: E402
from openapi_test_tool.generator import TestCaseType, generate_test_suite  # noqa: E402
from openapi_test_tool.parser import extract_spec_summary, load_openapi_spec  # noqa: E402


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text="", headers=None, elapsed_ms=12.5):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.headers = headers or {"Content-Type": "application/json"}
        self.elapsed = SimpleNamespace(total_seconds=lambda: elapsed_ms / 1000)

    def json(self):
        if self._json_data is None:
            raise ValueError("No JSON")
        return self._json_data



def _build_test_suite():
    spec_path = PROJECT_ROOT / "samples" / "sample_openapi.yaml"
    spec = load_openapi_spec(spec_path)
    summary = extract_spec_summary(spec)
    return generate_test_suite(summary)



def test_request_builder_builds_correct_url_with_path_params():
    suite = _build_test_suite()
    test_case = next(
        case
        for case in suite.test_cases
        if case.endpoint_path == "/users/{userId}" and case.test_type == TestCaseType.VALID_CASE
    )

    built_request = build_request("http://localhost:8000", test_case)

    assert built_request.url == "http://localhost:8000/users/10"



def test_request_builder_keeps_query_params():
    suite = _build_test_suite()
    test_case = next(
        case
        for case in suite.test_cases
        if case.endpoint_path == "/users/{userId}" and case.test_type == TestCaseType.VALID_CASE
    )

    built_request = build_request("http://localhost:8000", test_case)

    assert built_request.query_params == {"includePosts": True}



def test_response_validator_passes_when_status_code_is_expected():
    suite = _build_test_suite()
    test_case = next(
        case for case in suite.test_cases if case.endpoint_path == "/users" and case.test_type == TestCaseType.VALID_CASE
    )

    validation_result = validate_execution_result(
        test_case=test_case,
        actual_status_code=201,
        response_body={
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "age": 25,
            "role": "member",
        },
    )

    assert validation_result.passed is True
    assert validation_result.status_code_valid is True
    assert validation_result.schema_validation_applied is True



def test_response_validator_fails_when_status_code_is_unexpected():
    suite = _build_test_suite()
    test_case = next(
        case for case in suite.test_cases if case.endpoint_path == "/users" and case.test_type == TestCaseType.VALID_CASE
    )

    validation_result = validate_execution_result(
        test_case=test_case,
        actual_status_code=400,
        response_body={"message": "invalid"},
    )

    assert validation_result.passed is False
    assert validation_result.status_code_valid is False



def test_response_validator_validates_basic_json_schema_successfully():
    suite = _build_test_suite()
    test_case = next(
        case for case in suite.test_cases if case.endpoint_path == "/users/{userId}" and case.test_type == TestCaseType.VALID_CASE
    )

    validation_result = validate_execution_result(
        test_case=test_case,
        actual_status_code=200,
        response_body={
            "id": 10,
            "username": "alice",
            "email": "alice@example.com",
            "age": 25,
            "role": "member",
        },
    )

    assert validation_result.passed is True
    assert validation_result.validation_errors == []



def test_executor_handles_successful_request_with_mock(monkeypatch):
    suite = _build_test_suite()
    test_case = next(
        case for case in suite.test_cases if case.endpoint_path == "/users" and case.test_type == TestCaseType.VALID_CASE
    )

    def fake_request(**kwargs):
        return FakeResponse(
            status_code=201,
            json_data={
                "id": 1,
                "username": kwargs["json"]["username"],
                "email": kwargs["json"]["email"],
                "age": kwargs["json"]["age"],
                "role": kwargs["json"]["role"],
            },
        )

    monkeypatch.setattr(requests, "request", fake_request)

    summary = execute_test_suite([test_case], base_url="http://localhost:8000")

    assert isinstance(summary, TestExecutionSummary)
    assert summary.total_count == 1
    assert summary.passed_count == 1
    assert summary.results[0].actual_status_code == 201
    assert summary.results[0].passed is True



def test_executor_handles_timeout_with_mock(monkeypatch):
    suite = _build_test_suite()
    test_case = next(
        case for case in suite.test_cases if case.endpoint_path == "/users/{userId}" and case.test_type == TestCaseType.VALID_CASE
    )

    def fake_request(**kwargs):
        raise requests.exceptions.Timeout("timed out")

    monkeypatch.setattr(requests, "request", fake_request)

    summary = execute_test_suite([test_case], base_url="http://localhost:8000")

    assert summary.total_count == 1
    assert summary.failed_count == 1
    assert summary.results[0].passed is False
    assert "timed out" in summary.results[0].execution_error
