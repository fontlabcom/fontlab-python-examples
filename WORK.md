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

Remote tree inventory pins pyqt/examples at
83eed0514582c8deb60d9e9e6bff31ceffe4eaeb (805 files, 308 Python files) and
eyllanesc/QtExamples at a01fd7d10d45801b10876f94c07aaefb11bc2e12
(764 files, 157 Python files). Both recursive API trees were complete, not
truncated. These are source-file counts, not executable-example counts.
Receipt: parent verification/issue-101-ecosystem/evidence/examples-upstream-trees.json.
Original source bytes have not yet been acquired or ported.

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

## First four ports: reviewed code and actual native acceptance

Implementation701df4d fixes nativeASCII manifest read and constructor cleanup;
scopedreview bothfindingsaddressed/no newbreakage. Root clean-source native
ordinaryRemopy checks pass label/layout/click/window-modal alert/OKdismissal/
repeat/DesignerOKCancel;38trackedQObject/helper objects destroyed independently,
registry emptied/modulepath restored/FontLab alive. 627storedsettings andfont
records exactlymatchbeforeafter; all1569originalfiles rehashedunchanged. Five
owned-widget PNG renders inspected. Evidenceverification/first-native-batch.json.
Original94aec38nativefailure and701rootverifiergeometryfailure remainretained;
no wheel/install/fullcollectioncompletion claim. Wholebatchreview stillpending.

2026-10-14: Inventory execution-scope task addresses deferred findings M1/M2.
Module/class definition-time traversal now prunes only function/async/method/
lambda bodies for launch calls and main guards. Class bodies/headers, decorators
and defaults stay visible; unrestricted import/API/capability extraction remains
separate. No condition evaluation, function call graph or runtime claim added.
Output creation and both file writes now share the portable CLI error boundary.

Baseline: 46 tests passed. TDD focused RED: 16 failed, 8 passed, 15 deselected;
expected nested-deferred false positives, missed definition-time calls and three
uncaught PermissionErrors. GREEN: all 24 new scope/error cases passed. Complete
pinned Python 3.12 regenerations into two separate temporary outputs were byte
identical to each other and the checked-in JSON/index. No classification or
source-evidence changes in this corpus: 298 entrypoints, 14 ambiguous Python,
153 auxiliary Python, 3 ambiguous QML, all 465 Python parsed; 69 shared/repository
files remain unresolved. All 1,569 exact IDs/hashes/storage/category/target
mappings and four port IDs/targets plus Designer resource remain binding.
Manifest catalog hash and accepted native receipts/code/resources remain unchanged.
Both original archive hashes rechecked. Full suite: 70 passed; tools statement
coverage 92%; scoped lint/format and diff checks passed. No upstream/Qt/native
execution or sibling/source/archive changes. Every remaining collection port,
license/ambiguity/ownership review and native acceptance stays required.
Details: .superpowers/sdd/inventory-execution-scope/task-1-report.md.


2026-10-14: Second numbered batch adds ten entrypoint modules for examples
02, 07, 09, 10, all three 11 chat variants, 12, 13 and 14, at exact catalog
planned paths. Read pinned source/README/header evidence and first-batch pattern;
new modules import/build with injected QtCore/QtGui boundary doubles. No upstream
sources, source inventories, TODO checkboxes, first-batch ports/resources or
verification receipts changed; no commit made. The pre-existing untracked .omc
folder remains untouched.

Added explicit blocked records for 06 (missing QtQml/QtQuick), 08 (fbs PyQt6
standalone QApplication/freezer incompatible with the embedded host), and 15
(missing QtSql, including its initializer). All new native states are unexecuted.
Gallery 02 preserves its complete Riverbank/Nokia BSD source header and keeps
license review unresolved; other numbered entrypoints select the existing MIT
grant. Five copied editor/painter assets match catalog SHA-256 and recovered
bytes. Painter audio cannot use QSoundEffect through permitted QtCore/QtGui;
shot.wav is preserved and sound_supported=False explicitly reports the gap.

Shared editor code retains original menus/content/shortcuts with UTF-8 file I/O,
asynchronous unsaved-change/About dialogs, and named cleanup suppressing prompts.
Gallery and Fusion styles/palettes affect only owned widgets. Chat input() is
replaced by a name field; urllib uses socket timeouts, Python queues carry
results/payloads, GUI QTimers deliver UI changes, and close joins workers.
Original single-threaded polling remains distinct; the threadutil variant uses
50ms GUI delivery rather than a PyQt-only signal helper. Models retain parents
and wrappers; the custom table model checks invalid indexes, roles and parents.
Native checks and exact launch names are in docs/second-numbered-batch.md/README.

Verification: baseline required pytest gate passed 70 tests. The extended gate
`UV_CACHE_DIR=/tmp/fontlab-examples-uv PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run
--no-project --with pytest python -m pytest -q tests` passed 89 tests (19 new
cases), including every new build/import, exact identities/resource hashes,
model contracts, UTF-8 file success/failure, gallery defaults/progression,
painter positions/end(), worker error delivery and native-close/handle join.
The temporary UV_CACHE_DIR override is needed because the sandbox denies the
normal user cache. Ruff check and format --check passed for 29 Python files;
git diff --check passed. Tooling runs via uv run --no-project --with ruff because
uvx tools installation also targets a sandbox-denied user directory. Tests are
boundary evidence only; the controller owns native acceptance.


2026-10-14: Controller reported SIGSEGV during deferred deletion of PyQt Widgets:
PythonQt child signal receivers retained bound native-widget/subclass methods,
whose wrapper release could double-delete an already-dying QWidget. Added exact
signal/slot and string-signature connection records to ExampleHandle. close now
stops cleanup timers/workers, disconnects all pairs, clears callbacks/inspection
and retained models, releases port-owned native references, then closes alerts
and owner. Disconnection errors prevent progression to native teardown.

Converted gallery (7 connections), all three shared editors (5 action signals
plus each dynamic prompt), all three chats (3 signals each), and existing Signals
and Slots (1 signal). Models 12/13/14 have no explicit connections; retained model
references are cleared centrally. Gallery creates ownership before wiring,
clears child attributes, and releases its window cell. Editor/chat release native
closure cells held by subclass methods; named editor close still suppresses
prompts and chat close avoids touching a released timer. No native success claim,
manifest/resource/inventory/TODO/receipt changes, or commit.

Gate: UV_CACHE_DIR=/tmp/fontlab-examples-uv PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run
--no-project --with pytest python -m pytest -q tests — 103 passed. Added 14 cases
covering exact connection counts for all ten batch entrypoints and Signals and
Slots, stopped timers/workers before disconnection, callback/model/reference
release before alert/owner deletion, dynamic prompt disconnection, and subclass
closure-cell release. Ruff lint/format and git diff --check passed. Native
verification remains for the controller.

## 2026-10-14: Controller native launch/inspect/close for second batch

After the teardown fix (f384365), each of the ten implemented ports was run
separately in relaunched FontLab 9 via installed Remopy: launch, inspect, close
all succeed for 02, 07, 09, 10, 11 (three variants), 12, 13, 14; host alive after
each; open-font list unchanged. QStringListModel/QAbstractTableModel live in
PythonQt.QtGui in this host, not QtCore; ports and doubles corrected. Earlier
attempt crashed FontLab (double delete closing 02) before the fix. Receipts:
parent verification/issue-101-ecosystem/evidence/tg4-second-batch/. Interaction
acceptance (clicks, save prompts, thread messaging, painting holes) is still
pending, so ports.json native_acceptance remains "unexecuted".

QPainter interaction (native): direct super().paintEvent/mousePressEvent raised AttributeError (text unpainted, base click ignored). Replaced with explicit QPlainTextEdit base calls; native click now moves cursor 0->39, hole recorded, no callback errors.

Native interactions (controller): 02 disable toggle disables/restores all groups, timer progress 0->199 in 2.5 s; 13 model edit persists; 07 named close with unsaved text closes without prompt; fonts unchanged, host alive. Receipt native-interactions.json. Pending: 11 thread messaging (needs the chat server), editor Open/Save dialogs, 12 navigation.


## 2026-10-14: PythonQt reference survey and original insights

Read the house README/PLAN, WORK/CHANGELOG, handle/launcher, ports manifest,
QLabel/QPainter ports and existing Qt doubles/tests. Systematically read all
895 manifest-listed Python files in 29 source entries (the supplied task says
28; the manifest actually lists 29), starting jcfr, TypeRig, RobotLocomotion,
Slicer, Naali and CsoundQt. Scanner reads cover the full corpus; focused
contextual reads cover repeating patterns and a sample from every source.
The per-source byte-read ledger and 52 valid numbered citations are in
`docs/pythonqt-reference-insights.md`. These are not 895 deep human reviews.

Ranked 18 idioms with FontLab value, PythonQt gotchas and existing port coverage.
The manifest supplies only licence-file paths, not licence identifiers or grant
text; those files are absent from the reference tree. Citations and insights.json
therefore retain evidence paths and explicitly unresolved source grants. New
code is original Apache-2.0; no reference code/resources copied or executed.

Implemented the top 12 under ports/insights with named launcher discovery,
inspectable state, parent-owned children, tracked signals and disconnect-before-
delete cleanup. Added the small owned-build rollback context manager; release
child dictionaries, subclass fields and inspection/model callbacks before owner
close. Timers stop and filters detach first; already-destroyed owners avoid dead
native calls. All use injected QtGui widgets/models/private QObject and existing
FontLab event loop. Settings explicitly writes only proof/sample under
FontLabPythonExamples/InsightsSandbox on Save/Reset, never during build.
No runtime dependency changes; README launch names and CHANGELOG updated.

Wait, but boundary doubles cannot prove C++ model/paint/filter dispatch, wrapper
identity, floating-dock cleanup or deferred deletion safety. Native checklists
are recorded per example; all twelve native_acceptance values remain unexecuted
for the controller. PLAN/TODO were not changed or ticked. No commit.

Verification: baseline 103 tests passed in cached offline uv. Tests first failed
for absent insight names/manifest, then passed after implementation. Full suite:
127 passed (103 existing + 24 new), using the prescribed UV_CACHE_DIR and plugin
autoload settings, plus UV_OFFLINE=1 to use the cached pytest environment.
The exact supplied online gate was attempted twice and exited 2 before tests:
PyPI DNS lookup failed. The cached offline command is:
`UV_CACHE_DIR=/tmp/fontlab-examples-uv UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests`.
New tests cover every build/inspect/close and disconnect-before-delete sequence,
manifest targets/citations/licence evidence, meaningful interactions, invalid
model callbacks/input, bounded timers/logs, settings persistence/reset/error,
painter finally cleanup, partial-build rollback and dead-owner cleanup.
Scoped Ruff check/format pass for 17 Python files. Python 3.11 grammar/header
checks pass for 14 runtime files. Every one of the 895 reference files still
matches manifest bytes/SHA-256; manifest, ports.json and source catalog untouched.
`git diff --check` passes. Native acceptance remains the controller's next step.


## 2026-10-14: Native wrapper attribute correction

Controller acceptance found 11 insight launches failed at shared owned() assigning
window.controls; only the Python Canvas subclass accepted that field. Native
PythonQt class instances reject new Python attributes; Python subclasses permit
fields. Moved controls to ExampleHandle and clear them after signal disconnection
and before reference release/native owner deletion. Removed the native assignment
from fontlab_python_examples/insights.py. Replaced window.controls.update with
handle.controls.update in signal-lifetime, glyph-list, timer-batch, owned-key-filter,
metric-controls, glyph-properties, sandbox-settings, callback-errors, owned-dock
and contour-scene. Updated interaction tests and documented get(name).controls.
The common fix also covers metrics-table and contour-canvas builders.

Audited every AST attribute assignment and setattr/delattr in all runtime helpers
and all ports, including editor.py, chat.py, gallery, painting, themes and models.
Remaining custom fields belong to Python classes/subclasses: gallery WidgetGallery,
QPainter PlainTextEdit, insight Canvas/KeyObserver or ExampleHandle. label.text
is an existing Qt property. Editor/chat keep native references in closures and
use Qt setters; no additional unsafe assignments found. Their sources need no
change for this host restriction.

Hardened native-class doubles in tests/qt_doubles.py, tests/test_second_batch.py
and tests/insight_doubles.py with a constructor-scoped __setattr__ guard. Direct
native instances reject unknown fields; unmarked Python subclasses can add them.
Native simulated constructors/setters populate legitimate internal fields without
opening application assignments. Added widget/model/timer/settings/path/scene/
QObject regressions and an owned-build/controls-release test.

Tests first reproduced the permissive-double bug (expected AttributeError was
not raised); after guarding doubles, the old helper failed at the exact native
window.controls assignment. After moving controls to the handle, the prescribed
offline gate passes: 138 tests (127 previous + 11 regressions). Cleanup-order and
all second-batch tests pass under the stricter boundary. Ruff lint/format and
git diff --check pass. No reference, manifest, native acceptance, PLAN/TODO or
runtime dependency changes, and no commit. Controller must rerun native acceptance.

## 2026-10-14: Issue 103 insights native acceptance (controller)

First native run failed for 11 of 12: native PythonQt instances reject new
attributes (`window.controls = {}`); Codex fixed storage on handles and
hardened doubles (138 tests). Rerun after purging stale host modules: all 12
launch/inspect/close pass, host alive, fonts unchanged. Interactions pass:
signal-lifetime counts and relaunch reset, glyph-list filters, owned key filter
logs without consuming, spin/slider sync without recursion, callback errors keep
value, sandbox settings persist Unicode and reset. glyph-properties toggle not
yet exercised (pending). Receipts: parent evidence/i103-insights/.


## 2026-10-14: Insight ranks 13–18

Read the committed first batch (b1e2bf7), README/PLAN/work history, ranked guide,
handle/owned helper, Designer port, manifests and hardened doubles. Baseline gate:
138 passed. Reviewed official PythonQt decorator/ownership documentation and Qt
5.15 QUiLoader, QUndoStack, QUndoCommand and QMetaObject contracts before coding.
No framework/dependency added: stdlib queue/threading and compile/eval/exec plus
FontLab's existing Qt are sufficient. No reference code/resources copied.

Added six original Apache-2.0 examples, ranks 13–18: loaded-glyph-form,
worker-glyph-queue, owned-repl, plugin-tokens, metrics-undo,
compiled-slot-exposure. Each has inspectable state and documented controls on
ExampleHandle, no attributes on native widgets, no QApplication/exec loop,
no changes to fonts/preferences/Output, and native acceptance unexecuted.
Preserved all rank 1–12 manifest records and native evidence unchanged.

The original QUiLoader form has no implicit XML connections, owned parenting,
named-field discovery and QFile/loader finally cleanup. Worker Start is deferred
until click; one cancellable Python-only worker emits bounded plain-data results,
GUI timer drains them, and stop/completion/error join before UI cleanup. The console
has isolated sample globals and owned print/error output; it touches no global
stdout/display hooks. It is a short-command example, not a security sandbox.

Plug-in tokens allocate/detach menus/actions only on an owned QMainWindow.
Repeated install/unload is idempotent; the exact bound signal object is retained
and ExampleHandle.disconnect removes its tracked pair before menu deletion.
Disconnection failure leaves tokens live and prevents deletion. Menu owns action.
The undo stack operates on a Python advance dict; native command overrides change
only data, indexChanged updates owned UI, and stack.clear follows disconnection.
Python command receivers remain retained while Qt owns them; no manual command
delete. Compiled exposure calls existing compiled constructors/non-slot move(QPoint)
and native clear(), with metaobject slot discovery and clear missing-class errors;
no new native extension is compiled or registered in the host.

Wait, but doubles cannot prove native QUndoCommand shell dispatch/ownership or
compiled metaobject exposure. Those checks and complete controls-key contracts
are recorded in docs/insights-second-batch.md and catalog/insights.json for the
controller. Native acceptance is not inferred from tests. Existing glyph-properties
now tests toggle to alternate and back to default, including visible label text.
README/CHANGELOG/ranked guide updated; PLAN/TODO, reference manifest and corpus
untouched. No commit or runtime dependency changes.

Tests first failed because ranks 13–18 were missing, then passed after code and
hardened form/menu/metaobject/undo doubles. Requested gate:
UV_CACHE_DIR=/tmp/fontlab-examples-uv UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
uv run --no-project --with pytest python -m pytest -q tests — 164 passed
(138 baseline + 26 new). Tests cover all six builds/controls/inspect/close,
resource SHA-256, load/constructor/controls failures, absent native classes/slots,
worker GUI delivery/cancel/error/join, console namespace/reset/output, token
idempotency/disconnect failures, undo/redo/branch deletion and compiled slot calls.
Scoped Ruff check/format and git diff --check pass; runtime sources parse with
Python 3.11 grammar. First-batch manifest objects remain equal to committed HEAD.
