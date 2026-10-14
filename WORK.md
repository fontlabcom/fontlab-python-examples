---
this_file: WORK.md
---

# Work record

2026-10-14: Added the user's complete PythonQt example-port request to the root
and repository plans/task lists. Both supplied URLs identify pyqt/examples.
Read upstream README directly: numbered examples and official demos are included;
different license terms and current PyQt6 imports require per-file review and
Qt5/PythonQt adaptation. No source acquisition, port or native acceptance claimed.

2026-10-14: User extended the task to eyllanesc/QtExamples. Root and repository
plans now include both complete repositories, with the repeated pyqt URL counted
once. Checked upstream README/GitHub metadata: QtExamples includes official and
additional entries and declares GPL-3.0. Native verification remains pending.

2026-10-14: Complete acquisition and inventory supersede the historical acquisition
status above. Both recovery receipts now verify all 1,569 original bytes against
their pinned Git blobs and retain immutable archive hashes, per-file SHA-256 and
logical-to-storage paths. The verified mapping preserves QtExamples' case-distinct
`others/matplotlib/Subplot.py` and `subplot.py`; original archives remain unchanged.

Added the stdlib receipt-driven inventory tool and checked-in complete catalog.
Verified totals: pyqt/examples 805 files / 308 Python, QtExamples 764 / 157;
all 465 Python files parse. Static source evidence identifies 298 Python launch
candidates, 14 ambiguous Python candidates, 153 helpers and 3 uncertain QML
launcher candidates. All 1,569 files retain unique source/target identities;
69 shared or repository files have unresolved ownership. Resource/API/import
evidence and byte duplicate groups retain complete denominators. All license
reviews remain pending, including 43 files with no recognized declaration.

Verification: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest
--with pytest-cov python -m pytest -p pytest_cov -q tests --cov=tools
--cov-report=term-missing` passed 19 tests (86% tools coverage). Scoped Ruff lint
and formatting checks passed. Rebuilding from both verified roots into a clean
temporary directory yielded byte-identical JSON and Markdown. Exact source
recovery evidence is in the private `examples-upstream-trees.json` and
`examples-source-recovery.json` receipts; generated public output contains no
private absolute paths. No Qt, corpus example, fonts or settings were loaded.

All example implementations remain pending and all native states unexecuted.
Inventory coverage does not complete either collection's PythonQt ports.

2026-10-14: First real port batch implements four exact numbered-source IDs:
ce3e17a7a2a03a02 (QLabel), f5ddfd0eaacbf845 (QVBoxLayout),
79cc15680bc2cebb (Signals and Slots), 402068f40005cd66 (Qt Designer).
Read complete original sources, example/root READMEs and Designer XML. Selected
MIT under the pinned numbered-source grant, recording individual review and
Michael Herrmann attribution; copied only required Designer UI source with
unchanged 1,448 bytes, SHA-256 and Git blob identity. No screenshots/prose copied.
`catalog/ports.json` records implementation and license decisions separately;
`catalog/sources.json` and `catalog/INDEX.md` remain byte-identical.

Added import-safe named launcher and source-ID mapping, module-retained direct
native handles/JSON inspection, existing QApplication reuse, and delegated
owned-object cleanup through `fontlabapp.widgets.OwnedWidget`. Real Qt callback
opens a parented, asynchronous window-modal alert; the exact Designer UI retains
its original OK/Cancel connections. The external Remopy example uses ordinary
`FontLab.run()` with JSON variables and no setup/preferences calls. Reviewed
current local producer source and official Qt/PythonQt documentation first.

TDD: initial targeted run failed collection with missing
`fontlab_python_examples` (RED); focused runs then passed as implementation and
failure contracts were added (GREEN). Existing baseline: 19 tests passed.
Final verification: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with
pytest --with pytest-cov python -m pytest -p pytest_cov -q tests
--cov=fontlab_python_examples --cov=ports --cov-report=term-missing` passed all
44 tests, with 96% statement coverage for new launcher/ports. `uvx ruff check
tools tests fontlab_python_examples ports examples`, scoped Ruff format check,
`git diff --check`, exact resource/recovered-source hash checks and a real
host-free import/host-absence smoke passed. Test doubles establish contracts,
not actual native interactions. Native acceptance of all four remains pending
for independent root verification; both complete collections remain required.

2026-10-14: Task 1 round 1 fixes actual native load failure at 94aec38:
FontLab's bundled Python defaults text reads to ASCII; first named launch failed
before creating any widgets, and close also failed while parsing the manifest.
Both launcher JSON reads now explicitly select UTF-8, preserving all Unicode
metadata without changing locale/preferences or manifest/catalog/resource bytes.
Designer now enters QFile cleanup before attempting QUiLoader construction.

Tests first: default-ASCII text-reader boundary with actual UTF-8 Unicode JSON
and a failing loader-constructor double both failed before the fix (2 failed,
6 deselected). Both passed after the fixes. The Unicode test preserves names,
source-ID lookup, close and Unicode known-unported path handling; constructor
failure proves existing QFile close/delete with no owned widget creation.
Full relevant suite: 46 passed (96% launcher/port statement coverage); scoped
Ruff lint/format (24 files) and diff checks passed. Exact bytes of both catalogs,
static index and original Designer UI remain unchanged. Official pathlib
read_text encoding contract checked. Native acceptance of all four stays pending
for root's clean reviewed re-load; no native/producer/settings changes performed.
