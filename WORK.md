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

Native (controller): batch 2 all six launch/inspect/close pass after fixing QUndoStack.index (a method in PythonQt; double corrected). Interactions: undo/redo index 1/0/1, REPL executes in owned namespace, plugin tokens idempotent install/unload, glyph-properties toggles both ways. All 18 insights now native-passed.

## 2026-10-14: Removed PyQt Thread chat examples (owner decision D4)

The three pyqt/examples #11 chat ports and fontlab_python_examples/chat.py are removed: they messaged a third-party server (build-system.fman.io). Their source rows stay in the static catalog as unported upstream entries.


## 2026-10-14: Issue 101 — 23 official PythonQt ports (local handoff)

Implemented the exact requested 23 IDs on issue-101-pythonqt-examples; no commit
and no native FontLab run. Each entry uses build(qt) -> ExampleHandle, owned
controls, JSON inspection and the existing launcher. All 23 new manifest rows
remain native_acceptance=unexecuted; none is marked blocked based on the exported
host API inventory. Existing blocked rows and all 15 prior port records are
unchanged. PLAN.md, TODO.md, catalog/sources.json and pinned originals are
unchanged; no TODO items were ticked.

Read README/PLAN/TODO/work tail, licence history, source/port catalogs, existing
handle/launcher/editor/numbered ports/insights and tests before implementation.
Used the native echopy stubs and their Qt documentation to resolve class exports,
properties/methods, constructors and explicit native base handlers. Captured 105
native class member contracts for portable sealed doubles. qRegisterResourceData
is absent; no compiled rc or generated Python UI module is shipped/executed.
The two original stylesheet XML forms are loaded with QUiLoader. No QThread,
QApplication construction, app/modal exec loop, sys.exit or new Qt binding.
No runtime dependencies were added.

Added fontlab_python_examples/official.py as a per-build ownership adapter around
ExampleHandle, with exact tracked old-style signal pairs, callback argument
routing, asynchronous dialogs, isolated INI settings, dynamic editor/action
forget/disconnect, rollback and reference release before native deletion. Native
objects never receive Python-only attributes; Python subclasses retain source UI
logic. File/clipboard actions remain explicit. Inspection is passive. Resources
are exact copies with per-file source identities/hashes in the manifest.

Licensing evidence differs from the requested shorthand: these actual source
headers grant BSD-3-Clause, while the pinned collection README and LICENSE say
GPLv3. Every original source notice is retained verbatim, including stylesheet
companion/generated-UI notices. The GPL text and eight distinct source notices
are in ports/pyqt-official-LICENSE.md. Metadata conservatively records
BSD-3-Clause AND GPL-3.0-only with review_state=unresolved; this does not relicense
the sources or infer individual resource grants. Reconciliation is an open
licence-review question, not a native API blocker.

Wait, but passing doubles cannot establish native rendering, overload conversion,
PythonQt virtual dispatch, codec plug-ins or safe native destruction. Review also
found and fixed stale temporary translator controls, duplicate MDI document
connections, concurrent Close All prompts, transient delegate-editor callbacks,
exact-completion duplication and loader-constructor cleanup. Regression tests
failed before their respective fixes and pass afterward. The MNG codec still
requires an actual native playback decision. No local test is claimed as native
acceptance or wheel-installation evidence.

### Local verification commands and results

Shell commands ran through `rtk proxy`; the writable temporary uv cache keeps the
requested offline gate independent of the denied default cache. Baseline: 155
passed. Final: **215 passed in 3.32s (155 existing + 60 new)**, no skips/failures.
Coverage includes all 23 builds/inspect/controls/close, resource/provenance,
existing blocked reasons, wizard file output, async dialogs and editor saves,
chunked search/cancellation, MDI dynamic actions and sequential cancel, codecs,
completion, settings isolation/types, transient editor disconnection, painter
finally cleanup, failed construction and missing native classes.

```sh
UV_CACHE_DIR=/tmp/fontlab-examples-uv UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
UV_CACHE_DIR=/tmp/fontlab-examples-uv UV_OFFLINE=1 uv run --no-project --with ruff ruff check fontlab_python_examples/official.py ports/*/pyqt-official/*.py tests/test_official_batch.py tests/official_doubles.py tests/test_second_batch.py tests/test_ports.py
UV_CACHE_DIR=/tmp/fontlab-examples-uv UV_OFFLINE=1 uv run --no-project --with ruff ruff format --check fontlab_python_examples/official.py ports/*/pyqt-official/*.py tests/test_official_batch.py tests/official_doubles.py tests/test_second_batch.py tests/test_ports.py
git diff --check
```

Ruff check passes; format reports 28 files already formatted. All 28 changed
Python files (including all 23 ports) parse with ast.parse(feature_version=(3,11))
and have matching this_file headers. SHA-256 audit against the pinned verification
root passes for all 23 original entrypoints and all 107 source/copied-resource
pairs. The static source-catalog hash matches; all 15 pre-existing port objects
compare equal with git show HEAD:catalog/ports.json. Native stubs are not shipped;
the portable contract contains member kinds and stub hashes only. Diff whitespace
check passes. README has all 23 launch rows and remains under 200 lines.

### Native acceptance handoff — all checks pending

The complete controller guide is docs/pyqt-official-batch.md. Its current common
checks and every per-port adaptation/check are repeated below for this work log.
The orchestrator runs FontLab acceptance, records evidence and commits; this
worker has done neither.

1. Launch from a clean source checkout in FontLab 9.0.9780. Record Python/Qt
   versions, screenshot, title, inspect JSON, resource rendering and console
   exceptions. Repeated launch must reshow the same owned root.
2. Drive the controls below with native signals, clicks, key events and resizing;
   use temporary files for every read/write exercise. Inspection itself must
   leave files, clipboard, FontLab settings, fonts and global Qt styles unchanged.
3. Exercise native X/hide/reshow, then named close while a dialog, completion
   popup, movie, search or settings timer is active where applicable. Track
   QObject destruction, including dynamically created windows, actions and
   dialogs. All connections must disconnect before any `deleteLater`; process
   the host's event loop externally after close. Confirm no callback exceptions,
   no surviving owned UI/timers and FontLab still responsive. Repeat close, then
   relaunch and confirm fresh state. Never run a nested event loop in the port.
4. Verify that fonts, host windows, preferences, translators and global styles
   match the baseline. Clipboard changes are intentional only after explicitly
   driving Cut/Copy/Paste; restore the controller's clipboard fixture afterward.
5. Mark each manifest row passed only after retaining native evidence. If a
   required native wrapper/codec/virtual dispatch fails, record the precise API
   and block that row; doubles are not native acceptance.

### Per-port adaptations and checks

#### classwizard

`035f3fbd2b81479a` — `ports/dialogs/pyqt-official/classwizard-035f3fbd2b81479a.py`.
Five original wizard pages, fields and generated C++ skeletons retained. PNGs
load from files; output defaults to a temporary directory owned by the example.
Finish uses UTF-8 file writes and an asynchronous owned error message.

Native: confirm five `page_ids`, initial title `Class Wizard`, mandatory class
name prevents Next; enter `Sample`, toggle QObject/QWidget/default/copy
constructors, comments, include guard and base include. Navigate Back/Next to
exercise native `initializePage` dispatch and field registration. On Output
Files select a controller-owned temporary directory; Finish must produce the
selected `.h`/`.cpp` content. Missing output directory must show an owned error
without closing the wizard. Check all banner/logo/watermark images.

#### configdialog

`3f5f77c0358d9fef` — original three-page configuration dialog and three PNG icons.
No update/network implementation is added: upstream Start Update/Query buttons
are illustrative and unconnected.

Native: `contentsWidget.setCurrentRow(0/1/2)` must show Configuration/Update/Query
and change `current_page`; `page_count` is 3. Check five servers, three packages,
date/query controls, query spinbox 1–100, icons and Close.

#### extension

`a1c26dbf9f995edb` — original optional search extension and fixed-size layout;
vertical button-box orientation is explicit. Associated rc files are not runtime
dependencies of this source and are not copied.

Native: title `Extension`; `moreButton.click()` reveals `extension` and enlarges
the dialog; second click hides it and restores size. Check all five checkboxes,
Find field and default button. Upstream Find has no search callback.

#### findfiles

`63f2eeefd052f701` — asynchronous directory selection; GUI timer scans 64 KiB
chunks with cross-chunk text matching and a cancellable progress window. Starts
in an owned sample directory. No QApplication.processEvents/reentrant loop.

Native: choose a temporary directory containing two `.txt` files and a symlink;
set `fileComboBox` to `*.txt`, `textComboBox` to a unique Unicode substring, click
`findButton`. Expect exactly the matching non-symlink filename and size in
`filesTable`, `results`, `row_count`. Repeat with empty pattern/text; cancel a
large-file search through `progress`, check `searching` false and closed stream.
Missing directory reports `error`. Browse cancel preserves selection. Double
click opens a file only when deliberately driven; URL uses `fromLocalFile`.

#### standarddialogs

`e1a0a829f8f2e311` — all 15 original dialog buttons retained; input/color/font/file
and message choices use instances, open and callbacks, including custom warning
buttons. Native file-dialog option remains selectable.

Native: integer 42 → `integerLabel` `42%`; double 12.5 → `$12.5`; season Winter;
Unicode user name; color swatch/text and selected font update after acceptance.
Cancel each and verify previous labels. Test directory, one/multiple input files
and save-path selection (no file is written by this demo). Verify Abort/Retry/
Ignore, OK, Yes/No/Cancel and Save Again/Continue labels; Error Message suppression
checkbox still works. Close with each kind of child dialog open.

#### tabdialog

`dab5fd4c94ec518d` — original General/Permissions/Applications tabs inspect an
owned sample file instead of the process working directory. Permissions and
application associations remain illustrative, as upstream.

Native: 3 tabs, 30 application names, sample filename/path/size/timestamps and
permissions; select tabs and entries, toggle association checkbox; OK/Cancel
hide the dialog and named close releases the sample directory.

#### trivialwizard

`c0d4a173b261a3e5` — original three-page wizard, no QApplication.

Native: Introduction → Registration → Conclusion, Back and Finish/Cancel.
Check `page_ids` length 3, `current_id`, name/email editing and original text.
The original trivial wizard does not enforce required fields.

#### basiclayouts

`2f94fe07de765888` — original horizontal, grid and form groups and text editors.

Native: four buttons, three labelled grid rows, 3 form rows; edit both text
editors, resize and verify grid stretch and remaining-space behavior. OK,
Cancel and File/Exit affect only this dialog. Inspect original editor texts.

#### borderlayout

`f48955d43ed6196c` — original custom QLayout algorithm and item wrappers; native
base geometry calls are explicit. Negative item indexes now return None.

Native: six items (North, South, West, East 1, East 2, center). Resize root wide
and tall; verify `items` geometry and label positions, center fills remainder.
Exercise native virtual `count/itemAt/takeAt/sizeHint/setGeometry` dispatch;
track layout/item teardown as well as child widgets.

#### flowlayout

`675c9f79650d7507` — original flow layout; contentsMargins replaces unavailable
getContentsMargins and flag construction uses native integer enums.

Native: five original button texts. Resize narrow/wide; verify wrapping,
`heightForWidth`, spacing and `items` geometry. `item_count` stays 5; no missing
or double-deleted layout items during close/relaunch.

#### application

`7da7020aa7e2732b` — original menus, toolbars, status and editor; UTF-8 I/O,
asynchronous file/unsaved-change prompts; geometry settings use an owned INI.

Native: New/Open/Save/Save As using Unicode fixture; change text, try New/Open/X,
exercise Save, Discard and Cancel (including cancelling the save file dialog).
Failed I/O preserves text and modified state. Check title, toolbar icons,
selection-based Cut/Copy enablement, clipboard actions and About. Inspect
`text`, `file`, `modified`; host windows/preferences remain unchanged.

#### mdi

`1415facde30a25cf` — original MDI actions and document classes; asynchronous close
sequence for root and Close All; child X closes its enclosing subwindow after
approval; no application-wide layout-direction change. Document-modified
signals connect once, and closed/failed documents are excluded from reopen lookup. Dynamic Window-menu
callbacks disconnect before their actions are removed/deleted. Hidden children
remain owned until named cleanup; no DeleteOnClose Python-slot hazard.

Native: create two documents; edit/save each, reopen an existing path and confirm
activation rather than duplication. Tile/Cascade/Next/Previous; Window menu
selects each document, and repeated rebuilding leaves no duplicate callbacks.
Close/Close All/root X must honor each Save/Discard/Cancel, prompting one document
at a time. Reopen a discarded document and confirm disk contents are loaded. Switch layout
direction affects only this window. Check `documents` and owned INI cleanup.

#### sdi

`eba98690c141a070` — original separate document windows; all retained by the same
handle. Exit closes only this example's windows. Asynchronous prompts and owned
INI settings; no enumeration or closure of host windows.

Native: New twice creates three independent windows; Open in empty versus
modified windows and reopen existing path. Save/Save As Unicode fixtures;
Cancel one unsaved close and ensure it stays open. Exit affects all owned SDI
windows while preserving FontLab. Named close destroys all retained windows and
clears the per-build window list; relaunch starts numbering afresh.

#### basicdrawing

`907f39d8bf387501` — all 13 original shapes, pen/brush modes, gradients, texture,
antialiasing and transformations. Explicit QColor/brush constructor types;
QPainter ends in finally; original logo/brick assets are files.

Native: render every `shapeComboBox` option; change width (including cosmetic
zero), style/cap/join, every brush including 3 gradients/texture, antialiasing and
transformations. Check `shape/antialiased/transformed`, resize repeated tiles,
text/logo appearance and absence of active-painter warnings on close.

#### codecs

`19571722ed96aa9c` — native QTextCodec list and original codec ranking; async file
selection and encoding preview; direct native codec conversion replaces stream
shift operators. Supplied sample encodings copied unchanged.

Native: use supplied UTF-8, UTF-16, UTF-16BE/LE and ISO samples, switch
`encodingComboBox`, cancel then accept preview; main `text` changes only on
accept. Save As menu hides codecs unable to encode the current text. Save and
reopen each supported encoding, compare Unicode text and output bytes; failed
I/O stays owned. Record `codec_count` and actual available codecs.

#### customcompleter

`10ef4dacb4db4080` — exact wordlist loaded with pathlib into QtGui.QStringListModel;
QString activation overload; replacing a completer disconnects its old slot;
explicit native QTextEdit key/focus handlers.

Native: verify `word_count`, type 3+ characters, Ctrl+E, arrows/Enter/Tab/Escape,
case-insensitive matches, completion inserted at the text cursor. Select an
exact match and a longer completion. Exercise focus changes and close while
popup is visible; Exit leaves FontLab open.

### i18n

`eca1cd9ef1528607` — 15 exact QM resources; translation is per-window through its
owned QTranslator, never installed globally. Original language chooser, colored
windows and close filter retained; integer grid coordinates corrected. Temporary
language-name translators are released without entering the controls registry;
`window` continues to name the root after language windows open.

Native: 15 checkboxes; Show All/Hide All, individual toggles and X synchronize
window visibility and checks. Verify at least English, German and Arabic text
and RTL layout against the selected QM; host UI language/direction must not
change. Inspect `languages/windows`; close removes all event filters and children.

#### regexp

`626fd0acec74fd91` — original QRegExp syntax/case/minimal/capture controls. Fixed
discarded string.replace results in the escaped-pattern display.

Native: `(A)(\d+)` against `xxA123yy` → index 2, length 4, captures A123/A/123;
check escaped backslashes/quotes, invalid pattern coloring, case toggle,
minimal matching, wildcard and fixed-string modes. Six capture edits stay
read-only; refresh signals must not produce argument-count exceptions.

#### settingseditor

`9e41e71c41b116a8` — original tree, type delegate, location dialog and refresh
controls. Every application/scope preview uses owned temporary INIs; selected
INI/plist files are copied/imported. Fallbacks remain disabled. Windows registry
access is explicitly unavailable on this macOS host. Fixed false-string boolean
conversion and accommodated native validator result shapes. Timer is parented;
transient delegate editors leave controls before native destruction.

Native: Open Application Settings location dialog (Native/INI, User/System,
organization/application) must list only owned temp paths. Open copies of the
supplied INIs, edit bool/int/string/list/date/color/point/size values, verify type
and invalid-input rejection; original files stay byte-identical. Test plist
copy, Refresh and Auto-Refresh, no duplicate itemChanged callbacks. Close with
timer and location dialog open; verify owned INI directory removed.

#### icons

`505d60a757bbc177` — original 8-cell mode/state preview, image table, persistent
editors, inferred modes and size/style choices. Style changes visit only owned
widgets; explicit QTableWidgetItem signal signature; previewSize avoids native
QWidget.size name collision. Asynchronous multi-file chooser; delegate editor
callbacks disconnect before destroyEditor, and transient items are not retained
as controls.

Native: add supplied monkey on/off and find normal/disabled images, verify
inferred mode/state and each preview cell, toggle rows, edit delegate combos,
change 8–128 custom size and every standard metric size; Remove All empties
preview. Switch styles without changing FontLab. Close while persistent editors
are active; `image_count`, `preview_cells` and `icon_size` remain accurate.

#### movie

`a3b3cbe51c1506c6` — original animated-image player with async chooser, frame/speed/
fit/play/pause/stop. Frame slider blocks feedback while following the movie;
stop precedes callback disconnection and deletion. Original MNG copied unchanged.

Native: inspect supported `formats`, explicitly open supplied animation.mng;
verify `valid`, frame changes/count, Pause/Resume/Stop, frame seek, speed 1–9999%,
Fit to Window and resize. Unsupported MNG/plugin behavior must be recorded as a
capability blocker, not a successful playback. Closing during playback leaves
no frame callbacks or movie activity.

#### stylesheet

`876eab33b6a99e31` — exact original two UI XML files loaded by QUiLoader; explicit
tracked wiring replaces generated Python UI/autoconnect and pyqtSlot. Coffee,
Pagefold and Default QSS/images retained. Resource URLs rewrite only in memory;
style and QSS apply only to the owned root/editor, never QApplication. QFile and
QUiLoader cleanup also covers loader-constructor failure.

Native: original sample form/control texts, Coffee initial rendering; open
editor, select all three sheets and styles, edit CSS and Apply, save a temporary
QSS and compare text. Check all image-backed widget states and form interactions;
`sheet/applied/editor_visible` update. Cancel save, close root while editor open;
no global style changes or retained editor window.

#### tooltips

`e62ce3eb648cfb4c` — original shape paths, hit testing, dragging, tooltips and three
creation buttons; integer QPoint coordinates and small-window random bounds;
explicit native event delegation and painter finally cleanup.

Native: initially Circle/Square/Triangle; create each type, hover correct tooltip,
drag overlapping shapes and verify topmost hit testing, release then drag again.
Resize small/large; buttons remain positioned. `shapes` records tooltips and
positions; close during hover/drag without painter or callback warnings.


## 2026-10-14: Issue 101 — native failure regressions and corrective handoff

Controller findings from FontLab 9 launch -> inspect -> close: only Official
trivialwizard and Official stylesheet passed the prior version. Tooltips crashed
FontLab in PythonQtInstanceWrapper_negative/PyObjGetString: negating any wrapped
Qt value, including -QPoint(1, 2), is unsafe. Nineteen ports failed close because
release enumerated the synthetic PythonQt __dict__ and assigned None to native
QRect geometry. Extension and i18n rejected native constructor keyword arguments;
icons also surfaced the geometry/None failure during launch cleanup. Movie
inspection could not convert a native QByteArray with bytes(). These findings
supersede the previous local-only 215-test result; no native success is inferred
from that result or from the new doubles.

Reproduced the reported boundaries in doubles before changing production code:
52 of the existing 60 official tests failed, 8 passed. Native properties now
appear in the double's __dict__ and reject None on both native and subclass
instances; native constructors reject unproven keywords; wrapped value arithmetic
raises TypeError instead of pretending it is safe; QByteArray is opaque and only
its data() method returns bytes. This exposed the same geometry, kwargs,
negation/arithmetic and byte-conversion errors without crashing FontLab.

Fixed the ownership boundary by replacing __dict__ scanning with explicitly
listed Python reference fields at demo.track calls. Thirty Python subclasses
have named field lists; subclasses with no custom fields have empty lists.
Release clears only declared lists/dicts and custom object references. It leaves
all native properties and undeclared Python fields intact, disconnects first and
then follows the existing ExampleHandle/OwnedWidget delete sequence. Partially
constructed fields may be absent; inherited native methods remain untouched
until a Python field has actually shadowed them. Rollback preserves the original exception,
including icons constructor failures. Lists stay empty for native layout virtual
calls during teardown; timers are stopped by existing cleanup before release.

Audited every arithmetic expression in all 23 ports plus official.py: 332
binary/augmented operations after correction, with no remaining arithmetic on
QPoint/QPointF/QSize/QRect wrappers. Five unsafe sites were removed: one unary
QPoint negation, three point addition/subtraction sites in tooltips, and one QSize
addition in flowlayout. Tooltips now uses QPainter.save/restore and explicit
coordinate arithmetic; flowlayout constructs QSize from numeric components.
The AST guard permits unary +/- only on int/float literals (18 remaining sites),
with no name/call exceptions. Two safe-but-nonliteral negative slice expressions
were rewritten as nonnegative index calculations to keep that guard strict.

The complete constructor-keyword audit found two native sites. Extension now
constructs QDialogButtonBox() and calls setOrientation(Qt.Vertical). I18n uses
QDialog.__init__(self, parent), then setWindowFlags(Qt.Dialog |
Qt.WindowStaysOnTopHint). All native constructor calls in the batch/helper are
keyword-free. The native stubs expose setOrientation, setWindowFlags, painter
save/restore and QByteArray.data. Their generic __init__(*args, **kwargs) entries
are not proof of native keyword support; using simple positional construction
and separate setters avoids that unsupported inference. QByteArray.data() returning
bytes is supplied by the controller's actual PythonQt observation. Movie format
names and codec names now decode data() as ASCII, codec export writes data()
bytes, and the settings delegate decodes byte-array values as Latin-1.

### Per-port changes

| Port | Correction / audit result |
| --- | --- |
| classwizard | Declare only port-created page fields for release; native geometry is untouched. |
| configdialog | Declare the Python-owned page and list references for release. |
| extension | Use default QDialogButtonBox construction followed by setOrientation(Qt.Vertical); shared cleanup leaves native properties untouched. |
| findfiles | Declare all Python-owned UI/search state, including externally assigned timer/progress fields; use a nonnegative overlap slice instead of unary minus. |
| standarddialogs | Declare Python-owned labels/buttons/dialog references for release. |
| tabdialog | Shared release no longer enumerates synthetic native dictionaries; subclasses with no Python fields require no field cleanup. |
| trivialwizard | Audited; no port-source change needed. Controller reported the prior version passed launch/inspect/close. |
| basiclayouts | Declare Python-owned group/menu/editor references for release. |
| borderlayout | Release only the declared Python item list, keeping it empty for native virtual teardown. |
| flowlayout | Compute minimum QSize from numeric width/height components instead of wrapper addition; release only itemList. |
| application | Declare Python-owned editor/action/menu references for release. |
| mdi | Declare Python-owned subwindow/menu/document references, including _subwindow and _windowActions. |
| sdi | Declare Python-owned editor/action/menu references for release. |
| basicdrawing | Declare Python-owned painter values and controls for release. |
| codecs | Decode native codec-name QByteArray.data() as ASCII and write encoded QByteArray.data() bytes; declare Python-owned UI/codec references. |
| customcompleter | Declare completer/editor references for release; use a nonnegative suffix slice instead of unary minus. |
| i18n | Use positional parent-only QDialog construction and setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint); declare translator/window-map references. |
| regexp | Declare Python-owned capture/control references for release. |
| settingseditor | Declare Python-owned tree/delegate/dialog references; decode QByteArray.data() as Latin-1 for lossless byte editing. |
| icons | Declare Python-owned preview/table/action references; rollback no longer masks construction errors with a geometry=None error. |
| movie | Decode supported-format QByteArray.data() bytes as ASCII; declare Python-owned movie/control references. |
| stylesheet | Audited; no port-source change needed. Controller reported the prior version passed launch/inspect/close. |
| tooltips | Use QPainter.save/restore instead of unary QPoint negation; use coordinate arithmetic for hit testing and dragging; declare Python-owned shape/control references. |

### Regression tests and gates

Added 16 tests in tests/test_official_native_regressions.py, plus the icons case
in the existing partial-build rollback test: **17 new tests**. They cover the
AST unary guard, keyword-constructor guard, completeness/native-property
exclusion of release fields, six wrapper arithmetic operators on four value
types, null-property rejection, two keyword-rejecting constructors, native and
undeclared attribute preservation before deletion, tooltip paint/hit/drag
coordinates, flow minimum sizing, opaque QByteArray conversion, movie formats,
Unicode codec export and Latin-1 settings bytes. The existing per-port build,
inspect, controls, disconnect and close tests now use these stricter doubles.

Final requested gate (through rtk proxy; writable cache, offline, plugins off):

```sh
UV_CACHE_DIR=/tmp/fontlab-examples-uv UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
UV_CACHE_DIR=/tmp/fontlab-examples-uv UV_OFFLINE=1 uv run --no-project --with ruff ruff check fontlab_python_examples/official.py ports/*/pyqt-official/*.py tests/test_official_batch.py tests/official_doubles.py tests/test_official_native_regressions.py tests/test_second_batch.py tests/test_ports.py
UV_CACHE_DIR=/tmp/fontlab-examples-uv UV_OFFLINE=1 uv run --no-project --with ruff ruff format --check fontlab_python_examples/official.py ports/*/pyqt-official/*.py tests/test_official_batch.py tests/official_doubles.py tests/test_official_native_regressions.py tests/test_second_batch.py tests/test_ports.py
git diff --check
```

Results: **232 passed in 3.30s**, no failures/skips (215 previous + 17 regressions;
77 official-port tests total). Ruff check passes, 29 files already formatted;
29 Python files parse with Python 3.11 grammar, including all 23 ports. Source
SHA-256 verification passes for 23 original entrypoints and 107 copied-resource
pairs; all 15 prior manifest records and the source catalog hash remain unchanged.
Diff whitespace check passes. PLAN.md/TODO.md, originals and resources are
unchanged. No commit; still on issue-101-pythonqt-examples.

Wait, but this is a local corrective handoff, not another FontLab acceptance
run. Current manifest native states remain unexecuted for the revised batch;
the controller's prior two successes and failures are documented above. Rerun
all 23 launch/inspect/close checks, repeatedly paint/drag/resize tooltips, query
flow minimum size, launch extension/i18n/icons, inspect movie formats, export
Unicode through codecs and close with active dialogs/timers. Capture any original
icons launch exception now that rollback cannot mask it with geometry=None.
Licence review stays unresolved exactly as before: original BSD-3-Clause headers
and GPLv3 collection terms are retained without resolving their scope.


## 2026-10-14: Native slot-shadowing correction

Controller rerun passed launch/inspect/close for 22/23 ports; icons failed on
assignment to native QMainWindow.centralWidget. Stub grep audit of all 23 ports
and official.py (45 native subclasses, 303 self-attribute writes) found the same
collision in i18n's lazy language windows and no others. Both Python fields are
now _central_widget; native setCentralWidget()/centralWidget() remain intact,
including the existing centralWidget controls key and explicit reference release.

Doubles now reject assignment to every captured native method/slot, including
inherited methods. Complete method names for 105 existing contract classes were
extracted with rg; no stub was read wholesale for the audit. Before the fixes,
7 existing tests failed and the new AST check identified both collisions.
Three added tests cover AST/release/external assignments and native/inherited
slot rejection; interaction checks verify both real getter paths. Two old tests
now patch Python subclass methods at class level instead of illegally shadowing
native methods on instances.

Same offline pytest command as above: **235 passed in 3.58s** (3 new; 80 official
port tests). Scoped Ruff check/format passes for 30 files; Python 3.11 grammar
passes for all 30; git diff --check passes. Source/resource hashes and the 15 prior
manifest entries remain unchanged. No commit; PLAN/TODO untouched. Native rerun
of icons and i18n Show All remains pending. Licence scope remains unresolved.

## 2026-10-14: Controller native acceptance of the pyqt-official batch (23 ports)

Driver: parent `verification/issue-101-ecosystem/evidence/examples-batch3/accept_incremental.py`
(per-port launch → inspect → close, results flushed per port). First run (17:03, owner's
FontLab) and second run: tooltips segfaulted FontLab via unary minus on a QPoint
(PythonQt defect, filed Fontlab/fl#8479); 19 ports failed close (None assigned to native
`geometry`), extension/i18n rejected constructor keywords, movie failed QByteArray→bytes.
After two Codex fix rounds (cleanup only releases declared Python refs; no wrapper
arithmetic; positional constructors; QByteArray `.data()`; no native-slot shadowing):
**23/23 pass launch/inspect/close, host alive after each** (`native-fix2.jsonl`).
Offline gate: 235 passed. Catalog `native_acceptance` stays "unexecuted" until
per-port interactions (docs/pyqt-official-batch.md) are exercised; licence scope
(BSD-3-Clause headers vs collection GPLv3) remains open.


## 2026-10-14: Batch 4 — 18 official PythonQt ports

Implemented all 18 requested source IDs on issue-101-pythonqt-examples. No commit
and no native FontLab invocation; native_acceptance remains unexecuted for every
new row. Reused Demo, ExampleHandle, tests/test_official_batch.py,
tests/official_doubles.py, the captured native contract and the existing official
acceptance document. Added 15 byte-identical resources; no *_rc.py or generated
ui_mainwindow.py is shipped or executed. No packages added. All 38 previous port
records, PLAN.md, TODO.md and catalog/sources.json are unchanged.

Read the original source/header/resource files and host QtCore/QtGui/private
stubs before adapting APIs. The source headers grant BSD-3-Clause, including the
Jansen/Qt Company variants; the collection supplies GPLv3. Each new port and
manifest entry retains its actual notice with BSD-3-Clause AND GPL-3.0-only and
review_state unresolved. Expanded the existing official-source notice instead
of creating another licence document. Exact overloads, native virtual dispatch
and licence-scope reconciliation remain open for the controller.

Shared adaptations: all UI uses injected QtGui/QtCore, tracked connections,
explicit base event handlers and declared Python-only release fields. Stream
shifts become QBuffer/QDataStream QVariant calls with QByteArray.data(); custom
MIME names distinguish this encoding from upstream. Native QDrag.exec is invoked
only from Demo.drag, using the documented macOS operation that keeps the host
loop responsive; there are no QApplication/modal-dialog exec calls. Named close
fails before deletion during a drag and the cleanup guard remains queued for
retry. A regression caught that model detachment could emit selection callbacks
before disconnection: views now detach in the release phase, after disconnect
and before clearing Python model fields. Timers stop first; painters end in
finally; all positions use numerical components. Colour/brush constructors use
explicit native types. Address-book directories exist before inspection, only
owned paths are accepted, and load validates a plain string dictionary without
allowing pickle global/class construction.

### Commands and verification

Baseline: requested offline pytest command initially could not write the default
uv cache; using the existing writable temporary cache resolved this. Baseline
**235 passed in 3.54s**. The expanded exact-batch manifest test failed first with
18 missing IDs. Interaction tests then exposed incomplete double contracts and
verified fixes for invalid drag data, empty Find, model bounds, native properties,
active-drag close retries and disconnect-before-model-detach ordering. One
intermediate full run read the manifest during its rewrite (304 tests passed,
one teardown JSON-read error); final gates run after all source/manifest edits.
A whitespace check caught and removed one blank line at the licence file's EOF.

Commands (executed through rtk proxy):

```sh
UV_CACHE_DIR=/private/tmp/fontlab-examples-uv UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
UV_CACHE_DIR=/private/tmp/fontlab-examples-uv UV_OFFLINE=1 uv run --no-project --with ruff ruff check fontlab_python_examples/official.py fontlab_python_examples/handle.py ports/{draganddrop,effects,itemviews,tutorials}/pyqt-official/*.py tests/test_official_batch.py tests/official_doubles.py tests/test_official_native_regressions.py tests/test_official_slot_shadowing.py
UV_CACHE_DIR=/private/tmp/fontlab-examples-uv UV_OFFLINE=1 uv run --no-project --with ruff ruff format --check fontlab_python_examples/official.py fontlab_python_examples/handle.py ports/{draganddrop,effects,itemviews,tutorials}/pyqt-official/*.py tests/test_official_batch.py tests/official_doubles.py tests/test_official_native_regressions.py tests/test_official_slot_shadowing.py
git diff --check
```

Additional direct Python verification uses ast.parse(feature_version=(3, 11))
for the 24 changed Python files, compares SHA-256/Git-blob SHA/byte length for all
18 upstream entrypoints and 15 resource pairs, checks every original_notices
string against a reviewed original, verifies all 38 prior manifest records, and
compares PLAN/TODO/source catalog to HEAD. The captured contract matches hashes
of the three current host stub modules. No private paths are added to public
metadata; no fixture or double result is treated as native acceptance.

Final gates after the teardown-order correction: **305 passed in 4.68s**, zero
failures/errors/skips (**70 added** over baseline). Scoped Ruff check passes;
**24 files already formatted**; all **24 changed Python files parse with Python
3.11 grammar**. Verified **18 source entrypoints**, **15 byte-identical resource
pairs**, exact notice provenance and **38 unchanged prior manifest records**.
All three captured host-stub hashes match. git diff --check passes. README has
197 lines with balanced code fences. Branch remains issue-101-pythonqt-examples;
no commit. Pre-existing untracked .DS_Store and .omc/ remain untouched.

### Per-port adaptations and native acceptance checklist

For EVERY row: launch by ID, record actual versions/title/inspect JSON/screenshot,
reshow the same root, exercise the checks below, close via native X then named
close, process host events externally and record destruction of all owned UI,
models, actions, timers and dialogs. Finish/cancel any drag before named close;
verify an attempted active-drag close raises safely and succeeds on retry.
Repeat close and relaunch. FontLab, fonts, clipboard, preferences, global styles
and unrelated windows must remain unchanged. Mark passed only with retained
native interaction and teardown evidence. See the shared document for runnable
launcher calls and all control names.

- **5781fa4ba55c884f — Draggable icons** (`ports/draganddrop/pyqt-official/draggableicons-5781fa4ba55c884f.py`): Two original icon panels and three PNGs retained. QDataStream shift operators become explicit QVariant serialization through an owned QBuffer; MIME is application/x-fontlab-dnditemdata. Numeric hotspot subtraction replaces QPoint arithmetic. Moved labels hide until owned teardown; painters end in finally.

  Native: Expect title Draggable Icons and 3 visible icons in each of controls left/right. Natively drag boat/car/house between panels: default Copy keeps the source; Move hides it; Escape restores its original pixmap. Drag within a panel, confirm hotspot and inspect panels coordinates. Reject unrelated MIME; repeatedly copy/move and close after cancelling an active drag.

- **700e96dec485e7a8 — Draggable text** (`ports/draganddrop/pyqt-official/draggabletext-700e96dec485e7a8.py`): Exact 41-word file replaces compiled resources/QTextStream. Plain text and ASCII hotspot bytes use QByteArray.data(); invalid hotspots fall back to zero. All positions use components; Python label subclasses and native drag sources remain owned.

  Native: Expect Draggable Text, label_count 41, first word Qt. Use controls board.children() to drag a real label internally (Move) and between two separately owned port instances (Copy); drop external Unicode multiword text. Inspect labels text/positions/visibility. Escape keeps the source; malformed hotspot bytes do not raise. Close/relaunch restores 41 words.

- **da76600eaea7a121 — Fridge magnets** (`ports/draganddrop/pyqt-official/fridgemagnets-da76600eaea7a121.py`): Exact 48-word file, rounded painted magnet labels and external plain-text drop retained. Native QVariant text/point payload replaces stream shifts under application/x-fontlab-fridgemagnet. Explicit brush/color types, integer transparent image fill, component offsets and guaranteed painter end.

  Native: Expect Fridge Magnets, label_count 48, first word Colorless. Check rounded label rendering and transparency. Drag a magnet internally and copy it externally; cancel a hidden-source drag and confirm it reappears. Drop Unicode plain text and inspect individual words/coordinates. Reject malformed custom payload without losing the window.

- **c5b4e385cc921da4 — Drag-and-drop puzzle** (`ports/draganddrop/pyqt-official/puzzle-c5b4e385cc921da4.py`): Original QListWidget pieces and 5x5 board retained with the exact JPEG. Integer crops/grid coordinates, component hotspot arithmetic, local random.Random, corrected highlightedRect typo and native QVariant MIME. pyqtSignal becomes an owned single-shot completion timer; file and completion dialogs are asynchronous.

  Native: Expect Puzzle, piece_count 25, placed/in_place 0. Drive piecesList and puzzleWidget with native drag events: correct cell increments in_place; wrong cell does not; occupied cell rejects; drag back to list and Escape restore counts. Solve all 25: completion appears after drop returns and OK resets. Use restart/openImage, cancel chooser, reject bad image, and close with completion dialog open.

- **b823a76f79197d84 — Lighting** (`ports/effects/pyqt-official/lighting-b823a76f79197d84.py`): Original 25-item light/shadow scene and 30 ms GUI timer retained. Scene is parented; QPoint division becomes floating coordinate division, explicit QColor/QBrush overloads are used, timer stops before disconnect and painter ends in finally.

  Native: Expect Lighting and Shadows, 640x480, item_count 25, timer_active true. Let the native timer run; angle, light coordinates and 25 offsets must change while the halo and shadows render. Resize and pan/inspect scene. Close during animation, process events, and prove the timer and scene/effects are destroyed.

- **306c12d5cc1db46c — Chart** (`ports/itemviews/pyqt-official/chart-306c12d5cc1db46c.py`): Original custom PieView, legend, editable table, shared selection and both .cht files retained. Async file dialogs, UTF-8 CSV parsing before model replacement, numeric quantity validation and quoted CSV export replace Qt streams. Explicit base handlers, component geometry, QRegion.united and guaranteed painter end.

  Native: Expect Chart, 14 rows/2 columns, valid_items 14, total 188, first label Scientific Research. Edit quantities/labels in controls table/model; pie sectors and totals must follow, invalid/NaN quantities must not break painting. Select table cells and sectors/legend both ways; rubber-band, arrows, scrolling and resize must synchronize. openFile/writeFile round-trip Unicode/quoted labels in a controller temporary file; failed/cancelled load preserves data. Close with chooser or selection active.

- **227efef76ed4ac74 — Editable tree model** (`ports/itemviews/pyqt-official/editabletreemodel-227efef76ed4ac74.py`): Original hierarchy and generated form behavior retained; UI widgets/menus/shortcuts are explicitly reconstructed from the copied exact mainwindow.ui, without generated Python/autoconnect. UTF-8 default text, str.strip, integer QModelIndex IDs mapped to retained nodes, native dataChanged/headerDataChanged calls and bounds checks replace PyQt assumptions. View detaches before model-reference release.

  Native: Expect Editable Tree Model with 6 top-level rows and 2 columns. Compare against copied mainwindow.ui. Expand hierarchy, edit values, and drive insertChildAction/insertRowAction/insertColumnAction/removeRowAction/removeColumnAction at root and nested levels. Check [No data]/[No header], status position, action enablement and actual model notifications. Reject invalid ranges without mutation. Exercise remove-last-column then rebuild, and close during editing.

- **c98ae8ac71886586 — Frozen column** (`ports/itemviews/pyqt-official/frozencolumn-c98ae8ac71886586.py`): Exact grades.txt populates QStandardItemModel through pathlib. Original overlay and shared selection/scroll bars retained. Fix upstream self.logicalIndex/self.current typos; explicit native resize/moveCursor/scrollTo dispatch and tracked bidirectional signals.

  Native: Expect Frozen Column Example, 31 rows/10 columns. Scroll horizontally: green first column stays fixed; both vertical bars remain synchronized. Resize column 0 and rows via native headers, resize window and inspect frozen_geometry/frozen_width. Use Left-key navigation across the hidden boundary, select cells in both views, and close after scroll/resize.

- **090c76a87351e771 — Interview** (`ports/itemviews/pyqt-official/interview-090c76a87351e771.py`): Original lazy 1000x10 hierarchical model, three views, shared QItemSelectionModel, movable headers and both PNG icons retained. Numeric QModelIndex ID lookup replaces Python internal pointers; reject children under nonzero columns. Views detach before releasing model references.

  Native: Expect Interview, row_count 1000, column_count 10, first_item Item 0:0 and shared_selection true. Select through controls table/tree/listView and verify synchronized indexes and current item. Expand multiple lazy levels, move table headers, switch list selection and check folder/file/header icons. Close after repeated expansion without stale model callbacks.

- **878fe9f714df3b5e — Item-view puzzle** (`ports/itemviews/pyqt-official/puzzle-878fe9f714df3b5e.py`): Original QAbstractListModel/QListView variant and exact JPEG retained. Shared QVariant MIME with the drag-and-drop puzzle; integer coordinates, local RNG, timer completion and async dialogs. Correct removal inPlace arithmetic, highlightedRect typo, empty-model reset notifications and row bounds; detach view on cleanup. A QListView subclass routes startDrag through the tracked native drag boundary and removes source rows only after Move.

  Native: Expect 25 model pieces and an empty board. Exercise all puzzle checks above using native QListView/model drag/drop, including moving a correct piece away and cancelled drag rollback. Check model.mimeData/dropMimeData for multiple pieces and transfers to the other puzzle port. Restart repeatedly: exactly 25 rows, no invalid remove-row notifications. Solve/acknowledge and close while completion is pending.

- **321f8e535facafde — Simple tree model** (`ports/itemviews/pyqt-official/simpletreemodel-321f8e535facafde.py`): Exact default.txt parsed as UTF-8 with str.strip. Original TreeItem/TreeModel hierarchy retained; integer QModelIndex identity map replaces Python-object internalPointer, index bounds are checked and the view detaches before release.

  Native: Expect Simple Tree Model with 6 top-level rows and 2 columns Title/Summary. Expand every branch, verify original resource text and nested parent/index relationships. Resize columns, navigate by keyboard, select child rows and close while a deep branch is expanded. Relaunch must restore the original hierarchy.

- **e1f313d96e43adff — Address book part 1** (`ports/tutorials/pyqt-official/part1-e1f313d96e43adff.py`): Original editable Name and Address form only; no persistence or later-stage controls added. Native property reads and explicit Python-reference release.

  Native: Expect Simple Address Book; controls nameLine/addressText are editable and there is no Add button. Enter Unicode name and multiline literal <text>; inspect name/address exactly. Resize, hide/reshow and named close/relaunch: the new form is empty.

- **55bcde890cd77ed7 — Address book part 2** (`ports/tutorials/pyqt-official/part2-55bcde890cd77ed7.py`): Original add/submit/cancel stages and sorted contacts retained. Messages are owned asynchronous dialogs; addresses always use literal plain text.

  Native: Initially fields are read-only. Add enables editing; empty Submit opens Empty Field, a valid name/address increments contact_count, and a duplicate is rejected. Cancel restores old fields. Inspect contacts, button visibility and read-only state. Close with an information dialog open; relaunch has no contacts.

- **f4d9e2927469223c — Address book part 3** (`ports/tutorials/pyqt-official/part3-f4d9e2927469223c.py`): Part 2 adaptations plus original sorted Next/Previous navigation and wraparound; no later-stage edit/find/save controls.

  Native: Add Zoë, Ada and Łukasz; Next and Previous follow sorted names and wrap at each end. Check button enablement with 0, 1 and multiple contacts; Cancel retains selection. Confirm duplicate/empty handling and literal multiline addresses, then close/relaunch.

- **4d19e62d93dd761c — Address book part 4** (`ports/tutorials/pyqt-official/part4-4d19e62d93dd761c.py`): Original navigation/add/edit modes retained. Remove confirmation becomes an owned asynchronous Yes/No callback; rename collisions preserve both contacts and literal addresses are retained.

  Native: Add two contacts, Edit a name/address, reject a duplicate rename, and Cancel an edit. Remove/No keeps both; Remove/Yes selects the previous contact and reduces contact_count. Remove the last entry: empty read-only fields and appropriate disabled controls. Close with confirmation open and verify no later callback.

- **94ab271d023d1ca3 — Address book part 5** (`ports/tutorials/pyqt-official/part5-94ab271d023d1ca3.py`): Part 4 plus parented reusable FindDialog with one tracked accepted callback. Empty Find stays open instead of accepting stale text; missing-name notice is asynchronous. Preserve upstream Find enablement threshold (>2 contacts).

  Native: Add three contacts to enable findButton. Open Find: empty findSubmit keeps findDialog visible; findLine=Zoë selects its exact address; unknown name reports Contact Not Found. Cancel and repeated searches preserve state and never multiply callbacks. Close while Find or removal confirmation is open.

- **2719ebb336f3a29e — Address book part 6** (`ports/tutorials/pyqt-official/part6-2719ebb336f3a29e.py`): Part 5 plus asynchronous file choosers confined to a build-owned temporary directory. Pickle stores a plain string dictionary; load denies global/class construction and validates shape before replacing contacts. Outside/symlink paths are rejected; the sandbox exists before inspection and is removed on close.

  Native: Use inspect directory as the only save/load location. Save through saveButton, verify .abk bytes, edit contacts, then loadButton restores Unicode/literal addresses. Cancel dialogs, load empty/corrupt/wrong-shape data and try outside/symlink paths: errors preserve existing contacts and external files. Inspection writes nothing. Close removes the directory; relaunch creates an empty book/new directory.

- **bb1c114d38fb756a — Address book part 7** (`ports/tutorials/pyqt-official/part7-bb1c114d38fb756a.py`): Part 6 plus asynchronous vCard export confined to the same owned directory. UTF-8 pathlib output replaces QTextStream operators; retain vCard 2.1 layout, fix discarded address replace results and escape backslashes/semicolons.

  Native: Repeat part 6 checks. Select Zoë Example with a multiline address containing semicolon/comma/backslash; exportButton opens an owned chooser, acceptance writes the expected BEGIN/END, VERSION:2.1, N/FN and escaped ADR lines. Cancel writes nothing; external path is rejected. Close with chooser open, then confirm all export/pickle artifacts disappear with the owned directory.


Wait, but doubles cannot establish whether FontLab dispatches every protected
virtual, serializes pixmap/point QVariant values, renders each asset/effect, or
accepts every overload. Those are explicit checks above, not completed work.
No TODO items were ticked. Native execution and committing belong to the
orchestrator as requested.

## 2026-10-14: Controller native acceptance of pyqt-official batch 4 (18 ports)

Codex (no commit) ported 18 demos (itemviews, addressbook tutorial parts 1–7,
draganddrop, effects/lighting). Controller reran the offline gate: 305 passed.
Native launch/inspect/close (parent evidence/examples-batch4/, owner's FontLab with a
recovered document open, owner approved): 14/18 passed first; 4 failed importing
`pack_values` because FontLab still held batch 3's `fontlab_python_examples.official`
module. After purging the package modules (no live handles), the 4 reran and passed:
**18/18, host alive throughout**. Per-port interactions and licence scope pending.
