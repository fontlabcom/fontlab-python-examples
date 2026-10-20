---
this_file: DEPENDENCIES.md
---

# Dependencies

The inventory CLI uses Python 3.12's standard library: `ast` for source structure,
`tokenize` for Python encoding detection, `xml.etree.ElementTree` for UI/qrc
structure, `hashlib` for exact original hashes, and `argparse`/`json`/`pathlib`
for explicit local inputs and portable output. It has no Qt runtime dependencies.
Port-state regeneration adds no packages. It projects existing manifest metadata
and checks source hashes without accessing the private archive. State-dependent
tests use [pytest.skip](https://docs.pytest.org/en/stable/how-to/skipping.html),
with `clean_room_pending` as their only relocation skip condition.
Official [AST](https://docs.python.org/3/library/ast.html),
[tokenize](https://docs.python.org/3/library/tokenize.html) and
[ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html)
documentation were checked before implementation.

`pytest` supplies owned-fixture tests and committed-catalog acceptance checks;
`pytest-cov` is optional coverage tooling. Ruff provides scoped lint and formatting.
Use `uv run --no-project --with pytest` and `uvx ruff` to run them without adding
dependencies to FontLab's embedded interpreter. Upstream dependency imports and
requirements declarations are inventory evidence, not packages installed here.

The first four ports require FontLab's own PythonQt and existing QApplication.
`fontlab-fontlabapp` supplies `fontlabapp.widgets.OwnedWidget`; the launcher
imports that dependency only for launch, so catalog/help work outside the host.
No PyQt/PySide, Qt.py or second Qt runtime is required. Standard-library importlib
loads the four catalog-mapped port paths; pathlib resolves the exact UI resource.
`fontlab-remopy` is optional on the external controller only, used by
`examples/remopy.py` and `tools/native_cleanroom.py` to execute ordinary Python
in an already configured FontLab. The acceptance driver requires Python 3.11 and
adds no host dependencies. Its phases use the current local Remopy `FontLab.run`
result contract and the existing Fontlabapp ownership implementation.

Consumer calls were checked against the current local `fontlabapp/widgets.py`
and Remopy `control.py`/`execution.py`, and official
[PythonQt documentation](https://mevislab.github.io/pythonqt/),
[QUiLoader](https://doc.qt.io/qt-6/quiloader.html),
[QDialog open/modality](https://doc.qt.io/qt-6/qdialog.html) and
[QApplication](https://doc.qt.io/qt-6/qapplication.html) documentation.
Native prerequisite receipts confirm FontLab's actual clicked callback and
original Designer load/connections. Port interaction acceptance remains separate.


No additional
FontLab dependency is installed. All implemented ports retain PythonQt and
fontlab-fontlabapp ownership requirements. QSoundEffect, QtQml, QtQuick, QtSql
and the standalone fbs/PyQt6 freezer are recorded host capability gaps.


Batch 4 adds no packages. Standard-library csv, pathlib, pickle, math and a local
random.Random preserve the upstream data/animation behavior. Pickle is limited
to string dictionaries in an owned temporary directory and denies global/class
loading. Qt's QBuffer/QDataStream QVariant methods replace unsupported Python
stream operators. API names were checked against the host's QtCore/QtGui/private
stubs; [PythonQt datatype documentation](https://mevislab.github.io/pythonqt/Developer.html)
confirms QByteArray.data() and QVariant conversions. Exact overload and virtual
callback behavior still requires the controller's native acceptance.

## Re-evaluation 2026-10-15 (R046)

- No pip packages are installed into FontLab for the examples. Ports use FontLab's
  PythonQt only.
- `examples/recipes/` import sibling workspace packages: fontlab-fontlabapp, fontlab-glyport
  (including its synthesized `GlyphsApp`/`Foundation` modules) and, from the external
  controller, fontlab-remopy. The native drivers put the real checkouts on
  FontLab's sys.path in a guarded call and restore it afterwards.
- Development tools: pytest (`uv run --no-project --with pytest`), pytest-cov (optional)
  and ruff (`uvx ruff`). None of them run inside FontLab.

W1 adds no runtime dependency. Pending archived launchers need the exact local/private
rescued snapshot identified by rescue-index.json. FONTLAB_PRESERVED_ROOT is a test-only
byte-audit input; the snapshot is not included in public artifacts.


## Issue120 current documentation Z5

No runtime dependency added. Documentation uses locked ProperDocs/MaterialX, codeinclude and the already pinned PyMdown snippets extension; snapshots are inert data. Documentation-only plugin tests live under src_docs/tests and run in the locked docs environment.


## Issue120 documentation quality Z7

Documentation SDK tests now live under tests_docs and run in the locked documentation environment. Runtime tests stay on Python3.11. The real push gate combines both measurements without exclusions or a reduced threshold. No runtime menu body changes. All199lesson tests (including four legacy/lesson namespace orders),1993current root tests and5SDK tests pass. EXAMPLES_LEGACY_API_SOURCE selects only the reviewed read-only first-party legacy API; it does not redirect the current suite. Audit controls reject historical script and native-module execution. D21 deletions remain intact.

These local gates do not establish native/font/history/reopen or site-publication acceptance. Exact commands and retained failures are in the parent verification/issue-120/docs-quality-z7/.

Z10 adds no runtime dependency. App uses stdlib and FontLab PythonQt; menus require the reviewed unpublished App>=0.2.54.dev0. Standalone PyQt5==5.15.11/Qt5 and PySide6 checks run in separate private test processes and are never loaded into FontLab. Archived first-party Python source attribution is in NOTICE.

Z11 adds no runtime dependency. Typed Qt date policies use existing FontLab PythonQt. Optional Table.epochs is plain immutable integer data; old string-table callers retain their behavior. Menus require reviewed unpublished App>=0.2.55.dev0. Standalone Qt5/Qt6 remain separate private test processes.

Z13 adds no third-party dependency. Immutable topology/model helpers use stdlib and injected existing Qt. The two practical tree menus require reviewed unpublished App>=0.2.57.dev0 and Fly; actual native acceptance remains pending.


## Issue120 Z16 — complete part2 modification calendar candidate

The complete part2 calendar retains three locales, Monday/Sunday, single/no
selection, grid/navigation, every horizontal/vertical heading mode, selected/
minimum/maximum date editors, all weekday/weekend/header colours and first-Friday/
January-1 markings. Selected days show all matching current-font glyph metadata
in font order, all Unicode assignments, explicit unencoded values and exact local
timestamps. Undated glyphs are counted. Refresh replaces the entire observation.

Initial controls agree with the actual calendar; crossing limits synchronize all
three date editors. A copied owned date-surface palette preserves explicit named
colours on dark hosts, including readable headers/off-month dates; the surrounding
UI retains its host palette. Generic UI takes injected Qt and caller-owned signals.
Setup failures fence queued slots; all completion routes, parent destruction and
late Close release callbacks/data. Reads and planning share a bounded deadline.

Requires reviewed unpublished App>=0.2.60.dev0 via Fly. No font, selection, history,
preferences, file, clipboard or Output writer is added. The distinct part3 calendar
is not implemented by this entry. Originals/dependencies remain read-only and
unexecuted. Actual PythonQt/FontLab/getter/cache/font/history/dirty/reopen/native
workflow, release/integration/download/docs/publication and full issue120 gates
remain pending D25. Standalone scalar/Qt tests do not accept those requirements.


## Issue120 Z17 — complete distinct part3 calendar candidate

Part3 retains every Qt locale in original order, native language/country labels
and last matching initial locale, all seven week starts, both selection modes,
grid/navigation, every heading format, 1900–3000 date limits and MMM d yyyy
editors, four weekday/weekend colours and Bold/Italic/Plain headers. The latent
programmatic Green header rule remains without a new UI choice. Blue first-Friday
and red May1 switches are independent; May1 wins collisions. Only owned old marks
clear after page/year/switch changes. Full locale labels remain in the popup and
tooltip while the field stays bounded. No global locale or theme setting changes.

A shared injected-Qt base owns geometry, fields, coherent dates and callback
fencing. Part2 retains every public import path and its distinct policy. Both
modeless panels share whole captured local-day glyph reports and separate registry
keys. Source/type/empty/error/deadline/close/teardown paths remain complete.

Requires reviewed unpublished App>=0.2.61.dev0 through Fly. No original/corpus
script, native font/selection/history/preferences/clipboard/file/Output writer,
live install, canonical merge, release or publication is introduced. Actual
PythonQt/native UI/getter/font/cache/history/dirty/save/reopen and all original
issue120 source/integration/distribution/docs/publication gates remain pending D25.


## Issue120 Z20 — complete glyph-name completion pair

Implement both distinct part2/part3 custom-completer workflows over the complete
current-font glyph-name snapshot. Share injected Qt editor/model ownership in
App; preserve each original key, focus, suffix and menu policy. Use Qt itself
for case-insensitive sorting before completer binary search. Refresh keeps the
draft and discards stale vocabulary on failure. About information appears in
the modeless status area; Vocabulary names are escaped plain data. Disconnect
faults retain ownership and refuse Close for retry. Every ordinary completion,
parent destruction, setup failure and queued callback is owned and fenced.

Requires reviewed unpublished App>=0.2.63.dev0 through Fly. Originals/resources
remain read only, unexecuted and unbundled. No native font/selection/history/
preferences/file/Output writer or live install is added. Full installed PythonQt
behavior and complete font/cache/history/dirty/save/reopen preservation remain
pending D25, as do every original issue120 integration/distribution/publication
gate. Source and artifact checks do not constitute native acceptance.

## Issue120 Z24 frontend notices

No build/runtime dependency changes. Existing locked ProperDocs/MaterialX/plugin versions remain. Browser notice texts record pinned npm/publisher sources and the captured shared-theme/font responses; the full transitive review remains open.

Z27 spacing worksheets add no runtime dependency. Use existing injected FontLab PythonQt, shared draft_signals/layer_selection/tabular_width mechanics and Fly. Standalone PyQt5 is test-only rehearsal; foreign Qt is never imported into FontLab. Normal wheel/sdist installs retain declared dependency resolution and pip check; host architecture is aarch64 Python3.11.
