from __future__ import annotations

from openapi_test_tool.executor.api_runner import DEFAULT_TIMEOUT_SECONDS, send_request
from openapi_test_tool.executor.execution_model import TestExecutionResult, TestExecutionSummary
from openapi_test_tool.executor.request_builder import build_request
from openapi_test_tool.executor.response_validator import validate_execution_result
from openapi_test_tool.generator.testcase_model import GeneratedTestCase, TestCaseCategory


def execute_test_suite(
    test_cases: list[GeneratedTestCase],
    base_url: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> TestExecutionSummary:
    """Run all generated test cases without stopping on individual failures."""

    results: list[TestExecutionResult] = []

    for test_case in test_cases:
        built_request = build_request(base_url, test_case)
        raw_result = send_request(built_request, timeout_seconds=timeout_seconds)

        if raw_result.execution_error:
            results.append(
                TestExecutionResult(
                    test_id=test_case.test_id,
                    name=test_case.name,
                    method=test_case.method,
                    path=test_case.endpoint_path,
                    final_url=built_request.url,
                    category=test_case.category,
                    test_type=test_case.test_type,
                    expected_status_codes=list(test_case.expected_status_codes),
                    actual_status_code=raw_result.actual_status_code,
                    passed=False,
                    response_time_ms=raw_result.response_time_ms,
                    response_headers=raw_result.response_headers,
                    response_body=raw_result.response_body,
                    validation_errors=[],
                    execution_error=raw_result.execution_error,
                    source_operation_id=test_case.source_operation_id,
                )
            )
            continue

        validation_result = validate_execution_result(
            test_case=test_case,
            actual_status_code=raw_result.actual_status_code,
            response_body=raw_result.response_body,
        )

        results.append(
            TestExecutionResult(
                test_id=test_case.test_id,
                name=test_case.name,
                method=test_case.method,
                path=test_case.endpoint_path,
                final_url=built_request.url,
                category=test_case.category,
                test_type=test_case.test_type,
                expected_status_codes=list(test_case.expected_status_codes),
                actual_status_code=raw_result.actual_status_code,
                passed=validation_result.passed,
                response_time_ms=raw_result.response_time_ms,
                response_headers=raw_result.response_headers,
                response_body=raw_result.response_body,
                validation_errors=validation_result.validation_errors,
                execution_error=None,
                source_operation_id=test_case.source_operation_id,
            )
        )

    passed_count = sum(1 for result in results if result.passed)
    failed_count = len(results) - passed_count
    valid_passed_count = sum(
        1 for result in results if result.passed and result.category == TestCaseCategory.VALID
    )
    invalid_passed_count = sum(
        1 for result in results if result.passed and result.category == TestCaseCategory.INVALID
    )

    return TestExecutionSummary(
        total_count=len(results),
        passed_count=passed_count,
        failed_count=failed_count,
        valid_passed_count=valid_passed_count,
        invalid_passed_count=invalid_passed_count,
        results=results,
    )
