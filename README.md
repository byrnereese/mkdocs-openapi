# mkdocs-openapi

`mkdocs-openapi` generates predictable API reference pages from an OpenAPI
document. The plugin creates Markdown pages in memory and hands them back to
MkDocs, so the active theme, Markdown extensions, search, tags, navigation, and
link validation all participate in the normal build.

## Current status

This is an alpha implementation of the rendering contract demonstrated by the
Petstore example. It supports local OpenAPI 3.x JSON and YAML documents and one
specification per MkDocs site.

## Install for development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
```

## Configure

Place the specification under `docs_dir` and reference it directly from `nav`:

```yaml
plugins:
  - search
  - tags
  - openapi:
      output_dir: api-reference

nav:
  - Homepage: index.md
  - API Reference: openapi/spec.yaml
```

The source specification is consumed by the plugin and removed from the files
published to `site/`.

The single nav entry is expanded into:

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

The method labels shown above are CSS pseudo-elements. MkDocs nav labels remain
plain operation names, while generated filenames expose the HTTP method to
stable CSS attribute selectors.

## Configuration

| Option | Default | Description |
| --- | --- | --- |
| `output_dir` | `api-reference` | Virtual source directory for API and operation pages. |
| `models_dir` | `models` | Virtual source directory for component schemas. |
| `models_title` | `Models` | Navigation title inserted beside the API section. |
| `models_in_nav` | `true` | Include every model below the Models nav item. Set to `false` for very large schemas. |
| `tag_nav` | unset | Ordered tag navigation containing root-level tag names or titled groups of tag names. |
| `unlisted_tags` | `exclude` | Handle primary tags omitted from `tag_nav` with `exclude`, `append`, or `error`. |

The plugin automatically enables the Markdown extensions required by its
generated output: `admonition`, `attr_list`, `tables`,
`pymdownx.superfences`, and `pymdownx.tabbed`.

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

Plain string entries are rendered directly below API Reference. Group mappings
create an extra navigation level. Set `unlisted_tags` to `append` to add
unconfigured tags afterward in their default order, or to `error` to require an
exhaustive configuration. Unknown tags, duplicates, and empty groups fail the
build. If `tag_nav` is omitted, all tags retain the existing default order.

## Rendering behavior

- Each operation is generated as an in-memory Markdown page.
- Operations are grouped by their first OpenAPI tag.
- An operation with no tags is placed under `Untagged`.
- Additional operation tags are retained as page metadata for Material's tags
  plugin.
- Each `components.schemas` entry is generated as a model page.
- Local schema `$ref` values link to model pages.
- Truly inline schemas remain inline in the operation documentation.
- Operation and model slugs are deterministic, with numeric suffixes for
  collisions.
- The bundled stylesheet can be overridden with CSS custom properties such as
  `--api-method-get-color` and `--api-method-text-color`.

## Known first-version boundaries

- OpenAPI 3.x is supported; Swagger/OpenAPI 2.0 is rejected.
- One specification can be referenced per MkDocs site.
- External `$ref` documents are not resolved.
- Callbacks and webhooks are not yet rendered as operations.
- The first tag is the canonical navigation group for a multi-tag operation.

## Petstore example

The example at [`examples/petstore`](examples/petstore) builds directly from a
pinned Petstore specification:

```bash
.venv/bin/python examples/petstore/verify.py
.venv/bin/mkdocs build --strict -f examples/petstore/mkdocs.yml
```

The previous hand-authored design pages are retained under
`examples/petstore/reference` for comparison. They are not part of the MkDocs
build.

## Plugin documentation site

The primary project website is configured at the repository root. It includes
the plugin documentation and a generated Petstore example nested under the
Example site navigation:

```bash
.venv/bin/mkdocs serve
.venv/bin/mkdocs build --strict
```

## RingCentral stress example

The standalone [`examples/ringcentral`](examples/ringcentral) site exercises the
plugin with 517 operations and 1,481 reusable models:

```bash
.venv/bin/python examples/ringcentral/verify.py
.venv/bin/mkdocs build --strict -f examples/ringcentral/mkdocs.yml
```

Its output is written to `site-ringcentral/`.

## Tests

```bash
.venv/bin/pytest
```

The test suite covers JSON and YAML parsing, generated paths and navigation,
schema links, inline schemas, missing tags and operation IDs, duplicate slugs,
composed models, deterministic output, and a real strict MkDocs Material build.
