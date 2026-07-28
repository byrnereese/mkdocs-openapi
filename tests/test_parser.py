from __future__ import annotations

import json

import pytest
import yaml

from mkdocs_openapi.errors import OpenAPIError
from mkdocs_openapi.parser import load_spec, resolve_local_ref


DOCUMENT = {
    "openapi": "3.1.0",
    "info": {"title": "Example", "version": "1.0.0"},
    "paths": {},
}


@pytest.mark.parametrize(
    ("source_uri", "content"),
    [
        ("openapi.json", json.dumps(DOCUMENT)),
        ("openapi.yaml", yaml.safe_dump(DOCUMENT)),
        ("openapi.yml", yaml.safe_dump(DOCUMENT)),
    ],
)
def test_loads_json_and_yaml(source_uri: str, content: str) -> None:
    assert load_spec(content, source_uri) == DOCUMENT


def test_rejects_non_openapi_3_document() -> None:
    with pytest.raises(OpenAPIError, match="supports OpenAPI 3.x"):
        load_spec(
            yaml.safe_dump(
                {
                    "swagger": "2.0",
                    "info": {"title": "Old", "version": "1"},
                    "paths": {},
                }
            ),
            "old.yaml",
        )


def test_reports_invalid_input() -> None:
    with pytest.raises(OpenAPIError, match="Unable to parse"):
        load_spec("{not-json", "broken.json")


def test_resolves_escaped_local_json_pointer() -> None:
    document = {"components": {"schemas": {"a/b~c": {"type": "string"}}}}
    assert resolve_local_ref(
        document, {"$ref": "#/components/schemas/a~1b~0c"}
    ) == {"type": "string"}

