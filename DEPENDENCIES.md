---
this_file: DEPENDENCIES.md
---

# Dependencies

The inventory CLI uses Python 3.12's standard library: `ast` for source structure,
`tokenize` for Python encoding detection, `xml.etree.ElementTree` for UI/qrc
structure, `hashlib` for exact original hashes, and `argparse`/`json`/`pathlib`
for explicit local inputs and portable output. It has no Qt runtime dependencies.
Official [AST](https://docs.python.org/3/library/ast.html),
[tokenize](https://docs.python.org/3/library/tokenize.html) and
[ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html)
documentation were checked before implementation.

`pytest` supplies owned-fixture tests and committed-catalog acceptance checks;
`pytest-cov` is optional coverage tooling. Ruff provides scoped lint and formatting.
Use `uv run --no-project --with pytest` and `uvx ruff` to run them without adding
dependencies to FontLab's embedded interpreter. Upstream dependency imports and
requirements declarations are inventory evidence, not packages installed here.
