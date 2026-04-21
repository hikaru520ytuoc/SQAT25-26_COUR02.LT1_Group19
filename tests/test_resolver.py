import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openapi_test_tool.parser import SchemaResolver, load_openapi_spec  # noqa: E402


def test_resolve_basic_ref():
    spec_path = PROJECT_ROOT / "samples" / "sample_openapi.yaml"
    spec = load_openapi_spec(spec_path)
    resolver = SchemaResolver(spec)

    resolved = resolver.resolve({"$ref": "#/components/schemas/User"})

    assert resolved["type"] == "object"
    assert resolved["properties"]["email"]["type"] == "string"
    assert "id" in resolved["required"]
