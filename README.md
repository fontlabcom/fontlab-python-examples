---
this_file: README.md
---

# FontLab Python examples

Complete source catalog for planned PythonQt ports of
[pyqt/examples](https://github.com/pyqt/examples) and
[eyllanesc/QtExamples](https://github.com/eyllanesc/QtExamples), for use inside
running FontLab. Start at the [categorized index](catalog/INDEX.md).

Both pinned collections are fully acquired and verified locally: **1,569 files,
465 Python files**. The public catalog contains provenance and planned mappings;
the upstream originals remain local. **No examples are ported or native-tested
yet.** Source inventory does not complete the requested collections.

| Collection | Pinned revision | Original files | Python files |
| --- | --- | ---: | ---: |
| pyqt/examples | `83eed0514582c8deb60d9e9e6bff31ceffe4eaeb` | 805 | 308 |
| eyllanesc/QtExamples | `a01fd7d10d45801b10876f94c07aaefb11bc2e12` | 764 | 157 |

The [machine-readable catalog](catalog/sources.json) preserves every logical
source identity, exact original byte count, Git blob SHA, SHA-256, attribution
and license evidence, source URL, resource associations and distinct target path.
Both `others/matplotlib/Subplot.py` and `subplot.py` have separate mappings that
also remain distinct on a case-insensitive filesystem. Duplicate bytes retain
every original mapping.

Static analysis identifies 298 Python entrypoint candidates, 14 ambiguous Python
candidates, 153 auxiliary Python files, and 3 uncertain QML launcher candidates.
These counts are **not a confirmed executable-example denominator**. Main guards
and module launch calls provide evidence; uncertain files remain in scope.
Directory associations conservatively include shared/sibling resources. There
are 69 shared or repository files with unresolved example ownership; every one
has an individual catalog record. Native capability needs describe observed
source requirements, not host support.

## Regenerate the inventory

Use Python 3.12 and explicitly supply the two receipts and the verified source
roots. The recovery receipt supplies logical-to-storage mappings; unverified
archive extractions are not valid inputs. The tool checks complete receipt/tree
accounting, revisions and every original hash before writing output. It never
imports or executes upstream code or a Qt binding.

```sh
python tools/inventory.py \
  --tree-receipt "$TREE_RECEIPT" \
  --recovery-receipt "$RECOVERY_RECEIPT" \
  --source-root "pyqt/examples=$PYQT_SOURCE" \
  --source-root "eyllanesc/QtExamples=$QTEXAMPLES_SOURCE" \
  --output catalog
```

`TREE_RECEIPT` is `examples-upstream-trees.json`; `RECOVERY_RECEIPT` is
`examples-source-recovery.json`. Source-root variables must point to the verified
directories described by that receipt, including its case-collision mapping.
Repeated runs with unchanged receipts, bytes and interpreter produce identical
JSON and Markdown bytes. Output contains no private source-root paths.

## Verify the catalog tools

The tool uses only Python's standard library. Tests use pytest and owned fixtures;
they do not run a corpus example or modify FontLab, fonts or settings.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest \
  python -m pytest -q tests
uvx ruff check tools tests
uvx ruff format --check tools tests
```

## Licensing and remaining ports

The repository's Apache license does not relicense upstream inputs. Pinned
READMEs, actual notices and source headers supply per-file evidence. All 1,569
files retain **license review pending**; 43 have no recognized declaration.
Nearby notices may apply only to specific assets: their association is evidence,
not a blanket license assignment. Preserve the original notices and resolve
scope before distributing a port or copying upstream resources.

Every planned target is pending; every native state is unexecuted. Future ports
must use FontLab's existing PythonQt/Qt runtime and QApplication/event loop,
without loading PyQt, PySide or another Qt runtime. QML, WebEngine, multimedia,
GStreamer, matplotlib, database, network and platform examples remain in scope.
See [PLAN.md](PLAN.md) and [TODO.md](TODO.md) for the full remaining work.
