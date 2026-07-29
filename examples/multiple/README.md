# Multiple APIs example

This example builds two OpenAPI documents into isolated sections of one MkDocs
site. From the repository root:

```bash
.venv/bin/mkdocs build --strict -f examples/multiple/mkdocs.yml
```

The Pets models use the default `api-reference/pets/models` directory. The
Orders models demonstrate an explicit `models_dir`.
