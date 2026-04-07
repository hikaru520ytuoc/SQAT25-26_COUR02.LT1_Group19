from __future__ import annotations

from typing import Any

from openapi_test_tool.parser.models import (
    ApiParameter,
    EndpointSpec,
    OpenAPISpecSummary,
    RequestBodySpec,
    ResponseSpec,
)
from openapi_test_tool.parser.schema_resolver import SchemaResolver

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}
SUPPORTED_PARAMETER_LOCATIONS = {"path", "query", "header"}
JSON_CONTENT_TYPE = "application/json"



def extract_spec_summary(spec: dict[str, Any]) -> OpenAPISpecSummary:
    resolver = SchemaResolver(spec)
    endpoints: list[EndpointSpec] = []

    paths = spec.get("paths", {})
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        path_parameters = path_item.get("parameters", [])
        for method, operation in path_item.items():
            if method not in HTTP_METHODS:
                continue
            if not isinstance(operation, dict):
                continue
            endpoints.append(_extract_endpoint(path, method, operation, path_parameters, resolver))

    info = spec.get("info", {}) if isinstance(spec.get("info"), dict) else {}
    return OpenAPISpecSummary(
        openapi_version=spec["openapi"],
        title=info.get("title"),
        version=info.get("version"),
        path_count=len(paths),
        operation_count=len(endpoints),
        endpoints=endpoints,
    )



def _extract_endpoint(
    path: str,
    method: str,
    operation: dict[str, Any],
    path_parameters: list[dict[str, Any]],
    resolver: SchemaResolver,
) -> EndpointSpec:
    parameters = _merge_parameters(path_parameters, operation.get("parameters", []), resolver)
    request_body = _extract_request_body(operation.get("requestBody"), resolver)
    responses = _extract_responses(operation.get("responses", {}), resolver)

    return EndpointSpec(
        path=path,
        method=method.upper(),
        summary=operation.get("summary"),
        operationId=operation.get("operationId"),
        parameters=parameters,
        request_body=request_body,
        responses=responses,
    )



def _merge_parameters(
    path_parameters: list[dict[str, Any]],
    operation_parameters: list[dict[str, Any]],
    resolver: SchemaResolver,
) -> list[ApiParameter]:
    merged: dict[tuple[str, str], ApiParameter] = {}

    for parameter in path_parameters or []:
        parsed = _parse_parameter(parameter, resolver)
        if parsed is None:
            continue
        merged[(parsed.name, parsed.location)] = parsed

    for parameter in operation_parameters or []:
        parsed = _parse_parameter(parameter, resolver)
        if parsed is None:
            continue
        merged[(parsed.name, parsed.location)] = parsed

    return list(merged.values())



def _parse_parameter(parameter: dict[str, Any], resolver: SchemaResolver) -> ApiParameter | None:
    resolved_parameter = resolver.resolve(parameter)
    location = resolved_parameter.get("in")
    if location not in SUPPORTED_PARAMETER_LOCATIONS:
        return None

    schema = resolved_parameter.get("schema")
    resolved_schema = resolver.resolve(schema) if schema else {}

    return ApiParameter(
        name=resolved_parameter.get("name", ""),
        location=location,
        required=bool(resolved_parameter.get("required", False)),
        description=resolved_parameter.get("description"),
        schema_data=resolved_schema,
    )



def _extract_request_body(request_body: dict[str, Any] | None, resolver: SchemaResolver) -> RequestBodySpec | None:
    if not request_body or not isinstance(request_body, dict):
        return None

    resolved_request_body = resolver.resolve(request_body)
    content = resolved_request_body.get("content", {})
    if not isinstance(content, dict):
        return None

    json_content = content.get(JSON_CONTENT_TYPE)
    if not isinstance(json_content, dict):
        return None

    schema = json_content.get("schema")
    resolved_schema = resolver.resolve(schema) if schema else None

    return RequestBodySpec(
        required=bool(resolved_request_body.get("required", False)),
        content_type=JSON_CONTENT_TYPE,
        schema_data=resolved_schema,
    )



def _extract_responses(responses: dict[str, Any], resolver: SchemaResolver) -> list[ResponseSpec]:
    collected_responses: list[ResponseSpec] = []
    if not isinstance(responses, dict):
        return collected_responses

    for status_code, response in responses.items():
        if not isinstance(response, dict):
            continue

        resolved_response = resolver.resolve(response)
        content = resolved_response.get("content", {})
        response_spec = ResponseSpec(
            status_code=str(status_code),
            description=resolved_response.get("description"),
        )

        if isinstance(content, dict) and JSON_CONTENT_TYPE in content:
            json_content = content.get(JSON_CONTENT_TYPE, {})
            schema = json_content.get("schema")
            resolved_schema = resolver.resolve(schema) if schema else None
            response_spec.content_type = JSON_CONTENT_TYPE
            response_spec.schema_data = resolved_schema

        collected_responses.append(response_spec)

    return collected_responses
