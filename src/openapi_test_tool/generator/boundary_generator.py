from __future__ import annotations

from copy import deepcopy
from typing import Any

from openapi_test_tool.generator.testcase_model import GeneratedTestCase, TestCaseCategory, TestCaseType
from openapi_test_tool.generator.valid_case_generator import (
    build_expected_response_schema_map,
    build_valid_input_bundle,
    select_expected_success_status,
)
from openapi_test_tool.parser.models import EndpointSpec


def generate_boundary_test_cases(endpoint: EndpointSpec) -> list[GeneratedTestCase]:
    cases: list[GeneratedTestCase] = []
    path_params, query_params, headers, request_body = build_valid_input_bundle(endpoint)
    response_schemas = build_expected_response_schema_map(endpoint)

    for parameter in endpoint.parameters:
        boundary_value = _build_boundary_value(
            parameter.schema_data,
            current_value=_current_value(parameter.location, parameter.name, path_params, query_params),
        )
        if boundary_value is None:
            continue

        mutated_path = deepcopy(path_params)
        mutated_query = deepcopy(query_params)
        if parameter.location == "path":
            mutated_path[parameter.name] = boundary_value
        elif parameter.location == "query":
            mutated_query[parameter.name] = boundary_value
        else:
            continue

        cases.append(
            GeneratedTestCase(
                test_id="",
                name=f"{endpoint.method} {endpoint.path} - boundary value for parameter {parameter.name}",
                description=f"Use boundary value for {parameter.location} parameter '{parameter.name}'.",
                endpoint_path=endpoint.path,
                method=endpoint.method,
                path_params=mutated_path,
                query_params=mutated_query,
                headers=deepcopy(headers),
                request_body=deepcopy(request_body),
                expected_status_codes=select_expected_success_status(endpoint),
                expected_response_schemas=response_schemas,
                category=TestCaseCategory.VALID,
                test_type=TestCaseType.BOUNDARY_VALUE,
                source_operation_id=endpoint.operation_id,
                source_summary=endpoint.summary,
                source_metadata={"target": parameter.name, "location": parameter.location, "generator": "boundary_generator"},
            )
        )

    body_schema = endpoint.request_body.schema_data if endpoint.request_body else None
    if isinstance(body_schema, dict) and isinstance(request_body, dict):
        properties = body_schema.get("properties", {})
        for field_name, field_schema in properties.items():
            boundary_value = _build_boundary_value(field_schema, current_value=request_body.get(field_name))
            if boundary_value is None:
                continue

            mutated_body = deepcopy(request_body)
            mutated_body[field_name] = boundary_value
            cases.append(
                GeneratedTestCase(
                    test_id="",
                    name=f"{endpoint.method} {endpoint.path} - boundary value for body field {field_name}",
                    description=f"Use boundary value for request body field '{field_name}'.",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    path_params=deepcopy(path_params),
                    query_params=deepcopy(query_params),
                    headers=deepcopy(headers),
                    request_body=mutated_body,
                    expected_status_codes=select_expected_success_status(endpoint),
                    expected_response_schemas=response_schemas,
                    category=TestCaseCategory.VALID,
                    test_type=TestCaseType.BOUNDARY_VALUE,
                    source_operation_id=endpoint.operation_id,
                    source_summary=endpoint.summary,
                    source_metadata={"target": field_name, "location": "request_body", "generator": "boundary_generator"},
                )
            )

    return cases


def _current_value(location: str, name: str, path_params: dict[str, Any], query_params: dict[str, Any]) -> Any:
    if location == "path":
        return path_params.get(name)
    if location == "query":
        return query_params.get(name)
    return None


def _build_boundary_value(schema: dict[str, Any], current_value: Any) -> Any | None:
    schema_type = schema.get("type")

    if schema_type == "string":
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        if isinstance(min_length, int) and min_length >= 0:
            candidate = "x" * min_length
            if candidate != current_value:
                return candidate
        if isinstance(max_length, int) and max_length >= 0:
            candidate = "x" * max_length
            if candidate != current_value:
                return candidate
        return None

    if schema_type == "integer":
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, int) and minimum != current_value:
            return minimum
        if isinstance(maximum, int) and maximum != current_value:
            return maximum
        return None

    if schema_type == "number":
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and minimum != current_value:
            return float(minimum)
        if isinstance(maximum, (int, float)) and maximum != current_value:
            return float(maximum)
        return None

    return None
