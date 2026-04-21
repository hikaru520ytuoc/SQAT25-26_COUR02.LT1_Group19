from __future__ import annotations

from typing import Any

from jsonschema import ValidationError, validate

from openapi_test_tool.executor.execution_model import ResponseValidationResult
from openapi_test_tool.generator.testcase_model import GeneratedTestCase


def validate_execution_result(
    test_case: GeneratedTestCase,
    actual_status_code: int | None,
    response_body: Any,
) -> ResponseValidationResult:
    """Validate status code first, then optionally validate response schema."""

    validation_errors: list[str] = []
    status_code_valid = actual_status_code in test_case.expected_status_codes if actual_status_code is not None else False

    schema = _select_schema_for_status(test_case, actual_status_code)
    schema_validation_applied = schema is not None
    schema_validation_passed: bool | None = None

    if schema_validation_applied:
        if not isinstance(response_body, (dict, list)):
            schema_validation_passed = False
            validation_errors.append(
                "Expected a JSON response body for schema validation, but received non-JSON content."
            )
        else:
            try:
                validate(instance=response_body, schema=schema)
                schema_validation_passed = True
            except ValidationError as exc:
                schema_validation_passed = False
                validation_errors.append(f"Schema validation failed: {exc.message}")

    passed = status_code_valid and (not schema_validation_applied or schema_validation_passed is True)

    return ResponseValidationResult(
        status_code_valid=status_code_valid,
        schema_validation_applied=schema_validation_applied,
        schema_validation_passed=schema_validation_passed,
        validation_errors=validation_errors,
        passed=passed,
    )


def _select_schema_for_status(
    test_case: GeneratedTestCase,
    actual_status_code: int | None,
) -> dict[str, Any] | None:
    if actual_status_code is None:
        return None
    return test_case.expected_response_schemas.get(str(actual_status_code))
