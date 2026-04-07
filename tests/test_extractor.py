import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openapi_test_tool.parser import extract_spec_summary, load_openapi_spec  # noqa: E402


def test_extract_endpoints_from_sample_spec():
    spec_path = PROJECT_ROOT / "samples" / "sample_openapi.yaml"
    spec = load_openapi_spec(spec_path)

    summary = extract_spec_summary(spec)

    assert summary.path_count == 2
    assert summary.operation_count == 2

    endpoints = {(endpoint.method, endpoint.path): endpoint for endpoint in summary.endpoints}

    get_user = endpoints[("GET", "/users/{userId}")]
    assert get_user.operation_id == "getUserById"
    assert len(get_user.parameters) == 3
    assert any(parameter.location == "path" and parameter.name == "userId" for parameter in get_user.parameters)
    assert any(parameter.location == "query" and parameter.name == "includePosts" for parameter in get_user.parameters)
    assert any(parameter.location == "header" and parameter.name == "X-Trace-Id" for parameter in get_user.parameters)
    assert get_user.responses[0].schema_data is not None
    assert get_user.responses[0].schema_data["properties"]["name"]["type"] == "string"

    create_user = endpoints[("POST", "/users")]
    assert create_user.request_body is not None
    assert create_user.request_body.required is True
    assert create_user.request_body.schema_data["properties"]["email"]["format"] == "email"
