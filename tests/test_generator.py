from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from mkdocs_openapi.generator import generate_site


ROOT = Path(__file__).parents[1]


def petstore() -> dict:
    return json.loads(
        (
            ROOT / "examples/petstore/docs/openapi/spec.json"
        ).read_text()
    )


def test_generates_petstore_pages_and_navigation() -> None:
    generated = generate_site(petstore())

    assert len(generated.operations) == 19
    assert len(generated.models) == 6
    assert len(generated.pages) == 30
    assert [next(iter(item)) for item in generated.api_nav] == [
        "Overview",
        "pet",
        "store",
        "user",
    ]
    assert [next(iter(item)) for item in generated.models_nav] == [
        "Overview",
        "Order",
        "Category",
        "User",
        "Tag",
        "Pet",
        "ApiResponse",
    ]

    update_pet = generated.pages[
        "api-reference/pet/operation-put-update-pet.md"
    ]
    assert "`PUT`{ .http-method .put } `/pet`{ .operation-path }" in update_pet
    assert "**Schema:** [Pet](../../models/pet.md)" in update_pet
    assert "| `name` | string | **Yes** |" not in update_pet
    assert '=== "application/json"' in update_pet
    assert "tags:\n- pet\n- PUT" in update_pet

    pet_model = generated.pages["models/pet.md"]
    assert "| `name` | string | **Yes** |" in pet_model
    assert "[Category](category.md)" in pet_model
    assert "[Tag](tag.md)" in pet_model


def test_generation_is_deterministic() -> None:
    first = generate_site(petstore())
    second = generate_site(petstore())
    assert first.pages == second.pages
    assert first.api_nav == second.api_nav
    assert first.models_nav == second.models_nav


def test_handles_untagged_missing_ids_duplicates_and_inline_schemas() -> None:
    document = {
        "openapi": "3.1.0",
        "info": {"title": "Edges", "version": "1"},
        "paths": {
            "/things": {
                "get": {
                    "summary": "List things",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {
                                "type": ["integer", "null"],
                                "default": 10,
                            },
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"}
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "List things",
                    "operationId": "duplicate",
                    "tags": ["Things", "Public"],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"}
                                    },
                                }
                            }
                        }
                    },
                    "responses": {"204": {"description": "Created"}},
                },
            },
            "/other": {
                "post": {
                    "summary": "Other",
                    "operationId": "duplicate",
                    "tags": ["Things"],
                    "responses": {"204": {"description": "Created"}},
                }
            },
        },
    }

    generated = generate_site(document)
    uris = set(generated.pages)
    assert (
        "api-reference/untagged/operation-get-list-things.md" in uris
    )
    assert "api-reference/things/operation-post-duplicate.md" in uris
    assert "api-reference/things/operation-post-duplicate-2.md" in uris
    assert [group.primary_tag for group in generated.operations] == [
        "Untagged",
        "Things",
        "Things",
    ]

    inline = generated.pages[
        "api-reference/things/operation-post-duplicate.md"
    ]
    assert "**Schema:** object" in inline
    assert '"name": "string"' in inline
    assert "models/" not in inline


def test_renders_composed_models_as_links() -> None:
    document = {
        "openapi": "3.0.3",
        "info": {"title": "Composition", "version": "1"},
        "paths": {},
        "components": {
            "schemas": {
                "Base": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}},
                },
                "Child": {
                    "allOf": [
                        {"$ref": "#/components/schemas/Base"},
                        {
                            "type": "object",
                            "required": ["name"],
                            "properties": {"name": {"type": "string"}},
                        },
                    ]
                },
            }
        },
    }

    generated = generate_site(document)
    child = generated.pages["models/child.md"]
    assert "**All of:** [Base](base.md), object" in child
    assert "| `name` | string | **Yes** |" in child


def test_serializes_yaml_timestamp_examples() -> None:
    document = {
        "openapi": "3.0.3",
        "info": {"title": "Dates", "version": "1"},
        "paths": {},
        "components": {
            "schemas": {
                "Event": {
                    "type": "object",
                    "properties": {
                        "createdAt": {
                            "type": "string",
                            "format": "date-time",
                            "example": datetime(2026, 7, 28, 8, 30),
                        }
                    },
                }
            }
        },
    }

    generated = generate_site(document)
    assert '"createdAt": "2026-07-28T08:30:00"' in generated.pages[
        "models/event.md"
    ]
