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

All configured directories must be relative paths and must differ from one
another.

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
