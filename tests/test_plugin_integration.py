from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


def _write_spec(
    path: Path,
    *,
    title: str,
    tag: str,
    model: str,
    route: str,
) -> None:
    """Write a small OpenAPI document with one operation and model."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "openapi": "3.0.3",
                "info": {"title": title, "version": "1.0.0"},
                "tags": [{"name": tag}],
                "paths": {
                    route: {
                        "get": {
                            "tags": [tag],
                            "summary": f"List {tag.lower()}",
                            "operationId": f"list{tag}",
                            "responses": {
                                "200": {
                                    "description": "Success",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": (
                                                    "#/components/schemas/"
                                                    f"{model}"
                                                )
                                            }
                                        }
                                    },
                                }
                            },
                        }
                    }
                },
                "components": {
                    "schemas": {
                        model: {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"}
                            },
                        }
                    }
                },
            },
            sort_keys=False,
        )
    )


def test_mkdocs_builds_generated_markdown_with_material(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    spec_dir = docs / "openapi"
    spec_dir.mkdir(parents=True)
    (docs / "index.md").write_text("# Home\n")

    specification = {
        "openapi": "3.0.3",
        "info": {
            "title": "Tiny API",
            "description": (
                "An integration fixture.\n\n"
                "This specification includes:\n"
                "- Pet creation\n"
                "- Pet data models"
            ),
            "version": "1.0.0",
        },
        "tags": [{"name": "Pets", "description": "Pet operations."}],
        "paths": {
            "/pets": {
                "post": {
                    "tags": ["Pets"],
                    "summary": "Create a pet",
                    "operationId": "createPet",
                    "deprecated": True,
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Pet"
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Pet"
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string", "example": "Mochi"}
                    },
                }
            }
        },
    }
    (spec_dir / "spec.yaml").write_text(
        yaml.safe_dump(specification, sort_keys=False)
    )

    config = tmp_path / "mkdocs.yml"
    config.write_text(
        """
site_name: Tiny API
docs_dir: docs
site_dir: site
use_directory_urls: false
theme:
  name: material
  features:
    - navigation.indexes
plugins:
  - search
  - tags
  - openapi:
      output_dir: reference
      models_dir: data-models
      models_in_nav: false
      suppress_tag_overview: true
      suppress_method_badges: true
      tag_nav:
        - Core:
            - Pets
      unlisted_tags: error
nav:
  - Home: index.md
  - API Reference: openapi/spec.yaml
validation:
  nav:
    omitted_files: warn
  links:
    unrecognized_links: warn
""".strip()
        + "\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            str(config),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    site = tmp_path / "site"
    operation = site / "reference/pets/operation-post-create-pet.html"
    model = site / "data-models/pet.html"
    assert operation.is_file()
    assert model.is_file()
    assert (site / "reference/index.html").is_file()
    assert (site / "reference/pets/index.html").is_file()
    assert (site / "data-models/index.html").is_file()
    assert (site / "assets/mkdocs-openapi.css").is_file()
    assert (site / "assets/mkdocs-openapi.js").is_file()
    assert not (site / "openapi/spec.yaml").exists()

    operation_html = operation.read_text()
    reference_html = (site / "reference/index.html").read_text()
    assert "\n    Core\n" in reference_html
    assert ">Overview</a>" not in reference_html
    assert "<p>This specification includes:</p>" in reference_html
    assert "<li>Pet creation</li>" in reference_html
    assert "<li>Pet data models</li>" in reference_html
    assert 'data-api-endpoint>{"method": "POST", "endpoint": "/pets"}' in operation_html
    assert 'data-api-method="post"' in operation_html
    assert "../../data-models/pet.html" in operation_html
    assert '<span class="md-tag">POST</span>' in operation_html
    assert '<span class="md-tag">Pets</span>' in operation_html
    assert "Mochi" in operation_html
    assert "Page actions" in operation_html
    assert "View as Markdown" in operation_html
    assert "data-api-endpoint" in operation_html
    assert '<div class="api-endpoint">' not in operation_html
    assert '<div class="tabbed-set"' in operation_html
    assert "tabbed-alternate" not in operation_html
    assert "<strong>Schema:</strong> Pet" in operation_html
    assert '<div class="admonition warning">' in operation_html
    assert '<p class="admonition-title">Deprecated</p>' in operation_html
    assert "This operation is deprecated." in operation_html

    css = (site / "assets/mkdocs-openapi.css").read_text()
    assert "--api-method-post-color: #49cc90" in css
    assert "--api-method-text-color: #ffffff" in css
    assert ".md-typeset code.http-method" in css
    assert '.md-nav__link[data-api-method="post"]::before' in css
    assert "flex: 0 0 1.9rem" in css
    assert "overflow-x: auto" in css
    assert 'content: "DEL"' in css
    assert "Hide HTTP method badges" in css
    assert "display: none" in css

    # Generated Markdown is virtual: the plugin never writes into docs_dir.
    assert sorted(path.relative_to(docs).as_posix() for path in docs.rglob("*") if path.is_file()) == [
        "index.md",
        "openapi/spec.yaml",
    ]


def test_mkdocs_builds_models_inline_on_operation_pages(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n")
    _write_spec(
        docs / "openapi/pets.yaml",
        title="Pets API",
        tag="Pets",
        model="Pet",
        route="/pets",
    )
    config = tmp_path / "mkdocs.yml"
    config.write_text(
        """
site_name: Inline Models
docs_dir: docs
site_dir: site
use_directory_urls: false
theme:
  name: material
plugins:
  - openapi:
      models_mode: inline
nav:
  - Home: index.md
  - API Reference: openapi/pets.yaml
validation:
  links:
    unrecognized_links: warn
""".strip()
        + "\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            str(config),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    site = tmp_path / "site"
    operation = site / "api-reference/pets/operation-get-list-pets.html"
    assert operation.is_file()
    assert not (site / "models").exists()
    operation_html = operation.read_text()
    assert 'href="#model-pet"' not in operation_html
    assert 'id="model-pet"' not in operation_html
    assert "Properties" in operation_html


def test_mkdocs_builds_multiple_specifications(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n")
    _write_spec(
        docs / "openapi/pets.yaml",
        title="Pets API",
        tag="Pets",
        model="Pet",
        route="/pets",
    )
    _write_spec(
        docs / "openapi/orders.yaml",
        title="Orders API",
        tag="Orders",
        model="Order",
        route="/orders",
    )

    config = tmp_path / "mkdocs.yml"
    config.write_text(
        """
site_name: Multiple APIs
docs_dir: docs
site_dir: site
use_directory_urls: false
theme:
  name: material
  features:
    - navigation.indexes
plugins:
  - search
  - openapi:
      specs:
        pets:
          source: openapi/pets.yaml
          output_dir: references/pets
          models_in_nav: false
        orders:
          source: openapi/orders.yaml
          output_dir: references/orders
          models_dir: schemas/orders
          models_title: Order models
nav:
  - Home: index.md
  - APIs:
      - Pets API: openapi/pets.yaml
      - Orders API: openapi/orders.yaml
validation:
  nav:
    omitted_files: warn
  links:
    unrecognized_links: warn
""".strip()
        + "\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            str(config),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    site = tmp_path / "site"
    pets_operation = (
        site / "references/pets/pets/operation-get-list-pets.html"
    )
    orders_operation = (
        site / "references/orders/orders/operation-get-list-orders.html"
    )
    assert pets_operation.is_file()
    assert orders_operation.is_file()
    assert (site / "references/pets/models/pet.html").is_file()
    assert (site / "schemas/orders/order.html").is_file()
    assert not (site / "openapi/pets.yaml").exists()
    assert not (site / "openapi/orders.yaml").exists()

    pets_html = pets_operation.read_text()
    orders_html = orders_operation.read_text()
    assert "<strong>Schema:</strong> Pet" in pets_html
    assert "<strong>Schema:</strong> Order" in orders_html
    assert "<strong>Schema:</strong> <a" not in pets_html
    assert "<strong>Schema:</strong> <a" not in orders_html

    home_html = (site / "index.html").read_text()
    assert "Pets API" in home_html
    assert "Orders API" in home_html
    assert "Order models" in home_html


def test_mkdocs_ignores_external_spec_like_nav_links(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n")
    _write_spec(
        docs / "openapi/pets.yaml",
        title="Pets API",
        tag="Pets",
        model="Pet",
        route="/pets",
    )

    external_manifest = (
        "https://github.com/example/repository/blob/main/manifest.json"
    )
    config = tmp_path / "mkdocs.yml"
    config.write_text(
        f"""
site_name: API with external manifest
docs_dir: docs
site_dir: site
use_directory_urls: false
plugins:
  - openapi:
      specs:
        pets:
          source: openapi/pets.yaml
          output_dir: references/pets
nav:
  - Home: index.md
  - Pets: openapi/pets.yaml
  - Sample manifest: {external_manifest}
""".strip()
        + "\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            str(config),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    site = tmp_path / "site"
    assert (
        site / "references/pets/pets/operation-get-list-pets.html"
    ).is_file()
    home_html = (site / "index.html").read_text()
    assert f'href="{external_manifest}"' in home_html
    assert "Sample manifest" in home_html


def test_multi_spec_rejects_shared_generated_directory(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    _write_spec(
        docs / "openapi/pets.yaml",
        title="Pets API",
        tag="Pets",
        model="Pet",
        route="/pets",
    )
    _write_spec(
        docs / "openapi/orders.yaml",
        title="Orders API",
        tag="Orders",
        model="Order",
        route="/orders",
    )
    config = tmp_path / "mkdocs.yml"
    config.write_text(
        """
site_name: Multiple APIs
docs_dir: docs
site_dir: site
plugins:
  - openapi:
      specs:
        pets:
          source: openapi/pets.yaml
          output_dir: reference
        orders:
          source: openapi/orders.yaml
          output_dir: reference
nav:
  - Pets: openapi/pets.yaml
  - Orders: openapi/orders.yaml
""".strip()
        + "\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--config-file",
            str(config),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert (
        "specifications 'pets' and 'orders' use the same generated "
        "directory 'reference'"
    ) in result.stderr


def test_multi_spec_requires_every_nav_spec_to_be_registered(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    _write_spec(
        docs / "openapi/pets.yaml",
        title="Pets API",
        tag="Pets",
        model="Pet",
        route="/pets",
    )
    _write_spec(
        docs / "openapi/orders.yaml",
        title="Orders API",
        tag="Orders",
        model="Order",
        route="/orders",
    )
    config = tmp_path / "mkdocs.yml"
    config.write_text(
        """
site_name: Multiple APIs
docs_dir: docs
site_dir: site
plugins:
  - openapi:
      specs:
        pets:
          source: openapi/pets.yaml
          output_dir: references/pets
nav:
  - Pets: openapi/pets.yaml
  - Orders: openapi/orders.yaml
""".strip()
        + "\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--config-file",
            str(config),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert (
        "nav contains specifications not registered under specs: "
        "openapi/orders.yaml"
    ) in result.stderr
