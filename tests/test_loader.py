import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openapi_test_tool.parser import OpenAPILoaderError, load_openapi_spec  # noqa: E402


def test_load_yaml_successfully():
    spec_path = PROJECT_ROOT / "samples" / "sample_openapi.yaml"
    spec = load_openapi_spec(spec_path)

    assert spec["openapi"] == "3.0.3"
    assert "paths" in spec


def test_load_json_successfully(tmp_path):
    spec_data = {
        "openapi": "3.0.3",
        "info": {"title": "JSON API", "version": "1.0.0"},
        "paths": {
            "/health": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                        }
                    }
                }
            }
        },
    }
    spec_path = tmp_path / "sample_openapi.json"
    spec_path.write_text(json.dumps(spec_data), encoding="utf-8")

    spec = load_openapi_spec(spec_path)

    assert spec["info"]["title"] == "JSON API"
    assert "/health" in spec["paths"]


def test_load_fails_when_file_not_found():
    missing_path = PROJECT_ROOT / "samples" / "does_not_exist.yaml"

    with pytest.raises(OpenAPILoaderError, match="Spec file does not exist"):
        load_openapi_spec(missing_path)
