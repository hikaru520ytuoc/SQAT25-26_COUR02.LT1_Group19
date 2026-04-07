from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class OpenAPILoaderError(Exception):
    """Raised when an OpenAPI document cannot be loaded or validated."""


SUPPORTED_EXTENSIONS = {".yaml", ".yml", ".json"}



def load_openapi_spec(spec_path: str | Path) -> dict[str, Any]:
    """Load an OpenAPI 3.x document from YAML or JSON.

    This loader intentionally performs only the minimal validation needed for the
    MVP stage. More complete validation can be added later if the project grows.
    """

    path = Path(spec_path)
    if not path.exists():
        raise OpenAPILoaderError(f"Spec file does not exist: {path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise OpenAPILoaderError(
            f"Unsupported file extension '{path.suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    try:
        raw_content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OpenAPILoaderError(f"Could not read spec file: {path}") from exc

    try:
        if path.suffix.lower() == ".json":
            spec = json.loads(raw_content)
        else:
            spec = yaml.safe_load(raw_content)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise OpenAPILoaderError(f"Invalid spec format in file: {path}") from exc

    if not isinstance(spec, dict):
        raise OpenAPILoaderError("OpenAPI document must be a JSON/YAML object at the top level.")

    _validate_minimum_structure(spec)
    return spec



def _validate_minimum_structure(spec: dict[str, Any]) -> None:
    openapi_version = spec.get("openapi")
    if not openapi_version or not isinstance(openapi_version, str):
        raise OpenAPILoaderError("Missing required 'openapi' field.")

    if not openapi_version.startswith("3."):
        raise OpenAPILoaderError(
            f"Only OpenAPI 3.x is supported in this MVP. Received: {openapi_version}"
        )

    paths = spec.get("paths")
    if paths is None or not isinstance(paths, dict):
        raise OpenAPILoaderError("Missing or invalid required 'paths' field.")
