"""Check the virtual pages generated from the RingCentral specification."""

from __future__ import annotations

from pathlib import Path

from mkdocs_openapi.generator import generate_site
from mkdocs_openapi.parser import load_spec


ROOT = Path(__file__).parent


def main() -> None:
    source_uri = "openapi/rc-platform.yml"
    content = (ROOT / "docs" / source_uri).read_text()
    generated = generate_site(load_spec(content, source_uri))

    assert len(generated.operations) == 517
    assert len(generated.models) == 1_481
    assert len(generated.api_nav) - 1 == 81
    assert len(generated.pages) == 2_081

    methods: dict[str, int] = {}
    for operation in generated.operations:
        methods[operation.method] = methods.get(operation.method, 0) + 1
        page = generated.pages[operation.source_uri]
        assert f"`{operation.method}`{{ .http-method" in page
        assert f"`{operation.path}`{{ .operation-path }}" in page

    assert methods == {
        "DELETE": 54,
        "GET": 256,
        "PATCH": 24,
        "POST": 132,
        "PUT": 51,
    }

    list_contacts = generated.pages[
        "api-reference/external-contacts/operation-get-list-contacts.md"
    ]
    assert "**Operation ID:** `listContacts`" in list_contacts
    assert (
        "`/restapi/v1.0/account/{accountId}/extension/"
        "{extensionId}/address-book/contact`{ .operation-path }"
    ) in list_contacts
    assert generated.pages["models/account-directory-profile-image-resource.md"]

    print(
        "Verified 517 operations, 81 tag sections, 1,481 models, "
        "and 2,081 virtual Markdown pages."
    )


if __name__ == "__main__":
    main()
