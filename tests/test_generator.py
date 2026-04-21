import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openapi_test_tool.generator import TestCaseCategory, TestCaseType, generate_test_suite  # noqa: E402
from openapi_test_tool.parser import extract_spec_summary, load_openapi_spec  # noqa: E402


def _build_test_suite():
    spec_path = PROJECT_ROOT / "samples" / "sample_openapi.yaml"
    spec = load_openapi_spec(spec_path)
    summary = extract_spec_summary(spec)
    return generate_test_suite(summary)


def test_generate_valid_case_for_get_endpoint_with_path_and_query_params():
    suite = _build_test_suite()

    valid_get_cases = [
        case
        for case in suite.test_cases
        if case.endpoint_path == "/users/{userId}" and case.test_type == TestCaseType.VALID_CASE
    ]

    assert valid_get_cases
    test_case = valid_get_cases[0]
    assert test_case.method == "GET"
    assert test_case.path_params["userId"] == 10
    assert test_case.query_params["includePosts"] is True
    assert test_case.expected_status_codes == [200]
    assert test_case.category == TestCaseCategory.VALID


def test_generate_valid_case_for_post_endpoint_with_request_body():
    suite = _build_test_suite()

    valid_post_cases = [
        case
        for case in suite.test_cases
        if case.endpoint_path == "/users" and case.test_type == TestCaseType.VALID_CASE
    ]

    assert valid_post_cases
    test_case = valid_post_cases[0]
    assert test_case.method == "POST"
    assert test_case.request_body["username"] == "alice"
    assert test_case.request_body["age"] == 25
    assert test_case.request_body["role"] == "member"
    assert test_case.expected_status_codes == [201]


def test_generate_missing_required_field_case():
    suite = _build_test_suite()

    cases = [
        case
        for case in suite.test_cases
        if case.endpoint_path == "/users" and case.test_type == TestCaseType.MISSING_REQUIRED_FIELD
    ]

    assert cases
    assert any("username" not in case.request_body for case in cases)


def test_generate_wrong_data_type_case():
    suite = _build_test_suite()

    cases = [case for case in suite.test_cases if case.test_type == TestCaseType.WRONG_DATA_TYPE]

    assert cases
    assert any(case.path_params.get("userId") == "wrong_type" for case in cases if case.endpoint_path == "/users/{userId}")
    assert any(case.request_body.get("age") == "wrong_type" for case in cases if case.endpoint_path == "/users")


def test_generate_invalid_enum_case():
    suite = _build_test_suite()

    cases = [case for case in suite.test_cases if case.test_type == TestCaseType.INVALID_ENUM]

    assert cases
    assert any(case.request_body.get("role") == "__invalid_enum__" for case in cases if case.endpoint_path == "/users")


def test_generate_boundary_case():
    suite = _build_test_suite()

    cases = [case for case in suite.test_cases if case.test_type == TestCaseType.BOUNDARY_VALUE]

    assert cases
    assert any(case.path_params.get("userId") == 1 for case in cases if case.endpoint_path == "/users/{userId}")
    assert any(case.request_body.get("username") == "xxx" for case in cases if case.endpoint_path == "/users")


def test_testcase_generator_returns_non_empty_list():
    suite = _build_test_suite()

    assert suite.total_count > 0
    assert suite.valid_count > 0
    assert suite.invalid_count > 0
    assert suite.test_cases
