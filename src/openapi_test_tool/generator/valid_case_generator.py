from __future__ import annotations

from copy import deepcopy
from typing import Any

from openapi_test_tool.generator.testcase_model import GeneratedTestCase, TestCaseCategory, TestCaseType
from openapi_test_tool.parser.models import EndpointSpec


SUCCESS_STATUS_PRIORITY = (200, 201, 204)
CLIENT_ERROR_STATUS_PRIORITY = (400, 422)


def generate_sample_value(schema: dict[str, Any] | None) -> Any:
    """Create simple valid sample data from a resolved schema.

    The implementation intentionally covers only a practical subset of JSON Schema
    for the MVP. Unsupported constructs are handled conservatively.
    """

    if not schema:
        return None

    if "example" in schema:
        return deepcopy(schema["example"])
    if "default" in schema:
        return deepcopy(schema["default"])
    if schema.get("enum"):
        return deepcopy(schema["enum"][0])

    schema_type = schema.get("type")

    if schema_type == "string":
        return _generate_string_sample(schema)
    if schema_type == "integer":
        minimum = schema.get("minimum")
        if isinstance(minimum, int):
            return minimum
        return 1
    if schema_type == "number":
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)):
            return float(minimum)
        return 1.0
    if schema_type == "boolean":
        return True
    if schema_type == "array":
        item_schema = schema.get("items", {})
        return [generate_sample_value(item_schema)]
    if schema_type == "object" or "properties" in schema:
        properties = schema.get("properties", {})
        result: dict[str, Any] = {}
        for field_name, field_schema in properties.items():
            result[field_name] = generate_sample_value(field_schema)
        return result

    return None


def build_valid_input_bundle(endpoint: EndpointSpec) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Any | None]:
    """Build a reusable valid input bundle for one endpoint."""

    path_params: dict[str, Any] = {}
    query_params: dict[str, Any] = {}
    headers: dict[str, Any] = {}

    for parameter in endpoint.parameters:
        sample_value = generate_sample_value(parameter.schema_data)
        if parameter.location == "path":
            path_params[parameter.name] = sample_value
        elif parameter.location == "query":
            query_params[parameter.name] = sample_value
        elif parameter.location == "header":
            headers[parameter.name] = sample_value

    request_body = None
    if endpoint.request_body and endpoint.request_body.schema_data:
        request_body = generate_sample_value(endpoint.request_body.schema_data)

    return path_params, query_params, headers, request_body


def build_expected_response_schema_map(endpoint: EndpointSpec) -> dict[str, dict[str, Any] | None]:
    """Collect resolved response schemas keyed by status code for later execution."""

    schema_map: dict[str, dict[str, Any] | None] = {}
    for response in endpoint.responses:
        if response.schema_data is not None:
            schema_map[response.status_code] = deepcopy(response.schema_data)
    return schema_map


def select_expected_success_status(endpoint: EndpointSpec) -> list[int]:
    numeric_statuses = _extract_numeric_statuses(endpoint)
    for preferred_status in SUCCESS_STATUS_PRIORITY:
        if preferred_status in numeric_statuses:
            return [preferred_status]

    success_statuses = [status for status in numeric_statuses if 200 <= status < 300]
    if success_statuses:
        return [success_statuses[0]]

    if numeric_statuses:
        return [numeric_statuses[0]]

    return [200]


def select_expected_client_error_status(endpoint: EndpointSpec) -> list[int]:
    numeric_statuses = _extract_numeric_statuses(endpoint)
    for preferred_status in CLIENT_ERROR_STATUS_PRIORITY:
        if preferred_status in numeric_statuses:
            return [preferred_status]

    client_error_statuses = [status for status in numeric_statuses if 400 <= status < 500]
    if client_error_statuses:
        return [client_error_statuses[0]]

    return [400]


def generate_valid_test_cases(endpoint: EndpointSpec) -> list[GeneratedTestCase]:
    path_params, query_params, headers, request_body = build_valid_input_bundle(endpoint)
    response_schemas = build_expected_response_schema_map(endpoint)

    return [
        GeneratedTestCase(
            test_id="",
            name=f"{endpoint.method} {endpoint.path} - valid case",
            description="Valid request generated from parsed OpenAPI metadata.",
            endpoint_path=endpoint.path,
            method=endpoint.method,
            path_params=path_params,
            query_params=query_params,
            headers=headers,
            request_body=request_body,
            expected_status_codes=select_expected_success_status(endpoint),
            expected_response_schemas=response_schemas,
            category=TestCaseCategory.VALID,
            test_type=TestCaseType.VALID_CASE,
            source_operation_id=endpoint.operation_id,
            source_summary=endpoint.summary,
            source_metadata={"generator": "valid_case_generator"},
        )
    ]


def _extract_numeric_statuses(endpoint: EndpointSpec) -> list[int]:
    statuses: list[int] = []
    for response in endpoint.responses:
        try:
            statuses.append(int(response.status_code))
        except ValueError:
            continue
    return statuses


def _generate_string_sample(schema: dict[str, Any]) -> str:
    format_name = schema.get("format")
    if format_name == "email":
        base_value = "user@example.com"
    elif format_name == "uuid":
        base_value = "00000000-0000-0000-0000-000000000001"
    else:
        base_value = "sample_text"

    min_length = schema.get("minLength")
    max_length = schema.get("maxLength")

    if isinstance(min_length, int) and min_length > len(base_value):
        base_value = "x" * min_length
    if isinstance(max_length, int) and max_length >= 0:
        base_value = base_value[:max_length]

    return base_value
