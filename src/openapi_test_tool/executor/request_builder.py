from __future__ import annotations

from urllib.parse import urljoin

from openapi_test_tool.executor.execution_model import BuiltRequest
from openapi_test_tool.generator.testcase_model import GeneratedTestCase


JSON_CONTENT_TYPE = "application/json"


def build_request(base_url: str, test_case: GeneratedTestCase) -> BuiltRequest:
    """Build a concrete HTTP request from a generated test case.

    For invalid cases where a required path parameter is intentionally missing, the
    unresolved placeholder is kept in the path. This is a deliberate MVP choice so
    the malformed request remains visible and consistent during demos.
    """

    final_path = test_case.endpoint_path
    for name, value in test_case.path_params.items():
        final_path = final_path.replace(f"{{{name}}}", str(value))

    sanitized_query = {key: value for key, value in test_case.query_params.items() if value is not None}
    sanitized_headers = dict(test_case.headers)

    if test_case.request_body is not None and "Content-Type" not in sanitized_headers:
        sanitized_headers["Content-Type"] = JSON_CONTENT_TYPE

    base = base_url.rstrip("/") + "/"
    url = urljoin(base, final_path.lstrip("/"))

    return BuiltRequest(
        method=test_case.method,
        url=url,
        path=final_path,
        path_params=dict(test_case.path_params),
        query_params=sanitized_query,
        headers=sanitized_headers,
        json_body=test_case.request_body,
    )
