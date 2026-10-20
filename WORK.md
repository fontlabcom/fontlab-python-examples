---
this_file: WORK.md
---

# 2026-10-15: Independent clean-room receipt integration and native driver

Integrated the three merged batches on `issue-101-pythonqt-examples` at base
`db922a6`, without reading the private archive, original source trees or Git
history. `tools/integrate_cleanroom.py` validates exact 187-spec receipt coverage,
spec SHA-256, target/file paths and replacement headers, then uses the existing
catalogue projection/output tools on checked-in metadata only. It is repeatable
without original-tree acquisition. Reapplying resets replacement native states
and produces byte-identical ports.json, sources.json and INDEX.md.

- Clean-room results: **127 implemented, 60 blocked**, all with reviewed
  Apache-2.0 replacement grants, the exact spec hash and the requested review
  basis. Preserve archive/spec fields, immutable source provenance and all
  original resource records. Inventory projections use `port_license` for the
  new grant; they do not grant Apache-2.0 to archived original bytes/resources.
- Overall catalogue: **299 records, 148 implemented, 151 blocked, zero pending**.
  All 187 replacements/capability stubs are native **unexecuted**. Only the 21
  unchanged non-official implementations retain current native passes; earlier
  official-code receipts remain historical. All 1,569 original source identities
  and 465 Python-file identities remain in the inventory.
- Replace relocation absence assertions with receipt/state coverage. Retire tests
  tied to removed Python attributes, exact original fixtures and archived assets;
  retain the three independent spec-based batch suites, native-double/shared
  boundary regressions and unchanged non-official examples. Add public launcher
  coverage for all 187 records (including blocked host/builder rejection), receipt
  validation, deterministic integration and native-driver pure-part coverage.
  The previously missing-reference test passes in this checkout; it was not
  modified. No broad skip or failure suppression was added.
- Add executable `tools/native_cleanroom.py` (Python 3.11, external Remopy only).
  Client connection batches contain separate prepare/launch/inspect/close/verify/
  finish calls. Each phase restores sys.path and enforces a 3.5-second host
  budget with a four-second transport deadline. Purge stale example modules only
  without retained handles, put this checkout first, and assert the package and
  launcher import paths. Check visible top-level content, retained callback/model
  ownership, stopped timers/listeners/threads, destroyed owned QObjects, remaining
  windows/threads and removed owned temporary directories. Blocked launches must
  fail with their specific reason before host/builder access and without new
  windows, threads, descriptors or handles. Destruction witnesses retain plain
  state only and never touch a destroyed wrapper. Outputs include per-port JSONL,
  replacement hashes, phase timings and a summary of successes/failures/unknown
  outcomes and unrun IDs. Stop on uncertain execution or failed cleanup; never
  retry a timed-out launch or mark catalogue acceptance from this driver itself.
- Update README/INDEX/PLAN/TODO/CHANGELOG and dependency notes with current counts
  and the exact native command. Further native acceptance, interaction coverage,
  the 14 existing non-official resource grant gaps and docs-site integration remain.

Verification:

- Baseline required suite: **1 failed, 1,093 passed, 621 skipped**. The failure
  was the obsolete relocation absence assertion; the insight-reference fixture
  check passed here.
- Required final suite, with JUnit output outside the checkout:
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 UV_CACHE_DIR=/private/tmp/cleanroom-integration-uv
  uv run --no-project --with pytest python -m pytest -q tests
  --junitxml=/private/tmp/cleanroom-integration-final.xml`: exit 0,
  **1,485 passed, zero skipped**, 32.45 seconds.
- Native driver offline tests: **19 passed**, including connection errors,
  unknown outcomes/no launch retry, cleanup failure, deferred destruction,
  repeated prepare with retained state, sys.path restoration, module purge,
  batching and JSONL/summary generation with fake transports only.
- `python3 -m py_compile` passed all 14 changed/new Python files with
  `PYTHONPYCACHEPREFIX=/private/tmp/cleanroom-integration-pyc`.
- Scoped Ruff check/format passed; `git diff --check` passed. Metadata-only
  regeneration was byte-identical. Recipes, port sources, specs, implementation
  receipts and historical evidence were not modified; staging remains empty.

Native usage (not executed by this integration task):
`uv run --python 3.11 tools/native_cleanroom.py --batch-size 8
--output /private/tmp/fontlab-cleanroom-native.jsonl`.
Use `--ids id1 id2` or comma-separated IDs to select ports. The orchestrator runs
new native acceptance next. No FontLab call, git add or commit was made here.

# 2026-10-15: D7 public clean-room relocation

Removed the 431 unique files listed beneath `ports/` in the private archive's
committed manifest at `040b2e8`: 187 Python entrypoints, 243 resources and the
licence-notes file (the notice is already included in 431). Every public file
matched its committed SHA-256 before deletion. Checked remaining non-official
port/resource records, executable imports, exact file references and source-ID
references; none depended on a removed file. The legacy icon test now generates
an owned picture instead of opening its bundled icon. Catalogue-driven test
loading is guarded before file import; static audits exclude pending sources by
state. Absence assertions and archival metadata are not runtime dependencies.

Also removed 318 untracked compiled caches whose names match the archived source
identities, including four stale pre-move category paths. No original official
source/resource/cache directory remains. Checksums and paths are recorded in
`verification/clean-room-relocation.json`; no reference code was copied there.

All 187 port records retain exact source provenance and original target paths,
have `implementation: clean_room_pending`, reset current native acceptance,
drop removed-file licence/adaptation claims and point to the private archive
and public spec. Resource provenance and archive pointers remain. All 112
non-official port records are unchanged. Historical native receipts remain
historical, not current acceptance for removed ports. Inventory tools now apply
hash-bound port states, expose actual port paths alongside immutable planned
paths, and regenerate sources/INDEX and the source-catalogue hash together.

Copied exactly 187 Markdown specs and INDEX.json from committed private objects;
all 188 Git blob hashes match `040b2e8`. No original-reading checker/tests,
reference archive or private README was copied. The private repository was read
only. The independent implementation phase remains with another, unexposed worker.

Wait, but missing-file skips would hide broken replacements. Tests skip only
`clean_room_pending`, never file absence, and retain the collected cases; a state
change resumes source-loading tests. Shared helpers and non-official tests stay
active. New tests verify host-free rejection for every pending record, a guard
that resumes on state changes, hash-mismatch rejection, metadata-only handoff and
deterministic inventory CLI regeneration. No FontLab/native workflow was run.

Updated README, PLAN, TODO, CHANGELOG, dependency notes and the historical batch
notice. Preserved the existing 223-line ignore configuration and added only local
DS_Store/OMC exclusions; those existing artifacts were not deleted.

Verification (commands use the workspace `rtk proxy` wrapper):

- Baseline: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 UV_CACHE_DIR=/private/tmp/fontlab-uv-cache
  uv run --no-project --with pytest python -m pytest -q tests`: exit 0,
  **986 passed**.
- New tests first: the relocation-only file failed five cases before the
  launcher, state overlay and handoff existed; four synthetic cases passed after
  implementation, before deletion. Intermediate negative-existence and old
  static-state assertions failed as expected and were resolved.
- Full reviewed-source regeneration: `uv run --no-project python
  tools/inventory.py --tree-receipt
  ../verification/issue-101-ecosystem/evidence/examples-upstream-trees.json
  --recovery-receipt
  ../verification/issue-101-ecosystem/evidence/examples-source-recovery.json
  --source-root pyqt/examples=../verification/issue-101-ecosystem/examples-sources/pyqt--examples--83eed0514582c8deb60d9e9e6bff31ceffe4eaeb--verified
  --source-root eyllanesc/QtExamples=../verification/issue-101-ecosystem/examples-sources/eyllanesc--QtExamples--a01fd7d10d45801b10876f94c07aaefb11bc2e12--verified
  --reviews catalog/reviews.json --output catalog`: exit 0; 21 implemented,
  91 blocked and 187 clean-room pending, all 1,569 original identities retained.
- Requested full suite after changes: same command as baseline, exit 0,
  **451 passed, 621 skipped**. Scoped Ruff lint and format checks pass on all
  14 changed/new Python files; `git diff --check` passes.
- A later full run with `--junitxml=/private/tmp/clean-room-relocation-tests.xml`
  proved all 621 skipped cases cite `clean_room_pending`, without empty-parameter
  or unconditional relocation skips. It also collected newly appearing concurrent
  recipe work: **455 passed, 621 skipped, 1 failed** because that external work's
  test expected at least eight recipes while only one existed at collection.
  The recipe files/test were not created or edited by this task and are preserved.

No staging, commit, history rewrite or private-repository write was performed by this task.

# Work record

## 2026-10-15: Native catalog reconciliation, source roles and non-official licences

Baseline: **973 tests passed**. Added review/evidence tests first; the five initial
checks failed on absent receipts and unresolved catalog records before changes.

- Reconciled all **148 implemented** native records: 137 exact JSONL lines in
  parent evidence `examples-interactions/native-lic-final2.jsonl`, four first-batch
  records in `verification/first-native-batch.json` (preserving their stronger
  existing interaction/destruction receipt), and seven exact second-batch JSON
  records in parent evidence `tg4-second-batch/`. Each native pass cites file,
  SHA-256, line or JSON pointer, and launch/inspect/close selectors. A committed
  receipt keeps only the exact acceptance-field projections, avoiding private
  runtime paths and control contents. No new native execution or interaction,
  delayed-destruction, rendering or installed-distribution acceptance is claimed.
- Retained all **151 blocked** records as native unexecuted. Existing native
  tests that assumed later batches were unexecuted now check implementation
  state; the seven second-batch test subjects remain selected after acceptance.
- Reviewed **14 Python and 3 QML** candidates against source hashes and the
  recorded observations: two helpers, ten host plugins, one mathematical-plot
  Python launcher, one database initializer, two QML resources and one standalone
  QML entrypoint. Every reviewed record retains its original static classification,
  source mapping, reasoning and exact evidence references. Mathtext still requires
  matplotlib's PyQt/PySide backend; chapter6 still requires QML/plugin support.
  This metadata work does not implement either newly identified launcher.
- Resolved ownership of **69 shared files** at repository, collection,
  documentation or example scope. Assigned the fbs sibling project resources to
  its nested Python entrypoint and Quick's shared resources to animation/canvas;
  kept build/documentation membership distinct from proven runtime loads.
  `catalog/reviews.json` plus `inventory.py --reviews` makes the overlay repeatable
  and rejects missing reasoning/evidence or mismatched source hashes.
- Recorded **146 file licence/attribution reviews**: 112 non-pyqt-official port
  sources (including blocked records), 15 resources, and 19 original insight
  files. Exact pinned file/ancestor notices and source links are individually
  hashed. Removed the nonexistent nested fbs README from reviewed-file claims.
  Gallery 02 uses its explicit BSD exception under the root README's exception
  clause; its complete source notice remains intact. The numbered licence notice
  is synchronised with these decisions; no port source or resource bytes changed.
- **14 resource grants remain unresolved**: three logical copies of icon.svg,
  bullet.png and shot.wav in the numbered examples; styleexample's add.png,
  application.qss, blue.qss, khaki.qss, nature_1.jpg, nostyle.qss, remove.png,
  transparent.qss and stylewidget.ui. Existing source-code or collection notices
  do not establish an individual resource grant/creator attribution. Five inferred
  numbered-asset MIT selections were withdrawn rather than silently treated as
  evidence. No resource deletion or replacement was attempted.

Wait, but source review and old native receipts establish different facts. The
static catalog keeps runtime unexecuted; native passes live in the port manifest.
All **187 pyqt-official licence/resource records** compare equal to HEAD; their
licence decisions are left to the separate D7/clean-room work. All 1,569 original
source hashes and identities remain unchanged. Existing `.DS_Store` and `.omc/`
untracked entries predate this task and are preserved. No git add/commit.

Verification:

- Required full repository command: **986 passed** (973 baseline, 13 new tests),
  with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `UV_CACHE_DIR=/private/tmp/issue101-uv-cache`
  and `uv run --no-project --with pytest python -m pytest -q tests`.
- Final evidence/review test rerun: **13 passed**, including original evidence
  file hashes and exact records, missing-reason/evidence rejection, stale hashes,
  idempotence and preserved ambiguity for empty overlays. Both conditional
  workspace-original checks ran successfully; neither was skipped here.
- Inventory regeneration verified all **1,569** original files and reproduced
  `catalog/sources.json` and `catalog/INDEX.md` byte-for-byte.
- Scoped Ruff check and format check: all eight changed Python files pass.
- All 187 official records differ only in native fields. Every original source
  identity, hash, target and raw licence record matches HEAD. Protected trees
  differ only in the intended numbered-licence Markdown notice; no source edits.
- `git diff --check` passes; staging is empty. Final status contains the intended
  changes plus only the two pre-existing untracked entries noted above.

No added dependencies; only standard-library catalog processing and existing
pytest. Native interaction work, installed-distribution checks, documentation-site
integration and the unresolved grants remain separate follow-up work.

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


## 2026-10-14 — Official batch 5 (16 requested identities)

Direct single-agent source-checkout work on issue-101-pythonqt-examples; no
commit and no native FontLab run. Baseline: 305 tests passed. Initial offline
run with an empty writable UV cache could not resolve pytest; populated that
owned cache once with the network-enabled uv command, then used the exact
requested offline gate. Pre-existing DEPENDENCIES.md edits, .DS_Store and .omc/
were preserved. PLAN/TODO completion items remain unchanged.

Read README/PLAN/TODO, history/WORK tail, port manifest, handle/launcher/editor,
numbered/insight/official implementations and tests before changes. Reviewed
pinned originals and companion/generated UI sources; verified every selected
source/asset hash. The host-stub exported members and supplemental Qt 5.15
reference docs were checked before coding; consulted Qt’s official state,
property-animation, screen and system-tray documentation (the online Qt5 tray
page loaded; other archived pages were unavailable through web browsing, so the
local stubs’ embedded official reference text supplied that documentation).
No Qt binding, resource-registration blob or new dependency was introduced.

Implemented 15 ports plus an explicit non-allocating shared-memory blocker.
Graphics views use an explicit flush QWidget owner with a parented native view;
only the completed root is shown by the launcher. Extended official.py, the same official test/double/contract files, manifest,
README launch table and established controller/licence documents. Native state
transitions use owned native signal relays; Python callbacks remain tracked.
WorkerDelivery follows the insight worker pattern with bounded queues, timed
waits, stop/join before disconnect, error delivery and retained ownership when
join fails. Fixed explicit Python callback-field release while keeping native
methods/properties untouched; inherited/qualified native subclass references
are covered by the existing release-regression checks.

### Reproducible commands

```sh
UV_CACHE_DIR=/private/tmp/fontlab-uv-cache PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
```

Scoped Ruff lint/format, Python 3.11 grammar, original/asset provenance, prior
record equality and git diff --check results are recorded below after the final
run. Boundary checks cannot establish overload dispatch, virtual-handler
callbacks, animation rendering, platform permissions or native destruction.

### Every port’s adaptation and native acceptance checklist

Apply the common launch→inspect→native interaction→X/reshow→named close twice→
external event drain→complete owned destruction→relaunch acceptance sequence to
every implemented row. Retain versions/title/inspect JSON/render screenshots and
exceptions. FontLab, unrelated fonts/windows/settings/clipboard must stay
unchanged. Finish/cancel a drag before retrying a guarded close. Prove worker
join before owned native deletion. Do not infer native acceptance from tests.

- **0578c17977b471f1 — Embedded dialogs** (`ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py`): 100 proxy dialogs and original form controls/background retained. Generated PyQt UI becomes explicit QFormLayout controls; styles parent to the owned dialog. Native QTimeLine callbacks are tracked/stopped; currentValue uses the actual getter; native protected handlers are dispatched explicitly.

  Native: Expect title Embedded Dialogs Demo, dialog_count 100 and spacing 6. Use controls proxies to hover into/out of several dialogs; verify zoom, rotations, popup focus and cache changes. On controls dialog.ui change spacing (12), directionPicker (RTL/LTR), fontComboBox and stylePicker; verify only that dialog changes. Inspect remains inert. Close while a timeline and a combo popup are active; verify all 100 timelines and embedded dialogs are destroyed.

- **0788354954c8e613 — Mandelbrot** (`ports/threads/pyqt-official/mandelbrot-0788354954c8e613.py`): QThread/QMutex/QWaitCondition become a cancellable Python worker and bounded GUI timer drain. All eight refinement passes, original centre/scale and 512-entry spectral colormap are retained. Workers emit integer scanlines; only the GUI constructs/writes QImage. Zoom/scroll cancels and joins stale work; mouse release applies numeric deltas; the original cached drag preview is replaced by progressive row repainting.

  Native: Expect Mandelbrot, initial render_size 550x400 after kickoff, centre [-0.647011,-0.0395159], scale 0.00403897, pass progressing to 7. Exercise controls zoom(0.8), scroll(20,-20), start and stop plus native wheel, +/- and arrow keys, drag/release, resize and repaint. Verify detailed fractal rendering and host responsiveness. Stop/restart repeatedly; close during calculation and with an undrained queue, proving worker join and timer destruction.

- **1ca857d797199ecf — Diagram scene** (`ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py`): Original flowchart shapes, arrows, text editor, menus, toolbars and 15 PNGs retained. Custom PyQt signals become explicitly released Python callbacks; Qt signals still use the handle inventory. QPoint arithmetic and undocumented QLineF reference-output conversion become numeric geometry; zero-length arrows are guarded. Qt4 QString operations become Python strings; menus use popup and About uses asynchronous message. Removed items move to a hidden owned scene, avoiding deletion of connected Python targets; nonempty text is retained.

  Native: Expect Diagramscene, item_count 0, mode MoveItem. Use scene, buttonGroup, pointerTypeGroup, sceneScaleCombo and native mouse events to insert Conditional/Process/Input-Output, draw a real arrow between two shapes, move endpoints and verify the arrow follows. Edit text, font/colour/bold/italic/underline; keep nonempty text and remove empty text on focus loss. Test backgrounds, 50–150% scale, Bring/Send/Delete and asynchronous About. Delete shapes with arrows, then close with text focus and an open popup; verify discarded-scene and action destruction.

- **1cf57c0f2ac8880a — Animated tiles** (`ports/animation/pyqt-official/animatedtiles-1cf57c0f2ac8880a.py`): Original 64 tiles, five layouts, staggered durations, background and button images retained. PyQt QObject/pyqtProperty proxy becomes painted QGraphicsObject with native pos. Invisible owned QPushButtons relay item clicks into real QState transitions; no custom Qt signal registration. All timers, state machines and animations stop before disconnect; pixmaps are centred by paint coordinates.

  Native: Expect Animated Tiles and item_count 64. Use controls ellipse/figure8/random/tiled/centered via native clicks; inspect positions and verify every arrangement plus InOutBack interpolation/stagger. Resize view and check fitting and resource rendering. Close during transition and during the initial timer; confirm animations/state machine/timer destruction and a clean relaunch.

- **243ae486f9528e8c — Stickman** (`ports/animation/pyqt-official/stickman-243ae486f9528e8c.py`): 16 original nodes/bones, drawing/stabilisation and four byte-identical animation files retained. Native xChanged/yChanged replace positionChanged; native pos properties animate original frames. Original QDataStream binary layout is decoded into checked Python data using struct (including null QString); save uses explicit numeric stream writes. Native button relays implement J/D/C activity transitions; an owned timer implements random lightning and the 100 ms flash. Colour/death changes use entered callbacks rather than unregistered Python properties. Zero-length bones and all wrapper arithmetic are guarded.

  Native: Expect Stickman, node_count 16; frames jumping=5, dancing=9, chilling=25, dead=1. Focus controls view and send J, D, C; verify complete repeating motion and dragging nodes in stick mode via controls stickMan.setDrawSticks(True). Call strike.click(), verify white flash and dead face/pose after flash timer, then confirm activity keys do not resurrect it. Exercise coincident nodes and repaint. Close while moving/flashing; verify node/animation/timer destruction.

- **27709a02d37b9ba9 — Wait conditions** (`ports/threads/pyqt-official/waitconditions-27709a02d37b9ba9.py`): QThread/QMutex/QWaitCondition become Python producer/consumer workers using a real threading.Condition, an 8192-character ring and bounded GUI timer delivery. Preserve the 100000-character ACGT transfer; deterministic ACGT order replaces global qrand. An owned read-only log and Start/Stop controls replace process stderr output; timed waits and publish backpressure permit stop/join.

  Native: Expect Waitconditions, phase idle, received 0, data_size 100000 and buffer_size 8192. Click start and drain native events until phase done: received 100000 and prefix/suffix ACGT repeated 20 times. Stop midway, restart to a fresh result, start without draining until backpressure, then named close; verify both workers joined, no Qt calls off the GUI thread and no stderr/global app loop.

- **29f6a7d0a3bb6813 — States** (`ports/animation/pyqt-official/states-29f6a7d0a3bb6813.py`): Original text editor, radio options, six icons, state property assignments and animations retained. Uses native QGraphicsObject pos/rotation/opacity and real QState/QPropertyAnimation. Each scene, state machine, group and animation is owned; copied PNGs replace compiled resources.

  Native: Expect States with button_text Switch to state 2 and six rendered icons. Click controls button through 2→3→1 repeatedly; verify widget geometry, icons, rotations, opacities and Options appearance. Edit controls edit and select Herring/Blue Parrot/Petunias. Close mid-animation; confirm state machine/animations/proxy widgets are destroyed without callbacks.

- **2cd6ffc2b2ed65bb — Drag/drop robot** (`ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py`): Original ten-colour palette, articulated robot and looping native rotation/scale animations retained with exact head PNG. Image MIME converts using QPixmap.fromImage. QDrag uses the existing responsive drag boundary/close guard; painters end in finally. Local RNG replaces global qrand/qsrand; all native animations are stopped and owned.

  Native: Expect Drag and Drop Robot, palette_count 10 and an animated articulated robot. Natively drag colours from controls palette to each robot part; test rejected MIME and drag leave highlighting. After repeated drags verify the original occasional head image path, plus explicit image MIME to the head. Escape cancels a drag; attempt named close during drag and confirm safe refusal, finish/cancel and retry. Verify part colours, head_image, animation destruction and unchanged clipboard.

- **65d15d1fbc1b15e9 — Screenshot** (`ports/desktop/pyqt-official/screenshot-65d15d1fbc1b15e9.py`): Original options/preview controls retained. Startup and inspect do not capture or beep. New Screenshot schedules one owned cancellable timer; only its explicit callback calls primaryScreen.grabWindow. Save uses an asynchronous dialog and permits only this build’s temporary directory. No host settings or clipboard changes; timers stop before teardown.

  Native: Expect Screenshot, has_capture false, delay 5 and capture_pending false. Inspect twice and confirm no OS screen capture. Explicitly click newScreenshotButton (macOS may require capture permission); test 0/positive delay, Hide This Window, preview resize and cancellation by closing before timeout. Save using saveScreenshotButton inside the dialog’s owned directory; verify the PNG opens with the captured dimensions. Reject an outside path through saveTo. Close destroys timer/dialog and removes temporary files.

- **b7283d74afb78218 — Move blocks** (`ports/animation/pyqt-official/moveblocks-b7283d74afb78218.py`): Original four blocks, seven geometries, 1250 ms timer, elastic animations and sequential pauses retained. Custom QEvent/QAbstractTransition payload routing becomes a tracked GUI callback choosing a different state and clicking an invisible native button relay into QState transitions. Uses QRectF for native graphics geometry. Broad inventory dependencies are unused upstream imports/resources and are not copied.

  Native: Expect Move Blocks, block_count 4 and seven possible state_index values. Observe automatic changes, then call controls advance ten times: no adjacent repeated index and all four geometries change together. Verify elastic easing and the three original pauses; resize/repaint. Close while timer and animations are active; confirm destruction and no queued callback after close.

- **b95b687bbc541207 — Semaphores** (`ports/threads/pyqt-official/semaphores-b95b687bbc541207.py`): QThread/QSemaphore become two Python workers and actual threading.Semaphore synchronization around the original 8192-character ring; preserve the 100000-character transfer with deterministic ACGT data. Bounded GUI timer delivery replaces stderr; Start/Stop controls and timed semaphore acquisition permit clean cancellation/join even under backpressure.

  Native: Expect Semaphores, phase idle and received 0. Start, wait for done and verify received 100000, buffer_size 8192, matching deterministic prefix/suffix and stopped timer. Stop with producer/consumer blocked; restart, then close with a full delivery queue. Verify both workers joined, native destruction and FontLab responsiveness.

- **bd6c8feb783ba845 — Easing** (`ports/animation/pyqt-official/easing-bd6c8feb783ba845.py`): Original 47 easing choices, tunable period/amplitude/overshoot, line/circle paths and Qt logo retained. Generated UI is reconstructed with original control names; curve names come from the checked Qt enum list rather than PyQt enum reflection. Native QGraphicsObject.pos replaces pyqtProperty; circle updates assign native pos without emitting a fabricated signal. Curve icon painters end in finally.

  Native: Expect Easing curves, curve_count 47, curve OutBounce and path line. Use easingCurvePicker to choose Linear, InElastic, Back, Bounce and both splines; verify icon plots and enabled parameter controls. Change period/amplitude/overshoot, switch lineRadio/circleRadio, and observe actual interpolation and looping movement. Close during animation; confirm timer-free animation and scene/item destruction.

- **c1b878b63f80e733 — System tray** (`ports/desktop/pyqt-official/systray-c1b878b63f80e733.py`): Original icons, menu, message fields and notification actions retained. Tray starts hidden and Show icon unchecked; inspect never shows it or sends a notification. Quit closes this handle, with no QApplication quit or global quit-policy change. Native X hides the owned tray; message feedback is asynchronous. Tray hides before callback disconnection/native deletion.

  Native: Expect Systray, tray_visible false, icon_index 1 and original message text. Explicitly toggle showIconCheckBox; verify only this demo’s menu-bar/tray icon appears. Change all icons, minimize/restore with owned menu actions, explicitly send a message and exercise messageClicked feedback where supported. Native X must remove the icon; named close/quitAction must destroy tray/menu/dialog/actions while FontLab remains running. Record platform tray availability/notification restrictions.

- **de30d23621025fe6 — Application chooser** (`ports/animation/pyqt-official/appchooser-de30d23621025fe6.py`): Original four corner icons, selected centre geometry, restore-properties policy and default geometry animations retained. Invisible owned QPushButtons relay graphics-item clicks into real QState transitions; native QGraphicsWidget geometry replaces custom PyQt signals. Exact images replace compiled resources.

  Native: Expect Application Chooser, item_count 4 and four 64x64 corner geometries. Natively click each controls items entry: selected geometry becomes [86,86,128,128], previously selected icon returns to its original corner and native geometry interpolates. Check up/down image scaling, alignment and no visible relay buttons. Close mid-transition and verify scene/item/state-machine/animation destruction.

- **de35a965dfcfd678 — Shared memory (blocked)** (`ports/ipc/pyqt-official/sharedmemory-de35a965dfcfd678.py`): QSharedMemory exists, but the host exports no detach() and data/constData have no documented Python byte-buffer signature. The build reports the precise blocker without allocating an IPC key/segment. No in-process substitute is presented as IPC.

  Native: Confirm launcher/build raises the recorded NotImplementedError before any UI or IPC mutation. Recheck the actual host QSharedMemory.detach/data/constData exports; keep blocked unless safe byte access and explicit detach are proved. If exported in a future binding, native acceptance must include an owned unique key, two independent peers, image transfer, failure paths and destruction/unlink of the segment.

- **fcfaf9667206bbd6 — Colliding mice** (`ports/graphicsview/pyqt-official/collidingmice-fcfaf9667206bbd6.py`): Original seven mice, collision-aware steering/drawing and cheese background retained. Timers have an owned parent, integer 30 ms intervals and tracked slots; each stops before close. Local RNG avoids host-global seeding; coincident mice guard zero-length acos calculations. Positions use components and native mapping methods, never wrapper operators.

  Native: Expect Colliding Mice, mouse_count 7, original cheese background and animated mice. Observe movement, collision ear colours and steering away from the edge; pan/resize the view. Put two controls mice at the same position and confirm no divide-by-zero or paint exception. Close while all seven timers run; verify timer/scene/item destruction and a clean relaunch.

### Final batch-5 verification

Final requested offline gate: **370 passed in 5.62s**, zero failures/errors/skips,
**65 added** over the 305-test baseline. The scope is 15 implementations and one
explicit blocker, not native acceptance. All **21 changed Python files** pass
Ruff check, Ruff format --check and Python 3.11 grammar parsing, with correct
this_file records. **16 pinned entrypoint hashes** and **45 copied resource
pairs** are verified against the unchanged originals; **56 prior manifest
records** are structurally identical to HEAD. All **3 host-stub hashes** match
the captured contract. qRegisterResourceData remains absent. README has **191
lines**; PLAN/TODO remain unchanged. Screenshot save rejects outside paths as
inspectable errors without invoking the native save function.

```sh
UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
ruff check fontlab_python_examples/official.py tests/official_doubles.py tests/test_official_batch.py tests/test_official_native_regressions.py tests/test_ports.py ports/animation/pyqt-official ports/graphicsview/pyqt-official ports/desktop/pyqt-official ports/threads/pyqt-official ports/ipc/pyqt-official
ruff format --check fontlab_python_examples/official.py tests/official_doubles.py tests/test_official_batch.py tests/test_official_native_regressions.py tests/test_ports.py ports/animation/pyqt-official ports/graphicsview/pyqt-official ports/desktop/pyqt-official ports/threads/pyqt-official ports/ipc/pyqt-official
git diff --check
```

The provenance/grammar audit used ast.parse(feature_version=(3, 11)),
hashlib.sha256, byte-for-byte original/resource comparisons, and git show
HEAD:catalog/ports.json for prior-record equality. The source catalog and pinned
upstream tree were never edited. Branch remains issue-101-pythonqt-examples;
no commit. Native virtual dispatch, interpolation/rendering, complete native
object destruction, screen permissions and tray availability await controller
acceptance. Shared memory remains blocked by missing detach/byte-access API;
BSD-versus-collection-GPL and unnotified asset licence scope remain unresolved.

## 2026-10-14 — Native batch-5 enum/value-class correction

Controller reports 12/15 implementations passing native launch/inspect/close;
animatedtiles, dragdroprobot and moveblocks reject bare easing enums. Wrapped
all **7** easing calls with QEasingCurve(...). Audited **86 port files plus
official.py** against the local QtCore/QtGui stubs and their embedded Qt5
reference signatures. Also made gradient/palette/painter colours, robot cursors,
QPixmap fills and diagram colour fields explicit value objects. The stricter
colour double reproduced a deferred diagram text-insertion failure before its
fix. QColor(Qt.GlobalColor) constructs a colour; no implicit setter conversion
is assumed. QFont.setWeight(int), two-enum QWidget.setSizePolicy, QPainter pen/
brush-style overloads, QPainter.fillRect(GlobalColor) and QImage.fill integer/
GlobalColor overloads remain valid. Shortcut helpers already construct
QKeySequence values; official.py needed no further change.

Doubles reject bare easing/colour/cursor values and preserve legitimate enum
overloads. **14 regression cases added; 384 tests passed in 6.19s** with the
requested offline pytest command. Scoped Ruff check/format and Python 3.11
grammar pass for all **23 pending changed Python files**; git diff --check passes.
No TODO or acceptance-state changes and no commit. The three corrected launch
failures, plus changed drawing interactions, await native reacceptance; the
controller's 12 launch/inspect/close passes do not prove full interaction coverage.

## 2026-10-14: Controller native acceptance of pyqt-official batch 5 and full re-run

Batch 5 (Codex): 15 ports implemented, ipc/sharedmemory blocked (missing native
`detach()`, undocumented byte buffer). First native run: 12/15 passed; animatedtiles,
dragdroprobot and moveblocks failed because PythonQt does not convert a bare
QEasingCurve enum to the value class. Codex fix (same session): explicit
`QEasingCurve(...)`, plus colour/cursor/pixmap-fill boundaries audited across all 86
ports; offline gate 384 passed. Because earlier batches changed, the controller re-ran
native launch/inspect/close for all 56 pyqt-official ports (batches 3–5,
parent evidence/examples-batch5/native-all-official.jsonl): **56/56 pass, host alive
throughout**. Interactions and licence scope pending.

## 2026-10-14 — pyqt-official batch 6: 29 requested demos

Stayed on issue-101-pythonqt-examples, direct single-agent execution, no commit.
Preserved pre-existing DEPENDENCIES.md, .DS_Store and .omc changes. Read project
README/PLAN/TODO/WORK, catalog and existing ownership/launcher/editor, official
ports/tests/doubles/notice and worker queue patterns before implementation.
The initial requested offline test command failed to open the default uv cache;
reran with UV_CACHE_DIR=/private/tmp/fontlab-uv-cache. Added exact batch IDs first;
the manifest gate failed for the 29 missing identities before implementation.
Extended the existing official helper, tests and captured native contract rather
than adding another framework. All imported native classes were checked in
QtCore/QtGui/QtSvg/QtOpenGL/private stubs; QTextObjectInterface is absent and
textobject is explicitly blocked. QGL namespace constants are absent: use
QGLFormat.setSampleBuffers instead. No QThread adaptation is needed by this batch.
No PyQt/PySide runtime, QApplication construction/event loop, modal dialog exec,
resource registration, host quit/closeAllWindows or host settings/style writes.

Wait, but: passing build doubles does not exercise protected handlers or deferred
slots. Direct interaction and paint tests exposed obsolete QString.toInt, integer
coordinate/alpha dispatch, style-enum versus colour conversion, Save/Cancel
continuations, and callback references created outside child constructors.
Fixed those paths and explicitly release each private callback before deletion.
Print/Preview constructors own their QPrinter, avoiding premature destruction of
an externally allocated printer. Inspection must not allocate another QSettings;
Recent Files shares one temporary INI across its own windows. Source resource
example.html never becomes a save target. Existing regressions for no wrapper
negation/arithmetic, no native keywords, declared-reference release and sealed
native objects remain enforced. PLAN/TODO are unchanged.

Per-port adaptations and native acceptance checklist follow. Each native check
also requires two inert inspections, disconnect-before-delete, deferred native
destruction of every owned object, host alive, empty registry and clean relaunch.

### Batch 6 4efac54bae01fc62

`Official dockwidgets` — `ports/mainwindows/pyqt-official/dockwidgets-4efac54bae01fc62.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original letter, customer/paragraph docks, undo and toolbars retained. HTML save uses an owned asynchronous file dialog and UTF-8 stdlib I/O; printing uses a dialog-owned PDF-configured QPrinter. Four exact icon files replace compiled resources.

Native: Verify initial NAME/ADDRESS placeholders and company letter; select a customer and two standard paragraphs, edit and Undo. Float/re-dock each dock and toggle View actions. Save HTML to an owned temporary file, reopen and inspect text. Open/cancel Print, then explicitly accept an owned PDF destination and validate the PDF.

### Batch 6 60d40ce5671653cf

`Official menus` — `ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original menu actions, checkable formatting and alignment action group retained. Context menu uses popup instead of exec; About/Qt information is owned and asynchronous. Print remains the original informational menu action.

Native: Trigger New/Open/Save/Print/Undo/Redo/Cut/Copy/Paste and verify their infoLabel text. Toggle Bold/Italic and all four exclusive alignments. Right-click, dismiss and reopen the context menu; About/Qt remain responsive. Close with the popup visible.

### Batch 6 09afeea11be83f4f

`Official recentfiles` — `ports/mainwindows/pyqt-official/recentfiles-09afeea11be83f4f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: One shared owned temporary INI supplies all example windows; no Trolltech/user settings are read or written. UTF-8 stdlib file I/O replaces stream operators. New/Exit operate on owned windows only; the five recent actions share settings and the retained window list is cleared on close.

Native: Save six uniquely named owned files across two New windows; verify the five-entry order and labels synchronize, re-save one to move it to the front, and open a recent item. Cancel Open/Save As. Trigger Exit and confirm FontLab windows remain. Named close destroys both example windows and removes the owned INI; a new launch starts with no recent files.

### Batch 6 2d36e0fe43f5d49a

`Official separations` — `ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original CMY per-pixel extraction, recolouring, inversion, brightness recombination and image drag retained. qRed/qGreen/qBlue use integer channel extraction; custom imageChanged signals become released subclass callbacks. Colour/open/save dialogs are asynchronous; drag geometry uses components and QBuffer data remains QByteArray.

Native: Load an owned small RGB image with red/green/blue/white/black pixels. Verify Cyan/Magenta/Yellow and final composites, invert each plane, choose/cancel an ink colour and exercise all five brightness levels. Save/reopen PNG and verify pixels. Drag the final image to an owned target, cancel a drag and then close; no source is destroyed during drag.

### Batch 6 912e5c751b20ce97

`Official concentriccircles` — `ports/painting/pyqt-official/concentriccircles-912e5c751b20ce97.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: All four float/int and aliased/antialiased views retained. Integer QRect/QColor channels and alpha are explicit; four tracked timer targets stop before deletion, and painters end in finally.

Native: Verify the 2x2 labels/views and growing frames inspect list. Observe differences in float/int placement and antialiasing; resize while animated. Close with the 100 ms timer active, process deferred deletes and relaunch with frames reset.

### Batch 6 13a6bb9a9d2b9037

`Official painterpaths` — `ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Nine original paths, fill-rule/gradient colours, pen width/colour and rotation controls retained. Numeric enum casts become integers, brushes/colours are explicit value objects and painter cleanup is guaranteed.

Native: Verify nine rendered paths including text, cubic curve and star. Drive both fill rules, both gradient colours, pen colour, width 0/7/20 and rotation 0/45/360. Resize; check all nine views change consistently and close during repaint.

### Batch 6 b2d717e4d43806d2

`Official svgviewer` — `ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original bubbles SVG default plus cubic/spheres resources retained byte-for-byte. Native/Image/OpenGL renderers remain; QGL.SampleBuffers is replaced by QGLFormat.setSampleBuffers. The unavailable OpenGL branch is guarded. File dialogs are asynchronous, viewport callbacks are forgotten before replacement, and geometry uses components.

Native: Verify bubbles SVG appears on launch. Open cubic.svg and spheres.svg from copied assets; toggle Background/Outline, wheel zoom and pan. Switch Native/Image and, if hasOpenGL returns true, OpenGL and high-quality antialiasing repeatedly. Try missing/invalid SVG, cancel file selection, close after viewport replacement and confirm all scene/items/viewports are destroyed.

### Batch 6 c12a2071adbab88b

`Official transformations` — `ports/painting/pyqt-official/transformations-c12a2071adbab88b.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original clock/house/Qt/truck paths and cumulative translation/scaling/rotation retained. Text centring subtracts plain coordinates instead of negating QPointF; pen styles and fill brushes use verified native overloads.

Native: Choose each of four shapes. Set each of three operation combos to Translate/Scale/Rotate in different orders and compare cumulative transformed views with original. Resize and render axes/outlines/text. Close and relaunch after all transformations.

### Batch 6 c56cf1699b07b350

`Official calendar` — `ports/richtext/pyqt-official/calendar-c56cf1699b07b350.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original seven-column QTextTable calendar, month/year and font-size controls retained, including 640x256 startup size. Background highlighting uses explicit brush/colour values; cursor/table operations remain native.

Native: Select February 2024 and verify all 29 days, Monday-first headings and row boundaries. Select another month/year, font sizes 1/18/64, and the current month with today highlighted. Inspect month/year/font_size and title; close after repeated document replacement.

### Batch 6 c997677a2bdb4f34

`Official orderform` — `ports/richtext/pyqt-official/orderform-c997677a2bdb4f34.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original sample Mr Smith letter, editable quantities/privacy choice and tabbed documents retained. Details validation and discard confirmation are asynchronous; malformed quantities leave the dialog open with an inspectable error. Printing uses a dialog-owned printer configured for owned PDF output.

Native: Verify the initial sample letter and four products. New details: accept customer/address, quantities 0/2/negative and both offers choices; inspect added tabs/document tables. Enter nonnumeric quantity and verify no accept; leave details blank and test Yes/No discard. Cancel and explicitly accept PDF printing to an owned path; validate text and page layout.

### Batch 6 428c50abcef7adfe

`Official syntaxhighlighter` — `ports/richtext/pyqt-official/syntaxhighlighter-428c50abcef7adfe.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original C++ keyword/class/function/string/comment rules and multiline block state retained. File reads use UTF-8 stdlib I/O, dialogs and menus use tracked callbacks; native QSyntaxHighlighter virtuals/setFormat remain.

Native: Open an owned C++ fixture containing keywords, Qt classes, calls, strings, // comments and a multiline /* */ comment. Verify colours/styles and subsequent block recovery after edits; New clears the document. Cancel Open and select a missing file; inspect the error without losing the document. Close after repeated rehighlighting.

### Batch 6 b34b2f696a977e74

`Official textedit` — `ports/richtext/pyqt-official/textedit-b34b2f696a977e74.py` — **implemented**, native acceptance **unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Adaptation: Original rich-text formatting, lists, alignment, undo/redo, clipboard actions, document writer, sample HTML and platform icons retained. Save/New/Open/Close prompts use continuations. The sample resource is never a save target and its owned document image cache resolves original :/ URLs and its base URL resolves relative images. Print/Preview use dialog-owned PDF-configured printers; Export PDF uses an explicit asynchronous destination. All clipboard and preview connections are tracked.

Native: Verify sample HTML/logo and original 700x800 window. Format selected words with bold/italic/underline, family/size/colour, all alignment and list styles; test undo/redo, cut/copy/paste only on owned text. Save/reopen HTML and ODT; never overwrite copied example.html. Test Save/Discard/Cancel for New/Open/Close, including Save As cancellation. Preview and explicitly export an owned PDF, validate pages/text/images, close while clipboard/preview callbacks are live and verify disconnection.

### Batch 6 806fd814a2ea4d46

`Official textobject` — `ports/richtext/pyqt-official/textobject-806fd814a2ea4d46.py` — **blocked**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Blocked: QTextObjectInterface is absent from native QtGui stubs. A replacement image or HTML display would lose the inline custom SVG object-handler behavior; no fake interface, alternate Qt binding or resource module is supplied.

Native: Confirm launch reports the manifest blocker, does not create UI and leaves the host alive. Revisit only after the host exports QTextObjectInterface and supports native QTextDocument object handler registration/virtual callbacks.

### Batch 6 d6dc56a5318ffe71

`Official analogclock` — `ports/widgets/pyqt-official/analogclock-d6dc56a5318ffe71.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original hour/minute polygons, colours and minute/hour marks retained; the tracked one-second timer stops before deletion. Brush values and guaranteed painter end replace implicit conversion/destruction.

Native: Observe moving hands and marks over a minute, resize to rectangular and square shapes and verify aspect ratio/centering. Inspect title/geometry, close with the timer active, confirm native timer/widget destruction and relaunch.

### Batch 6 356e4e807f1e789f

`Official calculator` — `ports/widgets/pyqt-official/calculator-356e4e807f1e789f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original precedence, unary operators, memory and error display retained. Integer grid rows fix Python 3 division; all button callbacks are tracked and the native Button.sizeHint handler is called explicitly.

Native: Drive 2+3*4=14, 9/0=####, Sqrt of a negative number, reciprocal of zero, decimal/sign/backspace/Clear/Clear All, and MC/MS/M+/MR. Verify size hints, display_text and memory. Close after an error and relaunch at zero.

### Batch 6 b91effc45f81fbb0

`Official calendarwidget` — `ports/widgets/pyqt-official/calendarwidget-b91effc45f81fbb0.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original locale, first day, selection mode, navigation/grid, headers, date limits and formatting controls retained. Enum values are passed as integers and text-format colours as explicit brushes; locale iteration uses enumerate.

Native: Switch locale/first weekday/selection mode, grid/navigation and both header styles. Set min/max/selected date within and outside limits. Change weekday/weekend colours, header format, First Friday and May First; navigate months and inspect selected_date. Close after dateChanged/selectionChanged round trips.

### Batch 6 499e965d86347920

`Official charactermap` — `ports/widgets/pyqt-official/charactermap-499e965d86347920.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original BMP grid, fonts/styles/sizes, tooltip, selected text and explicit clipboard action retained. Python int replaces QString.toInt; indexes use integer division. characterSelected becomes a released callback and font-merging toggles are wired. Clipboard writes happen only on explicit To clipboard.

Native: Select A and a non-ASCII BMP character, verify tooltip/codepoint and appended lineEdit text. Change font/style/size and toggle automatic font merging; try invalid size. Verify inspection leaves clipboard unchanged, then explicitly copy owned sample text and restore the controller clipboard fixture. Scroll/repaint the grid and close.

### Batch 6 3040b9f6b267a196

`Official digitalclock` — `ports/widgets/pyqt-official/digitalclock-3040b9f6b267a196.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original one-second timer, LCD filled segments and blinking colon retained. The rendered display string is retained as declared Python state for meaningful inspection; timer callbacks disconnect and stop on close.

Native: Verify hh:mm with a blinking colon and inspect display_text. Wait for at least two ticks and a minute transition, resize, close with the timer active and relaunch without duplicate updates.

### Batch 6 f702b62aa47629ad

`Official groupbox` — `ports/widgets/pyqt-official/groupbox-f702b62aa47629ad.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original exclusive radios, checkable/flat groups, independent/tristate checkboxes, toggle/flat/default buttons and nested popup menu retained with native widget ownership.

Native: Test both exclusive radio groups, disabled checkable group, all checkboxes/tristate values, flat/normal/toggle buttons, popup menu and submenu. Verify group enabling and exclusivity; close with a popup visible and relaunch.

### Batch 6 16456ba02f4b79cc

`Official imageviewer` — `ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original scroll area, image label, zoom/normal/fit behavior and image printing retained. Opening and printing are asynchronous; zoom multiplies plain width/height integers rather than QSize wrappers. An unused default host printer is excluded from construction.

Native: Open an owned PNG/JPEG and an invalid file, cancel selection, zoom to both limits, Normal Size and Fit to Window, resize and verify scrollbar centering/action enablement. Cancel Print, then explicitly write an owned PDF and verify image scaling; close with a dialog open.

### Batch 6 84cb59e07adfae2c

`Official lineedits` — `ports/widgets/pyqt-official/lineedits-84cb59e07adfae2c.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original echo modes, validators, alignments, input masks and read-only controls retained. Removing a validator uses the native null pointer None via setValidator, without assigning None to a native property.

Native: Drive all four echo modes, integer/double/no validator, each alignment, phone/date/license/no mask and both read-only states. Type valid and invalid values and inspect text/control state. Close after validator replacement.

### Batch 6 8e5aa13798c2763c

`Official scribble` — `ports/widgets/pyqt-official/scribble-8e5aa13798c2763c.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original drawing, pen width/colour, image open/save/clear and printing retained. resizeImage now returns the resized copy to preserve the intended image rather than rebinding the wrong instance. Coordinates/radii are integers; painters end reliably and save/open/close confirmations are asynchronous. Image format names decode QByteArray.data; printing starts with owned PDF output.

Native: Draw with mouse press/move/release, resize larger/smaller without losing strokes, change/cancel pen colour and width 1/5/50. Save/reopen each available PNG/JPEG format in owned files, Clear, and test Save/Discard/Cancel on Open/Close including cancelled Save As. Explicitly validate owned PDF print output, then close while dirty.

### Batch 6 248e64416b9b218c

`Official shapedclock` — `ports/widgets/pyqt-official/shapedclock-248e64416b9b218c.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original frameless masked clock, drag behavior and context Exit retained. Global position arithmetic subtracts components, QRegion geometry is integer, Exit closes only owned windows and the timer stops before deletion.

Native: Verify circular mask at several sizes and both hand polygons. Drag by the left button and confirm the offset remains stable; open context menu and Exit without quitting FontLab. Close during a drag/timer tick, verify mask/timer/widget destruction and relaunch.

### Batch 6 36805750b888fba6

`Official sliders` — `ports/widgets/pyqt-official/sliders-36805750b888fba6.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original horizontal/vertical slider-scrollbar-dial synchronization, min/max/value, inversion and orientation controls retained. Custom PyQt group valueChanged relays use each native dial signal; all native connections are tracked.

Native: Change value in each slider/scrollbar/dial and spinbox; verify horizontal=vertical. Change min/max, invert appearance and key bindings, switch orientation and exercise keyboard/page steps. Close during changes and relaunch with range 0..20/value 5.

### Batch 6 468179092748a72e

`Official spinboxes` — `ports/widgets/pyqt-official/spinboxes-468179092748a72e.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original integer, percent/currency, date/time, meeting-format and floating precision controls retained; native overloaded signals use explicit QString/int signatures and date/time properties use read.

Native: Test integer -20/20, zoom Automatic/1000%, currency, date/time limits, every meeting format including time-only. Drive decimals 0/2/4/100 across the three double boxes, test step/wrapping limits and inspect values. Close after repeated format changes.

### Batch 6 9e21c6536fda7a23

`Official styles` — `ports/widgets/pyqt-official/styles-9e21c6536fda7a23.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original gallery and progress timer retained. Style and palette changes are scoped to the owned root and the created style is parented; FontLab application style/palette remain unchanged. Integer progress updates advance by at least one until maximum, fixing truncation stall.

Native: Record FontLab application style/palette before launch. Change every available style and standard/original palette, disable/re-enable groups, exercise tabs and widgets, and observe progress reaching maximum. Verify host style/palette unchanged and timer stopped after close/relaunch.

### Batch 6 e63bffc17abf2fde

`Official tetrix` — `ports/widgets/pyqt-official/tetrix-e63bffc17abf2fde.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original board, pieces, key controls, next preview, scoring/levels and timer retained. Custom score/level/line signals become released LCD callbacks; timer intervals/grid dimensions are integer and native base virtuals are explicit. Exit is owned; the demo does not reseed the host RNG.

Native: Start, move/rotate/drop and pause/resume; verify next preview/LCDs/inspect board, score and level. Fill/clear a line, test wall/floor collisions and game-over restart. Verify both rotation directions for nonsquare pieces. Close while QBasicTimer is active and verify released LCD callbacks/timer destruction.

### Batch 6 509e781f1267967f

`Official wiggly` — `ports/widgets/pyqt-official/wiggly-509e781f1267967f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original animated text, sine-table offsets, hues and line-edit control retained. QBasicTimer uses the exported three-argument start(interval, timerType, receiver), integer text coordinates and explicit QWidget.timerEvent fallback.

Native: Change lineEdit text including empty/non-ASCII input and inspect text/step. Observe each character moving/colouring over multiple timer events; resize and close while active. Confirm timer stops and no stale callback on relaunch.

### Batch 6 136c45cc9f97c218

`Official windowflags` — `ports/widgets/pyqt-official/windowflags-136c45cc9f97c218.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original type/hint radio/checkbox controls and owned preview retained. Zero starts the integer flags mask instead of calling an enum type; setWindowFlags invokes QWidget explicitly and preview geometry uses coordinate components.

Native: Exercise each Window/Dialog/Sheet/Drawer/Popup/Tool/ToolTip/Splash type and every hint, checking preview text and geometry. Drag and close/reopen the preview; verify parent remains responsive even for Popup. Named close destroys root/preview and all button callbacks; host windows remain.

### Final batch-6 verification

The exact offline gate passes **474 tests**, zero failures/errors/skips. The batch
adds **90 cases** over the repository's 384-test baseline: 28 implementation
build/inspect/controls/disconnect/close cases and 62 batch-specific cases including
all 28 inert inspections/constructor-failure rollbacks, the interface blocker,
real control/dialog continuations, virtual rendering paths and callback release.
The final direct rendering checks require integer drawText coordinates and every
QPainter context to end exactly once (guarded by isActive in finally). The sample
rich-text resource URL is explicitly backed by the owned QTextDocument cache;
resource file bytes remain unchanged.

Scoped Ruff check and Ruff format --check pass for **32 changed Python files**;
all 32 parse with Python 3.11 grammar and have matching this_file records. The
provenance audit verifies **29 original entrypoint hashes**, **29 verbatim original
file notices**, **48 byte-identical copied resource pairs**, **5 native stub hashes**
and structural equality of all **72 prior manifest records**. Native states for
all 29 are unexecuted. One entry is blocked, 28 are implemented. The official
manifest now has 84 implemented demos, 2 blockers and 215 resource copies.
README is 179 lines. PLAN.md, TODO.md and catalog/sources.json are byte-identical
to HEAD; the branch/HEAD remain issue-101-pythonqt-examples / cbb20f2. No commit.
No third-party dependency was added and pre-existing DEPENDENCIES.md edits remain.

Commands (run directly; rtk proxy forwards the commands without rewriting them):

```bash
UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests

task_python_files=(
  ports/mainwindows/pyqt-official/dockwidgets-4efac54bae01fc62.py
  ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py
  ports/mainwindows/pyqt-official/recentfiles-09afeea11be83f4f.py
  ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py
  ports/painting/pyqt-official/concentriccircles-912e5c751b20ce97.py
  ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py
  ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py
  ports/painting/pyqt-official/transformations-c12a2071adbab88b.py
  ports/richtext/pyqt-official/calendar-c56cf1699b07b350.py
  ports/richtext/pyqt-official/orderform-c997677a2bdb4f34.py
  ports/richtext/pyqt-official/syntaxhighlighter-428c50abcef7adfe.py
  ports/richtext/pyqt-official/textedit-b34b2f696a977e74.py
  ports/richtext/pyqt-official/textobject-806fd814a2ea4d46.py
  ports/widgets/pyqt-official/analogclock-d6dc56a5318ffe71.py
  ports/widgets/pyqt-official/calculator-356e4e807f1e789f.py
  ports/widgets/pyqt-official/calendarwidget-b91effc45f81fbb0.py
  ports/widgets/pyqt-official/charactermap-499e965d86347920.py
  ports/widgets/pyqt-official/digitalclock-3040b9f6b267a196.py
  ports/widgets/pyqt-official/groupbox-f702b62aa47629ad.py
  ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py
  ports/widgets/pyqt-official/lineedits-84cb59e07adfae2c.py
  ports/widgets/pyqt-official/scribble-8e5aa13798c2763c.py
  ports/widgets/pyqt-official/shapedclock-248e64416b9b218c.py
  ports/widgets/pyqt-official/sliders-36805750b888fba6.py
  ports/widgets/pyqt-official/spinboxes-468179092748a72e.py
  ports/widgets/pyqt-official/styles-9e21c6536fda7a23.py
  ports/widgets/pyqt-official/tetrix-e63bffc17abf2fde.py
  ports/widgets/pyqt-official/wiggly-509e781f1267967f.py
  ports/widgets/pyqt-official/windowflags-136c45cc9f97c218.py
  fontlab_python_examples/official.py
  tests/test_official_batch.py
  tests/official_doubles.py

)
RUFF_CACHE_DIR=/private/tmp/fontlab-ruff-cache ruff check "${task_python_files[@]}"
RUFF_CACHE_DIR=/private/tmp/fontlab-ruff-cache ruff format --check "${task_python_files[@]}"
python - "${task_python_files[@]}" <<'GRAMMAR'
import ast, sys
from pathlib import Path
for name in sys.argv[1:]:
    ast.parse(Path(name).read_text(), feature_version=(3, 11))
    assert "this_file: " + name in Path(name).read_text()
print(len(sys.argv) - 1, "Python 3.11 files checked")
GRAMMAR
git diff --check
git branch --show-current
git rev-parse HEAD
```

The hash/provenance audit used hashlib.sha256 and byte comparisons against the
unchanged pinned sibling verification tree, catalog/sources.json and the five
sibling Echopy native stubs; git show HEAD:catalog/ports.json supplied the 72 prior
records. No native FontLab acceptance was run: protected virtual dispatch,
rendering fidelity, exact constructor overloads, native deferred destruction,
OpenGL availability and actual PDF/clipboard behavior are the controller's
remaining checks. Original BSD-versus-collection-GPL scope remains unresolved for
28 batch entries and their unnotified assets; textedit selects the explicit
original GPLv3 alternative. The missing QTextObjectInterface binding is the only
implementation blocker in this batch.

## 2026-10-14 — Native orderform addAction return correction

Controller reports 27/28 batch-6 implementations passing native launch/inspect/
close; orderform fails on printAction.setShortcut. The actual call inserts an
already-created QAction, selecting QWidget's void addAction(QAction) overload,
not the text-only QAction factory. Retain Demo.action's explicit QAction and
tracked triggered connection, insert it with a separate menu.addAction statement,
then set the shortcut. Audited all 115 port files plus official.py: 248 addAction
calls; orderform was the sole unsafe consumed return. Remaining 36 consumed
returns are text-only factories; official.py has no addAction call. Native stubs
confirm QAction(text, parent), QKeySequence shortcut and QWidget's void insertion.

The doubles now return None for existing-action insertion (preserving
QActionGroup's different return) and callable/receiver-slot overloads. Two new
regressions reproduced the exact NoneType failure and audit violation before the
fix. All 11 added cases now pass: overload contracts, retained/tracked Print action,
nonblocking print dialog, disconnect-before-delete and an all-port AST audit.

Commands: UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest
-q tests: **485 passed in 8.85s**, no failures/errors/skips. Scoped ruff check and
ruff format --check pass for all 33 pending changed Python files; Python 3.11
ast.parse checks pass for those files and all 116 audited files. git diff --check
passes. CHANGELOG updated; TODO and manifest acceptance states unchanged. Branch
issue-101-pythonqt-examples, HEAD cbb20f2, no commit. Orderform awaits native rerun.

## 2026-10-14: Controller native acceptance of pyqt-official batch 6 and full re-run

Batch 6 (Codex): 28 ports implemented (widgets, mainwindows, painting, richtext),
textobject blocked (no native QTextObjectInterface). First native run 27/28;
orderform used the return value of `addAction(QAction)`, which is void in PythonQt.
Codex fix (same session): explicit tracked QAction, 248 calls audited, doubles
enforce overload returns; offline 485 passed. Controller re-ran native
launch/inspect/close for all 84 pyqt-official ports (batches 3–6, parent
evidence/examples-batch6/native-all-official.jsonl): **84/84 pass, host alive**.

## 2026-10-14 — Batch 7: 27 official PythonQt ports

Baseline: exact offline test command passed 485 tests. Worked directly on
issue-101-pythonqt-examples; no commit and no native FontLab acceptance.
The existing Demo/ExampleHandle/WorkerDelivery, official tests/doubles, manifest,
licence notice and controller guide are extended. No third-party dependency was
added; pre-existing DEPENDENCIES.md, .DS_Store and .omc changes are preserved.
PLAN.md, TODO.md and catalog/sources.json are unchanged.

The following per-port adaptations and native acceptance instructions are also
appended to docs/pyqt-official-batch.md; its common five-step host baseline,
interaction, disconnect-before-delete, destruction and relaunch checks apply.

## Batch 7: item views, graphics, drag/drop and owned network

All 27 entries are implemented; every new native acceptance state is **unexecuted**.
The common acceptance steps above apply to every row. Tests use strict doubles and
real owned localhost transport; they do not prove PythonQt virtual dispatch or rendering.
Network decision D4 permits only each port's numerical 127.0.0.1/free-port peer; there
is no DNS, internet, system broadcast, host settings/cache or global cursor change.
Native TCP/UDP clients and HTTP manager explicitly disable proxies.

### Batch 7 43c6c2f6f5f036d3

`Official delayedencoding` — `ports/draganddrop/pyqt-official/delayedencoding-43c6c2f6f5f036d3.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original SVG view/Export and lazy PNG drag retained. pyqtSignal becomes the native retrieveData virtual callback with a per-drag encoded flag; file assets, component-safe values, balanced painters and owned buffer replace resource registration.

Native: Check SVG and Export icon; inspect encoding_count=0. Start a real native drag, cancel once (no requested PNG), then drop into Drop Site or a controller-owned file target. Confirm retrieveData dispatch, valid PNG bytes/size, one encoding per drag and responsive FontLab. Finish/cancel any drag before named close; verify no MIME producer/slot survives.

### Batch 7 fa6823667fdb918f

`Official dropsite` — `ports/draganddrop/pyqt-official/dropsite-fa6823667fdb918f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original drop area, MIME/content table and Clear/Quit retained. Direct owned change callback replaces custom signal; raw bytes use QByteArray.data(), and QImage values use QPixmap.fromImage.

Native: Drive dropArea with native text, HTML, URL, image and binary drags; formats must show all MIME types and binary 00 FF correctly. Confirm displayed content changes on drop, drag-leave resets and clearButton empties rows. Close with a drag hovering; no stale Python callback.

### Batch 7 a96a7978c0b9f6ee

`Official anchorlayout` — `ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: All seven labelled proxy buttons and all 24 original anchors retained, with typed background brush and parent-owned scene; no wrapper arithmetic.

Native: Check labels A-G and each proxy geometry. Resize window and anchorWidget to narrow/wide/tall sizes; verify original horizontal/vertical centre relationships and min/preferred/max sizes. Click all buttons (upstream has no callback). Named close must destroy scene and seven proxies.

### Batch 7 fff97a435b73d548

`Official elasticnodes` — `ports/graphicsview/pyqt-official/elasticnodes-fff97a435b73d548.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original nine-node/twelve-edge force graph, arrows, drag, keyboard and zoom retained. Component point offsets replace wrapper operators; private RNG, integer timer interval, explicit native handlers and stopMotion own teardown.

Native: Expect node_count=9, edge_count=12. Drag centerNode and another node; confirm edges follow and timer settles. Arrow keys move the centre; space/enter shuffle; wheel/+/- zoom within source limits. Exercise step/scaleView, resize/background/shadows and arrow rendering; close during active motion, then relaunch.

### Batch 7 a58650b5461c0f48

`Official padnavigator` — `ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original 3x3 pad, native key/state transitions, history, flip/selection animations and optional OpenGL retained. Exact form.ui loads natively, PNGs load from files; entered callbacks set fill instead of a custom Qt meta-property. Typed easing values, component coordinates and explicit animation/state shutdown.

Native: Verify nine icons/background and hostName/form controls. Any key dismisses splash; arrows wrap selection in both directions. Return/Enter flips to the form, edits stay owned, and returns restore the selected history position. Check tilt, opacity, half-flip scale/fill and resize fit. Close midway through animation and confirm machine/animation shutdown. Exercise software viewport and OpenGL when available.

### Batch 7 9dab02b61cebbdb7

`Official basicsortfiltermodel` — `ports/itemviews/pyqt-official/basicsortfiltermodel-9dab02b61cebbdb7.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original ten mails, dual views, date-display filtering and case/syntax/column controls retained. Proxy model moves to QtGui, native properties use read(), parent ownership and explicit native fallback.

Native: Expect source_rows=10, initial proxy_rows=4. Set sender pattern Andy (2), no match (0), empty (10); exercise regexp/wildcard/fixed string, case toggles and all three filter columns including displayed date. Click headers to sort, check real proxy/view order. Close/relaunch without selection callbacks.

### Batch 7 0a3b15766909bdc3

`Official coloreditorfactory` — `ports/itemviews/pyqt-official/coloreditorfactory-0a3b15766909bdc3.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original names/colours and colour-list factory retained. QMetaType.type("QColor") resolves the native type; a per-delegate factory/creator plus explicit QColor/index conversion replaces pyqtProperty and leaves the host default factory unchanged.

Native: Expect Alice/aliceblue, Neptun/aquamarine, Ferdinand/springgreen. Double-click a colour cell, confirm native creator virtual dispatch and colour swatches; choose a new colour and commit/cancel. Name editing must use the standard editor. Check a separate host table keeps its editor factory; close with an editor open and verify native factory/creator lifetime.

### Batch 7 cc95f9719b8e4eda

`Official combowidgetmapper` — `ports/itemviews/pyqt-official/combowidgetmapper-cc95f9719b8e4eda.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original five records, rich addresses, Home/Work/Other and mapper navigation retained. QStringListModel lives in QtGui; mapping property uses native QByteArray and a private model field.

Native: Next/Previous traverse Alice, Bob, Carol, Donald, Emma with original addresses/types 0,1,2,0,2; endpoint buttons disable correctly. Change name/address/type, leave the editor and navigate back; verify actual mapper commits. Inspect current_index and row_count=5; close with an editor focused.

### Batch 7 029ea0dabe87ae57

`Official customsortfiltermodel` — `ports/itemviews/pyqt-official/customsortfiltermodel-029ea0dabe87ae57.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original ten mails and text/date filters retained. QtGui proxy plus scalar Julian-day/ISO comparisons avoid Qt wrapper ordering; QDateTime values bypass email matching correctly.

Native: Expect initial proxy_rows=5; Sports gives 3, no match 0, empty 10 with original inclusive dates. Change fromDateEdit/toDateEdit to narrow/empty/inverted ranges. Exercise syntaxes/case and sender-email/date sorting; confirm actual native lessThan/filterAcceptsRow dispatch and visible order. Close/relaunch.

### Batch 7 4b8851287931abd0

`Official dirview` — `ports/itemviews/pyqt-official/dirview-4b8851287931abd0.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original read-only QFileSystemModel/tree retained; argv and host filesystem defaults become an owned temporary directory containing example.txt.

Native: Wait for model directory load; root_path must be owned and read_only true, column_count=4. Expand/select example.txt, resize/sort columns and confirm editing cannot write. Named close destroys watcher/model and removes the owned directory; host files stay unchanged.

### Batch 7 67170c89593ad35e

`Official fetchmore` — `ports/itemviews/pyqt-official/fetchmore-67170c89593ad35e.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original directory list, 100-row fetch batches, alternating backgrounds and population log retained. Starts with 205 owned files; custom signal becomes an owned callback set after log creation. Fix inclusive insertion range and reject child/empty fetches.

Native: Drive lineEdit to owned fixtures. Repeated fetchMore should insert 100,100,7 rows for 205 files plus dot entries; verify rowsInserted bounds, alternating backgrounds and log totals. Empty/missing directory must not crash or insert an invalid range. Scroll the real view to trigger native canFetchMore/fetchMore; close while fetching.

### Batch 7 d50ad6638357e669

`Official pixelator` — `ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original image table, grayscale circle delegate, pixel-size control and file/about/print actions retained. Exact qt.png, private model, asynchronous image/large-image/print dialogs; bounded GUI print timer and owned PDF printer replace modal loops/processEvents.

Native: Check original qt.png as circles, change pixelSizeSpinBox 4-32, load an owned PNG and cancel chooser. Trigger printAction: large-image Yes/No is async, printer defaults to an owned PDF, progress rows advance; cancel through progress and close during printing. Validate a completed PDF externally and painter/timer teardown.

### Batch 7 a59dae9770bfbefb

`Official simpledommodel` — `ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Stdlib minidom preserves element/text/comment/processing-instruction/attribute behaviour without absent QtXml. Native tree uses numeric internal IDs, async chooser and tracked model replacement; invalid XML retains the previous model.

Native: Initial root label=owned contains comment, processing instruction and child/text; headers Name/Attributes/Value. Use loadXml/openAction for a fixture with whitespace/comments/namespaces, expand all levels and verify native parent/index relationships. Malformed/missing XML sets error and retains the old tree. Replace twice, close and confirm retired/current models are destroyed.

### Batch 7 39de33366209402d

`Official simplewidgetmapper` — `ports/itemviews/pyqt-official/simplewidgetmapper-39de33366209402d.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original five records, rich addresses, age spinner and mapper navigation retained. QtGui mapper uses a private model field and tracked callbacks.

Native: Next/Previous traverse Alice/Bob/Carol/Donald/Emma with ages 20,31,32,19,26. Edit name/address/age, leave focus/navigate back and verify native mapper persistence. Endpoint buttons and current_index/row_count must match. Close with an editor focused.

### Batch 7 ddb20b1b68b18a91

`Official spinboxdelegate` — `ports/itemviews/pyqt-official/spinboxdelegate-ddb20b1b68b18a91.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original 4x2 multiplication values and 0-100 editor retained; QtGui styled delegate/model are parent-owned with explicit native editor geometry and retained controls.

Native: Initial rows [[1,2],[2,4],[3,6],[4,8]]. Double-click row 2 column 1, expect 6; commit 42 through the native editor and verify model/inspect. Test 0/100 bounds, cancellation and resizing editor geometry. Close while editing; model/delegate/editor must be destroyed.

### Batch 7 bf3b39a8c2df8e94

`Official spreadsheet` — `ports/itemviews/pyqt-official/spreadsheet-bf3b39a8c2df8e94.py` — **implemented**, native acceptance **unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Adaptation: Original 10x6 expense sheet, formula operations, date/completion delegate, menus and context actions retained, with all four companion notices. Explicit subclass clone/recursive cell evaluation, cycle guard, typed brushes/shortcuts and async arithmetic/colour/font/owned PDF preview replace unsafe/native-attribute and modal patterns.

Native: Initial total=21883; putFormula("C2","200") changes total to 21933. Drive formulaInput and all +,-,*,/,sum actions, division by zero and cyclic references; verify live cells, not just inspect. Test date formats/editor calendar/completion, colour/font/clear and context menu. Preview printer is dialog-owned and defaults to temporary PDF; validate PDF, then close with arithmetic/editor/preview open. Check native item data/clone virtual dispatch.

### Batch 7 dc59f268ee01e364

`Official stardelegate` — `ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original four music rows, painted stars/diamonds and hover/release editor retained. Integer QVariant ratings replace Python objects; original rating objects remain inside the Python painter/editor. Component QSize and list polygons, explicit native fallback and balanced paint.

Native: Initial ratings [5,4,3,5]. Double-click a star cell, hover across centres including 0/5 boundaries, release to commit; cancel another editor. Verify integer model values, stars/diamonds, selection background and standard text-cell editing. Close with an editor active; no Python editing signal is left attached.

### Batch 7 cf15c3e91cdd8ded

`Official storageview` — `ports/itemviews/pyqt-official/storageview-cf15c3e91cdd8ded.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original ten-column mounted-volume model and size/tooltip formatting retained, with QtGui table model and QByteArray.data() decoding. Volume enumeration is read-only and captured at build.

Native: Check headers and native mounted-volume count; compare root/name/device/filesystem/total/free/available/ready/read-only/valid with read-only host observations. Hover rows for all ten tooltip values and size units; expand/select/sort/resize. Repeated inspection must not refresh volumes or write to them; close model/view.

### Batch 7 79f3a23172968ad2

`Official blockingfortuneclient` — `ports/network/pyqt-official/blockingfortuneclient-79f3a23172968ad2.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original host/port/Get Fortune/status UI retained. Missing QThread/mutex/condition become WorkerDelivery with cancellable stdlib socket reads and GUI timer; owned loopback fixture sends the exact Qt_4_0 frame. Other host/port inputs are rejected before DNS/socket creation.

Native: Click getFortuneButton repeatedly; inspect fortune, statusLabel and button recovery. Change hostLineEdit/portLineEdit to foreign values and expect an owned error without network contact. Close during connect/read/drain; worker joins and listener port is released. Relaunch for fresh state; host GUI remains responsive.

### Batch 7 0bba8a80541ab04f

`Official broadcastreceiver` — `ports/network/pyqt-official/broadcastreceiver-0bba8a80541ab04f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original receiver/status/Quit retained. Native QUdpSocket writes to an owned localhost UDP socket; bounded GUI timer/stdlib recvfrom replaces the unavailable PyQt tuple readDatagram overload. No real broadcast or fixed global port.

Native: Invoke sendSample, then wait for pollTimer: expect Received datagram: "Broadcast message 1" and received list. Send multiple owned samples, verify ordering/bounded history. Inspect is inert. Close while draining, verify socket/free port and both timers released, then relaunch.

### Batch 7 90721289b8108c4f

`Official broadcastsender` — `ports/network/pyqt-official/broadcastsender-90721289b8108c4f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original Start/Quit, one-second sender and message counter retained. Native QUdpSocket targets the port-owned localhost receiver; bounded stdlib receive drain replaces raw C-buffer readDatagram; no broadcast address or fixed port.

Native: Click startButton, observe messages 1,2,3 at one-second intervals; status/counter and received list agree. Invoke sendSample for an explicit extra datagram. No packet leaves 127.0.0.1. Close while active; sender, receiver and timers release the free port; relaunch resets message_no.

### Batch 7 fbb4e3c7288fed7c

`Official fortuneclient` — `ports/network/pyqt-official/fortuneclient-fbb4e3c7288fed7c.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original host/port/Get Fortune/status UI and asynchronous QTcpSocket retained. A WorkerDelivery-owned localhost server supplies framed UTF-16 fortunes; partial reads accumulate bytes. Numeric endpoint validation, NoProxy and no host network-session/settings writes.

Native: Click getFortuneButton repeatedly and verify distinct original fortunes/status/button recovery. Drive fragmented delivery/error via the owned peer; foreign hostCombo/portLineEdit values must fail before connection. Close with tcpSocket active and server queue pending; disconnect callbacks, abort socket, join server and release port.

### Batch 7 aad57160cfd51894

`Official fortuneserver` — `ports/network/pyqt-official/fortuneserver-aad57160cfd51894.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original server-status/Quit and seven fortunes retained. A plain-data WorkerDelivery listener binds only 127.0.0.1/free port; exact Qt_4_0 UInt16/QString wire format and owned probe replace network-session/global interface/settings behaviour.

Native: Run probe or connect a controller-owned localhost client to endpoint; decode the UInt16/QString packet and verify original fortunes/sent_count. Connect repeatedly, close during a request or full delivery queue, and confirm worker joined/free port released. No host network settings or global interfaces change.

### Batch 7 409f3d46a9555f23

`Official http` — `ports/network/pyqt-official/http-409f3d46a9555f23.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original URL/Download/Quit/progress/cancel behaviour retained with QNetworkAccessManager and NoProxy. Owned HTTP fixture/output, before-request numerical endpoint validation, exported FollowRedirectsAttribute=False, no external redirect/authentication/SSL flows; reply disconnect precedes abort/delete.

Native: Download default sample.txt, wait until downloading=false, check 38 bytes and exact owned file content. Cancel an active request and expect output removal/button recovery; /missing exercises failure. Foreign URL/port, credentials and redirects must not contact another peer. Close during active reply/progress; listener, reply callbacks and temporary files disappear. HTTPS/authentication are intentionally outside the D4 local fixture.

### Batch 7 d8803c2afaabf3d5

`Official lightmaps` — `ports/network/pyqt-official/lightmaps-d8803c2afaabf3d5.py` — **implemented**, native acceptance **unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Adaptation: Original city selection, slippy coordinates/panning, magnifier/feathered ring and night mode retained. Missing QtXml is irrelevant; QObject uses private, custom update signals become direct owned callbacks, all wrapper arithmetic is component-based. Owned HTTP PNG fixture/cache replaces internet tiles/global disk cache; replies and hold timer stop on close.

Native: Choose Oslo/Berlin/Jakarta, wait for tile_count, verify coordinates and the clearly labelled offline fixture. Pan by mouse/arrows, hold/Z magnifier and release, move lens, toggle night mode; check ring/clipping/tiling and repeated resize. Verify traffic only reaches endpoint and no host cache/browser is used. Close mid-download/hold/zoom; server joins and native replies/timers/owned tile file disappear. Geographic map imagery is not supplied.

### Batch 7 ebf87d5f5390b0fd

`Official loopback` — `ports/network/pyqt-official/loopback-ebf87d5f5390b0fd.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original 50 MiB transfer, 64 KiB payloads, Start/Quit and client/server progress retained. Native QTcpSocket sends to a WorkerDelivery-owned localhost receiver; bounded plain-data counts drain on GUI timer, NoProxy and no global cursor override.

Native: Click startButton for full 50 MiB; bytes_written/bytes_received equal total_bytes and both progress bars complete. Start again and close mid-transfer; client aborts, server worker joins, callbacks disconnect and port releases. For quick diagnostics only, set window.TotalBytes to 128 KiB; full acceptance still requires original 50 MiB. Host cursor/windows remain unchanged.

### Batch 7 98f207907001ce47

`Official threadedfortuneserver` — `ports/network/pyqt-official/threadedfortuneserver-98f207907001ce47.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original threaded-server/status/Quit and seven fortunes retained. Unavailable QThread/socket-descriptor Qt worker becomes a cancellable plain Python listener/handler plus GUI timer drain; this bounded worker services accepted requests serially on an owned localhost/free port.

Native: Run probe and several controller-owned localhost clients; each must receive a complete valid Qt_4_0 fortune frame, without Qt access from a worker. Verify sent_count and close while a client is connected/queue is full; worker joins and port releases. Relaunch for fresh endpoint; host stays responsive.

### Final batch-7 gates and evidence

The final exact offline command passes **572 tests in 11.27s**, with zero failures,
errors or skips: **87 cases added** to the 485-test baseline. These include the
27 added generic build/inspect/controls/disconnect/close cases and 60 batch-7
cases covering inert inspection, failed-build rollback, native export/unsafe-call
contracts, real owned localhost TCP/UDP/HTTP, fragmented Qt_4_0 wire framing,
worker stop/join, ports/files/timer release, models/delegates, lazy MIME encoding,
DOM node relationships, formula cycles and arithmetic continuations, paint paths,
owned printing/preview, colour factories, graphics/state controls and local tiles.
The doubles enforce the captured host surface; rendering and virtual dispatch
still require native acceptance. The threaded fortune server services accepted
connections serially in one bounded Python worker; it has no Qt worker thread.
HTTP serves plain local HTTP; internet authentication/SSL/redirect flows are not
exercised under D4. Lightmaps retains its original magnifier and coordinates but
serves a clearly labelled generated offline PNG instead of geographic tiles.

Commands (rtk proxy forwards them unchanged):

```sh
UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
RUFF_CACHE_DIR=/private/tmp/fontlab-ruff-cache python - <<'CHECK'
import ast, json, subprocess
from pathlib import Path
records = json.loads(Path("catalog/ports.json").read_text())["ports"]
files = [r["target_path"] for r in records if r.get("native_checklist", "").startswith("docs/pyqt-official-batch.md#batch-7-")]
assert len(files) == 27
files += ["fontlab_python_examples/official.py", "tests/test_official_batch.py", "tests/official_doubles.py"]
subprocess.run(["ruff", "check", *files], check=True)
subprocess.run(["ruff", "format", "--check", *files], check=True)
for filename in files:
    text = Path(filename).read_text()
    ast.parse(text, feature_version=(3, 11))
    assert "this_file: " + filename in text
print(len(files), "Python 3.11 files checked")
CHECK
git diff --check
git branch --show-current
git rev-parse HEAD
```

Scoped Ruff check/format pass for **30 Python files**; ast.parse with
feature_version=(3, 11) and this_file checks pass for all 30, including all 27 new
ports. A direct hashlib/byte audit verifies **27 original entrypoint hashes**,
**32 verbatim original notices** (including five companion Python headers),
**15 exact resource copies**, **six Echopy native stub hashes**, and structural
identity of **all 101 prior manifest records**. PLAN.md, TODO.md and
catalog/sources.json are byte-identical to HEAD. README is 197 lines. Source
originals were never edited and compiled resource blobs are neither copied nor
executed. No new implementation blocker was found in the exported stubs; all 27
new entries are implemented/unexecuted. The 25 BSD-header entries retain the
existing unresolved collection-GPL scope, while spreadsheet/lightmaps select
explicit GPLv3 alternatives. Asset-specific licence scope remains unresolved.

A final direct review corrected lazy MIME's advertised-format/encoded-data
confusion, callback registration before fetch-more construction completes,
QDateTime email sorting, recursive spreadsheet text dispatch, caller-owned
printer lifetime (preview now owns its printer), integer star ratings, map wrapper
subtraction and feathered magnifier rendering. Fresh tests cover these paths.
Native API inspection used the sibling Echopy stubs and the Qt 5.15 reference
embedded in them; QTcpServer's official documentation was also consulted:
https://doc.qt.io/archives/qt-5.15/qtcpserver.html .

Branch/HEAD remain **issue-101-pythonqt-examples /
2f174565d9ed876681c631409b841bd497d8d637**. No staging or commit. The controller
must run the per-port native checklist above, particularly custom creator/delegate,
item/model/MIME virtual callbacks, animation/OpenGL, PDF/PNG rendering and actual
deferred native destruction. Test doubles and localhost transport do not resolve
those remaining acceptance questions.

## 2026-10-14 — Controller storageview deadline correction

Controller reports 26/27 native batch-7 launch/inspect/close passes, host alive;
storageview exceeded run_python's fixed five-second deadline. The native stub
and controller both confirm mountedVolumes returns a tuple (11 native volumes).
StorageModel now starts empty/loading and scans only in an owned single-shot GUI
timer callback, normalizing to a list and resetting the model. Inspect returns
cached row_count/loading without scans. The shared Demo.defer tracks connections,
stops on close and guards stale callbacks before accessing native objects.

Audited all **142 port Python files** for reads, enumeration, writes and network
work reached during build. Also deferred fetchmore's 205 fixture writes (at most
32 per tick) and its directory listing; deferred dirview sample/root setup.
Other startup reads are bounded pinned assets (largest copied startup image file 42,654
bytes), short sample/UI/animation/word-list files or fixed asset directories.
The larger 235,456-byte audio asset is not read/played during build. Arbitrary
user-file loads/searches are explicit actions; network requests/accept loops
already use async Qt or owned Python workers, with only localhost bind/listen
setup in build. No further expensive synchronous startup scan/request was found.

Eight added regressions first failed, then passed: empty/11-volume tuple scans,
scan error, close before any tick for all three ports, bounded fixture writes and
deferred root setup. Existing model/fixture tests now drive the owned timers.
Exact offline gate: **580 passed**, no failures/errors/skips. Scoped Ruff
check/format and Python 3.11 grammar checks pass; git diff --check passes.
Commands: UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest
-q tests; RUFF_CACHE_DIR=/private/tmp/fontlab-ruff-cache ruff check and ruff format
--check on the three itemview ports, official.py, official_doubles.py and
 test_official_batch.py; ast.parse(feature_version=(3, 11)); git diff --check.

Native rerun: storageview must launch within the deadline, initially show
row_count=0/loading=true, then finish loading the reported 11 volumes outside
run_python; repeated inspect must stay fast. Rerun fetchmore/dirview through
deferred initialization and close before/between timer ticks; verify no writes,
scans or callbacks after close. No native rerun performed here; manifest native
states stay unexecuted. No commit, staging or TODO edits.

## 2026-10-14: Controller native acceptance of pyqt-official batch 7 and full re-runs

Batch 7 (Codex): 27 ports (itemviews, graphicsview, draganddrop, network; network
demos bound to 127.0.0.1 only). First native run 26/27: storageview exceeded the 5 s
run_python deadline (synchronous QStorageInfo.mountedVolumes() model; natively a tuple).
Codex fix: deferred, timer-driven population for storageview, fetchmore and dirview;
offline gate 580 passed. Full native re-runs of all 111 pyqt-official ports in
agent-owned no-document sessions (parent evidence/examples-batch7/): run 1 crashed
FontLab at port 20 (icons, SIGSEGV in QSpinBox.setRange text layout — heap state from
earlier activity; crash-icons-230515.ips); icons alone, ports 1–19 + icons, and
bridge-driver + 1–19 + icons all passed; run 2 passed **111/111, host alive**. The crash
is recorded as an intermittent open host issue (1 of 4 sequence runs).

## 2026-10-14 — Batch 8: remaining 74 official entrypoints

Scope: port or precisely block all 74 remaining pinned pyqt-official entrypoints.
Stay on issue-101-pythonqt-examples; no staging, commit or TODO/PLAN changes.
Read README/PLAN/TODO/WORK/CHANGELOG, port manifest, ownership/launcher/editor
helpers, earlier ports and strict doubles/tests. Baseline exact offline gate:
**580 passed**. A new 16-supported-port test was run first and failed as expected
before implementation. All work performed directly in the current agent.

Result: **16 implemented, 58 blocked**, all native acceptance **unexecuted**.
Together all 187 official candidates are accounted for (127 implemented, 60
blocked), not all natively accepted. Preserve every one of the 128 prior manifest
records structurally. No new package dependency; existing stdlib, PythonQt and
pytest infrastructure suffice. No upstream files or compiled resources modified.

Reuse Demo/ExampleHandle/official tests and strict doubles. Extend Demo with
tracked XML UI loading and an owned QLocalServer fortune service; retain the
existing fortune_packet wire encoding. Every signal uses the existing tracked
connection path. No QApplication creation, nested loops, external network, user
settings, clipboard or user-file writes. Schema's first validation uses an owned
GUI timer, and all temporary socket state belongs to the example. Existing worker
pattern reviewed; no new demo needs a worker or unavailable QThread.

Wait, but: a QWidget existing in QtGui does not make its raw OpenGL functions or
Designer plugin interface available. Six raw-GL ports are precisely blocked,
while the painter-only OpenGL comparison remains real. qtdemo's complete launch
behavior depends on missing Quick/QML/PyQt runtime/external tools; no reduced
gallery is presented as that launcher. QtSql alternatives are documented, not
silently substituted. Module docstrings carry real copyright/licence grants:
retain all five GPL-2.0-or-later notices and Denviso's HPND grant. Boundary tests
inject schema responses and cannot prove native XSD validation or virtual dispatch.

Per-port adaptations and native acceptance checklist (also appended with stable
anchors to docs/pyqt-official-batch.md):

| Source ID | Target | Disposition / adaptation | Native acceptance |
| --- | --- | --- | --- |
| `a1273c8940d43221` | `ports/activeqt/pyqt-official/webbrowser-a1273c8940d43221.py` | blocked: PythonQt does not export QAxContainer; required native APIs: QAxWidget. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `38465a8f4b1a229f` | `ports/dbus/pyqt-official/chat-38465a8f4b1a229f.py` | blocked: PythonQt does not export QtDBus; required native APIs: QDBusAbstractAdaptor, QDBusAbstractInterface, QDBusConnection, QDBusMessage. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `ab719a6a5c3afe4a` | `ports/dbus/pyqt-official/listnames-ab719a6a5c3afe4a.py` | blocked: PythonQt does not export QtDBus; required native APIs: QDBusConnection, QDBusInterface. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `30cfa75ad45b3447` | `ports/dbus/pyqt-official/ping-30cfa75ad45b3447.py` | blocked: PythonQt does not export QtDBus; required native APIs: QDBusConnection, QDBusInterface, QDBusReply. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `57a381bc8260c85d` | `ports/dbus/pyqt-official/pong-57a381bc8260c85d.py` | blocked: PythonQt does not export QtDBus; required native APIs: QDBusConnection. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `54c7440bdcdc3dfc` | `ports/dbus/pyqt-official/car-54c7440bdcdc3dfc.py` | blocked: PythonQt does not export QtDBus; required native APIs: QDBusAbstractAdaptor, QDBusConnection. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `3cf5db95a691d200` | `ports/dbus/pyqt-official/controller-3cf5db95a691d200.py` | blocked: PythonQt does not export QtDBus; required native APIs: QDBusAbstractInterface, QDBusConnection. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `27bf65f8b059fd96` | `ports/designer/pyqt-official/calculatorform-27bf65f8b059fd96.py` | implemented: Original calculatorform.ui loaded with QUiLoader; both valueChanged(int) slots explicitly tracked; original spin ranges and sum display retained. | Verify Calculator Form geometry/labels; set inputSpinBox1=7 and inputSpinBox2=8 then 0; inspect sums 15 then 8. Check spin ranges/keyboard input and both tracked signals. |
| `960c701fa6221ac5` | `ports/designer/pyqt-official/plugins-960c701fa6221ac5.py` | blocked: PythonQt has no QtDesigner module or QPyDesignerCustomWidgetPlugin/QDesignerCustomWidgetInterface and no PyQt Designer Python plugin loader. plugins.py launches external Designer with PYQTDESIGNERPATH/PYTHONPATH; that integration cannot run in the host. Eight plain widgets have separate standalone ports; HelloGLWidget is separately blocked. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `4d24cd77c74a8801` | `ports/designer/pyqt-official/analogclock-4d24cd77c74a8801.py` | implemented: Standalone green clock, hour/minute hands and timezone offsets retained. Owned 1 s timer; native QTime notification converted to JSON text. Designer plugin/meta-properties/signals blocked separately. | Verify green clock hands/ticks and live repaint at 1 s. controls[setTimeZone](-3), then resetTimeZone(); inspect offsets -3/0 and timezone/time notification values; resize and screenshot hands. Close during timer activity. |
| `9941e3c752b3a3b7` | `ports/designer/pyqt-official/bubbleswidget-9941e3c752b3a3b7.py` | implemented: Standalone bubbles retain mouse creation/expansion, rising motion, random gradients, colour/count/author setters and start/stop. All point arithmetic uses components; QColor channels are integers and ellipse uses QRectF; two timers owned. No host-global RNG reseeding. Designer integration separately blocked. | setBubbles(3); inspect three moving positions. Hold left mouse to expand, drag and release a fourth bubble; verify gradients, radii and removal above top. setBubbles(-1) gives zero; stop/start timers and setColor1/setColor2. Close while bubbleTimer and animation_timer are active. |
| `1321540b04f33117` | `ports/designer/pyqt-official/counterlabel-1321540b04f33117.py` | implemented: Standalone counter preserves range/offset/int-and-string notifications and scaled text. Original initial setValue(123) remains out of range so displays 1. QPointF text overload and scalar subtraction replace unsafe overload/negation; zero metrics dimensions guarded. Designer integration separately blocked. | Initial value/min/max are 1. setMaximum(200), setOffset(5), setValue(123); inspect 128 and "128" notifications while painted numeric value remains 123. stepDown, setMinimum(150), out-of-range setValue(-100), then setMaximum(10); verify clamping/range consistency and scaled text under resize. |
| `7ba49e67588b1329` | `ports/designer/pyqt-official/datetimeedit-7ba49e67588b1329.py` | implemented: Both standalone date/time editor subclasses retain popup/calendar settings and resetters. Explicit native protected mousePressEvent; calendarWidget() replaces PyQt typed findChild. Python layout/calendar references have private names. Original Denviso HPND permission retained; collection GPL scope unresolved. Designer integration separately blocked. | Open both calendar popups via native mouse; exercise date and time edits. On dateEdit/dateTimeEdit drive set/reset FirstDayOfWeek, GridVisible, HorizontalHeaderFormat, VerticalHeaderFormat and NavigationBarVisible. Confirm popup values persist and calendarPopup stays true. Close with a calendar popup open. |
| `5941e31267112c98` | `ports/designer/pyqt-official/helloglwidget-5941e31267112c98.py` | blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `de4979a99c6d0bed` | `ports/designer/pyqt-official/multipagewidget-de4979a99c6d0bed.py` | implemented: Original two pages, insertion/removal, combo selection, current-index and page-title setters retained. Private layout name avoids native layout slot shadowing. Python notifications replace unavailable PyQt signals; Designer integration blocked separately. | Verify two original labels/Page 1/Page 2; select second combo item natively. setPageTitle("Second"), insertPage(0, owned QLabel), removePage(0); inspect counts/titles/current index and notifications. Confirm removed page remains owned until cleanup. |
| `773db5c24ae98ffb` | `ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py` | implemented: Original star/polygon path, angle/sides/radii/gradient setters retained. Repair upstream max(3, QColor) typo to copy QColor; minimum three sides and clamped angle retained. Designer integration separately blocked. | Verify five-sided gradient star. setNumberOfSides(0) yields 3; setAngle(400) yields 360; setInnerRadius(12), setOuterRadius(80), setInnerColor/setOuterColor(QColor); screenshot changed path/colours and inspect sides/radii/path element count. |
| `bcfa5de0140286d5` | `ports/designer/pyqt-official/pydemo-bcfa5de0140286d5.py` | implemented: Original read-only HTML, author inheritance and relative text zoom retained; zoom changes exposed in inspect notifications. Designer integration separately blocked. | Verify original read-only HTML and author David Boddie. setZoom(3), setZoom(-2), resetZoom(); inspect notifications and visual font sizes. setAuthor("Example Author"), resetAuthor(); verify author metadata only. |
| `5125860585e98b3a` | `ports/designer/pyqt-official/pythonconsolewidget-5125860585e98b3a.py` | implemented: Original explicit Python expression evaluation, qApp access and successful-command Up/Down history retained. Evaluation starts only on Return/control, never inspect; errors now visible in inspect. No process/global event loop construction. Designer integration separately blocked. | Confirm empty startup/history and no evaluation during inspect. Type 6 * 7 and press Return; inspect output 42/history. Type 1 / 0; retain input, report error, leave history unchanged. Native Up/Down recall/clear; evaluate qApp to confirm existing host application, without changing it. |
| `0ad3432ccdca7ac0` | `ports/ipc/pyqt-official/localfortuneclient-0ad3432ccdca7ac0.py` | implemented: Original seven fortunes, Qt_4_0 UInt16/QString framing and duplicate retry retained. Create an owned QLocalServer peer; lock endpoint to a unique short temporary socket path. Fragmented payload validation and tracked retry/timeout timers; no request in inspect. Abort sockets, close server and remove temporary path on close. | Verify initially listening/sent=0/received=0 and read-only owned endpoint. Click Get Fortune; await host event delivery, inspect one of seven fortunes and sent/received increment. Repeat to exercise duplicate retry; close while request/retry/timeout is pending. Retain evidence socket and temporary directory disappear. |
| `a14d08fe23965bec` | `ports/ipc/pyqt-official/localfortuneserver-a14d08fe23965bec.py` | implemented: Original seven-fortune QLocalServer retained at an owned short unique socket path. Add an explicit owned-client test button; retain status/Quit. Reuse original Qt fortune wire framing. Accepted sockets remain owned by server, aborted before deletion; never remove another server endpoint. | Verify listening status and no startup request. Click Test owned client; await native newConnection/readyRead and original seven-fortune payload; sent/received increment. Repeat, then Quit/hide/reshow; named close aborts accepted/client sockets and removes only this endpoint. |
| `74af8d8d2d7774b8` | `ports/multimedia/pyqt-official/audiodevices-74af8d8d2d7774b8.py` | blocked: PythonQt does not export QtMultimedia; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `c391afd8516131e1` | `ports/multimedia/pyqt-official/audiooutput-c391afd8516131e1.py` | blocked: PythonQt does not export QtMultimedia; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat, QAudioOutput. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `f6d352360ae9bdfb` | `ports/multimediawidgets/pyqt-official/camera-f6d352360ae9bdfb.py` | blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAudioEncoderSettings, QCamera, QCameraImageCapture, QCameraViewfinder, QImageEncoderSettings, QMediaMetaData, QMediaRecorder, QMultimedia, QVideoEncoderSettings. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `5eb4b9eaa2d5c9dc` | `ports/multimediawidgets/pyqt-official/player-5eb4b9eaa2d5c9dc.py` | blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAbstractVideoBuffer, QMediaContent, QMediaMetaData, QMediaPlayer, QMediaPlaylist, QVideoFrame, QVideoProbe, QVideoWidget. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `a57a89e523c75b7f` | `ports/multimediawidgets/pyqt-official/videographicsitem-a57a89e523c75b7f.py` | blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QGraphicsVideoItem, QMediaContent, QMediaPlayer. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `481c128fba3a714b` | `ports/multimediawidgets/pyqt-official/videowidget-481c128fba3a714b.py` | blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QMediaContent, QMediaPlayer, QVideoWidget. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `c82d1af7d1a7b0cf` | `ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py` | implemented: Original native QWidget/OpenGL QOpenGLWidget 30-circle QPainter comparison and Qt text retained. Apply four-sample format only to owned GL widget; no global default-format mutation. Tracked 50 ms timer; both painter contexts always end. | Verify title, Native/OpenGL labels, two 200x200 canvases, 30 animated gradient circles and Qt text. Await timer; inspect equal native_elapsed/opengl_elapsed, wrap at 1000. Retain screenshots of both real paint backends. Check host default surface format unchanged; close with timer active. |
| `303ea3ee09c4677d` | `ports/opengl/pyqt-official/grabber-303ea3ee09c4677d.py` | blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `1ad60855ca28f3cc` | `ports/opengl/pyqt-official/hellogl-1ad60855ca28f3cc.py` | blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `b383fecf912548bb` | `ports/opengl/pyqt-official/openglwindow-b383fecf912548bb.py` | blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `fcada4fff6524fcf` | `ports/opengl/pyqt-official/overpainting-fcada4fff6524fcf.py` | blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `ed6d42d4faa7e0bb` | `ports/opengl/pyqt-official/textures-ed6d42d4faa7e0bb.py` | blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `5a8e48d2a1396cea` | `ports/pyuic/pyqt-official/compile-on-the-fly-5a8e48d2a1396cea.py` | implemented: Exact demo.ui loaded via QUiLoader instead of PyQt loadUiType code generation. Explicit tracked Add-items auto-slot, original Clear and OK wiring. Runtime UI behavior retained; Python code generation itself is unavailable. | Click button1 twice: list contains This/is/a/demo twice, count 8. button2 clears. okButton accepts/hides asynchronously; reshow same root then named close. Confirm original demo.ui size/title/control texts and three tracked connections. |
| `b7db02f540cc7559` | `ports/pyuic/pyqt-official/load-ui1-b7db02f540cc7559.py` | implemented: Exact demo.ui loaded via QUiLoader instead of PyQt loadUi. Track original Clear and OK wiring. Preserve original no-Python-slot behavior: Add items does nothing. | Verify original demo.ui geometry/texts. button1 deliberately leaves list empty, matching original source without Python auto-slot. button2 clears, okButton accepts/hides; two tracked XML connections. Reshow and named close. |
| `b9660f4ee653ca01` | `ports/pyuic/pyqt-official/load-ui2-b9660f4ee653ca01.py` | implemented: Exact demo.ui loaded via QUiLoader, replacing PyQt loadUi(target). Track original Add-items auto-slot, Clear and OK. Root is loader-created owned QDialog; UI behavior retained without generated PyQt classes. | Click button1 twice: inspect eight items; button2 clears; okButton accepts/hides. Reshow and named close. Verify original geometry/texts and three tracked connections; no generated PyQt class or extra event loop. |
| `8847cbce50b72500` | `ports/qml/pyqt-official/adding-8847cbce50b72500.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `dd226ba9fbb7b330` | `ports/qml/pyqt-official/attached-dd226ba9fbb7b330.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `eb7a89f07f63cca7` | `ports/qml/pyqt-official/binding-eb7a89f07f63cca7.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, QQmlProperty, QQmlPropertyValueSource, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `ad499afe23726248` | `ports/qml/pyqt-official/coercion-ad499afe23726248.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `6417cdcf1bfd1752` | `ports/qml/pyqt-official/default-6417cdcf1bfd1752.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `81a6f0d16c203608` | `ports/qml/pyqt-official/grouped-81a6f0d16c203608.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `75ca5ac77ecefd6d` | `ports/qml/pyqt-official/methods-75ca5ac77ecefd6d.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `d0a18273fa604bb6` | `ports/qml/pyqt-official/properties-d0a18273fa604bb6.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `0a13f60f5f0561db` | `ports/qml/pyqt-official/signal-0a13f60f5f0561db.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `738a22ef3062ed51` | `ports/qml/pyqt-official/valuesource-738a22ef3062ed51.py` | blocked: PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, QQmlProperty, QQmlPropertyValueSource, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `85a56a1f3c25ccca` | `ports/qtdemo/pyqt-official/qtdemo-85a56a1f3c25ccca.py` | blocked: The full qtdemo launcher delegates to PyQt executables and qmlscene (menumanager.py launchExample/launchQmlExample), including QtQuick/QtQml examples. FontLab exports neither QtQuick nor QtQml and cannot load PyQt as a second Qt runtime. Qt Assistant remote control is an external dependency too. A reduced menu disabling these launch behaviors would not preserve the pinned launcher; blocked on these composite dependencies, not on QWidget. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `835281a1ab864833` | `ports/quick/pyqt-official/animation-835281a1ab864833.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `36246fcbffecdeba` | `ports/quick/pyqt-official/canvas-36246fcbffecdeba.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `e1316fee99c63555` | `ports/quick/pyqt-official/abstractitemmodel-e1316fee99c63555.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `68d664f95f48ce52` | `ports/quick/pyqt-official/objectlistmodel-68d664f95f48ce52.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `b64d66dbce7274fe` | `ports/quick/pyqt-official/stringlistmodel-b64d66dbce7274fe.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `34538a4e2600b918` | `ports/quick/pyqt-official/customgeometry-34538a4e2600b918.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickItem, QQuickView, QSGFlatColorMaterial, QSGGeometry, QSGGeometryNode, QSGNode, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `6b1f4f5590a5518a` | `ports/quick/pyqt-official/chapter1-basics-6b1f4f5590a5518a.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `8d1557cbfed9c7a0` | `ports/quick/pyqt-official/chapter2-methods-8d1557cbfed9c7a0.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `3cd3713a5dc9f6dc` | `ports/quick/pyqt-official/chapter3-bindings-3cd3713a5dc9f6dc.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `831ac8ea61da03f3` | `ports/quick/pyqt-official/chapter4-custompropertytypes-831ac8ea61da03f3.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQuickItem, QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `b88e7eb0fcb53264` | `ports/quick/pyqt-official/chapter5-listproperties-b88e7eb0fcb53264.py` | blocked: PythonQt does not export QtQuick / QtQml; required native APIs: QQmlListProperty, QQuickItem, QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `4dbe92cd1e720dce` | `ports/remoteobjects/pyqt-official/modelviewclient-4dbe92cd1e720dce.py` | blocked: PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectNode. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `781a3a959215eb81` | `ports/remoteobjects/pyqt-official/modelviewserver-781a3a959215eb81.py` | blocked: PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectHost, QRemoteObjectRegistryHost. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `54cbd9afababdf71` | `ports/remoteobjects/pyqt-official/directconnectdynamicclient-54cbd9afababdf71.py` | blocked: PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectNode. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `2f1e2f679775d89e` | `ports/remoteobjects/pyqt-official/directconnectdynamicserver-2f1e2f679775d89e.py` | blocked: PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectHost. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `333f0272885ca1b7` | `ports/remoteobjects/pyqt-official/registryconnecteddynamicclient-333f0272885ca1b7.py` | blocked: PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectNode. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `b83377c9b48aec14` | `ports/remoteobjects/pyqt-official/registryconnecteddynamicserver-b83377c9b48aec14.py` | blocked: PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectHost, QRemoteObjectRegistryHost. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `0b0d8d2fae153e5e` | `ports/sql/pyqt-official/cachedtable-0b0d8d2fae153e5e.py` | blocked: PythonQt does not export QtSql; required native APIs: QSqlTableModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `2c4c366f259d7d80` | `ports/sql/pyqt-official/querymodel-2c4c366f259d7d80.py` | blocked: PythonQt does not export QtSql; required native APIs: QSqlQuery, QSqlQueryModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `9030a87a532b8d8f` | `ports/sql/pyqt-official/relationaltablemodel-9030a87a532b8d8f.py` | blocked: PythonQt does not export QtSql; required native APIs: QSqlQuery, QSqlRelation, QSqlRelationalDelegate, QSqlRelationalTableModel, QSqlTableModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `0677ebfd7fa2cc60` | `ports/sql/pyqt-official/tablemodel-0677ebfd7fa2cc60.py` | blocked: PythonQt does not export QtSql; required native APIs: QSqlTableModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `8d5ea81a74e30222` | `ports/webkit/pyqt-official/domtraversal-8d5ea81a74e30222.py` | blocked: PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `f4000cf8ca288375` | `ports/webkit/pyqt-official/fancybrowser-f4000cf8ca288375.py` | blocked: PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `6ed36280660df7ea` | `ports/webkit/pyqt-official/formextractor-6ed36280660df7ea.py` | blocked: PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `ca47b83fbf3f31b9` | `ports/webkit/pyqt-official/framecapture-ca47b83fbf3f31b9.py` | blocked: PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `47298251b3c83ecf` | `ports/webkit/pyqt-official/previewer-47298251b3c83ecf.py` | blocked: PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `ae16288fede27692` | `ports/webkit/pyqt-official/simpleselector-ae16288fede27692.py` | blocked: PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. | Verify recorded absent modules/members; launch(id) must fail with its exact blocker before host/UI/network/process access; registry and FontLab state unchanged. |
| `1e5d0f7289e1b36e` | `ports/xmlpatterns/pyqt-official/schema-1e5d0f7289e1b36e.py` | implemented: Exact schema.ui, three XSDs and six XML instances copied. Preserve native QXmlSchema/Validator, native diagnostic callback, highlighter and error cursor/full-width selection. Defer initial validation to owned timer. Reject DTD/entities/schema locations/imports/includes before native evaluation; QByteArray plus explicit empty base QUrl prevents URL-loading overloads. No stdlib XSD substitute. | Launch under 5 s with loading=true/valid=null. After owned initializeTimer, validate all six original instances across Contact/Recipe/Order: valid=true for three valid, false for three invalid, native diagnostic line/column and full-width red selection. Edit malformed XML then correct it; verify syntax colours and multi-line comments. Test DTD/external schemaLocation input: report rejection without outbound traffic. Close before initialization and after diagnostics; verify handler/highlighter/timer destruction. |


Verification commands and final results:

```sh
UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
# 685 passed in 13.42s; no failures, errors or skips (baseline 580).
```

Scoped `RUFF_CACHE_DIR=/private/tmp/fontlab-ruff-cache ruff check` and
`ruff format --check` on all 74 new ports plus official.py,
official_doubles.py, test_official_batch.py and test_ports.py: **78 files pass**.
`ast.parse(..., feature_version=(3, 11))` and this_file checks pass for all 78.
`git diff --check` passes. Strict native regressions plus official tests passed
**527 tests** before the final full gate. All new blocked builds and named
launches reject before host access; all new implemented rows exercise the existing
build/inspect/control/disconnect-before-delete/close parametrization. XML tests
inject native validator responses; they do not implement or verify an XSD engine.
Local IPC transport tests use actual owned Unix sockets, with fragmented/malformed
frames, timeout, pending close and endpoint removal covered.

Direct hashlib/byte audit: **74 original entrypoint hashes, 76 verbatim original
notices (including two companion Python headers), 14 exact resource copies, eight
Echopy module stub hashes**. All **128 prior manifest records** are structurally
unchanged. PLAN.md, TODO.md and catalog/sources.json remain byte-identical to HEAD.
No PyQt/PySide import, compiled resource blob, new dependency or native FontLab
execution was introduced. No commit or staging. Source IDs in README, manifest,
per-port native checklist anchors and this work log cover all 74 rows.

Open acceptance questions: native protected/virtual callback dispatch in the
standalone painters/date editors/highlighters/schema message handler; actual
OpenGL framebuffer rendering and unchanged host format; QLocalServer/Socket
native delivery and asynchronous socket teardown; six real Qt XSD outcomes;
loaded UI geometry and deferred QObject destruction. The controller must run the
individual native checklists above and preserve host-alive/destruction evidence.
Licence scope remains unresolved for 64 BSD/GPL records, the Denviso HPND/GPL
record and assets without individual notices. The 58 capability blockers remain
blocked until actual missing APIs/dependencies are supplied or a behavior change
is explicitly approved. No substitute is counted as an implementation.

Final direct review also preserves ET boundary parse-error line/column in the schema error selection. Verified all 12 absent module stubs and missing QOpenGLContext.versionFunctions / QOpenGLFunctions_1_1 / QOpenGLFunctions_2_0 against the current native stub source. The complete offline gate was rerun after this source correction.

Final post-correction offline gate: **685 passed in 12.64s**. Scoped Ruff check/format and Python 3.11 grammar: **78 files pass**. git diff --check passes; branch/HEAD remain issue-101-pythonqt-examples / 948cd13; staging is empty.

## 2026-10-14: Controller native acceptance of pyqt-official batch 8 (all remaining entrypoints)

Codex accounted for the last 74 pyqt-official entrypoints: 16 implemented, 58 blocked with
exact missing native modules/classes (QtQml/QtQuick, QtWebKit*, QtDBus, QtSql,
QtMultimedia*, QtRemoteObjects, QtDesigner, ActiveQt). Offline gate 685 passed (controller
rerun). Native launch/inspect/close of the 16 implemented ports in an agent-owned
no-document session: **16/16 pass, host alive** (parent evidence/examples-batch8/native.jsonl).
A sample of 5 blocked records raises NotImplementedError at launch with the host alive
(native-blocked-sample.jsonl). Catalog: 202 records (138 implemented, 64 blocked); every
pyqt-official entrypoint is now ported or precisely blocked.


## 2026-10-14: Remaining 97 entrypoints, batch 9 (native unexecuted)

Scope: all 94 QtExamples entrypoints and the last three numbered chats.
Result: 10 implemented, 87 precise blockers. Stay on issue-101-pythonqt-examples;
no staging, commit or native execution. All 202 prior manifest records, pinned
originals, catalog/sources.json, PLAN.md and TODO.md remain unchanged.

Read README/PLAN/TODO/WORK, source/port catalogs, handle/launcher/editor, existing
numbered and insight worker ports, official Demo/WorkerDelivery/LocalServer/IPC
ports, doubles and tests before implementation. Baseline gate: 685 passed in
13.04 s. Cache default was not writable; reran with the existing writable
/private/tmp/fontlab-uv-cache, offline throughout. Wrote the exact 97-entry
coverage test first; observed expected failure before implementation.

Wait, but source-level candidates and doubles cannot establish functioning
FontLab ports: the 87 missing-capability records remain blocked and all 97
native states remain unexecuted. Keep the ambiguity/QML/auxiliary scope intact.
Qt backend matplotlib is not Agg-only, so no unverified matplotlib install
or fake static-canvas replacement is counted. Strict interaction tests exposed
a QWindow flags property read; corrected via read(). Doubles now preserve
HTTP query strings, appendPlainText/appendRow/clear behavior and read-only state.

Every adaptation and exact native acceptance checklist is recorded below.

| ID | Target path | Result | Licence | Notable adaptations / blocker |
| --- | --- | --- | --- | --- |
| `93131a29a3b71ea3` | `ports/graphics-painting/eyllanesc/main-93131a29a3b71ea3.py` | blocked | GPL-3.0-only | PythonQt does not export QtCharts (QtChart); required native APIs: QAreaSeries, QChart, QChartView, QLineSeries. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `e1c73422208670cb` | `ports/multimedia/eyllanesc/main-e1c73422208670cb.py` | blocked | GPL-3.0-only | PythonQt does not export QtCharts (QtChart); required native APIs: QChart, QChartView, QLineSeries, QValueAxis, QXYSeries. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `9fed8c2f3765272b` | `ports/graphics-painting/eyllanesc/main-9fed8c2f3765272b.py` | blocked | GPL-3.0-only | PythonQt does not export QtCharts (QtChart); required native APIs: QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QValueAxis. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `c862c1b57a0a0412` | `ports/charts/eyllanesc/main-c862c1b57a0a0412.py` | blocked | GPL-3.0-only | PythonQt does not export QtCharts (QtChart); required native APIs: QBarCategoryAxis, QBarSeries, QChart, QChartView, QVBarModelMapper, QValueAxis. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `f9107c0d26ffc4aa` | `ports/graphics-painting/eyllanesc/main-f9107c0d26ffc4aa.py` | blocked | GPL-3.0-only | PythonQt does not export QtCharts (QtChart); required native APIs: QBoxPlotSeries, QBoxSet, QChart, QChartView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `6bd9cbb60a6ac008` | `ports/charts/eyllanesc/main-6bd9cbb60a6ac008.py` | blocked | GPL-3.0-only | PythonQt does not export QtCharts (QtChart); required native APIs: QChart, QLineSeries, QSplineSeries. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `032d404c69db6baa` | `ports/graphics-painting/eyllanesc/main-032d404c69db6baa.py` | blocked | GPL-3.0-only | PythonQt does not export QtCharts (QtChart); required native APIs: QCandlestickSeries, QCandlestickSet, QChart, QChartView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `4bc27e706ac146f5` | `ports/corelib/eyllanesc/main-4bc27e706ac146f5.py` | implemented | GPL-3.0-only | Reuse the existing local IPC port with an owned unique endpoint and explicit peer. Preserve Qt 5.10 UInt32 + QString framing; correct upstream len(message) prefix to serialized payload byte length and currentFortune assignment/hostLineEdit.ext typo. Inert inspection, timeout, duplicate retry timer and socket abort before close. |
| `cb1871959e42607b` | `ports/corelib/eyllanesc/main-cb1871959e42607b.py` | implemented | GPL-3.0-only | Reuse the existing local IPC port with an owned unique endpoint and explicit peer. Preserve Qt 5.10 UInt32 + QString framing; correct upstream len(message) prefix to serialized payload byte length and currentFortune assignment/hostLineEdit.ext typo. Inert inspection, timeout, duplicate retry timer and socket abort before close. |
| `04e8e49f95de6cf5` | `ports/corelib/eyllanesc/dialog-ui-04e8e49f95de6cf5.py` | blocked | GPL-3.0-only | PythonQt.QtCore.QSharedMemory lacks detach(). The associated Dialog requires native shared-memory image exchange and explicit detach; the generated UI entrypoint launches that same Dialog. An owned segment cannot be implemented and safely released. |
| `24b0b2aa8998d701` | `ports/corelib/eyllanesc/main-24b0b2aa8998d701.py` | blocked | GPL-3.0-only | PythonQt.QtCore.QSharedMemory lacks detach(). The associated Dialog requires native shared-memory image exchange and explicit detach; the generated UI entrypoint launches that same Dialog. An owned segment cannot be implemented and safely released. |
| `7bddaa324636868a` | `ports/platform/eyllanesc/ping-7bddaa324636868a.py` | blocked | GPL-3.0-only | PythonQt does not export QtDBus; required native APIs: QDBusConnection, QDBusInterface, QDBusReply. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `fa5e7696ac61b89f` | `ports/platform/eyllanesc/pong-fa5e7696ac61b89f.py` | blocked | GPL-3.0-only | PythonQt does not export QtDBus; required native APIs: QDBusConnection, QDBusInterface, QDBusReply. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `9d1a670d70c19b6a` | `ports/qml/eyllanesc/main-9d1a670d70c19b6a.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQuickView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `3299c18eadf92b5d` | `ports/qml/eyllanesc/main-3299c18eadf92b5d.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQuickView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `f581c1e4f121df88` | `ports/qml/eyllanesc/main-f581c1e4f121df88.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `2529316479664459` | `ports/qml/eyllanesc/main-2529316479664459.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQuickView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `6386ec6f1ca4ffd4` | `ports/qml/eyllanesc/main-6386ec6f1ca4ffd4.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQmlApplicationEngine, QQmlContext, QQuickWindow. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `92fc3cf4b5dd009c` | `ports/embedded/eyllanesc/main-92fc3cf4b5dd009c.py` | implemented | GPL-3.0-only | Reuse the previously adapted LightMaps/SlippyMap/MapZoom behavior: owned localhost tile fixture/cache and numeric component geometry instead of wrapper operators; preserve city actions, night inversion, 701 ms hold and magnifier/pan. About opens an owned asynchronous notice, never external OpenStreetMap. Fix upstream fractional dimensions and zoomPixmap variable error. |
| `631cc1bc310c00b9` | `ports/embedded/eyllanesc/main-631cc1bc310c00b9.py` | implemented | GPL-3.0-only | Exact stylewidget.ui and all eight QSS/image files copied. QUiLoader connections reconnected explicitly through Demo; style button auto-slots wired explicitly. QSS applies only to the owned window, not QApplication; full-screen launch and application/organization metadata writes removed. Preserve value/scrollbar/show/enable wiring. |
| `3525151ac8d550f5` | `ports/graphics-painting/eyllanesc/main-3525151ac8d550f5.py` | blocked | GPL-3.0-only | PythonQt.QtGui.QGradient lacks the NightFade preset and its preset constructor overload, required by RasterWindow.renderNow for its exact background. QWindow/QBackingStore exist, but a replacement gradient is not supplied. |
| `a207ef153f0b81b7` | `ports/threads-processes/eyllanesc/main-a207ef153f0b81b7.py` | blocked | GPL-3.0-only | The original launcher spawns sys.executable with a PyQt5/PySide2 binding and launches quickcontrols2/gallery, which requires absent QtQml/QtQuick/QtQuickControls2. PythonQt also has no Python Signal/Slot declaration API. Replacing it with the in-host examples launcher changes its subprocess/binding-selection behavior; it is blocked. |
| `0d72445fb116793d` | `ports/network/eyllanesc/audiodevicesbase-ui-0d72445fb116793d.py` | blocked | GPL-3.0-only | PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `307534c4e8e2211c` | `ports/multimedia/eyllanesc/main-307534c4e8e2211c.py` | blocked | GPL-3.0-only | PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `eea833917398267a` | `ports/network/eyllanesc/main-eea833917398267a.py` | blocked | GPL-3.0-only | PythonQt.QtCore has no QXmlStreamReader, required by GSuggestCompletion.handleNetworkData to parse suggestions. A stdlib XML parser plus owned localhost suggestion/search server is a possible behavior-preserving future adaptation; this record does not claim that substitution is implemented. |
| `ecc2e23449331df1` | `ports/network/eyllanesc/main-ecc2e23449331df1.py` | implemented | GPL-3.0-only | Reuse the existing 50 MiB/64 KiB loopback transfer implementation; owned 127.0.0.1 receiver and native QTcpSocket sender. Replace unparented server, blocking retry dialog, global cursor and premature deleteLater with owned Python receiver/timer delivery and tracked cleanup. |
| `ccad55f9e06bfa93` | `ports/platform/eyllanesc/main-ccad55f9e06bfa93.py` | blocked | GPL-3.0-only | PythonQt does not export QtPositioning; required native APIs: QGeoCoordinate, QGeoPositionInfo, QGeoPositionInfoSource. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `0b7e380ab45addbd` | `ports/graphics-painting/eyllanesc/main-0b7e380ab45addbd.py` | blocked | GPL-3.0-only | PythonQt.QtGui.QMatrix4x4 exposes neither __mul__ nor a matrix-product method. PaintedWindow.paintEvent requires projection * view * model; wrapper arithmetic is forbidden in FontLab. QRasterWindow exists, but numeric matrix replacement is not implemented. |
| `b1c25455dbcb6bac` | `ports/graphics-painting/eyllanesc/main-b1c25455dbcb6bac.py` | implemented | GPL-3.0-only | Preserve native QWindow/QBackingStore, two top-level windows, Window B child and extra-screen windows. Owned QTimer replaces startTimer; explicit finally ends image/backing painters before endPaint/flush. Per-build colors, explicit backing-store delete and subclass-reference release. Demo/launcher now distinguish QWindow from QWidget without assigning native widget attributes. Preserve original Backspace rule. |
| `8284e0348b6f7020` | `ports/qml/eyllanesc/main-8284e0348b6f7020.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `b4d27c5a05969f77` | `ports/qml/eyllanesc/main-b4d27c5a05969f77.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQmlApplicationEngine, QQuickStyle. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `f5ecef06968ffad8` | `ports/qml/eyllanesc/main-f5ecef06968ffad8.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `bd4a25944ae5b2d7` | `ports/qml/eyllanesc/main-bd4a25944ae5b2d7.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `9e402cdc525108dd` | `ports/qml/eyllanesc/main-9e402cdc525108dd.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `3ed66f4363a81cf2` | `ports/platform/eyllanesc/main-3ed66f4363a81cf2.py` | blocked | GPL-3.0-only | PythonQt does not export QtSerialPort; required native APIs: QSerialPortInfo. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `b2127700642ffb25` | `ports/platform/eyllanesc/main-b2127700642ffb25.py` | blocked | GPL-3.0-only | PythonQt does not export QtSerialPort; required native APIs: QSerialPortInfo. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `a3c7c0e56d0452cf` | `ports/database/eyllanesc/main-a3c7c0e56d0452cf.py` | blocked | GPL-3.0-only | PythonQt does not export QtSql; required native APIs: QSqlDatabase, QSqlQuery, QSqlTableModel. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. |
| `5b93264cdefad0d7` | `ports/database/eyllanesc/main-5b93264cdefad0d7.py` | blocked | GPL-3.0-only | PythonQt does not export QtSql; required native APIs: QSqlDatabase, QSqlQuery, QSqlRelation, QSqlRelationalDelegate, QSqlRelationalTableModel. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. |
| `fd7c0bbed85eb2d4` | `ports/database/eyllanesc/main-fd7c0bbed85eb2d4.py` | blocked | GPL-3.0-only | PythonQt does not export QtSql; required native APIs: QSqlDatabase, QSqlQuery, QSqlRelation, QSqlRelationalDelegate, QSqlRelationalTableModel, QSqlTableModel. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. |
| `b92988bc55b506ee` | `ports/webengine/eyllanesc/main-b92988bc55b506ee.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick / QtWebEngine; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `ea0deb959e907448` | `ports/webengine/eyllanesc/main-ea0deb959e907448.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick / QtWebEngine; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `da960851c5ad3baa` | `ports/webengine/eyllanesc/main-da960851c5ad3baa.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick / QtWebEngine; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `5646535663e933c0` | `ports/webengine/eyllanesc/main-5646535663e933c0.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick / QtWebEngine; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `a4f928dfc9be8596` | `ports/webengine/eyllanesc/main-a4f928dfc9be8596.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEnginePage, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `e6abb656a88ccad4` | `ports/webengine/eyllanesc/cookiedialog-ui-e6abb656a88ccad4.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEngineCookieStore, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `1e800054206a98ec` | `ports/webengine/eyllanesc/cookiewidget-ui-1e800054206a98ec.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEngineCookieStore, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `0dfe1b3b36d41c8d` | `ports/webengine/eyllanesc/main-0dfe1b3b36d41c8d.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEngineCookieStore, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `8460861d4a65f625` | `ports/webengine/eyllanesc/mainwindow-ui-8460861d4a65f625.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEngineCookieStore, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `1f671605e1034b71` | `ports/webengine/eyllanesc/main-1f671605e1034b71.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEnginePage. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `72838df47d1eddc0` | `ports/webengine/eyllanesc/main-72838df47d1eddc0.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEnginePage, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `a7eae99cebfb1806` | `ports/webengine/eyllanesc/main-a7eae99cebfb1806.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEnginePage, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `2253cce5a4c3a077` | `ports/webengine/eyllanesc/mainwindow-ui-2253cce5a4c3a077.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEnginePage, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `23d091dcf5a72224` | `ports/webengine/eyllanesc/main-23d091dcf5a72224.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `c9510fb6daa7d1bd` | `ports/webengine/eyllanesc/main-c9510fb6daa7d1bd.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEnginePage, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `7fece60acaf2b392` | `ports/webengine/eyllanesc/main-7fece60acaf2b392.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEnginePage, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `856b2b33c69b4e19` | `ports/webengine/eyllanesc/main-856b2b33c69b4e19.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `11ec97a8c43a5283` | `ports/webengine/eyllanesc/main-11ec97a8c43a5283.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEnginePage, QWebEngineProfile, QWebEngineUrlRequestJob, QWebEngineUrlScheme, QWebEngineUrlSchemeHandler, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `768c423bdd1fa074` | `ports/network/eyllanesc/main-768c423bdd1fa074.py` | blocked | GPL-3.0-only | PythonQt does not export QtWebSockets; required native APIs: QWebSocketServer. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `edeef5f840c20e15` | `ports/network/eyllanesc/google-search-edeef5f840c20e15.py` | implemented | GPL-3.0-only | Preserve QString completion/model/toolbar XML query and response behavior against owned localhost HTTP suggestions. Replace lib.py custom signals and blocking QEventLoop in splitPath with textEdited debounce and asynchronous replies; abort old reply and disconnect before delete, two-second request timeout, refuse redirects, parse with original stdlib ElementTree. No external Google request. |
| `08ba2f1b1fe02894` | `ports/qml/eyllanesc/main-08ba2f1b1fe02894.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtQuick; required native APIs: QQmlApplicationEngine. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `a0ac1b252a14609e` | `ports/gstreamer/eyllanesc/main-a0ac1b252a14609e.py` | blocked | GPL-3.0-only | PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QMediaContent, QMediaPlayer, QVideoWidget. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. The Qt GStreamer pipeline player/video sink is also unavailable. |
| `f13380d705146bff` | `ports/matplotlib/eyllanesc/subplot-f13380d705146bff.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `52871219c50cdd21` | `ports/matplotlib/eyllanesc/barchart-demo-52871219c50cdd21.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `7cc9bd76e925db18` | `ports/matplotlib/eyllanesc/date-7cc9bd76e925db18.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `b76dc05cb743e9fc` | `ports/matplotlib/eyllanesc/ellipse-demo-b76dc05cb743e9fc.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `43f4640a040ded3e` | `ports/matplotlib/eyllanesc/fill-43f4640a040ded3e.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `26b75bfff47f567d` | `ports/matplotlib/eyllanesc/histogram-features-26b75bfff47f567d.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `5354655012c2060e` | `ports/matplotlib/eyllanesc/image-demo-5354655012c2060e.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `6cb023a08571bf96` | `ports/matplotlib/eyllanesc/legend-6cb023a08571bf96.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `1ffcdfb872b0e689` | `ports/matplotlib/eyllanesc/log-demo-1ffcdfb872b0e689.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `8fc6773f10b89095` | `ports/matplotlib/eyllanesc/main-8fc6773f10b89095.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas and NavigationToolbar2QT, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `5c181bebc7c9773c` | `ports/matplotlib/eyllanesc/path-patch-5c181bebc7c9773c.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `e2f27c6394aa70c8` | `ports/matplotlib/eyllanesc/pcolormesh-levels-e2f27c6394aa70c8.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `5d8303b0b2237124` | `ports/matplotlib/eyllanesc/pie-features-5d8303b0b2237124.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `19398065f86e2762` | `ports/matplotlib/eyllanesc/plot-streamplot-19398065f86e2762.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `80aa961de86e1704` | `ports/matplotlib/eyllanesc/polar-demo-80aa961de86e1704.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `2588c05ccd043d91` | `ports/matplotlib/eyllanesc/scatter-demo2-2588c05ccd043d91.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `8cb9580232bd8081` | `ports/matplotlib/eyllanesc/simple-plot-8cb9580232bd8081.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `207f7ce534696c20` | `ports/matplotlib/eyllanesc/subplot-207f7ce534696c20.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `96777c686c66d526` | `ports/matplotlib/eyllanesc/surface3d-96777c686c66d526.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `d82b14fd5e1eb010` | `ports/matplotlib/eyllanesc/table-demo-d82b14fd5e1eb010.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `ee1562b25c092ee8` | `ports/matplotlib/eyllanesc/tex-demo-ee1562b25c092ee8.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `60a3d030c4744735` | `ports/matplotlib/eyllanesc/buttons-60a3d030c4744735.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `f5d13b3c5b699ab3` | `ports/matplotlib/eyllanesc/check-buttons-f5d13b3c5b699ab3.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `620da7edd0cd23fc` | `ports/matplotlib/eyllanesc/cursor-620da7edd0cd23fc.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `c6effccd6f31f416` | `ports/matplotlib/eyllanesc/lasso-selector-demo-c6effccd6f31f416.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `f2767c945bece214` | `ports/matplotlib/eyllanesc/menu-f2767c945bece214.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `21a081a01365c096` | `ports/matplotlib/eyllanesc/multicursor-21a081a01365c096.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `22be270b0ff2abf7` | `ports/matplotlib/eyllanesc/radio-buttons-22be270b0ff2abf7.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `01be5e33878e4940` | `ports/matplotlib/eyllanesc/rectangle-selector-01be5e33878e4940.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `9007853b5b845ed9` | `ports/matplotlib/eyllanesc/slider-demo-9007853b5b845ed9.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `1862a5f7d89bd9b6` | `ports/matplotlib/eyllanesc/span-selector-1862a5f7d89bd9b6.py` | blocked | GPL-3.0-only | The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed. |
| `b3c5b8f7bcf09a1d` | `ports/video-overlay/eyllanesc/main-b3c5b8f7bcf09a1d.py` | blocked | GPL-3.0-only | PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QGraphicsVideoItem, QMediaContent, QMediaPlayer. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `e9392311a500d3dd` | `ports/video-overlay/eyllanesc/main-e9392311a500d3dd.py` | blocked | GPL-3.0-only | PythonQt does not export QtQml / QtMultimedia; required native APIs: QAbstractVideoBuffer, QAbstractVideoFilter, QAbstractVideoSurface, QQmlApplicationEngine, QVideoFilterRunnable, QVideoFrame, QVideoSurfaceFormat, qmlRegisterType. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. |
| `1e79bddb6d52574d` | `ports/network/pyqt-examples/01-single-threaded-1e79bddb6d52574d.py` | implemented | MIT | Replace third-party chat HTTP endpoint with an owned localhost service and console input with owned name field. stdlib HTTPConnection replaces requests; 250 ms deadline. Preserve single GUI-thread 1000 ms polling pattern with bounded local requests. Stop/join workers before disconnect/delete; no dependency installed. |
| `88fa78cafb505cfa` | `ports/network/pyqt-examples/02-multithreaded-88fa78cafb505cfa.py` | implemented | MIT | Replace third-party chat HTTP endpoint with an owned localhost service and console input with owned name field. stdlib HTTPConnection replaces requests; 250 ms deadline. Cancellable Python worker, bounded plain-data queue and GUI timer drain replace infinite daemon/threadutil signals; 1000 ms display cadence. Stop/join workers before disconnect/delete; no dependency installed. |
| `83bc55d45ae367d0` | `ports/network/pyqt-examples/03-with-threadutil-83bc55d45ae367d0.py` | implemented | MIT | Replace third-party chat HTTP endpoint with an owned localhost service and console input with owned name field. stdlib HTTPConnection replaces requests; 250 ms deadline. Cancellable Python worker, bounded plain-data queue and GUI timer drain replace infinite daemon/threadutil signals; 30 ms GUI delivery cadence. Stop/join workers before disconnect/delete; no dependency installed. |


| ID | Native acceptance checklist |
| --- | --- |
| `93131a29a3b71ea3` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("93131a29a3b71ea3") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `e1c73422208670cb` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("e1c73422208670cb") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `9fed8c2f3765272b` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("9fed8c2f3765272b") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `c862c1b57a0a0412` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("c862c1b57a0a0412") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `f9107c0d26ffc4aa` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("f9107c0d26ffc4aa") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `6bd9cbb60a6ac008` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("6bd9cbb60a6ac008") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `032d404c69db6baa` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("032d404c69db6baa") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `4bc27e706ac146f5` | Launch under 5 s; endpoint is a unique owned Unix socket, hostLineEdit read-only. Click getFortuneButton twice; inspect fortune/received/pending and verify seven original fortunes and UInt32/Qt QString frames. Request Unicode from an owned peer; fragmented/truncated frames and requestTimer timeout report an error without host changes. Close while pending and while retryTimer is active, relaunch; socket path gone, all timers stopped, slots disconnected and owned objects destroyed. |
| `cb1871959e42607b` | Launch under 5 s; listening=true on a unique owned Unix socket. Click getFortuneButton (Test owned client); observe sent and received, fortune text and UInt32/Qt QString payload. Check fragmented frame/error/timeout handling. Close while a peer is connected, verify server/socket/timer destruction and endpoint removal; relaunch creates a new endpoint. |
| `04e8e49f95de6cf5` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("04e8e49f95de6cf5") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `24b0b2aa8998d701` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("24b0b2aa8998d701") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `7bddaa324636868a` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("7bddaa324636868a") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `fa5e7696ac61b89f` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("fa5e7696ac61b89f") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `9d1a670d70c19b6a` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("9d1a670d70c19b6a") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `3299c18eadf92b5d` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("3299c18eadf92b5d") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `f581c1e4f121df88` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("f581c1e4f121df88") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `2529316479664459` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("2529316479664459") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `6386ec6f1ca4ffd4` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("6386ec6f1ca4ffd4") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `92fc3cf4b5dd009c` | Launch Light Maps under 5 s; no external network, localhost tiles/cache only. Drive osloAction/berlinAction/jakartaAction, nightModeAction, arrow keys, Z magnifier, mouse pan/701 ms hold and resize; inspect latitude/longitude/zoom/night_mode/tile_count and magnifier state. About opens only an owned asynchronous notice. Check visual magnifier/city/pan/inversion behavior, close during tile request and drag; timers/workers/sockets/cache stop and disappear, host stays alive. |
| `631cc1bc310c00b9` | Launch original Form UI under 5 s; spinBox and both horizontalScrollBars track values in both directions. Drive pushButton Enable and pushButton_2 Show toggles. Click blueStyle/khakiStyle/transparentStyle/noStyle, verify original images/QSS and owned-window-only styling. Verify no full-screen takeover or QApplication identity/style change; close and relaunch, destroy UI/loader/buffer and disconnect all declared/explicit callbacks. |
| `3525151ac8d550f5` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("3525151ac8d550f5") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `a207ef153f0b81b7` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("a207ef153f0b81b7") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `0d72445fb116793d` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("0d72445fb116793d") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `307534c4e8e2211c` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("307534c4e8e2211c") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `eea833917398267a` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("eea833917398267a") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `ecc2e23449331df1` | Launch under 5 s; inspection sends no data. Click startButton: transfer exact 50 MiB in 64 KiB chunks against owned 127.0.0.1 receiver, bytes_written/bytes_received reach total_bytes and progress bars finish. Repeat; error state is owned and no global cursor change. Close mid-transfer; native tcpClient aborts, receiver worker joins and free port is released before widgets are deleted. |
| `ccad55f9e06bfa93` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("ccad55f9e06bfa93") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `0b7e380ab45addbd` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("0b7e380ab45addbd") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `b1c25455dbcb6bac` | Launch under 5 s; two native QWindow top levels (Window A/B), ChildOfB, plus one window per non-primary screen. Inspect window_count/windows titles/colors/geometry/image_size/text. Type/draw in each, Enter/Backspace (source keeps final one-character text), resize without losing old strokes; exercise renderTimerN and real expose/resize callbacks. Verify native QBackingStore paint begins, painters end, endPaint then flush. Close/relaunch including pending render; timers stop, backing stores deleted exactly once, all QWindows/children destroyed, host alive and screen/host state unchanged. |
| `8284e0348b6f7020` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("8284e0348b6f7020") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `b4d27c5a05969f77` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("b4d27c5a05969f77") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `f5ecef06968ffad8` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("f5ecef06968ffad8") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `bd4a25944ae5b2d7` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("bd4a25944ae5b2d7") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `9e402cdc525108dd` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("9e402cdc525108dd") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `3ed66f4363a81cf2` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("3ed66f4363a81cf2") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `b2127700642ffb25` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("b2127700642ffb25") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `a3c7c0e56d0452cf` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("a3c7c0e56d0452cf") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `5b93264cdefad0d7` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("5b93264cdefad0d7") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `fd7c0bbed85eb2d4` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("fd7c0bbed85eb2d4") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `b92988bc55b506ee` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("b92988bc55b506ee") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `ea0deb959e907448` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("ea0deb959e907448") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `da960851c5ad3baa` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("da960851c5ad3baa") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `5646535663e933c0` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("5646535663e933c0") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `a4f928dfc9be8596` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("a4f928dfc9be8596") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `e6abb656a88ccad4` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("e6abb656a88ccad4") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `1e800054206a98ec` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("1e800054206a98ec") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `0dfe1b3b36d41c8d` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("0dfe1b3b36d41c8d") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `8460861d4a65f625` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("8460861d4a65f625") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `1f671605e1034b71` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("1f671605e1034b71") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `72838df47d1eddc0` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("72838df47d1eddc0") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `a7eae99cebfb1806` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("a7eae99cebfb1806") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `2253cce5a4c3a077` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("2253cce5a4c3a077") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `23d091dcf5a72224` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("23d091dcf5a72224") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `c9510fb6daa7d1bd` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("c9510fb6daa7d1bd") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `7fece60acaf2b392` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("7fece60acaf2b392") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `856b2b33c69b4e19` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("856b2b33c69b4e19") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `11ec97a8c43a5283` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("11ec97a8c43a5283") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `768c423bdd1fa074` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("768c423bdd1fa074") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `edeef5f840c20e15` | Launch 640x60 line edit under 5 s; inspection causes no request. Type Unicode to drive textEdited/suggestTimer or invoke search; expect exact input, input + PythonQt and input + FontLab from owned localhost XML response, row_count=3 and pending=false. Select completion natively, test empty query, replace pending request and requestTimer timeout. Close with popup/reply active: disconnect before abort/delete, stop timers, join fixture worker and release port; no Google/network redirect contact. |
| `08ba2f1b1fe02894` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("08ba2f1b1fe02894") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `a0ac1b252a14609e` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("a0ac1b252a14609e") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `f13380d705146bff` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("f13380d705146bff") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `52871219c50cdd21` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("52871219c50cdd21") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `7cc9bd76e925db18` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("7cc9bd76e925db18") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `b76dc05cb743e9fc` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("b76dc05cb743e9fc") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `43f4640a040ded3e` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("43f4640a040ded3e") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `26b75bfff47f567d` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("26b75bfff47f567d") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `5354655012c2060e` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("5354655012c2060e") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `6cb023a08571bf96` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("6cb023a08571bf96") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `1ffcdfb872b0e689` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("1ffcdfb872b0e689") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `8fc6773f10b89095` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("8fc6773f10b89095") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `5c181bebc7c9773c` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("5c181bebc7c9773c") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `e2f27c6394aa70c8` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("e2f27c6394aa70c8") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `5d8303b0b2237124` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("5d8303b0b2237124") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `19398065f86e2762` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("19398065f86e2762") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `80aa961de86e1704` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("80aa961de86e1704") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `2588c05ccd043d91` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("2588c05ccd043d91") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `8cb9580232bd8081` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("8cb9580232bd8081") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `207f7ce534696c20` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("207f7ce534696c20") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `96777c686c66d526` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("96777c686c66d526") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `d82b14fd5e1eb010` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("d82b14fd5e1eb010") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `ee1562b25c092ee8` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("ee1562b25c092ee8") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `60a3d030c4744735` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("60a3d030c4744735") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `f5d13b3c5b699ab3` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("f5d13b3c5b699ab3") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `620da7edd0cd23fc` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("620da7edd0cd23fc") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `c6effccd6f31f416` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("c6effccd6f31f416") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `f2767c945bece214` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("f2767c945bece214") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `21a081a01365c096` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("21a081a01365c096") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `22be270b0ff2abf7` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("22be270b0ff2abf7") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `01be5e33878e4940` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("01be5e33878e4940") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `9007853b5b845ed9` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("9007853b5b845ed9") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `1862a5f7d89bd9b6` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("1862a5f7d89bd9b6") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `b3c5b8f7bcf09a1d` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("b3c5b8f7bcf09a1d") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `e9392311a500d3dd` | Confirm the recorded missing module/member/backend against the FontLab/Echopy exports. Call launch("e9392311a500d3dd") and direct build with an untouched host: both must raise NotImplementedError with the exact recorded reason before host lookup, UI, network, subprocess or resource access. Verify registry and FontLab state unchanged. This is blocker acceptance, not a functioning port. |
| `1e79bddb6d52574d` | Launch under 5 s; no console input. Set name/message to Unicode, drive returnPressed/send_message, then wait for the one-second pollTimer. Inspect exact name: message text, sent/received and cleared edit. Requests contact only the owned numerical localhost endpoint and have 250 ms deadlines. Test owned service failure; close with polling active, verify fixture worker joined, timer stopped, slots disconnected and port freed. Host stays alive and relaunch starts empty. |
| `88fa78cafb505cfa` | Launch under 5 s; set Unicode name/message, returnPressed queues POST, Python worker polls every 500 ms; one-second GUI timer drains results. Inspect worker_alive/phase/timer_active, sent/received and exact displayed text. Repeat sends, close immediately after enqueue and during poll; both owned service and client workers must join before disconnect/delete, with no Qt call from a worker, no third-party traffic and released localhost port. |
| `83bc55d45ae367d0` | Launch under 5 s; set Unicode name/message, returnPressed queues POST; Python worker polls every 500 ms, 30 ms GUI delivery replaces threadutil custom signal. Verify exact displayed name: message, cleared input, sent/received and worker state. Close with pending results and relaunch; service/client workers stop and join before slots disconnect/delete; no native wrapper crosses a worker boundary or third-party request occurs. |

Verification commands/results will follow after final gates.

Final verification (after adding real map/loopback interaction checks):

```sh
UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
# 903 passed in 17.89 s, no failures/errors/skips; baseline 685.
ruff check --no-cache <97 new ports + 7 changed helper/test files>
# All checks passed: 104 files.
ruff format --check --no-cache <same 104 files>
# 104 files already formatted.
# ast.parse(source, feature_version=(3, 11)) + this_file: 104 files pass.
git diff --check
# Pass after removing a trailing blank line in the appended controller guide.
```

A total of 218 new checks extend the existing suite. Interaction coverage uses
real owned localhost HTTP/Unix/TCP transport with native doubles: Unicode chat,
UInt32/QString fortunes, asynchronous suggestion query/XML/reply cancellation,
style/UI connections, maps/pan/magnifier/night painting, loopback transfer,
native-window input/backing-store ordering, disconnect-before-delete and rollback
of every implemented build. Doubles enforce GUI-thread-only Qt access. These are
boundary checks, not native FontLab visual/virtual/overload acceptance.

Direct final byte/hash/notice audit: 97 pinned original entrypoints (byte count,
SHA-256 and Git blob SHA), nine byte-identical style UI/QSS/image resources,
102 verbatim source/companion headers, eight current native-module stub hashes,
299 unique names and case-folded target paths. All 298 Python entrypoint
candidates plus the database initializer now have 299 records: 148 implemented,
151 blocked. All 202 pre-existing records are structurally unchanged. All 97 new
records use native_acceptance=unexecuted, with README rows and exact per-port
checklist anchors. PLAN.md, TODO.md and catalog/sources.json remain byte-identical
to HEAD. No binding/dependency installation, upstream write or native execution.
Branch remains issue-101-pythonqt-examples, HEAD 92c03f8, staging empty; pre-existing
.DS_Store and .omc entries left alone.

Open acceptance questions: real PythonQt QWindow virtual input/resize/expose
callbacks and explicit non-QObject QBackingStore deletion; QUiLoader's original
style form connections and image/QSS rendering; QCompleter popup selection and
QNetworkReply cancellation; native UInt32/QString IPC, QTcpSocket transfer and
map magnifier painting; clean worker shutdown and complete deferred QObject
teardown without affecting FontLab. The orchestrator must run the per-port
checklists above and retain host-alive/destruction evidence before committing.
The NightFade preset, matrix multiplication and QXmlStreamReader blockers could
be revisited with separately reviewed behavior-preserving substitutions; no such
substitution is counted here. Qt-backed matplotlib and absent native-module demos
remain blocked. Individual style asset grants remain unresolved where no notice
exists; repository GPL terms and all exact provenance are retained.

## 2026-10-14: Native screen-property regression

Controller reports 9/10 batch-9 native launch/inspect/close checks pass without
crash; QPA windows failed because instance primaryScreen is None, not callable.
Use static QApplication.screens()[0] as primary and compare screen name plus
numeric geometry, never wrapper identity/equality. Audit of all port/helper Python
sources found one other affected path: screenshot read the null class property;
it now also uses the first static screen, only on explicit capture. No screenAt
or other QGuiApplication application-screen calls remain.

Doubles now expose the class null QScreen property and instance None, with static
screen enumeration. Five added checks cover property call rejection, duplicate
primary wrappers, same-name screens with different geometry, all-port call audit
and empty-screen screenshot handling. Existing capture test uses static screens.
Verification: baseline 903 passed; full offline pytest gate 908 passed in 18.66 s
(UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest
-q tests). Scoped ruff check/format --check: four Python files pass. Python 3.11
grammar: all 313 ports plus two changed tests pass. git diff --check passes;
staging empty, no commit. Native reacceptance of QPA windows and screenshot remains
with the orchestrator; no native verification state is inferred from doubles.

## 2026-10-14: Controller native acceptance of the eyllanesc/QtExamples batch (all remaining entrypoints)

Codex handled the last 97 catalogued entrypoints (94 eyllanesc/QtExamples + 3 pyqt/examples):
10 implemented, 87 blocked with the exact missing native module/classes (QtWebEngine, QtQml/
QtQuick, QtCharts, QtSql, QtMultimedia, GStreamer, matplotlib Qt backends). Native first run
9/10: qpa/windows called `app.primaryScreen()`, which in PythonQt is a property (null QScreen on
the class, None on the instance); Codex fix uses `QApplication.screens()` (screenshot port too);
offline gate 908 passed. Native re-run: **10/10 pass, host alive** (parent
evidence/examples-batch9/native-fix1.jsonl). Catalog: 299 records (148 implemented, 151 blocked);
no catalogued entrypoint is unaccounted for.


## 2026-10-15: Native official-port interaction regressions

Read all nine failing records in the controller's `examples-interactions` results
and their per-step actions. Worked only in this checkout; no evidence-directory
writes, catalog acceptance changes, staging or commit. Baseline: 908 tests pass.

1. Calculator: explicitly bind buttons to digit/unary/additive/multiplicative
   slots. Audit every port across all batches: remove all eleven sender() calls
   in calculator, spreadsheet, recentfiles, scribble and diagramscene. Capture
   each QAction/editor separately. Also repair the calculator's independently
   recorded sizeHint error: copy the native minimumSizeHint property rather than
   call the class's QSize-valued sizeHint property.
2. Spreadsheet: remove the Python QTableWidgetItem subclass. Keep formulas and
   cycle state in Python dictionaries/sets keyed by (row, column); recompute real
   native DisplayRole/colour/alignment/status roles while blocking recursive
   itemChanged. Native wrapper edits, formula-input edits and delegate commits
   share the same formula state; cycle and division-by-zero results preserved.
   Delegate editor setup reads the retained sheet/formulas, never a subclass
   retrieved through a parent wrapper. Plain-item formula()/display() calls gone.
   Full subclass audit: no other QTableWidgetItem, QListWidgetItem, QTreeWidgetItem
   or QStandardItem Python subclasses remain. Graphics retrieval audit repairs
   elasticnodes (retained nodes/edges), dragdroprobot (palette), collidingmice
   (mice), embeddeddialogs (proxies), and diagramscene (data-role ID lookup).
   Native wrappers are resolved before isinstance or Python-method access;
   native item identity uses data-role IDs where required. Non-QObject centerNode
   is explicitly exposed in controls, fixing the ninth failing native record.
3. Application: retain document.contentsChanged -> documentWasModified and add
   document.modificationChanged -> setWindowModified for edits and flag resets.
   Test Unicode insertPlainText editing and save/reset. setPlainText deliberately
   clears modified; the native table's expectation of True after replacement is
   inconsistent with Qt/original semantics. Correct reacceptance uses an editing
   operation, e.g. insertPlainText('Zoë draft'), and verifies save clears the flag.
4. Animatedtiles: QState transitions subscribe to the native clicked(bool)
   signature, not its argument-omitting convenience form. Apply the same audit
   fix to appchooser, states, stickman and moveblocks. An explicit tile click
   stops the initial ellipse timer, preventing startup from overriding selection.
   Doubles require an exact emitted transition signature and assert the 8x8 grid
   and centered positions. Native asynchronous timing remains unverified here.
5. Broadcast ports: preserve each owned Python receiver bound to 127.0.0.1:0
   with the bounded GUI polling drain; no native readDatagram/BoolResult output
   overload or ShareAddress/readyRead is used in this implementation. Replace
   string QHostAddress construction with explicit LocalHost, verify toString()
   equals the owned IPv4 host before sending, and reject incomplete UDP writes.
   Strict doubles perform real localhost datagram transport, require explicit
   LocalHost, and exercise failure without advancing message_no. String address
   dispatch is a diagnosis hypothesis, not a newly observed native fact: live
   probing was blocked. Native reacceptance must verify both timer and sample
   sends; these local results do not establish the native UDP defect is resolved.
6. CounterLabel: inspect the pinned original getValue/setValue/paintEvent.
   Raw value and paint stay 123; offset affects the two valueChanged notifications
   (128 and '128'). Preserve that original behaviour and document it in getValue;
   test incrementing, notifications and rejected out-of-range input. The existing
   native expectation value == 128 must instead check raw value plus notifications.
7. Spinboxdelegate: Demo.transient removes editors from controls, connections and
   subclass ownership records on destroyed without reading invalid wrappers.
   Apply to all retained item-view delegate editors (spreadsheet, stardelegate,
   coloreditorfactory too). Test native destruction, committed value 42,
   inspection/close after destruction, and older-editor destruction while a newer
   editor occupies the same control name.

Regression-first run: seven failures and three passes exposed the original bugs
under stricter doubles. Add 22 regression cases; all-port sender AST audit covers
all ports. Doubles now return None from sender(), return base native item wrappers
sharing only native data, expose destroyed-property failures, model document
editing/modification/reset, and enforce the full clicked(bool) transition signature.

Documentation consulted: Qt 5 [QTextEdit](https://doc.qt.io/archives/qt-5.15/qtextedit.html),
[QSignalTransition](https://doc.qt.io/archives/qt-5.15/qsignaltransition.html),
[QUdpSocket](https://doc.qt.io/archives/qt-5.15/qudpsocket.html),
[QTableWidgetItem](https://doc.qt.io/archives/qt-5.15/qtablewidgetitem.html),
and QAbstractButton's declared clicked(bool) signal; inspected captured PythonQt
stubs and the pinned original CounterLabel locally. No new dependency.

Verification:
- Full offline pytest: 930 passed (baseline 908); 22 new cases. Command:
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 UV_CACHE_DIR=/private/tmp/fontlab-uv-cache UV_OFFLINE=1 uv run --no-project --with pytest python -m pytest -q tests`.
- Scoped Ruff check and format --check: all 25 changed/new Python files pass.
- Python 3.11 grammar and this_file records: all 322 checked sources pass.
- git diff --check passes. Staging empty; no commit.
- Full-tree Ruff also run: two unchanged HEAD findings remain: I001 in
  tests/test_official_slot_shadowing.py and EXE001 in
  tools/collect_pythonqt_reference.py (HEAD file mode 100644). Scoped work is clean.
- Evidence results/log/runner/test-table hashes match their SHA256SUMS entries.
  interactions.py and README.md already have 00:04:26 modification timestamps and
  do not match that older manifest; no evidence file was modified by this work.
- A native run_python probe was rejected with 'MCP tool call requires approval,
  but approval policy is never'. No native reacceptance occurred. Do not replace
  the controller's 72/81 count or mark native acceptance passed from doubles.

## 2026-10-15: Controller native interaction acceptance (controls exercised)

New driver (parent evidence/examples-interactions/: interactions.py, run_interactions.py,
458 static tests) exercises 81 official ports in 150+ steps (clicks, values, keys, actions)
in an agent-owned no-document FontLab session. First run 72/81. Native facts found:
`QObject.sender()` is None in PythonQt slots (calculator); `QTableWidget.item()` returns native
wrappers losing Python subclass attributes (spreadsheet); retained delegate editors outlive
Qt (spinboxdelegate); loopback UDP broadcast pair. Four failures were driver expectations
(elasticnodes key, application cursor/modified semantics, counterlabel offset semantics,
animatedtiles float noise) and were corrected in the driver. Codex fixes (this commit) + driver
fixes: **81/81 interaction pass**; launch/inspect/close of all 137 implemented ports after the
fixes: **137/137 pass, host alive**. 46 ports remain without scripted interactions (file
dialogs, real drag/drop, clipboard, screen capture, tray, 50 MiB loopback), listed with
reasons in the evidence README. Offline gate 930 passed.

## 2026-10-15: New interaction file/settings/teardown regressions

Read the controller's `native-interactions-new21-rerun.jsonl` and `.log` in
the parent evidence/examples-interactions directory. No evidence files edited.
These changes supersede the earlier source hashes for affected ports; the
historical native counts above do not establish acceptance of these changes.

- Recentfiles: convert all three recentFileList reads to plain lists at the
  PythonQt boundary. The settings double now returns tuples for stored lists.
  Verify reordering, duplicate removal, five-item truncation and menu data.
  Audit every port's settings reads; geometry/scalar values and the generic
  settingseditor value delegate require no mutable-list operations.
- Files: every shared Save selection and PDF output is checked with owned_path.
  Guard direct open/save methods too, including textedit after suffix handling;
  rejected paths show an owned asynchronous message and preserve document state.
  Cover application/SDI/MDI/recentfiles, codecs, stylesheet, dockwidgets,
  scribble, separations, imageviewer, classwizard and settingseditor. Extend the
  same boundary to the numbered text-editor helper. Preserve immutable packaged
  resource loading and existing owned address-book/screenshot checks. Fixed
  fixture/download/tile writers already construct their paths in Demo.temp_dir.
  Validate both classwizard output paths before writing either file. Recheck
  print/preview output immediately before rendering; confine settings INI copies.
- Teardown: remove the temporary directory after owned window close callbacks,
  through a retryable after_close callback. Track the TemporaryDirectory object,
  original mkdtemp path and device/inode; refuse borrowed, retargeted, symlinked
  or replaced directories. LocalFortune uses the same registered ownership with
  its shorter /tmp IPC prefix. No sweep or deletion of old directories.
- Standarddialogs: force owned non-native QFileDialogs even when the native
  checkbox is changed programmatically; disable that checkbox in the UI.
  Shared file selection uses NonModal plus show(), with tracked accepted()
  callbacks. The double exposes fileNameEdit only for DontUseNativeDialog;
  regression tests check the drivable child and asynchronous visibility.

Regression-first run reproduced 18 failures and one existing passing path check.
Expanded to 33 new cases, covering outside files, symlink/sibling escapes,
appended extensions, classwizard partial-write prevention, print paths and exact
temporary-directory ownership. Existing round-trip fixtures now live inside the
port's owned folder. Every shared official build/close test also checks removal
of any temporary directory created during construction.

Consulted official [Qt QFileDialog](https://doc.qt.io/archives/qt-5.15/qfiledialog.html),
[QSettings](https://doc.qt.io/archives/qt-5.15/qsettings.html) and
[TemporaryDirectory](https://docs.python.org/3.11/library/tempfile.html#tempfile.TemporaryDirectory)
contracts and the local OwnedWidget implementation. Tuple-return semantics are
the controller's observed PythonQt fact. No new dependency.

Verification:
- Full repository suite: **963 passed** (baseline 930), using
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 UV_CACHE_DIR=/private/tmp/fontlab-uv-cache
  UV_OFFLINE=1 uv run --no-project --with pytest python -m pytest -q tests`.
- Supplied driver static gate: **781 passed**, with PYTHONDONTWRITEBYTECODE=1
  and pytest `-p no:cacheprovider`. SHA-256 and modification-time snapshots of
  all 16 evidence files match before/after this gate; the directory is untouched.
- Scoped Ruff lint and format checks: all 26 changed/new Python files pass.
  Python 3.11 grammar and this_file checks: 352 repository Python sources pass.
  git diff --check passes; staging empty; no commit.
- Full-tree Ruff was rerun. Existing HEAD findings remain: EXE001 for the
  non-executable tools/collect_pythonqt_reference.py; format differences in that
  file and ports/insights/metrics-undo.py. Those unrelated files were not edited.
- Native run_python readiness probe was rejected with
  "MCP tool call requires approval, but approval policy is never". Live
  reacceptance remains pending; doubles and static driver tests do not prove
  PythonQt rendering, interaction or delayed native destruction acceptance.

## 2026-10-15: Read-source policy and test temp-directory regressions

Controller reported native interaction 101/102 and launch/inspect/close 137/137
after the preceding fixes. Codecs could not open its own bundled UTF-8 sample;
the owned-path policy had incorrectly restricted reads. Those native results
describe the preceding source state, not acceptance of the changes below.

Audit every owned_path call in all ports and shared helpers. Remove ownership
checks from codecs, application/SDI/MDI/recentfiles, rich and numbered editors,
scribble/imageviewer/separations, address-book parts 6/7 and settings imports.
Shared open/multiple-file/directory selections accept readable user paths;
the owned flag is now only an initial-directory hint for reads. Save selections,
direct saves, PDF/export paths and settings destinations retain owned_path.
INI imports read the chosen source into an owned copy; plist imports populate
owned settings. Preserve address-book data-only unpickling.

Add an autouse fixture that monkeypatches tempfile.tempdir to a separate pytest
tmp_path_factory directory for each test. The late.ini regression asserts that
its owned root is inside that fixture and restores its patched close hook in
finally, including assertion failures. Remove its deliberately foreign pytest
fixture directory only after proving port close leaves it intact. No real-temp
directory sweep or runtime cleanup-policy change.

Tests first reproduced 15 read-policy failures with 26 passes. The corrected
suite covers the exact bundled codecs sample through a non-native QFileDialog,
owned/user read sources, denied writes, external INI/plist copy isolation,
numbered-editor read-then-save refusal and an AST audit of every open/load method.
Wait, but local doubles cannot establish native QFileDialog or image rendering
acceptance; the controller's native rerun remains separate.

Documentation checked: Python 3.11
[tempfile](https://docs.python.org/3.11/library/tempfile.html#tempfile.tempdir),
[pytest temporary directories](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
and [Qt 5 QSettings](https://doc.qt.io/archives/qt-5.15/qsettings.html).
No dependency changes.

Verification:
- Full offline repository gate: **973 passed** (baseline 963), using
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 UV_CACHE_DIR=/private/tmp/fontlab-uv-cache
  UV_OFFLINE=1 uv run --no-project --with pytest python -m pytest -q tests`.
- Driver static gate: **781 passed**, with PYTHONDONTWRITEBYTECODE=1 and
  `-p no:cacheprovider`; all 18 evidence files' SHA-256 and modification times
  match before/after. No native or evidence-file edits.
- Scoped Ruff lint and format checks: 29 changed/new Python files pass.
  Python 3.11 grammar and this_file checks: all 352 checked sources pass.
  Full-tree Ruff retains the existing EXE001 in tools/collect_pythonqt_reference.py
  and formatting differences there and in ports/insights/metrics-undo.py.
- Real tempfile.gettempdir(), resolved $TMPDIR and /tmp contained zero directly
  nested fontlab-official-* directories before and after the full repository gate.
  A recursive check of the final pytest run directory also found zero matching
  directories. No directories were deleted from those locations by a sweep.
- git diff --check passes; no staging or commit.

## 2026-10-15: Controller native acceptance — extended interactions (102 ports)

Driver coverage extended to 102 of 127 implemented official ports (file dialogs answered
with owned temp/asset paths through the ports' own non-native dialogs; dropsite handler fed a
real QMimeData). Native runs found and Codex fixed: QSettings list values are tuples
(recentfiles); textedit Save As could write outside its owned temp dir (writes now confined,
reads allowed from assets/user files); temp dirs now removed on close; standarddialogs uses an
owned non-native dialog; a unit test leaked temp dirs (now tmp_path-isolated). Final native
run in an agent-owned no-document session: **interactions 102/102, launch/inspect/close
137/137, 0 leftover temp dirs, host alive** (parent evidence/examples-interactions/
native-interactions-final.jsonl, native-lic-final2.jsonl). 25 ports remain without scripted
interaction (real drag/drop, mouse/key-only, user clipboard/screen/tray, visual-only),
listed with reasons in the evidence README. Offline gate 973 passed.

D7 artifact recheck: all 188 handoff blobs match the private commit; all 112
non-official record dictionaries are unchanged. A fresh full real-input inventory
run into a separate temporary output reproduced sources.json, INDEX.md and
ports.json byte-for-byte. The staged diff is empty. Concurrent recipe work also
advanced the public branch HEAD through recipe-only commits; relocation changes
remain unstaged and those commits were not made by this task.

Final complete-suite rerun, including the now-completed concurrent recipe additions:
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 UV_CACHE_DIR=/private/tmp/fontlab-uv-cache uv run
--no-project --with pytest python -m pytest -q tests
--junitxml=/private/tmp/clean-room-relocation-final-tests.xml`: **476 passed,
621 skipped, zero failures** (exit 0). Parsed the XML: every skip cites
`clean_room_pending`. Recipe-only commits completed outside this task; final
status contains only intended relocation edits, 431 deletions, the 188 handoff
files and four new test/tool/verification files. Staged diff remains empty.

## 2026-10-15 issue 104 lanes L6b/L6c (recipes, clean-room native acceptance)

- Recipes: nine in `examples/recipes`, each native-checked on an owned font
  (`examples/recipes/<name>/native.py` through `verification/issue-104/fl-native.sh
  --mutating --lane L6b`; evidence `examples-recipes/`). Measured: Edit > Undo does
  not restore native script edits in 9.0.9783, so no recipe claims undo.
- Native acceptance: `tools/native_cleanroom.py` over all 187 records, final runs
  `examples-cleanroom/final01..05` (187/187) and the controller's independent run
  `examples-cleanroom/controller/` (187/187 after one transport-fd false alarm, since
  fixed). Recorded with `python3 tools/record_native.py
  ../verification/issue-101-ecosystem/evidence/examples-cleanroom/native-acceptance-proposal.json
  --commit 9bec8bb` -> passed 127, blocked_verified 60.
- Interactions: `examples-cleanroom/interactions_cleanroom.py` -> 106 passed, 21
  skipped (network 8, user files 5, printing 3, file dialog 2, clipboard 2, tray 1),
  60 blocked; 523/727 controls changed and read back.
- Tests: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m
  pytest -q tests` -> 1500 passed.

## 2026-10-15 issue 104 lane L6d (1): event checks for 22 clean-room ports

`verification/issue-104/fl-native.sh --lane L6d -- uv run --project fontlab-remopy python
verification/issue-101-ecosystem/evidence/examples-cleanroom/events_cleanroom.py OUT.jsonl`
sends QMouseEvent/QKeyEvent/QDragEnter+QDrop (owned QMimeData) to the ports' own widgets;
checks use inspect() state or QWidget.grab hashes. Final: 20 passed, 2 skipped
(delayedencoding: QDrag.exec drag-out only; broadcastsender: LAN broadcast). Offline
table tests: `test_events_table.py` 3 passed. A first run failed shapedclock (helper
recomputed screen positions from the moving window) and tetrix (wrong piece-count
assumption); both fixed in the driver.

## 2026-10-15 issue 104 lane L6d (2): recipes through the Scripts-menu route

`verification/issue-104/fl-native.sh --mutating --lane L6d -- uv run --project
fontlab-remopy python verification/issue-101-ecosystem/evidence/examples-recipes/menu_route.py`
copies each recipe folder to a temp dir, fills GLYPHS/PAIRS/OFFSET/REFERENCE/WIDTH in the
copy, runs it with Remopy execute_script on the owned fixture font, parses the printed
report and applies the recipe's native checks: 9/9 passed. fontlabapp/glyport checkouts
are put on sys.path in a guarded call before the script and restored after; FontLab's
sys.path verified clean afterwards. Offline: `test_menu_route.py` 4 passed.

## 2026-10-15 review fixes (R-examples, NEEDS_FIXES)

Commits 135212d (review citations), 6e2ef2f (recipes), f358589 (native acceptance
bound to run commit and dependency closure), then the catalogue record below.
Tests: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m
pytest -q tests` -> 1532 passed. Native (fl-native.sh --lane L6c, clean tree at
f358589): `uv run --python 3.11 tools/native_cleanroom.py --batch-size 8 --ids ...
--output .../examples-cleanroom/review/run0N.jsonl`. run01-02 40/40 each; run03 23
passed, then storageview (cf15c3e91cdd8ded) timed out in inspect (status unknown,
stopped safely) and left its session, so run04/run05 refused at prepare ("An earlier
acceptance session still needs cleanup"). Re-run of those 84 ids with --reset-stale
(reset 1 session, 33 witnesses) as run06-08: 84/84. Logs `review/run01-05.log`,
`review/run06-08.log`.
The old proposal (native-acceptance-proposal.json, commit 9bec8bb, rewritten by D9) is
refused: `python3 tools/record_native.py apply ... --commit 9bec8bb` -> "run commit
9bec8bb is not in this checkout's history" (exit 1).
Recorded: `python3 tools/record_native.py propose --output review/proposal.json
review/run01..03,06..08.jsonl` -> 187 ports, then `apply review/proposal.json --commit
f3585891067184a0f14d708b805a766e2073331e` -> passed 127, blocked_verified 60.

## 2026-10-15 review round 2 (RR-examples: 2 P2 not addressed)

Commit c4b09c7. Tests 1542 passed. Fuzz (scratch): exact containment agreed with a
4000-step flattening on 9000 random points over 300 random cubic/line contours.
Native: `verification/issue-104/fl-native.sh --mutating --lane L6b -- uv run --project
fontlab-remopy python fontlab-python-examples/examples/recipes/contour_direction/native.py
.../examples-recipes/contour_direction-rr2.json` -> exit 0, all 11 checks (new: 1-unit
sliver at (4,90) inside the hump is a counter). Scripts-menu route re-run for all nine
(`examples-recipes/menu_route.py`) -> 9/9, exit 0.


## 2026-10-15 review round 3 (RR2-examples: collapsed contours)

Commit 56e1c11. Tests 1546 passed (new: collapsed one-node and four-coincident
contours skipped and reported; an unreadable second glyph leaves the first
unmutated; start index after reversal). Native: contour_direction/native.py ->
`examples-recipes/contour_direction-rr3.json`, exit 0, 12/12 checks (report skipped
[{glyph U, contour 3}]). Scripts-menu route 9/9, exit 0.

## 2026-10-15 closing check (PLAN/TODO review)

- Glyphs recipes in Glyphs: `uv run --quiet --no-project --with pyobjc-framework-Cocoa
  python verification/issue-101-ecosystem/evidence/examples-recipes/glyphs-app/run_recipes_in_glyphs.py
  "/Applications/Glyphs 3.app" glyphs3.json` exit 0 (3.5.1, 10/10 checks, quit); same
  with Glyphs 4.app exit 0 (4.2, 10/10, quit). In-memory GSFont only, never added to
  Glyphs.fonts or saved; refuses if that Glyphs is already running.
- FontLab drivers re-run after docstring updates: glyphs_tabular_figures and
  glyphs_path_report native.py exit 0 (`examples-recipes/*-final.json`).
- Licence provenance: `python3 .../examples-licences/provenance.py fontlab-python-examples
  provenance.json` -> 14 unresolved; 5 byte-identical and 4 whitespace-equal to Qt
  qtbase styleexample (5.15, 6.5); 5 pyqt assets untraced. Left unresolved for the owner.
- Coverage review (inline script): 299 records; 148 implemented all passed with
  evidence and files; 151 blocked all with blocked_reason; 18 insights; 9 recipes.
- Tests: 1546 passed.

## 2026-10-15 L6e: resource replacements and docs export

- `python3 tools/replacement_assets.py --write`, `--record`, `--check` (14 files
  current). Commit d3ab76d. Tests 1549 passed.
- Native acceptance (`verification/issue-104/fl-native.sh --lane L6e -- bash -c "cd
  fontlab-python-examples && uv run --python 3.11 tools/native_cleanroom.py --reset-stale
  --batch-size 4 --ids 1151b1cb878f192a a601a41dc5a3c23a a33bb8c2dce4e115
  631cc1bc310c00b9 --output .../examples-resources/acceptance01.jsonl"`) exit 0: 4/4,
  clean tree at d3ab76d. Recorded with `record_native.py propose` + `apply --commit
  d3ab76d...` -> passed 4 (commit 35f4e41). The clean-room proposal still validates (187).
- Interaction checks (`.../examples-resources/replaced_checks.py`): interactions01
  failed 4/4 (driver bugs: `windowIcon` is a property; the result's stderr key broke
  equality checks); interactions02 failed 3 (the editors show the icon only as an
  About-box image, not as the window icon; check changed to decoding the SVG);
  interactions03 exit 0, 4/4.
- `python3 tools/docs_export.py` -> 40 pages + manifest; `--check` current; every
  in-page anchor resolves under Python-Markdown toc (299/299, checked with
  `uv run --no-project --with markdown`). Tests 1556 passed.

## 2026-10-15 review R-L6e fixes

- New tests first (tests/test_replacement_assets.py; docs-export input test): 9 failed.
- `replacement_assets.py`: `stale()` regenerates in memory, exact match only; `--record`
  refuses everything on any mismatch; background is `files/nature_1.png` (stored-deflate
  PNG), upstream `nature_1.jpg` removed and recorded as moved. Generator output hash
  identical on CPython 3.11.14 arm64, 3.11.16 x86_64, 3.12.12, 3.13.10 (367a0dd93e7e045d).
- `docs_export.py`: manifest inputs include the 10 recipe READMEs.
- Commit b9ead3f; tests 1566 passed.
- Native at b9ead3f (fl-native.sh --lane L6e): native_cleanroom 4/4
  (`examples-resources/acceptance02.jsonl`), recorded with record_native apply;
  replaced_checks.py interactions04 4/4 (background PNG decodes at 320x240).

## 2026-10-15 closing check

The last TODO item (docs-lane wiring) was verified from fontlab-python-docs:
`mkdocs.yml` has the "Examples: examples/index.md" nav entry; `api-sources.lock.json`
(ff4c5e4, "examples be2712b") lists 41 `examples/` entries whose sha256 all match the
current `docs-export/` files (HEAD be2712b); `.build/content/examples` holds 40 pages.
PLAN.md and TODO.md are now empty; the item moved to CHANGELOG.md.

2026-10-15 workspace reconciliation: fresh source suite 1567passed/0skipped, exit0.
Exact command and retained initial failures: parent verification/plan-todo-audit-20261015/baseline-tests.json.
Completed repository plans were archived where no repository tasks remain;
workspace integration/release gates remain separate.

## 2026-10-15 — GetGo real-font scope added

The owner supplied the GetGo corpus for actual tests/examples. Source checkout
revision25a4d6d7099143090093e5820660b77222ac670b,99VFJs294313046bytes. Copied
all99 unchanged under fontlab-python-examples/testdata/getgo; retained81Apache,
11CC0 and7OFL records with original licence texts, SHA-256, public font-page and
VFJ/TTF links, embedded notices and registry attribution. No source font edited.
Tests failed first on missing manifest; actual-file/static checks now run. Native
corpus/mutation/export tests and practical examples are new active scope.

## 2026-10-16 - E1 GetGo native acceptance (issue 106)

- Fixtures verified (ac98f06); corpus3 99/99; edits7 + edits9-heavy: 17 fonts edit/save/reopen equal,
  static TTF/OTF 17/17 (fontTools), variable 6/16 (10 reproduce on unedited originals; cosm filed as
  Fontlab/fl#8506; F1 is fixing sources). Examples: examples1 8/13, examples2(+rest) 12/13, examples3-all
  13/13 with X2's uncommitted _shared.py close fix. Details and commands: verification/issue-106/reports/E1-getgo-native.md.
- Open: F1 re-sync; commit _shared.py fix; README/native_manifest status.

## 2026-10-16 - examples4-all

`fl-native.sh --mutating --lane E1-getgo-native -- ... native_getgo_examples.py --output .../examples4-all`
exit 0: 13/13 PASS at f151195 (spacing 0.11 s, closed_stray_documents 0). docs_export --check 42 files
current; suite 1881 passed. Open: F1 VFJ re-sync (controller sends file list and hashes).

## 2026-10-16 Samples copy
- `python3 tools/sync_samples.py` (106 scripts copied, rc 0); `--check` rc 0; `python3 tools/docs_export.py` then `--check` rc 0 (43 files).
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest --with fonttools python -m pytest -q tests`: 1886 passed (rc 0). Without fontTools the two pre-existing outline-pen tests fail on the missing module.


## 2026-10-19 — isolated packaged GetGo source milestone

Selected only B5-owned lesson/menu files into a clean feature checkout based on
28bc505. Canonical/inherited rescued relocation and deleted old tests are excluded.
Original legacy directories and tests remain as Git records them on this branch.
Source19modules/99fonts/16distributed menus are byte-identical to reviewed B5.
Native acceptance and canonical migration remain pending.

First clean package test run:13fail/185pass because the B5 integration test
required the inherited untracked root rescue-index. Kept that original migration
check in the B5 worktree. This clean branch tests the13exact expected menu paths
directly (same route/original-main/no-import-launch oracles), preserving source
provenance and fixture hashes without importing the owner's unrelated migration.

Fresh clean-branch checks:
- Lesson source suite198passed(exit0), Python3.11 integrationenv with EXAMPLES_APP_SOURCE pointing only to reviewed App integration.
- Broad original root suite initially1802passed/21skip then2fail/1error due systemGit and absent ignored reference location. HomebrewPATH fixedGit fixtures; reference-only test passes with FONTLAB_WORKSPACE and FONTLAB_EXAMPLES_REFERENCE pointing to real read-only canonical references. No corpus code runs.
- Full remaining root suite1864passed/21existing native/evidence skips/1deselected(exit0); the deselected source-citation test separately1passed(exit0). No skip or production behavior changed to pass.
- Fresh clean package wheel/sdist built as unpublished1.0.4.dev0 under verification/issue-120/app-integration/lessons-dist; normal dependency installs pass.
- Combined App/Glyport/clean-GetGo installed179tests per wheel/sdist pass;241runtime/resourcehashes,99fonts and16menus verified each. Both uv pip checks pass, delegatedqtsafe identities/import origins pass.
Native validation remains pending. No unrelated owner relocation/deletions staged.


## 2026-10-19 — D3 current GetGo documentation and native manifest

The main lessonREADME still described onlythree entries and obsolete App0.2.22
minimum while the candidate ships16and requires0.2.26.dev0. Rewrote142lines
with all16actualmenus, matched devpackage setup, model/form behavior, GetGo
ownedfixture/edit/export limits and explicit historical-vs-pending acceptance.
No oldnativeacceptance is applied to the new13entries.
Native manifest's checker still referenced archived examples.getgo._checks;
changed it to the shipped fontlab_python_lessons.getgo._checks.assert_expected.
FontInfo observation now matches the actual read-onlyQPlainTextEdit JSON report.
Queued native acceptance must enforce its own in-hostdeadline/cancellation;
client/run_python timeouts do not stop hostcode. No nativeexecution claimed.

First newtest imported the archivedchecker from this legacy-containing checkout,
so strengthened it to require the distributed namespace. Red1failure; corrected
manifest green. Full199lesson cases pass, upfrom198. Initial artifactinstall
was attempted before the buildprocess finished and found no archive; after its
recorded completion, both normalfresh installs pass without dependencybypass.
Both installed wheel/sdist179existing integration cases pass. Isolated Python-I
probes independentlyimport/call checker with noarchivednamespace, verify242
reviewed runtime/resource hashes,99fonts,16menus, deadlinegate and UIobservation;
both uvpipchecks pass. CurrentREADME bytes match both packagearchives.
Exact normalinstall arguments/logs, checks and hashes:verification/issue-120/getgo-docs-d3/.

Commands: `rtk proxy env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 EXAMPLES_APP_SOURCE=/Users/adam/Developer/vcs3/github.fontlabcom/fontlab-scripting/.worktrees/issue120-vanilla-app/src/fontlabapp QT_QPA_PLATFORM=offscreen /Users/adam/Developer/vcs3/github.fontlabcom/fontlab-scripting/verification/issue-120/vanilla-session/wheel-env/bin/python -m pytest -q lessons/candidate_tests/models_candidate`:exit0,199passed.
Rootbuild: `rtk proxy env PATH=<Homebrew-bin>:<local-bin>:/usr/bin:/bin SETUPTOOLS_SCM_PRETEND_VERSION=1.0.4.dev0 uv build .worktrees/issue120-getgo-package/lessons --out-dir verification/issue-120/getgo-docs-d3/dist`:exit0.
From/tmp, eachnewinstalledPython-I with pytestconfigdisabled runs retained
D3installed-tests179cases(exit0) and artifact_probe.py(exit0); checksexactcommands
retained in checks.json. ScopeRuff/whitespace run beforecommit.

Wait, but: no rendered-site or native acceptance follows from packagedREADME
and checker verification. Newfunctions/nativeUI/history/fullscope remainpending.

Issue120 W1: integrate reviewed A3/A4 launcher bytes with D3/T1 menus in isolation. Index metadata reviewed for relative paths/no private absolute paths; source bodies remain external. Three Scriptmix comment-header moves use a strict overlay, retaining immutable migration rows, hashes and tag history. Verification results follow.

W1 source verification (2026-10-20): full root suite3843passed/21workspace-private-evidence skips, lessons199passed.
Commands: rtk proxy env PATH=<Homebrew-bin>:<local-bin>:/usr/bin:/bin PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 FONTLAB_WORKSPACE=<workspace> FONTLAB_PRESERVED_ROOT=<retained Examples tree> <reviewed T1 wheel-env>/bin/python -m pytest -q -rs tests:exit0. Lessons: QT_QPA_PLATFORM=offscreen EXAMPLES_APP_SOURCE=<reviewed T1 source>/fontlabapp, python -m pytest -q -rs lessons/candidate_tests/models_candidate --confcutdir lessons/candidate_tests/models_candidate:exit0.
All494 archived wrapper bytes and all16 practical facade bytes retained exactly. Installed Fly/App rejects every absent archived source before native imports. No original copied/imported/executed; no native acceptance or archive cleanup. Initial system-Git/xcrun failures retained; explicit Homebrew PATH fixes invocation. Exact commands/logs and per-menu hashes live in parent verification/issue-120/menu-integration-w1/. Canonical/live installs/releases/publication unchanged.


## Issue120 current documentation Z5

The current 510-menu source catalogue is separate from the historical 42-page export. Retained manifests are validated before replacing accepted output, without running legacy exporters. Eighteen first-party Apache-2.0 insight listings are frozen inert text with hash/licence manifests. D21 intentional legacy deletions are preserved. Safe hash-named build snapshots prevent parenthesized filenames disappearing through codeinclude.

Full maintained suite:1,993 passed. Locked documentation suite:20 passed. Both changed production modules exceed 80% statement and branch coverage with zero exclusions. Strict self-contained offline build passes; all510 actual rendered menu bodies and all18 inert historical listings match source text exactly. Initial16-view accessibility check passed; final retained-page check is recorded in the parent Z5 evidence. Historical counts remain299/148/151, not current native acceptance.

Wait, but: local source/build/browser checks are not native FontLab execution or whole issue120 acceptance. D25 native connectivity, complete branch/routes/archive/distribution/release and publication gates remain open. No canonical checkout, live install or remote site changed. Exact commands, retained failed attempts and receipts are in the parent workspace verification/issue-120/docs-z5/.


## Issue120 documentation quality Z7

Documentation SDK tests now live under tests_docs and run in the locked documentation environment. Runtime tests stay on Python3.11. The real push gate combines both measurements without exclusions or a reduced threshold. No runtime menu body changes. All199lesson tests (including four legacy/lesson namespace orders),1993current root tests and5SDK tests pass. EXAMPLES_LEGACY_API_SOURCE selects only the reviewed read-only first-party legacy API; it does not redirect the current suite. Audit controls reject historical script and native-module execution. D21 deletions remain intact.

These local gates do not establish native/font/history/reopen or site-publication acceptance. Exact commands and retained failures are in the parent verification/issue-120/docs-quality-z7/.


## Issue120 Z10 — complete part2 glyph sorting/filtering candidates

Adapt both basic/custom part2 source/proxy workflows to the complete current
font's names, all Unicode assignments and local modification dates. Shared App
Table/Query, Qt controls and owned model lifetime keep all three pattern modes,
independent case switches, Basic key-column/native QRegExp, Custom first-two-
column OR/inclusive dates/angle-tail ordering, both views and modeless Close.
Raw demonstration records are replaced; initial dates are unrestricted and date
limits explicit. Custom's ignored column control stays visible and disabled.
Two immutable source-index identities now route to practical Models commands.
Original bodies/resources and all other menus stay untouched. Distinct part3
contracts remain pending. Qt5/Qt6 and metadata-shaped tests are offline evidence;
native PythonQt callbacks/read/cache/font/history/save/reopen and publication/
integration/release gates remain open under D25. No original numerator changes.


Z10 documentation output: `./build.sh --offline` now renders into `.build/site`,
separate from retained authored guides in `docs`. Two successive real clean
builds preserve the guide bytes. The earlier default overwrote those guides in
the isolated test checkout; their exact branch bytes were restored and the first
render retained as evidence. No canonical owner path or live site was changed.


## Z10 verified source/artifact checkpoint — 2026-10-20

96new App controls; full source2201passed. All6whole new modules and both
practical menu modules100%statements/branches,zero exclusions. Examples1996
passed;6locked SDK tests. Actual standalone arm64 Qt5.15.19/PyQt5.15.11 tests
pass42cases against the independently installed App0.2.54.dev0 wheel; four
light/dark renders inspected. Standalone Qt5 and Qt6 are separate processes;
neither is a native FontLab/PythonQt acceptance result.

Normal independent wheel/source installs each pass App2199/2generated-shim
skips,Glyport2997/3existing skips,Fontport4489/2existing skips with63known
warnings,Lessons197,Scriptmix1074/1existing skip and Examples1996. All483
runtime/resource pairs match all4packages/two installs;169priorApp files and
668unchanged prior menu payloads are exact. Two indexed wrappers move to Models
through a hash-bound overlay;all494originalsource identities/bytes remain.
Two original part3 variants remain separate pending workflows.

Retained first-red tests and the first Qt checkbox-accessor mismatch. The real
clean docs build exposed deletion of8tracked historical guides in this isolated
checkout. Their exact branch bytes were restored; site_dir now targets.build/site.
A tests-first real clean-build regression reproduces the deletion then passes
twice;two actual strict builds preserve all8guides. All510current sources render
exactly and the full site passes the private-path/credential scan. Missingbs4in
the docs environment is retained; the audit uses an isolated uv dependency.

All11zone originals,7247source ledger,1111owner hashes and3canonical statuses
remain unchanged. NativeTCPerrno61/fence retained;no native driver,canonical
merge,live install,tag/release/site publication or accepted numerator change.
Full goal/native/integration/distribution/publication remain open.

Wait, but: native QObject virtual callbacks, actual metadata/getter/cache/font/
history/dirty/save/reopen preservation and original/native workflows are still
unproved. This is a complete source/artifact candidate,not98%project acceptance.
Exact commands/exits and retained evidence are in the private workspace's
verification/issue-120/sort-filter-z10/command-receipts.json and root WORK.md.


## Issue120 Z11 — complete part3 typed-date workflows

Both official part3 Basic/Custom models now adapt complete current-font metadata
through shared App controls. Typed QDateTime cells, locale short-date matching,
native QRegExp syntaxes, inclusive calendar-day limits, case-sensitive email-token
text comparison and original ISODate ordering remain distinct from part2. Data-
specific demo filters become full-font snapshots with explicit optional limits.
Read-only models, Refresh/refusal and all completion routes keep owned lifetime.

Tests exposed two timestamp-reader defects: displayed local dates assumed an
already-local stamp and the source fence lost within-second changes. A local
copy and native epoch milliseconds now preserve the intended observations. An
optional immutable epoch channel keeps exact typed-cell instants (including DST
folds); Basic retains millisecond ordering, Custom retains its source comparator.
No new native font API, writer, original-source execution or live install is used.
Standalone tests do not establish actual PythonQt/font/cache/history/persistence
acceptance. All original/native/integration/distribution/publication gates stay open.


## Z11 verified source/artifact checkpoint — 2026-10-20

43 new App tests; full source 2244 passed. All seven changed whole production
modules and both new menu facades have 100% statement/branch coverage, with zero
exclusions. Examples 1999 passed plus six locked SDK tests. Independently installed
App 0.2.55.dev0 passes 139 focused controls in standalone arm64 Qt 5.15.19 /
PyQt 5.15.11; four light/dark public-entrypoint renders were inspected. These
external processes are not native PythonQt acceptance.

Normal wheel and source installs each pass App 2242/2 generated-shim skips,
Glyport 2997/3 existing skips, Fontport 4489/2 existing skips (63 known warnings),
Lessons 197, Scriptmix 1074/1 existing skip and Examples 1999. All 485 runtime/
resource pairs match; the App source archive contains 326 audited files.
170 prior App files and 668 prior menu payloads remain exact; five shared App
modules intentionally change and two helpers are added. Both original part3
source bodies and all 494 indexed identities remain byte exact, with two
practical routing replacements. Examples now has 20 candidate facades and 490
preserved-source dispatchers; the original accepted numerator does not change.

The strict docs build, all 510 exact rendered source bodies, full-site privacy
scan and eight authored-guide hashes pass. All 11 zone originals, the 7247-row
ledger, 1111 owner hashes and three canonical Git statuses remain unchanged.
Retained first-red controls cover metadata/local time, millisecond source fences,
typed epoch cells, initial proxy reactivation and new menus. The corrected
test-fixture date and formatting/import failures remain visible in evidence.

Wait, but: actual PythonQt virtuals, metadata getter behavior, complete font/
cache/history/dirty/save/reopen, original workflow, integration/distribution/
release and publication acceptance remain open. D25 is pending and the busy
fence remains held. No native driver, restart, canonical merge, live installation,
tag, release or site publication was performed. Exact commands, exit codes and
retained evidence are in the workspace's private typed-date-z11 directory.


## Issue120 Z13 — complete read-only Simple Tree Model pair

Both archived part2/part3 read-only tree entrypoints now show complete current-
font glyph metadata through a generic immutable App tree and injected Qt model.
Each glyph keeps font order, every Unicode assignment and its local modification
date; missing values stay explicit. Expand/collapse and cell selection are
read-only. Part2 retains fixed columns, noneditable EditRole text, row/column
status and File > Exit; part3 retains DisplayRole-only text and parent-item
column counts. Their separate editable-tree entrypoints remain outside this pair.

Source-specific synthetic outline/default.txt loading becomes structured native
metadata input, using the existing source-fenced reader. Capture and model
construction share one deadline. Refresh replaces the entire model and selection
owner; failure removes all results. Model virtual failures are contained and
obsolete callbacks become inert. All completion routes release owned resources.
The raw sources/resources are preserved and never executed or packaged here.

Requires reviewed unpublished App>=0.2.57.dev0 through Fly. Standalone Qt model
tester/view/lifecycle checks and ordinary artifacts do not establish PythonQt
virtual dispatch, native getter/font/cache/history/dirty/save/reopen acceptance.
Native D25, integration/distribution/release/publication and the full original
goal remain open. No new native API, writer or live installation is used.


## Z13 verified source/artifact checkpoint — 2026-10-20

66 new App controls; full source 2341 passed. All four complete new production
modules exceed 80% statements and branches with zero exclusions: three are
100%/100%; the owned panel is 95.97%/95.00%. Both new menus have 100%/100%.
Examples 2002 passed plus six locked SDK tests. Independently installed arm64
Qt5.15.19/PyQt5.15.11 passes all 66 focused controls, including Qt's actual model
tester, ragged/deep hierarchy, duplicate occurrences, stale/foreign indices,
roles/flags, expansion, selection, deadline/failure/worker-thread refusals and
all six completion routes plus File > Exit and parent destruction. Four final
installed public-entrypoint light/dark renders were directly inspected.

Final App0.2.57.dev0 normal wheel/source installs each pass App2339/two generated-
shim skips, Glyport3017/three existing skips, Fontport4489/two existing skips
with63known warnings, Lessons197, Scriptmix1074/one existing skip and Examples
2002. Cold Fly imports include the new tree APIs. All489runtime/resource pairs
and335App source-archive files match current source; licensing/privacy/Python3.11
audits pass. Every177priorApp runtime file and all other package payloads remain
exact; only four App helpers are added.

Strict docs build, all510exact rendered menu bodies, full-site privacy scan and
eight authored-guide hashes pass. All494original identities/bodies, the original
part3default.txt asset,668prior menu payloads,11zone originals,7247-row ledger,
1111owner hashes and three canonical Git statuses remain unchanged. Two wrapper
routes intentionally replace prior dispatchers; total menus remain670. Examples
has22candidate facades/488preserved-source dispatchers. No native numerator changes.

Retained first-red data/menu/thread controls, stdlib optional-Jython import-probe
test-harness correction, complete-suite cwd failure and hardcoded old-dispatcher
harness failures. Tests now preserve every original indexed assertion while
using each adaptation's explicit shared API module. Added the missing Result
docstring section, retained original part2 File > Exit and tightened view-detach/
exception fencing before the final build. Existing editable-tree entrypoints
remain separate and pending. No source body or original asset was executed.

Wait, but: standalone Qt5/Qt6 and immutable scalar tests are not FontLab/PythonQt
virtual/getter/font/cache/history/dirty/save/reopen or original native acceptance.
D25 remains pending, TCPerrno61 and the busy fence hash unchanged. No native
driver, restart, preference change, live install, canonical merge, tag, release
or site publication occurred. All original workflow/package/integration/docs/
distribution/release gates stay open. Exact commands/exits, failed attempts and
receipts are in the workspace's private glyph-tree-z13 folder and root WORK.md.

## Issue120 Z16 — implementation in progress

Fresh inherited App 2,422 and Examples 2,002 suites pass. Added the complete part2 calendar/current-font local-day report, generic controls/formats, owned panel and one hash-bound Fly menu move. 95 focused App checks pass before final full/artifact/native gates; the separate part3 calendar remains pending. Original scripts are read only and never run. D25 remains pending with TCP errno61 and unchanged busy fence. Exact source/Qt/commands are retained in calendar-z16 and root WORK.md.

## Issue120 Z16 — complete part2 calendar source/artifact checks

App 2,517 and Examples 2,004 source tests pass; the locked documentation SDK adds
six passes. The 95 new App checks cover every part2 calendar option, scalar local-
day metadata, exact order/Unicode/epoch retention, undated/invalid/empty/DST cases,
main-thread refusal, coherent bounds/defaults, format ownership, setup failures,
readable light/dark date surfaces and all six completion routes/parent teardown.
Every whole new module has 100% statements and branches except the complete owned
panel at 100% statements/93.33% branches. Zero exclusions. The moved menu is
100% statements/branches; all 494 indexed identities retain their assertions.

Final App 0.2.60.dev0 (app-artifacts-v3) passes normal wheel/source installations
and dependency checks. In each review-v2 install: App 2,515/two generated-shim
skips, Glyport 3,054/three existing skips, Fontport 4,489/two skips/63 known
warnings, Lessons 197, Scriptmix 1,074/one skip and Examples 2,004 pass. Cold Fly
imports cover all new public APIs without bindings or reverse package imports.
All 495 runtime/resource pairs and all 349 App contained source files match
current source, archives and both installs. All 183 prior App and all 115 Glyport
runtime files remain exact; only four App runtime modules are added.

Installed standalone arm64 Qt5.15.19/PyQt5.15.11 passes all 95 focused checks.
The actual public entrypoint renders in light and dark palettes; two installed
renders match the candidate source pixel-for-pixel and were directly inspected.
Only owned scalar data and widgets are used in the external preview. The first
dark render exposed unreadable named black dates/headers; an owned copied palette
repairs Base/AlternateBase/text roles and retains dim off-month dates, while the
form/report keep their parent theme. The independent failing palette test and
initial render are retained. No FontLab native outcome is inferred.

Strict offline docs build, all 510 current source-rendered bodies, full-site
privacy scan and all eight authored-guide hashes pass. One dispatcher moves to
Widgets/Glyph Modification Calendar.py through a hash-bound overlay. All 669
other menu bodies, 494 original source bodies, 11 zone originals, 7,247 ledger
rows, 1,111 owner hashes and three canonical documentation statuses are unchanged.
The separate part3 calendar (May 1 and bold/italic headers) is unchanged/pending.
Current Examples layout: 23 candidate facades and 487 preserved-source dispatchers.

Retain absent-module first red, from-package lazy-native import failures, the
Ruff import rewrite correction, instance-vs-class Qt enum failures, initial dark
readability failure, the missing destination folder attempt and fixture re-export
lint repairs. Class-level enums and qualified imports now work in both external
Qt bindings. Test-only import/style changes caused artifact v2/v3 rebuilds; no
coverage/test threshold, native gate, frozen source or accepted numerator changed.

Wait, but: these source/installed/standalone Qt/doc checks do not prove actual
PythonQt callback/getter/cache/font/history/dirty/save/reopen preservation or any
original native workflow. D25 is pending, TCP errno61 and the same busy fence;
no native driver, restart, preference change, live install, canonical merge,
tag/release or site publication occurred. Every original issue120 gate remains
open. Goal ACTIVE; 98% unproved. Exact commands/exits and evidence are retained
in calendar-z16 and root WORK.md. Feature push gates are recorded separately.

## Issue120 Z17 — in progress

Fresh inherited App 2,517/Examples 2,004 suites pass. Implemented distinct part3 calendar and shared base/panel; 158 focused calendar checks pass before final full/artifact gates. D25 is still pending with TCP errno61 and unchanged busy fence. Original/corpus bodies remain read only and unexecuted. Exact verification is retained privately in calendar-official-z17 and root WORK.md.

## Issue120 Z17 — source and artifact verification

Implemented the distinct part3 calendar through show_official(): full ordered Qt locale rows, seven week starts, 1900–3000 range, four colors, Bold/Italic/Plain headers and independent first-Friday/May-1 marks. Shared date/signal lifecycle preserves part2 exactly. Old owned marks clear when controls or page change.

Fresh full source suites: App 2,580; Examples 2,006; SDK 6. Strict offline docs pass. Six changed whole App modules exceed 80% statements and branches with zero exclusions (base 95.89/100, dialog 100/93.33, other four 100/100). The new menu is 100/100. Ordinary independent wheel and sdist installs pass App 2,578/2 existing skips, Glyport 3,054/3, Fontport 4,489/2 with 63 existing warnings, Lessons 197, Scriptmix 1,074/1 and Examples 2,006. All 498 runtime/resource pairs match. App candidate is 0.2.61.dev0.

Standalone installed arm64 Qt5 5.15.19 passes 158 focused checks. All 603 locale rows are retained. Four light/dark renders match source exactly; part2 also matches its prior candidate exactly. All 510 Examples menus render source exactly, and all eight authored guides/privacy checks pass. All 669 other menu bodies, 494 original bodies, 11 zone originals, 7,247 ledger rows, 1,111 owner hashes and three canonical statuses are unchanged. Prior 184 App and all 115 Glyport runtime files remain exact apart from three intentional App changes and three additions.

Wait, but: standalone Qt and installed checks do not establish native PythonQt behavior or full font/cache/history/dirty/save/reopen preservation. D25 remains pending. No native calls, restart, live install, canonical merge, release or site publication. Every native/original acceptance gate remains pending; 98% is unproved. Exact commands, logs and artifacts are retained in verification/issue-120/calendar-official-z17 and root WORK.md. Feature hook results are recorded separately.


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

Z20 visual acceptance caught the preserved part2 one-pixel completion popup. A tests-first content-width repair now applies the existing Qt popup-size calculation to both variants; key/focus/insertion policies stay distinct. Retain the initial candidate/renders and repeat final full/source/ordinary-install/Qt5 gates with artifact v2. Native qualification remains pending.

## Z20 final source/artifact verification

Final source suites: App 2,693 and Examples 2,008; SDK six. Five whole new production modules exceed 80% statements/branches with zero exclusions: _completion_events.py 98.39/96.43; _glyph_completion_controls.py 100.0/100.0; _glyph_completion_dialog.py 100.0/96.88; completion_editor.py 100.0/95.83; glyph_completion.py 100.0/100.0. Fresh v2 ordinary wheel and sdist installs each pass App 2,691/two existing skips, Glyport 3,064/three, Fontport 4,489/two with 63 existing warnings, Lessons 197, Scriptmix 1,074/one and Examples 2,008; cold Fly imports remain host free. All 504 runtime/resource pairs, all 191 previous App runtime files and 363 contained App source files match. Candidate App is 0.2.63.dev0.

Installed standalone arm64 Qt5 5.15.19 passes 101 focused controls. All four source/installed UI renders match exactly. Direct inspection found the retained part2 one-pixel popup defect; the independent red control and first candidates/renders remain retained. Both popups now use content width. All 510 rendered menu bodies and eight historical authored guides remain exact. The two hash-bound facade replacements preserve 494 original bodies, 668 other menu payloads, eleven zone originals, 7,247 dispositions, 1,111 canonical owner hashes and three canonical statuses. Actual native PythonQt semantics and complete font/cache/history/dirty/save/reopen remain unqualified under D25.

The site-wide API-default audit exposed a stale public-repository classification: fresh GitHub API evidence confirms Scriptmix is public. The API-specific ten-license profile is not an Examples licence determination. Examples now includes the full reviewed MaterialX/Lunr MIT texts as well as Apache-2.0. A separate whole-byte scan uses the explicit three-text Examples profile and verified public repository; complete transitive frontend notice/publication qualification remains open. No native run, live install, canonical merge, tag/release or site publication occurs. Real hook/ref verdicts are retained in the parent workspace evidence.

The source-only commit guard rejected generated .build output before staging Examples. Add .build/ to .gitignore and verify git check-ignore; keep all generated bytes privately available. App source push already passed its real hook. No generated output was committed.

## Issue120 Z23 — complete editable glyph-tree pair

Implement both original editable-tree controllers over full local glyph metadata. Retain distinct sibling/child/column positions, text/QVariant values, header/default labels, part3 key sequences/mnemonics/separators, selection action enablement/status and ordinary delegate editing. Shared App model/view/editor/signal mechanics stage complete replacement views before releasing the current draft. Refresh refuses edited-draft discard; Reset Draft explicitly requests reload; capture/setup faults preserve the prior draft. Failed disconnects retain exact owners. Close button retries control/editor failures; terminal failures retain the destruction tombstone and use window Close. Every ordinary completion, parent destruction, constructor fault and queued callback is fenced. No original body/resource is executed or bundled. Requires reviewed unpublished App>=0.2.66.dev0 through Fly. Native PythonQt and full font/getter/cache/history/dirty/save/reopen, integration/distribution/docs/release/publication gates remain pending D25.

Tests-first expected failures and full source/normal artifact/Qt5/documentation/owner/hook commands, exit codes and final verdicts are retained in verification/issue-120/editable-glyph-tree-z23 in the parent workspace. Preserve archived bodies and all original acceptance denominators. Wait, but: source and standalone Qt do not prove compiled FontLab PythonQt or native preservation.

## Issue120 Z24 — frontend notice candidate

Three baseline suites pass. Tests first reject absent notice artifacts; the authored full-text SHA/link/provenance checks then pass. Notice/provenance pages retain 23 named component groups (24 where print-site is shipped). No runtime assets, source producers, original examples or archive bytes change. Complete transitive closure, Wordcut embedded modules/dictionary, TinySegmenter, Clipboard leaf notices, CSS data SVGs and full publication qualification remain open. Exact commands and failed attempts are retained in the parent workspace at verification/issue-120/frontend-notices-z24. Strict-build, full-suite, browser/privacy and preservation acceptance follow this candidate. Wait, but: a named-component notice batch does not prove the complete transitive inventory or a published site.

Z24 fresh local acceptance: locked strict build passes; served-browser checks verify all26 named full-text bodies and manifest against source, with four desktop/mobile and light/dark views. Documentation tests pass (8); all original menu and guide bytes remain exact. All-byte privacy checks pass with the existing repository-specific text profile. Complete transitive inventory/publication remains false. The real source-branch pre-push gate records the full baseline coverage/test outcome in parent-workspace evidence.

## Issue120 Z26 notice byte preservation

Git autocrlf=input silently normalized three source-bound upstream notice payloads in HEAD. Add scoped `/src_docs/md/licenses/** -text`; restore only bytes proven by unchanged manifest hashes. Preserve all prior attributes and manifests. Regression uses a private temporary Git repository with command-scoped autocrlf=input and checks all notice index, checkout-index and archive bytes, including CRLF probes for LF-only notices. It works from Git-free SDK/source archives and explicitly skips only the Git distribution check if Git itself is absent. No production module or dependency changes.

Tests-first red and green receipts, all84 notice byte audits, full source/docs suites, locked offline strict builds, served notice URLs and privacy receipts live in parent `verification/issue-120/notice-byte-preservation-z26/`. Exact commands and exits are in `N4-notice-bytes-report.md`. Publication/transitive inventory flags remain false; native acceptance remains pending. No commit/push/native/live install.

## Issue120 Z26 — isolate notice-regression Git environment

The earlier pushed notice-byte regression inherited repository-local Git variables
from real pre-push hooks. The controller retained and restored its own affected
Scriptmix worktree index; all437physical source files remained byte-identical
to HEAD. The three earlier notice commits remain published; their completed
real hook exits do not prove parent-index preservation.

Tests first reproduce parent index/config/object mutations using two private
repositories only, for both default and alternate parent index paths. Child Git
commands now remove names returned by `git rev-parse --local-env-vars` from a
copied environment before init/add/checkout/archive, and have10second deadlines.
The injected-context regression preserves the caller environment and compares
every parent file, including index, config, refs, objects and unstaged content.
The original full-notice byte assertions and CRLF probes are unchanged.

Exact commands, exits, ordinary baselines, red/green controls and source-only
acceptance are retained in workspace
`verification/issue-120/notice-env-isolation-z26/`; see
`docs/maestro/issue120/layer-navigation-z26/N11-notice-env-fix-report.md`.
All commands run through `rtk proxy`; an initial machine PATH selection of broken
`/usr/bin/git` is retained separately, followed by actual Homebrew Git controls.
No production module, notice payload/manifest, attribute, dependency, hook, Git
configuration, coverage floor/baseline, source lock or live/native state changed.

Wait, but: successful isolation tests do not accept the whole issue120 workflow.
This corrective candidate requires fresh independent review before commit/push;
all native, integration, release, transitive inventory and publication gates remain.

Final frozen-code checks: Examples complete docs suite11passed; Git-free notice suites
API5/Examples5/Scriptmix6pass. No-Git runs retain manifest checks and report
API2pass/3skip, Examples2pass/3skip, Scriptmix3pass/3skip. Removing only child
environment isolation fails both parent-preservation controls in all3private
copies; removing attributes still fails actual index-byte normalization in all3.
All84upstream notice payloads remain byte-exact across source, original, HEAD,
index, fresh checkout, archive and built site.

```sh
rtk proxy /opt/homebrew/bin/python3.11 verification/issue-120/notice-env-isolation-z26/verify.py suites
rtk proxy /opt/homebrew/bin/python3.11 verification/issue-120/notice-env-isolation-z26/verify.py suites examples scriptmix
rtk proxy /opt/homebrew/bin/python3.11 verification/issue-120/notice-env-isolation-z26/negative_isolation.py
rtk proxy /opt/homebrew/bin/python3.11 verification/issue-120/notice-env-isolation-z26/verify.py bytes
```

Full-suite prerequisites: retained API failure required its existing hardcoded
TypeRig sibling layout; supplied an evidence-only alias to the frozen source.
Examples first full-docs attempt used API's environment and failed on missing
print-site plugin; rerun with each repository's existing locked docs environment
passes. No dependency or configuration change. Exact nested argv/exits and
failed attempts remain in the parent verification receipts. Independent review
and later actual-hook before/after index/config/origin preservation are pending.


## Issue120 curated practical menu delivery

`Scripts/` now contains 28 reviewed practical facades in one category level;
482 remaining archived dispatchers leave the active menu. All 494 historical source
identities remain in the unchanged rescue index. Twelve mapped adaptations stay
native-pending/original-workflow-unaccepted; 482 other identities remain backlog.
Exact retired wrappers remain in private recovery. No archived body is executed
or distributed. Complete reviewed Lessons source/resources already remain under
`lessons/`, including 16 packaged menus and 99 licensed GetGo fonts.

Validation: 544 current menu/docs tests, 199 Lessons tests, actual canonical App/Fly
and Lessons public dispatch for 28 facades / 56 launches, strict local documentation
and 28 exact rendered menu source checks. Native PythonQt/font/history/lifecycle/
save/reopen acceptance and release/publication remain separate gates.
