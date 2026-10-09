# mkdocs-openapi

Generate predictable, repeatable API reference documentation from an OpenAPI
specification.

`mkdocs-openapi` reads a local OpenAPI document referenced from `nav`, generates
Markdown pages in memory, and returns them to MkDocs. MkDocs and the active
theme remain responsible for converting those pages into HTML.

[Install the plugin](installation.md){ .md-button .md-button--primary }
[Explore the example](example-site/index.md){ .md-button }

## What it generates

- An API overview page
- One navigation section for each OpenAPI tag
- One page for each operation
- Reusable component schemas as standalone pages or inline operation sections
- Links from schema `$ref` values to the corresponding model documentation
- Material tag metadata for operation tags and HTTP methods
- Hierarchical navigation with compact method badges

The generated pages participate in the normal MkDocs pipeline:

```text
OpenAPI JSON or YAML
        ↓
mkdocs-openapi
        ↓
In-memory Markdown pages
        ↓
Markdown extensions and MkDocs plugins
        ↓
MkDocs Material templates
        ↓
Static HTML site
```

## Minimal configuration

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

The plugin replaces the OpenAPI nav entry with the generated hierarchy. The
source specification is not copied into the published site.

## Design goals

### Predictable

Generated paths, headings, ordering, and schema links are deterministic. Slug
collisions receive stable numeric suffixes.

### Native to MkDocs

The plugin produces Markdown instead of final HTML. Search, tags, navigation,
theme overrides, Markdown extensions, and link validation continue to work as
they do for authored documentation.

### Optimized for Material

The generated pages use inline parameter details, response content tabs,
admonitions, fenced code blocks, page metadata, and attribute lists. Bundled
styles and interactions provide method badges, scrollable endpoint URLs, copy
controls, and Markdown page actions.

## Current scope

The current release supports:

- OpenAPI 3.x
- JSON and YAML specifications
- Multiple specifications with isolated output directories
- Local component-schema `$ref` values
- Parameters, request bodies, responses, security requirements, and examples
- Inline and composed schemas
- Tagged, multi-tagged, and untagged operations

Current boundaries:

- External `$ref` documents are not yet resolved
- Swagger/OpenAPI 2.0 is not supported
- Callbacks and webhooks are not yet rendered as operations
- The first tag is the canonical navigation group for a multi-tag operation
