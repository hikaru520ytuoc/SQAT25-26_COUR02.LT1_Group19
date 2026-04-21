from __future__ import annotations

from copy import deepcopy
from typing import Any

from openapi_test_tool.generator.testcase_model import GeneratedTestCase, TestCaseCategory, TestCaseType
from openapi_test_tool.generator.valid_case_generator import (
    build_expected_response_schema_map,
    build_valid_input_bundle,
    select_expected_client_error_status,
)
from openapi_test_tool.parser.models import EndpointSpec


def generate_invalid_test_cases(endpoint: EndpointSpec) -> list[GeneratedTestCase]:
    test_cases: list[GeneratedTestCase] = []
    test_cases.extend(_generate_missing_required_parameter_cases(endpoint))
    test_cases.extend(_generate_missing_required_field_cases(endpoint))
    test_cases.extend(_generate_wrong_data_type_cases(endpoint))
    test_cases.extend(_generate_invalid_enum_cases(endpoint))
    test_cases.extend(_generate_empty_value_cases(endpoint))
    return test_cases


def _generate_missing_required_parameter_cases(endpoint: EndpointSpec) -> list[GeneratedTestCase]:
    cases: list[GeneratedTestCase] = []
    path_params, query_params, headers, request_body = build_valid_input_bundle(endpoint)
    response_schemas = build_expected_response_schema_map(endpoint)

    for parameter in endpoint.parameters:
        if not parameter.required or parameter.location not in {"path", "query"}:
            continue

        mutated_path = deepcopy(path_params)
        mutated_query = deepcopy(query_params)
        if parameter.location == "path":
            mutated_path.pop(parameter.name, None)
        else:
            mutated_query.pop(parameter.name, None)

        cases.append(
            GeneratedTestCase(
                test_id="",
                name=f"{endpoint.method} {endpoint.path} - missing required parameter {parameter.name}",
                description=f"Omit required {parameter.location} parameter '{parameter.name}'.",
                endpoint_path=endpoint.path,
                method=endpoint.method,
                path_params=mutated_path,
                query_params=mutated_query,
                headers=deepcopy(headers),
                request_body=deepcopy(request_body),
                expected_status_codes=select_expected_client_error_status(endpoint),
                expected_response_schemas=response_schemas,
                category=TestCaseCategory.INVALID,
                test_type=TestCaseType.MISSING_REQUIRED_PARAMETER,
                source_operation_id=endpoint.operation_id,
                source_summary=endpoint.summary,
                source_metadata={
                    "target": parameter.name,
                    "location": parameter.location,
                    "generator": "invalid_case_generator",
                },
            )
        )

    return cases


def _generate_missing_required_field_cases(endpoint: EndpointSpec) -> list[GeneratedTestCase]:
    body_schema = endpoint.request_body.schema_data if endpoint.request_body else None
    if not isinstance(body_schema, dict):
        return []

    required_fields = body_schema.get("required", [])
    properties = body_schema.get("properties", {})
    if not required_fields or not isinstance(properties, dict):
        return []

    path_params, query_params, headers, request_body = build_valid_input_bundle(endpoint)
    response_schemas = build_expected_response_schema_map(endpoint)
    if not isinstance(request_body, dict):
        return []

    cases: list[GeneratedTestCase] = []
    for field_name in required_fields:
        if field_name not in properties:
            continue

        mutated_body = deepcopy(request_body)
        mutated_body.pop(field_name, None)

        cases.append(
            GeneratedTestCase(
                test_id="",
                name=f"{endpoint.method} {endpoint.path} - missing required body field {field_name}",
                description=f"Remove required request body field '{field_name}'.",
                endpoint_path=endpoint.path,
                method=endpoint.method,
                path_params=deepcopy(path_params),
                query_params=deepcopy(query_params),
                headers=deepcopy(headers),
                request_body=mutated_body,
                expected_status_codes=select_expected_client_error_status(endpoint),
                expected_response_schemas=response_schemas,
                category=TestCaseCategory.INVALID,
                test_type=TestCaseType.MISSING_REQUIRED_FIELD,
                source_operation_id=endpoint.operation_id,
                source_summary=endpoint.summary,
                source_metadata={"target": field_name, "location": "request_body", "generator": "invalid_case_generator"},
            )
        )

    return cases


def _generate_wrong_data_type_cases(endpoint: EndpointSpec) -> list[GeneratedTestCase]:
    cases: list[GeneratedTestCase] = []
    path_params, query_params, headers, request_body = build_valid_input_bundle(endpoint)
    response_schemas = build_expected_response_schema_map(endpoint)

    for parameter in endpoint.parameters:
        wrong_value = _build_wrong_type_value(parameter.schema_data)
        if wrong_value is None:
            continue

        mutated_path = deepcopy(path_params)
        mutated_query = deepcopy(query_params)
        if parameter.location == "path":
            mutated_path[parameter.name] = wrong_value
        elif parameter.location == "query":
            mutated_query[parameter.name] = wrong_value
        else:
            continue

        cases.append(
            GeneratedTestCase(
                test_id="",
                name=f"{endpoint.method} {endpoint.path} - wrong type for parameter {parameter.name}",
                description=f"Use wrong data type for {parameter.location} parameter '{parameter.name}'.",
                endpoint_path=endpoint.path,
                method=endpoint.method,
                path_params=mutated_path,
                query_params=mutated_query,
                headers=deepcopy(headers),
                request_body=deepcopy(request_body),
                expected_status_codes=select_expected_client_error_status(endpoint),
                expected_response_schemas=response_schemas,
                category=TestCaseCategory.INVALID,
                test_type=TestCaseType.WRONG_DATA_TYPE,
                source_operation_id=endpoint.operation_id,
                source_summary=endpoint.summary,
                source_metadata={"target": parameter.name, "location": parameter.location, "generator": "invalid_case_generator"},
            )
        )

    body_schema = endpoint.request_body.schema_data if endpoint.request_body else None
    if isinstance(body_schema, dict) and isinstance(request_body, dict):
        properties = body_schema.get("properties", {})
        for field_name, field_schema in properties.items():
            wrong_value = _build_wrong_type_value(field_schema)
            if wrong_value is None:
                continue

            mutated_body = deepcopy(request_body)
            mutated_body[field_name] = wrong_value
            cases.append(
                GeneratedTestCase(
                    test_id="",
                    name=f"{endpoint.method} {endpoint.path} - wrong type for body field {field_name}",
                    description=f"Use wrong data type for request body field '{field_name}'.",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    path_params=deepcopy(path_params),
                    query_params=deepcopy(query_params),
                    headers=deepcopy(headers),
                    request_body=mutated_body,
                    expected_status_codes=select_expected_client_error_status(endpoint),
                    expected_response_schemas=response_schemas,
                    category=TestCaseCategory.INVALID,
                    test_type=TestCaseType.WRONG_DATA_TYPE,
                    source_operation_id=endpoint.operation_id,
                    source_summary=endpoint.summary,
                    source_metadata={"target": field_name, "location": "request_body", "generator": "invalid_case_generator"},
                )
            )

    return cases


def _generate_invalid_enum_cases(endpoint: EndpointSpec) -> list[GeneratedTestCase]:
    cases: list[GeneratedTestCase] = []
    path_params, query_params, headers, request_body = build_valid_input_bundle(endpoint)
    response_schemas = build_expected_response_schema_map(endpoint)

    for parameter in endpoint.parameters:
        invalid_value = _build_invalid_enum_value(parameter.schema_data)
        if invalid_value is None:
            continue

        mutated_path = deepcopy(path_params)
        mutated_query = deepcopy(query_params)
        if parameter.location == "path":
            mutated_path[parameter.name] = invalid_value
        elif parameter.location == "query":
            mutated_query[parameter.name] = invalid_value
        else:
            continue

        cases.append(
            GeneratedTestCase(
                test_id="",
                name=f"{endpoint.method} {endpoint.path} - invalid enum for parameter {parameter.name}",
                description=f"Use value outside enum for {parameter.location} parameter '{parameter.name}'.",
                endpoint_path=endpoint.path,
                method=endpoint.method,
                path_params=mutated_path,
                query_params=mutated_query,
                headers=deepcopy(headers),
                request_body=deepcopy(request_body),
                expected_status_codes=select_expected_client_error_status(endpoint),
                expected_response_schemas=response_schemas,
                category=TestCaseCategory.INVALID,
                test_type=TestCaseType.INVALID_ENUM,
                source_operation_id=endpoint.operation_id,
                source_summary=endpoint.summary,
                source_metadata={"target": parameter.name, "location": parameter.location, "generator": "invalid_case_generator"},
            )
        )

    body_schema = endpoint.request_body.schema_data if endpoint.request_body else None
    if isinstance(body_schema, dict) and isinstance(request_body, dict):
        properties = body_schema.get("properties", {})
        for field_name, field_schema in properties.items():
            invalid_value = _build_invalid_enum_value(field_schema)
            if invalid_value is None:
                continue

            mutated_body = deepcopy(request_body)
            mutated_body[field_name] = invalid_value
            cases.append(
                GeneratedTestCase(
                    test_id="",
                    name=f"{endpoint.method} {endpoint.path} - invalid enum for body field {field_name}",
                    description=f"Use value outside enum for request body field '{field_name}'.",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    path_params=deepcopy(path_params),
                    query_params=deepcopy(query_params),
                    headers=deepcopy(headers),
                    request_body=mutated_body,
                    expected_status_codes=select_expected_client_error_status(endpoint),
                    expected_response_schemas=response_schemas,
                    category=TestCaseCategory.INVALID,
                    test_type=TestCaseType.INVALID_ENUM,
                    source_operation_id=endpoint.operation_id,
                    source_summary=endpoint.summary,
                    source_metadata={"target": field_name, "location": "request_body", "generator": "invalid_case_generator"},
                )
            )

    return cases


def _generate_empty_value_cases(endpoint: EndpointSpec) -> list[GeneratedTestCase]:
    cases: list[GeneratedTestCase] = []
    path_params, query_params, headers, request_body = build_valid_input_bundle(endpoint)
    response_schemas = build_expected_response_schema_map(endpoint)

    for parameter in endpoint.parameters:
        if not parameter.required or parameter.schema_data.get("type") != "string":
            continue

        mutated_path = deepcopy(path_params)
        mutated_query = deepcopy(query_params)
        if parameter.location == "path":
            mutated_path[parameter.name] = ""
        elif parameter.location == "query":
            mutated_query[parameter.name] = ""
        else:
            continue

        cases.append(
            GeneratedTestCase(
                test_id="",
                name=f"{endpoint.method} {endpoint.path} - empty value for parameter {parameter.name}",
                description=f"Use empty string for required {parameter.location} parameter '{parameter.name}'.",
                endpoint_path=endpoint.path,
                method=endpoint.method,
                path_params=mutated_path,
                query_params=mutated_query,
                headers=deepcopy(headers),
                request_body=deepcopy(request_body),
                expected_status_codes=select_expected_client_error_status(endpoint),
                expected_response_schemas=response_schemas,
                category=TestCaseCategory.INVALID,
                test_type=TestCaseType.EMPTY_VALUE,
                source_operation_id=endpoint.operation_id,
                source_summary=endpoint.summary,
                source_metadata={"target": parameter.name, "location": parameter.location, "generator": "invalid_case_generator"},
            )
        )

    body_schema = endpoint.request_body.schema_data if endpoint.request_body else None
    if isinstance(body_schema, dict) and isinstance(request_body, dict):
        required_fields = set(body_schema.get("required", []))
        properties = body_schema.get("properties", {})
        for field_name, field_schema in properties.items():
            if field_name not in required_fields or field_schema.get("type") != "string":
                continue

            mutated_body = deepcopy(request_body)
            mutated_body[field_name] = ""
            cases.append(
                GeneratedTestCase(
                    test_id="",
                    name=f"{endpoint.method} {endpoint.path} - empty value for body field {field_name}",
                    description=f"Use empty string for required request body field '{field_name}'.",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    path_params=deepcopy(path_params),
                    query_params=deepcopy(query_params),
                    headers=deepcopy(headers),
                    request_body=mutated_body,
                    expected_status_codes=select_expected_client_error_status(endpoint),
                    expected_response_schemas=response_schemas,
                    category=TestCaseCategory.INVALID,
                    test_type=TestCaseType.EMPTY_VALUE,
                    source_operation_id=endpoint.operation_id,
                    source_summary=endpoint.summary,
                    source_metadata={"target": field_name, "location": "request_body", "generator": "invalid_case_generator"},
                )
            )

    return cases


def _build_wrong_type_value(schema: dict[str, Any]) -> Any | None:
    schema_type = schema.get("type")
    if schema_type in {"integer", "number"}:
        return "wrong_type"
    if schema_type == "boolean":
        return "wrong_type"
    if schema_type in {"array", "object"}:
        return "wrong_type"
    if schema_type == "string":
        return 12345
    return None


def _build_invalid_enum_value(schema: dict[str, Any]) -> Any | None:
    enum_values = schema.get("enum")
    if not enum_values:
        return None

    return "__invalid_enum__"
