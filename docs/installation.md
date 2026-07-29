# Installation

## Requirements

- Python 3.10 or newer
- MkDocs 1.6 or newer
- An OpenAPI 3.x JSON or YAML document

MkDocs Material is recommended. The generated Markdown can be rendered by other
themes, but the reference styling and navigation badges are designed for
Material.

## Install the package

Install the released package into the same Python environment as MkDocs:

```bash
python -m pip install mkdocs-openapi
```

To work from a local checkout, install the module in editable mode:

```bash
python -m pip install -e .
```

For development and testing:

```bash
python -m pip install -e '.[test]'
```

## Add the plugin

Place the OpenAPI document below your MkDocs `docs_dir`:

```text
docs/
├── index.md
└── openapi/
    └── spec.yaml
```

Reference the specification directly from `nav`:

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

The `tags` plugin is optional, but recommended when using MkDocs Material. Each
operation page includes its OpenAPI tags and HTTP method as page metadata.

## Configuration options

| Option | Default | Description |
| --- | --- | --- |
| `output_dir` | `api-reference` | Virtual source directory for API, tag, and operation pages. |
| `models_dir` | `models` | Virtual source directory for component-schema pages. |
| `models_title` | `Models` | Navigation title inserted beside the generated API section. |
| `models_in_nav` | `true` | Include every model in navigation. Set to `false` to link only the Models index. |
| `suppress_tag_overview` | `false` | Omit tag Overview links from navigation while retaining the generated pages. |
| `suppress_method_badges` | `false` | Hide HTTP method badges in Material's primary navigation. |
| `tag_nav` | unset | Ordered tag navigation. Entries may be tag names or titled sections containing tag names. |
| `unlisted_tags` | `exclude` | Behavior for primary operation tags omitted from `tag_nav`: `exclude`, `append`, or `error`. |
| `specs` | unset | Mapping of specification IDs to multi-spec configuration. |

All configured directories must be relative paths and must differ from one
another.

### Configure multiple specifications

Sites with more than one OpenAPI document use an explicit `specs` mapping:

```yaml
plugins:
  - search
  - openapi:
      models_in_nav: false
      specs:
        pets:
          source: openapi/pets.yaml
          output_dir: api-reference/pets
        orders:
          source: openapi/orders.yaml
          output_dir: api-reference/orders
          models_dir: api-reference/orders/models
          models_title: Order models
          models_in_nav: true

nav:
  - Homepage: index.md
  - APIs:
      - Pets: openapi/pets.yaml
      - Orders: openapi/orders.yaml
```

Every spec entry requires:

- a unique ID, such as `pets`;
- a `source` path below `docs_dir` that appears in `nav` exactly once; and
- a unique `output_dir`.

`models_dir` defaults to `<output_dir>/models`. `models_title`,
`models_in_nav`, `suppress_tag_overview`, `tag_nav`, and `unlisted_tags`
inherit their top-level values and can be overridden per specification.
`suppress_method_badges` applies to the whole site. The plugin validates all
generated paths before adding any virtual files, so output collisions fail the
build with the owning specification IDs.

### Select, order, and group tags

Use `tag_nav` to make the generated navigation authoritative instead of relying
on the tag order in the OpenAPI document:

```yaml
plugins:
  - openapi:
      tag_nav:
        - Phone:
            - Business Hours
            - Call Blocking
            - Call Control
            - Call Forwarding
            - Call Handling Rules
            - States
            - State-based Rules
            - Interaction Rules
            - Forwarding Targets
        - SMS and Fax:
            - Fax
            - Message Exports
            - Message Store
            - Pager Messages
            - SMS
            - High Volume SMS
      unlisted_tags: exclude
```

Each mapping creates an additional navigation level. A plain string places a
tag directly below the API Reference section:

```yaml
tag_nav:
  - Authentication
  - Phone:
      - Business Hours
      - Call Control
  - Webinars
```

Configured tags must be primary tags used by at least one operation. A tag
cannot appear more than once. Unknown tags, duplicate tags, duplicate section
titles, and empty sections cause the build to fail.

`unlisted_tags` controls tags that are used as an operation's first tag but do
not appear in `tag_nav`:

- `exclude` omits their tag and operation pages.
- `append` adds them at the root level after configured entries, preserving the
  OpenAPI declaration order.
- `error` fails the build and lists the missing tags.

When `tag_nav` is unset, `unlisted_tags` has no effect and the plugin preserves
its existing behavior: all primary tags are rendered in OpenAPI declaration
order, followed by undeclared tags in encounter order.

## Markdown extensions

The plugin automatically enables the extensions required by its output:

- `admonition`
- `attr_list`
- `tables`
- `pymdownx.superfences`
- `pymdownx.tabbed`

You can enable additional extensions normally in `mkdocs.yml`.

## Customize method colors

Override the bundled CSS custom properties in your own stylesheet:

```css
:root {
  --api-method-get-color: #61affe;
  --api-method-post-color: #49cc90;
  --api-method-put-color: #fca130;
  --api-method-delete-color: #f93e3e;
  --api-method-text-color: #ffffff;
}
```

Add the override after the plugin stylesheet:

```yaml
extra_css:
  - stylesheets/extra.css
```

## Build the site

Preview locally:

```bash
mkdocs serve
```

Build with warnings treated as errors:

```bash
mkdocs build --strict
```
