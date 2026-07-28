# RingCentral example

This standalone site builds the complete RingCentral API reference from a
1.6 MB OpenAPI 3.0 YAML document.

From the repository root:

```bash
source .venv/bin/activate
python -m pip install -e '.[test]'
python examples/ringcentral/verify.py
mkdocs build --strict -f examples/ringcentral/mkdocs.yml
```

The production build is written to `site-ringcentral/`.

To preview it:

```bash
mkdocs serve -f examples/ringcentral/mkdocs.yml
```

MkDocs serves the example at <http://127.0.0.1:8000>.

The example enables Material's `navigation.prune` feature because the generated
site contains more than 2,000 pages. It also disables individual model entries
in navigation with `models_in_nav: false`; the Models item links to the complete
model index instead.
