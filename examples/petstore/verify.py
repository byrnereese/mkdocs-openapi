"""Check the virtual pages generated from the pinned Petstore document."""

from __future__ import annotations

from pathlib import Path

from mkdocs_openapi.generator import generate_site
from mkdocs_openapi.parser import load_spec


ROOT = Path(__file__).parent


def main() -> None:
    source_uri = "openapi/spec.json"
    content = (ROOT / "docs" / source_uri).read_text()
    generated = generate_site(load_spec(content, source_uri))

    assert len(generated.operations) == 19
    assert len(generated.models) == 6
    assert len(generated.pages) == 30
    assert {operation.primary_tag for operation in generated.operations} == {
        "pet",
        "store",
        "user",
    }

    for operation in generated.operations:
        page = generated.pages[operation.source_uri]
        assert f"`{operation.method}`{{ .http-method" in page
        assert f"`{operation.path}`{{ .operation-path }}" in page

    update_pet = generated.pages[
        "api-reference/pet/operation-put-update-pet.md"
    ]
    assert "**Schema:** [Pet](../../models/pet.md)" in update_pet
    assert "| `name` | string | **Yes** |" not in update_pet
    assert "| `name` | string | **Yes** |" in generated.pages["models/pet.md"]

    print(
        "Verified 19 virtual operation pages, 6 virtual model pages, "
        "and reusable-schema links."
    )


if __name__ == "__main__":
    main()

