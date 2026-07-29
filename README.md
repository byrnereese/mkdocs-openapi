# mkdocs-openapi

Generate predictable, native MkDocs API reference pages from an OpenAPI
document.

`mkdocs-openapi` converts an OpenAPI 3.x JSON or YAML document into Markdown
pages during the MkDocs build. Because the pages participate in the normal
MkDocs pipeline, they work with site navigation, search, tags, Markdown
extensions, link validation, and theme customization.

> [!IMPORTANT]
> `mkdocs-openapi` is designed and tested around
> [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). Its
> generated markup and bundled navigation styles take advantage of Material's
> layout and CSS conventions. Other themes may render the generated Markdown,
> but are not currently a supported or tested target.

## Status

This project is currently alpha software. It supports one or more local
OpenAPI 3.x documents per MkDocs site.

See the [changelog](CHANGELOG.md) for release history.

## Requirements

- Python 3.10 or later
- MkDocs 1.6 or later
- Material for MkDocs 9.6 or later (recommended and tested theme)

## Installation

Install the plugin and Material for MkDocs:

```bash
python -m pip install mkdocs-openapi mkdocs-material
```

If you already have a Material for MkDocs project, install only the plugin:

```bash
python -m pip install mkdocs-openapi
```

Confirm that MkDocs can discover the plugin:

```bash
mkdocs get-deps
```

## Quick start

Place your OpenAPI document under the MkDocs `docs_dir`. With the default
`docs/` directory, a minimal project might look like this:

```text
.
├── docs
│   ├── index.md
│   └── openapi
│       └── spec.yaml
└── mkdocs.yml
```

Enable the plugin in `mkdocs.yml`, then reference the OpenAPI document directly
from `nav`:

```yaml
site_name: My API

theme:
  name: material

plugins:
  - search
  - openapi

nav:
  - Home: index.md
  - API Reference: openapi/spec.yaml
```

Build or preview the site normally:

```bash
mkdocs serve
```

The OpenAPI nav entry is replaced with generated API pages:

```text
API Reference
├── Overview
├── First tag
│   ├── Overview
│   ├── GET First operation
│   └── POST Second operation
└── Second tag
    └── ...
Models
├── Overview
└── One page per component schema
```

The source specification is consumed during the build and is not copied into
the published site.

## Multiple specifications

Use `specs` when a site contains more than one OpenAPI document. Each entry
has a stable ID, a source path matching its `nav` entry, and an isolated output
directory:

```yaml
plugins:
  - search
  - openapi:
      specs:
        pets:
          source: openapi/pets.yaml
          output_dir: api-reference/pets
        orders:
          source: openapi/orders.yaml
          output_dir: api-reference/orders
          models_dir: api-reference/orders/models
          models_title: Order models

nav:
  - Home: index.md
  - APIs:
      - Pets: openapi/pets.yaml
      - Orders: openapi/orders.yaml
```

`source` and `output_dir` are required for every entry. `models_dir` defaults
to `<output_dir>/models`. The remaining rendering and navigation options may
be set globally and overridden for an individual specification. Every
configured source must appear in `nav` exactly once, and every OpenAPI document
in `nav` must be registered under `specs`.

## Material for MkDocs integration

The plugin automatically:

- adds its bundled `mkdocs-openapi.css` stylesheet;
- enables `admonition`, `attr_list`, `tables`, `pymdownx.superfences`, and
  `pymdownx.tabbed`;
- enables the alternate tab style used by Material;
- generates native Markdown pages that participate in Material search, tags,
  navigation, and table-of-contents behavior; and
- displays HTTP method badges in Material's primary navigation.

The method badge colors can be customized with CSS variables:

```css
:root {
  --api-method-get-color: #61affe;
  --api-method-post-color: #49cc90;
  --api-method-put-color: #fca130;
  --api-method-delete-color: #f93e3e;
  --api-method-text-color: #ffffff;
}
```

Add your override after the plugin stylesheet using the normal MkDocs
`extra_css` setting:

```yaml
extra_css:
  - stylesheets/extra.css
```

## Configuration

Plugin options are configured below the `openapi` entry:

```yaml
plugins:
  - search
  - tags
  - openapi:
      output_dir: api-reference
      models_dir: models
      models_title: Models
      models_in_nav: true
      suppress_tag_overview: false
      suppress_method_badges: false
```

| Option | Default | Description |
| --- | --- | --- |
| `output_dir` | `api-reference` | Virtual source directory for API and operation pages. |
| `models_dir` | `models` | Virtual source directory for component schema pages. |
| `models_title` | `Models` | Navigation title inserted beside the API section. |
| `models_in_nav` | `true` | Include every model below the Models nav item. Set to `false` for very large schemas. |
| `suppress_tag_overview` | `false` | Omit each tag's Overview link from generated navigation. The overview pages are still generated. |
| `suppress_method_badges` | `false` | Hide HTTP method badges in Material's primary navigation. |
| `tag_nav` | unset | Ordered tag navigation containing root-level tag names or titled groups of tag names. |
| `unlisted_tags` | `exclude` | Handle primary tags omitted from `tag_nav` with `exclude`, `append`, or `error`. |
| `specs` | unset | Mapping of specification IDs to multi-spec source, output, and optional per-spec overrides. |

When `specs` is set, each entry accepts:

| Option | Default | Description |
| --- | --- | --- |
| `source` | required | OpenAPI file below `docs_dir`; must match an entry in `nav`. |
| `output_dir` | required | Unique virtual source directory for this API. |
| `models_dir` | `<output_dir>/models` | Unique virtual source directory for this API's schemas. |
| `models_title` | global value | Navigation title for this API's schemas. |
| `models_in_nav` | global value | Whether every schema is included in navigation. |
| `suppress_tag_overview` | global value | Whether tag Overview links are omitted for this API. |
| `tag_nav` | global value | Tag navigation for this API. |
| `unlisted_tags` | global value | Handling of primary tags omitted from this API's `tag_nav`. |

### Tag navigation

`tag_nav` controls which primary OpenAPI tags are rendered, their order, and
whether they appear below an additional navigation level:

```yaml
plugins:
  - openapi:
      tag_nav:
        - Phone:
            - Business Hours
            - Call Blocking
            - Call Control
        - SMS and Fax:
            - Fax
            - Message Store
            - SMS
      unlisted_tags: exclude
```

Plain string entries are rendered directly below the API Reference section.
Group mappings create an additional navigation level.

Set `unlisted_tags` to:

- `exclude` to omit tags not listed in `tag_nav`;
- `append` to add unlisted tags after the configured tags; or
- `error` to require an exhaustive tag configuration.

Unknown tags, duplicates, and empty groups fail the build. If `tag_nav` is
omitted, all tags retain their default order.

## Rendering behavior

- Operations are grouped by their first OpenAPI tag.
- Operations without tags are placed under `Untagged`.
- Additional operation tags are retained as page metadata for Material's tags
  plugin.
- Each `components.schemas` entry generates a model page.
- Local schema `$ref` values link to generated model pages.
- Inline schemas remain inline in operation documentation.
- Operation and model slugs are deterministic, with numeric suffixes for
  collisions.

## Current limitations

- Swagger/OpenAPI 2.0 documents are rejected.
- External `$ref` documents are not resolved.
- Callbacks and webhooks are not rendered as operations.
- The first tag is the canonical navigation group for a multi-tag operation.
- Themes other than Material for MkDocs are not currently tested or supported.

## Examples

### Petstore

The Petstore example demonstrates the standard rendering contract:

```bash
.venv/bin/python examples/petstore/verify.py
.venv/bin/mkdocs build --strict -f examples/petstore/mkdocs.yml
```

### Multiple APIs

The multiple-API example generates two isolated references in one build:

```bash
.venv/bin/mkdocs build --strict -f examples/multiple/mkdocs.yml
```

### RingCentral

The RingCentral example stress-tests the plugin with 517 operations and 1,481
reusable models:

```bash
.venv/bin/python examples/ringcentral/verify.py
.venv/bin/mkdocs build --strict -f examples/ringcentral/mkdocs.yml
```

Its output is written to `site-ringcentral/`.

## Development

Clone the repository and install it in editable mode with test dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
```

Run the test suite:

```bash
pytest
```

Build the project documentation:

```bash
mkdocs build --strict
```

Or preview it locally:

```bash
mkdocs serve
```

## License

`mkdocs-openapi` is distributed under the MIT License. See
[`LICENSE`](LICENSE) for details.
