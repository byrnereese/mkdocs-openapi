from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from mkdocs_openapi.errors import OpenAPIError
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


def test_inlines_reachable_models_without_generating_model_pages() -> None:
    document = {
        "openapi": "3.0.3",
        "info": {"title": "Inline models", "version": "1"},
        "paths": {
            "/nodes": {
                "post": {
                    "summary": "Create a node",
                    "requestBody": {
                        "$ref": "#/components/requestBodies/NodeBody"
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Node"
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {
            "requestBodies": {
                "NodeBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/Node"
                            }
                        }
                    }
                }
            },
            "schemas": {
                "Node": {
                    "type": "object",
                    "required": ["child"],
                    "properties": {
                        "child": {"$ref": "#/components/schemas/Child"}
                    },
                },
                "Child": {
                    "type": "object",
                    "properties": {
                        "parent": {"$ref": "#/components/schemas/Node"}
                    },
                },
                "Unused": {"type": "string"},
            },
        },
    }

    generated = generate_site(document, models_mode="inline")
    operation = generated.pages[
        "api-reference/untagged/operation-post-create-a-node.md"
    ]

    assert generated.models_nav == []
    assert not any(uri.startswith("models/") for uri in generated.pages)
    assert "model reference" not in generated.pages["api-reference/index.md"]
    assert "**Schema:** [Node](#model-node)" in operation
    assert operation.count("### Node { #model-node }") == 1
    assert operation.count("### Child { #model-child }") == 1
    assert "[Child](#model-child)" in operation
    assert "[Node](#model-node)" in operation
    assert "Unused" not in operation


def test_rejects_invalid_models_mode() -> None:
    with pytest.raises(OpenAPIError, match="models_mode must be one of"):
        generate_site(petstore(), models_mode="separate")


def test_suppresses_tag_overviews_from_navigation_only() -> None:
    generated = generate_site(
        _tagged_document("Alpha", "Beta"),
        suppress_tag_overview=True,
    )

    for item in generated.api_nav[1:]:
        children = next(iter(item.values()))
        assert [next(iter(child)) for child in children] == [
            f"Get {next(iter(item))}"
        ]

    assert "Overview" in generated.api_nav[0]
    assert "api-reference/alpha/index.md" in generated.pages
    assert "api-reference/beta/index.md" in generated.pages


def test_configures_nested_tag_navigation_order_and_filtering() -> None:
    document = _tagged_document("Alpha", "Beta", "Gamma")

    generated = generate_site(
        document,
        tag_nav=[
            {"Second section": ["Gamma", "Alpha"]},
            "Beta",
        ],
        unlisted_tags="exclude",
    )

    assert [next(iter(item)) for item in generated.api_nav] == [
        "Overview",
        "Second section",
        "Beta",
    ]
    nested = generated.api_nav[1]["Second section"]
    assert [next(iter(item)) for item in nested] == ["Gamma", "Alpha"]
    assert [operation.primary_tag for operation in generated.operations] == [
        "Alpha",
        "Beta",
        "Gamma",
    ]


def test_excludes_unlisted_tags_and_their_pages() -> None:
    generated = generate_site(
        _tagged_document("Alpha", "Beta"),
        tag_nav=["Beta"],
    )

    assert [next(iter(item)) for item in generated.api_nav] == [
        "Overview",
        "Beta",
    ]
    assert [operation.primary_tag for operation in generated.operations] == [
        "Beta"
    ]
    assert not any("/alpha/" in uri for uri in generated.pages)
    assert any("/beta/" in uri for uri in generated.pages)


def test_appends_unlisted_tags_in_default_order() -> None:
    generated = generate_site(
        _tagged_document("Alpha", "Beta", "Gamma"),
        tag_nav=[{"Featured": ["Gamma"]}],
        unlisted_tags="append",
    )

    assert [next(iter(item)) for item in generated.api_nav] == [
        "Overview",
        "Featured",
        "Alpha",
        "Beta",
    ]


@pytest.mark.parametrize(
    ("tag_nav", "unlisted_tags", "message"),
    [
        (["Missing"], "exclude", "not a primary operation tag"),
        (["Alpha", {"Again": ["Alpha"]}], "exclude", "more than once"),
        ([{"Empty": []}], "exclude", "non-empty list"),
        (["Alpha"], "error", "does not list.*Beta"),
    ],
)
def test_rejects_invalid_tag_navigation(
    tag_nav: list, unlisted_tags: str, message: str
) -> None:
    with pytest.raises(OpenAPIError, match=message):
        generate_site(
            _tagged_document("Alpha", "Beta"),
            tag_nav=tag_nav,
            unlisted_tags=unlisted_tags,
        )


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


def _tagged_document(*tag_names: str) -> dict:
    return {
        "openapi": "3.0.3",
        "info": {"title": "Tagged", "version": "1"},
        "tags": [{"name": name} for name in tag_names],
        "paths": {
            f"/{name.lower()}": {
                "get": {
                    "tags": [name],
                    "summary": f"Get {name}",
                    "operationId": f"get{name}",
                    "responses": {"200": {"description": "OK"}},
                }
            }
            for name in tag_names
        },
    }
