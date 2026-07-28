"""Load and validate OpenAPI JSON or YAML documents."""

from __future__ import annotations

import json
from collections.abc import Mapping

import yaml

from .errors import OpenAPIError


def load_spec(content: str, source_uri: str) -> dict:
    """Parse and minimally validate an OpenAPI 3.x document."""
    try:
        if source_uri.lower().endswith(".json"):
            document = json.loads(content)
        else:
            document = yaml.safe_load(content)
    except (json.JSONDecodeError, yaml.YAMLError) as error:
        raise OpenAPIError(f"Unable to parse {source_uri}: {error}") from error

    if not isinstance(document, Mapping):
        raise OpenAPIError(f"{source_uri} must contain a mapping at its root")

    version = str(document.get("openapi", ""))
    if not version.startswith("3."):
        value = version or "missing"
        raise OpenAPIError(
            f"{source_uri} uses unsupported OpenAPI version {value!r}; "
            "mkdocs-openapi currently supports OpenAPI 3.x"
        )

    paths = document.get("paths", {})
    if not isinstance(paths, Mapping):
        raise OpenAPIError(f"{source_uri} has a non-mapping 'paths' value")

    return dict(document)


def resolve_local_ref(document: dict, value: object) -> object:
    """Resolve a local JSON Pointer `$ref`, returning other values unchanged."""
    if not isinstance(value, dict):
        return value
    ref = value.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return value

    current: object = document
    try:
        for raw_part in ref[2:].split("/"):
            part = raw_part.replace("~1", "/").replace("~0", "~")
            if not isinstance(current, dict):
                return value
            current = current[part]
    except KeyError:
        return value
    return current

