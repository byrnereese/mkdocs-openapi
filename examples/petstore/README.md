# Petstore design reference

This site is the end-to-end reference implementation for `mkdocs-openapi`. Its
only authored content page is `docs/index.md`; the API reference and model pages
are generated as in-memory Markdown from `docs/openapi/spec.json`.

The earlier hand-authored design pages are retained under `reference/` for
comparison, but they are not included in the MkDocs build.

## Design rules

1. One navigation section is generated for each OpenAPI tag.
2. Every operation is rendered on its own page.
3. Operations retain their order from the OpenAPI `paths` object.
4. Every reusable component schema is rendered on its own model page.
5. An OpenAPI `$ref` links to a model page instead of expanding inline.
6. The method and path are visible together at the start of every operation.
7. Operation pages carry Material tag metadata for the OpenAPI tag and method.
8. Native Markdown handles prose, tables, headings, and code blocks.
9. Material extensions handle admonitions, tabs, and collapsible sections.
10. Custom CSS is limited to presentation Markdown cannot express well.
11. Empty sections are omitted instead of displaying placeholder content.

## Navigation method badges

MkDocs navigation labels are plain text. CSS cannot select only the first word
of a label, and embedding HTML in `mkdocs.yml` would make the configuration
fragile.

Generated operation filenames begin with `operation-{method}-`. The bundled
plugin stylesheet matches that portion of each link's `href` and adds a method
badge with a `::before` pseudo-element. The actual link text remains the
operation name.

Method colors are CSS custom properties. The defaults match Swagger UI:

| Method | Variable | Default |
| --- | --- | --- |
| GET | `--api-method-get-color` | `#61affe` |
| POST | `--api-method-post-color` | `#49cc90` |
| PUT | `--api-method-put-color` | `#fca130` |
| DELETE | `--api-method-delete-color` | `#f93e3e` |

Badge text is white by default, matching Swagger UI:

```css
--api-method-text-color: #ffffff;
```

This foreground can be overridden alongside the method colors when a site
requires a different contrast profile.

## Expected production output

With `site_dir: ../../site`, the build creates:

```text
site/
├── index.html
├── api-reference/
│   ├── index.html
│   ├── pet/
│   │   ├── index.html
│   │   └── operation-{method}-{operation}.html
│   ├── store/
│   │   ├── index.html
│   │   └── operation-{method}-{operation}.html
│   └── user/
│       ├── index.html
│       └── operation-{method}-{operation}.html
└── models/
    ├── index.html
    └── {model}.html
```

MkDocs normally creates directory URLs such as `pet/index.html`. This reference
sets `use_directory_urls: false` so each operation and model is emitted as a
flat `.html` file within its section.

## Build and verify

From the repository root, run:

```bash
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python examples/petstore/verify.py
.venv/bin/mkdocs build --strict -f examples/petstore/mkdocs.yml
```

The first check inspects the virtual Markdown directly and confirms that all
operations and reusable models are represented. The strict build checks the
complete MkDocs pipeline, navigation, and links.
