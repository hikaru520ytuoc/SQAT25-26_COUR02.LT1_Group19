from __future__ import annotations

import json
from typing import Any

from openapi_test_tool.generator.boundary_generator import generate_boundary_test_cases
from openapi_test_tool.generator.invalid_case_generator import generate_invalid_test_cases
from openapi_test_tool.generator.testcase_model import GeneratedTestCase, TestCaseCategory, TestSuiteSummary
from openapi_test_tool.generator.valid_case_generator import generate_valid_test_cases
from openapi_test_tool.parser.models import OpenAPISpecSummary


def generate_test_suite(spec_summary: OpenAPISpecSummary) -> TestSuiteSummary:
    all_cases: list[GeneratedTestCase] = []

    for endpoint in spec_summary.endpoints:
        endpoint_cases: list[GeneratedTestCase] = []
        endpoint_cases.extend(generate_valid_test_cases(endpoint))
        endpoint_cases.extend(generate_invalid_test_cases(endpoint))
        endpoint_cases.extend(generate_boundary_test_cases(endpoint))
        all_cases.extend(_deduplicate_cases(endpoint_cases))

    _assign_test_ids(all_cases)

    valid_count = sum(1 for case in all_cases if case.category == TestCaseCategory.VALID)
    invalid_count = sum(1 for case in all_cases if case.category == TestCaseCategory.INVALID)

    return TestSuiteSummary(
        total_count=len(all_cases),
        valid_count=valid_count,
        invalid_count=invalid_count,
        test_cases=all_cases,
    )


def _deduplicate_cases(cases: list[GeneratedTestCase]) -> list[GeneratedTestCase]:
    unique_cases: list[GeneratedTestCase] = []
    seen_signatures: set[str] = set()

    for case in cases:
        signature = _case_signature(case)
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        unique_cases.append(case)

    return unique_cases


def _case_signature(case: GeneratedTestCase) -> str:
    payload: dict[str, Any] = {
        "endpoint_path": case.endpoint_path,
        "method": case.method,
        "path_params": case.path_params,
        "query_params": case.query_params,
        "headers": case.headers,
        "request_body": case.request_body,
        "expected_status_codes": case.expected_status_codes,
        "category": case.category.value,
        "test_type": case.test_type.value,
        "source_metadata": case.source_metadata,
    }
    return json.dumps(payload, sort_keys=True, default=str)


def _assign_test_ids(cases: list[GeneratedTestCase]) -> None:
    for index, case in enumerate(cases, start=1):
        case.test_id = f"TC-{index:03d}"
