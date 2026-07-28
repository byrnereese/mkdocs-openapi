from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


def test_mkdocs_builds_generated_markdown_with_material(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    spec_dir = docs / "openapi"
    spec_dir.mkdir(parents=True)
    (docs / "index.md").write_text("# Home\n")

    specification = {
        "openapi": "3.0.3",
        "info": {
            "title": "Tiny API",
            "description": "An integration fixture.",
            "version": "1.0.0",
        },
        "tags": [{"name": "Pets", "description": "Pet operations."}],
        "paths": {
            "/pets": {
                "post": {
                    "tags": ["Pets"],
                    "summary": "Create a pet",
                    "operationId": "createPet",
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
    assert not (site / "openapi/spec.yaml").exists()

    operation_html = operation.read_text()
    assert 'class="http-method post"' in operation_html
    assert "../../data-models/pet.html" in operation_html
    assert '<span class="md-tag">POST</span>' in operation_html
    assert '<span class="md-tag">Pets</span>' in operation_html
    assert "Mochi" in operation_html

    css = (site / "assets/mkdocs-openapi.css").read_text()
    assert "--api-method-post-color: #49cc90" in css
    assert "--api-method-text-color: #ffffff" in css
    assert ".md-typeset code.http-method" in css
    assert "flex: 0 0 2.35rem" in css

    # Generated Markdown is virtual: the plugin never writes into docs_dir.
    assert sorted(path.relative_to(docs).as_posix() for path in docs.rglob("*") if path.is_file()) == [
        "index.md",
        "openapi/spec.yaml",
    ]
