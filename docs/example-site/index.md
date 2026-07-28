# Example site

This section is generated from the Swagger Petstore OpenAPI 3.0 document. It
demonstrates the complete plugin workflow using a realistic specification with
19 operations, three tags, multiple content types, authentication schemes, and
six reusable models.

[Browse the Petstore API](api-reference/index.md){ .md-button .md-button--primary }
[Browse the models](models/index.md){ .md-button }

## Configuration

The main documentation site uses this configuration:

```yaml
plugins:
  - search
  - tags
  - openapi:
      output_dir: example-site/api-reference
      models_dir: example-site/models

nav:
  - Overview: index.md
  - Installation: installation.md
  - Example site:
      - Introduction: example-site/index.md
      - Petstore API: example-site/openapi/spec.json
```

The plugin expands `Petstore API` in place. The API hierarchy and Models
section therefore remain nested beneath the top-level Example site item.

## Generated structure

```text
example-site/
├── api-reference/
│   ├── index.html
│   ├── pet/
│   │   ├── index.html
│   │   └── operation-{method}-{operation}/
│   ├── store/
│   └── user/
└── models/
    ├── index.html
    └── {model}/
```

This documentation site uses MkDocs' default directory URLs. Setting
`use_directory_urls: false` produces flat operation files ending in `.html`
instead.

## What to inspect

- The left navigation is grouped by OpenAPI tag.
- Each operation has its own page and stable URL.
- Method badges in the page and navigation share the same colors.
- Request content types use Material content tabs.
- Operation pages link to reusable model pages instead of expanding `$ref`
  schemas inline.
- Material tags expose the resource and HTTP method for each operation.

The pinned document comes from the
[Swagger Petstore API](https://petstore3.swagger.io/api/v3/openapi.json).

## Larger example

The repository also contains a standalone RingCentral example with 517
operations, 81 tag sections, and 1,481 reusable models. It serves as a
large-scale compatibility and performance fixture:

```bash
python examples/ringcentral/verify.py
mkdocs build --strict -f examples/ringcentral/mkdocs.yml
```
