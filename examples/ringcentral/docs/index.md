# RingCentral API example

This site demonstrates `mkdocs-openapi` against the RingCentral API, a
large real-world OpenAPI 3.0 specification.

| Metric | Count |
| --- | ---: |
| Paths | 360 |
| Operations | 517 |
| OpenAPI tags | 81 |
| Component schemas | 1,481 |
| Generated Markdown pages | 2,081 |

[Browse the API reference](api-reference/index.md){ .md-button .md-button--primary }
[Browse the models](models/index.md){ .md-button }

## Why this example matters

The RingCentral document exercises substantially more of the plugin than the
Petstore fixture:

- Deeply nested and recursive component schemas
- Hundreds of path, query, and body parameters
- GET, POST, PUT, PATCH, and DELETE operations
- OAuth 2.0 security requirements and scopes
- JSON, multipart, form, binary, audio, and other media types
- YAML-native timestamp examples
- Large tag and model navigation hierarchies

## Navigation performance

The site enables Material's `navigation.prune` feature. With more than 2,000
pages, pruning prevents the entire navigation hierarchy from being repeated in
the HTML for every page.

It also sets `models_in_nav: false`. The Models item links to the searchable
model index instead of repeating 1,481 individual model links on every page.
All model pages are still generated and linked from operations.

## Source

The specification is pinned locally at
`docs/openapi/rc-platform.yml`. The plugin consumes it during the build and does
not publish the source YAML into the generated site.
