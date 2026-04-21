from __future__ import annotations

from copy import deepcopy
from typing import Any


class SchemaResolverError(Exception):
    """Raised when an internal OpenAPI schema reference cannot be resolved."""


INTERNAL_SCHEMA_PREFIX = "#/components/schemas/"


class SchemaResolver:
    """Resolve a limited subset of OpenAPI internal references.

    Supported form:
    - #/components/schemas/SchemaName
    """

    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec
        self.schemas = spec.get("components", {}).get("schemas", {})

    def resolve(self, node: Any) -> Any:
        return self._resolve_node(node, seen_refs=set())

    def _resolve_node(self, node: Any, seen_refs: set[str]) -> Any:
        if isinstance(node, dict):
            if "$ref" in node:
                ref_path = node["$ref"]
                return self._resolve_ref(ref_path, seen_refs)

            resolved_dict: dict[str, Any] = {}
            for key, value in node.items():
                resolved_dict[key] = self._resolve_node(value, seen_refs=set(seen_refs))
            return resolved_dict

        if isinstance(node, list):
            return [self._resolve_node(item, seen_refs=set(seen_refs)) for item in node]

        return node

    def _resolve_ref(self, ref_path: str, seen_refs: set[str]) -> Any:
        if not ref_path.startswith(INTERNAL_SCHEMA_PREFIX):
            raise SchemaResolverError(
                f"Unsupported $ref '{ref_path}'. Only {INTERNAL_SCHEMA_PREFIX}* is supported."
            )

        if ref_path in seen_refs:
            raise SchemaResolverError(f"Circular $ref detected for '{ref_path}'.")

        schema_name = ref_path.removeprefix(INTERNAL_SCHEMA_PREFIX)
        schema = self.schemas.get(schema_name)
        if schema is None:
            raise SchemaResolverError(f"Schema reference not found: {ref_path}")

        updated_seen_refs = set(seen_refs)
        updated_seen_refs.add(ref_path)
        return self._resolve_node(deepcopy(schema), seen_refs=updated_seen_refs)
