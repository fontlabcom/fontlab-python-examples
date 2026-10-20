---
this_file: CHANGELOG.md
---

# Changelog

## v1.0.2 (2026-10-16)

Samples: 106 FontLab 9 GUI scripts under examples/samples (copied from Scripts/Samples with tools/sync_samples.py) and a Samples page in docs-export.


## 2026-10-16 - Samples GUI scripts

- examples/samples/: the 106 Samples GUI scripts copied byte for byte from FontLab 9's deployed Scripts/Samples (fontlab-samples 38cf218), with a README generated from each script's #FLM line and docstring (tools/sync_samples.py, --check). docs-export gains samples.md, an index link and a samples count. tests/test_samples.py; suite 1886 passed with fontTools; docs-export 43 files current.

## Release - GetGo testdata re-sync (issue 106)

Seven GetGo VFJs re-synced with getgo-fonts cf1319f (export fixes); manifest axes, name and hashes updated. Native: corpus 99/99, examples 13/13. Merged issue-101-pythonqt-examples into main.

## 2026-10-16 - GetGo examples native acceptance (moved from TODO.md)

- Owned GetGo copies close via close_font(save=False) (f151195); native status recorded in README and native_manifest.json (7ed3e39). Native run examples4-all: 13/13 pass, spacing 0.11 s, 0 stray documents (verification/issue-106/evidence/getgo/examples4-all). Suite 1881 passed with fontTools; docs-export 42 files current.

## 2026-10-16 - GetGo fixtures and provenance (moved from TODO.md)

- Copied the 99 GetGo VFJs unchanged into testdata/getgo (81 Apache-2.0, 11 CC0-1.0, 7 OFL-1.1) with the three licence texts and a manifest pinning source revision 25a4d6d7, SHA-256, glyph/master/axis counts, public code.fontlab.com page and VFJ/TTF links. Verified against the upstream checkout and fonts.json, all 297 links HTTP 200; `*.vfj -diff` in .gitattributes (ac98f06; tools/verify_getgo_source.py, 206 tests).

## 2026-10-15 — completed checklist (moved from TODO.md)

- Acquire, pin and Git-blob-verify all 805 pyqt/examples source files.
- Acquire, pin and Git-blob-verify all 764 eyllanesc/QtExamples source files.
- Catalog all 1,569 original files/resources with exact hashes and portable planned paths.
- Extract source imports, entrypoint evidence, resource associations and license evidence.
- Correct deferred-body launch/main-guard evidence and portable output filesystem errors; reproduce all mappings.
- Publish a categorized candidate index and retain every original mapping.
- Port every numbered example to PythonQt in FontLab: each is implemented or precisely blocked (06 QML, 08 packaging, 15 QtSql blocked; 11 removed by D4); implemented ones launch and close natively (workspace evidence examples-first-native-sdd/, tg4-second-batch/, examples-numbered-complete-scope.json).
- Port every official demo to PythonQt in FontLab: all 187 official entrypoints accounted (127 implemented, 60 precisely blocked); launch/inspect/close 137/137 and blocked records refuse launch (workspace evidence examples-interactions/, examples-batch9/).
- Port every official and additional eyllanesc/QtExamples entry to PythonQt in FontLab: all accounted (implemented or precisely blocked; 299 records, 148 implemented, 151 blocked); the 10 eyllanesc implementations pass natively (6ef7756).
- Provide simple in-host/external launch and owned cleanup. (2026-10-15 native: launch/inspect/close 137/137 implemented ports; all 151 blocked records refuse launch with NotImplementedError before host access; evidence in parent verification/issue-101-ecosystem/evidence/examples-interactions/ and examples-batch9/native-blocked-all.json.)
- Implement first four exact numbered-source ports and copy verified Designer UI.
- Record five individual source/resource MIT reviews in a separate port manifest.
- Provide first-batch named launch/inspect/close, retained handles and Remopy example.
- Accept first four source-loaded ports with native clicks, layout/text, alert dismissal/repeat, Designer OK/Cancel and tracked owned teardown.

## 2026-10-15 — issue 101/104 examples work completed (moved from PLAN.md/TODO.md)

- 148 implemented native-acceptance records carry exact evidence file/record
  citations with cross-checking tests.
- 14 Python and 3 QML candidates and all 69 shared-file ownership records resolved,
  preserving original identities and reasoning (`catalog/reviews.json`).
- Per-file licences and attribution for all non-pyqt-official ports, resources and
  original insights in `catalog/licenses.json` (14 resources still await an owner
  decision; see PLAN.md).
- D7: 187 official records relocated, 431 archive-verified files removed, prose-only
  public handoff copied from private commit 040b2e8; catalogue states/INDEX
  regenerated; source-dependent tests gated on `clean_room_pending` only.
- All 187 official examples independently implemented or explicitly blocked under
  Apache-2.0 (127 implemented, 60 blocked), with hash-bound receipts merged.
- Short-phase Remopy native acceptance driver and offline tests; native acceptance
  of the 187 clean-room records recorded with `tools/record_native.py`, re-run and
  re-recorded at f358589 after review R-examples (127 passed, 60 blocked verified).
- Native interactions: 106 passed and 21 skipped by reason; mouse/key/drop checks for
  22 ports: 20 passed and 2 skipped by reason.
- Nine native-checked recipes in `examples/recipes`, all passing through the
  Scripts-menu route (9/9). The two Glyphs scripts also ran inside Glyphs 3.5.1 and
  4.2 on an in-memory font (curve extent, shift, anchor move, other master untouched,
  components refused, empty list, path report); workspace evidence
  `examples-recipes/glyphs-app/`.
- Coverage review: 299 records, 148 implemented (each with native pass, evidence and
  file), 151 blocked (each with `blocked_reason`), 18 insights, 9 recipes.

## v1.0.1 (2026-10-16)

GetGo edit/export driver exports all variable fonts it can (rafi-italic-var Variable PS remains fontlab/fl#8507); tests find the workspace from any worktree; GetGo testdata re-synced.


- 2026-10-15: Docs integration complete. The docs lane wired `docs-export/` into
  fontlab-python-docs (its commits c8f6092 and 6a68778; nav entry "Examples"). Its
  source lock (ff4c5e4) pins this repository's export at be2712b: all 41 export files
  match their locked hashes, and the build has 40 example pages.

- 2026-10-15 (review R-L6e): replacement assets are recorded and checked only as exact
  generator output; the background is a deterministic PNG (no sips JPEG); the docs
  export manifest hashes the recipe READMEs too.

- 2026-10-15 (L6e): The 14 resources without an individual grant are replaced by
  self-authored files generated by `tools/replacement_assets.py` (editor icon,
  bullet-hole pixmap, synthesized shot sound, spin box images, background picture,
  four style sheets and a new style-switcher form); catalog/licenses.json has 0
  unresolved records, and the upstream identities and findings are kept. The 4 ports
  that load them passed native acceptance again (`tools/native_cleanroom.py`, now also
  for ports with replaced resources, recorded at d3ab76d) and their interaction checks
  (workspace evidence `examples-resources/`).
- 2026-10-15 (L6e): `tools/docs_export.py` exports the catalogue as Markdown pages
  with a manifest into `docs-export/` for the documentation site.

- 2026-10-15: contour_direction plans every glyph before its first edit and skips
  (and reports) collapsed closed contours instead of raising after partial edits.

- 2026-10-15: Review round 2 (RR-examples). `apply_reviews` requires an existing
  evidence root and resolves every evidence selector to the reviewed file's record.
  contour_direction tests nesting exactly on the Bézier segments (recursive
  subdivision) instead of a 16-step flattening.

- 2026-10-15 (R046): DEPENDENCIES.md records the dependency re-evaluation (no host
  packages; recipes import sibling workspace packages; dev tools via uv).

- 2026-10-15: Review fixes (R-examples). Native acceptance is now bound to its run:
  `tools/native_cleanroom.py` hashes each port's dependency closure (own files, ports
  it loads, launcher package) before it runs and records the examples commit, a dirty
  flag and revision stability; `tools/record_native.py propose|apply` refuses
  incomplete phase envelopes, unclean teardown, resets, host-touching blocked ports,
  closures that differ from the run commit or the working tree, dirty or unknown run
  commits and a driver that differs from the run commit. All 187 clean-room records
  re-run at f358589 (127 passed, 60 blocked verified; workspace evidence
  `examples-cleanroom/review/`). `tools/catalog_reviews.py` resolves review citations.
  Recipes: empty-GLYPHS guards for round/contour menu entries, curve-aware contour
  direction, exact outline bounds and current master for tabular figures
  (`glyph_names=[]` is no work), finite bounded kerning values.

- 2026-10-15: All nine recipes also pass when run the way the Scripts menu runs them
  (file executed as `__main__` with menu constants filled in a temporary copy; workspace
  evidence `examples-recipes/menu_route.py`, `menu-*.json`).

- 2026-10-15: Mouse/keyboard/drop checks for the 22 clean-room ports without state
  controls (workspace evidence `examples-cleanroom/events_cleanroom.py`,
  `events-final.jsonl`): 20 passed, 2 skipped by reason.

- 2026-10-15: Native acceptance of all 187 clean-room records in FontLab 9.0.9783
  (127 implemented pass launch/inspect/close with clean owned teardown, 60 blocked
  raise their reason without host access), recorded by the new
  `tools/record_native.py` (validates every entry against its evidence and the
  current port files; refuses stale proposals). 148 implemented records now carry
  native passes. Five mainwindows ports pass `QKeySequence` to `setShortcut`.
  `tools/native_cleanroom.py`: `--fontlabapp-src`, `--reset-stale`, a session
  reset after any unclean port, transport-safe descriptor checks, robust owned-object
  traversal, and a resolvable `fontlab-remopy` source. Interactions (workspace
  evidence): 106 passed, 21 skipped by reason.
- 2026-10-15: Add nine FontLab 9 recipes in `examples/recipes` with native drivers
  and `tests/test_recipes.py` (TypeRig- and Glyphs-inspired, reimplemented).

- 2026-10-15: Integrate all 187 independent clean-room receipts (127 implemented,
  60 blocked) with reviewed Apache-2.0 replacement grants and spec hashes. Preserve
  immutable original provenance and archived resource metadata; regenerate source
  projections/INDEX and the manifest hash without reading originals. Current total:
  148 implemented, 151 blocked; 127 replacement implementations remain native
  unexecuted, with only 21 unchanged non-official native passes retained.
- Replace relocated-file absence assertions and obsolete implementation-specific
  tests with receipt, public-launcher and independent behavioral coverage. Keep
  shared/native-boundary and unchanged non-official tests active. Add
  `tools/native_cleanroom.py`: bounded per-phase Remopy calls, exact-checkout
  imports, sys.path restoration, blocked zero-side-effect checks, owned native
  destruction checks and JSONL/summary output. Native acceptance runs separately.

- 2026-10-15: Relocate all 187 official demos to the private archive at `040b2e8`.
  Remove 431 archived source/resource/notice files after hash and dependency
  checks; remove stale compiled caches too. Preserve source provenance and add
  archive/spec pointers with `clean_room_pending` state and no removed-file
  licence or current native-pass claims. Publish 187 behavioural specs plus their
  index; keep original-reading checkers private. Regenerate source/index states,
  reject pending launches before host access and resume tests by catalogue state.

- 2026-10-15: Reconcile all 148 implemented native acceptance records with exact
  evidence files, line/JSON-pointer selectors and hashes; retain 151 unexecuted
  blocked records. Review 17 uncertain candidates and 69 shared-file owners with
  reproducible inventory overlays. Add 146 per-file non-official licence and
  attribution records; preserve pyqt-official licences and expose 14 resource
  grant gaps. Keep source ports, examples and reference trees unchanged.

- 2026-10-15: Correct owned-path enforcement to apply only to writes. Allow
  bundled assets and user files as read sources across codecs, editors, image
  loaders, address books and settings imports; settings edits still use owned
  copies. Isolate default test temporary files in pytest directories and restore
  the late-close test hook in finally. Add read/write regression and source-audit
  coverage; no commit.

- 2026-10-15: Normalize PythonQt tuple-valued recent-file settings; confine
  file-writing ports' open/save/export paths to their owned temporary directories
  with visible refusal messages. Keep standarddialogs file selectors non-native
  and non-modal. Remove exact owned temporary directories after window close
  callbacks, with object/path/directory-identity checks and retryable cleanup.
  Add 33 regression cases and strengthen the shared doubles and teardown checks.
  Native reacceptance remains pending; no commit or evidence-directory edits.

- 2026-10-14: Fix native screen selection in QPA windows and screenshot; use
  static screen enumeration instead of the null primaryScreen property. Compare
  name/geometry and cover native property semantics and screen aliases in doubles.

- 2026-10-14: Account for the remaining 97 requested entrypoints (94 QtExamples
  and three numbered chats): ten owned PythonQt implementations and 87 precise
  blockers, all native acceptance unexecuted. Extend existing Demo, IPC, worker,
  localhost and doubles infrastructure; preserve QWindow painting, style UI/assets,
  maps, loopback, asynchronous suggestions and three chat delivery variants.
  Record GPL-3.0-only/MIT evidence, exact resource hashes and per-entry native
  checklists. No binding/dependency installation, TODO completion or commit.

- 2026-10-14: Account for all remaining 74 official entrypoints: 16 PythonQt
  implementations and 58 precise capability/dependency blockers, native acceptance
  unexecuted. Preserve 14 exact UI/XML/XSD copies, per-source licences including
  GPL docstrings and Denviso HPND, and all 128 previous port records. Extend the
  existing Demo/doubles/tests, README launch table and per-port controller guide;
  retain owned IPC peers, tracked UI connections, standalone Designer widgets,
  real painter/OpenGL comparison and native XML schema validation. No new
  dependencies, commits or TODO changes.
  Exact offline gate: 685 tests pass; scoped Ruff and Python 3.11 checks pass
  for all 78 changed Python files, with provenance and whitespace checks passing.

- 2026-10-14: Defer storageview volume enumeration after the controller reported
  the five-second native launch deadline; cache tuple results and expose loading.
  Audit all 142 port Python files; defer fetchmore fixture writes/directory scans
  and dirview root setup using tracked, cancellable owned timers. Add eight
  regressions for deferred startup, tuple/empty/error cases and early close.

- 2026-10-14: Implement 27 further official itemviews, graphicsview, drag/drop and
  network ports with 15 exact assets, per-file notices and unexecuted native states.
  Extend the existing Demo/WorkerDelivery/doubles/tests and per-port controller
  guide; retain scoped factories, numeric DOM IDs, async PDF/UI, component geometry
  and cancellable owned localhost servers. Preserve actual Qt fortune framing;
  no external hosts, proxies, broadcast or host settings/cache writes. No commit
  or TODO changes; native virtual dispatch/rendering/teardown await the orchestrator.
  Exact offline gate: 572 tests pass; 30-file Ruff/3.11 checks and provenance audit
  pass, with all 101 prior manifest records preserved.

- 2026-10-14: Fix orderform retaining a void addAction result by keeping its
  explicit tracked QAction before menu insertion. Audit every port/helper,
  enforce native overload returns in doubles and add 11 regression cases;
  offline suite passes 485 tests. Native orderform rerun remains required.

- 2026-10-14: Account for all 29 batch-6 widgets/mainwindows/painting/richtext
  demos: 28 PythonQt implementations and a precise QTextObjectInterface blocker.
  Preserve 48 original resource copies, GPL-compatible headers and actual file
  notices; extend existing tracked ownership, async colour/print helpers, strict
  Qt doubles and per-port native checklists. Settings/style/quit remain scoped
  to owned UI; native acceptance is unexecuted. No TODO changes or commit.

- 2026-10-14: Fix native easing enum/value-class dispatch in three batch-5
  ports; audit colour/cursor/fill boundaries across all ports and enforce the
  exported value types in doubles, with 14 additional regression cases.

- 2026-10-14: Account for all 16 batch-5 official demos: implement 15 animation,
  graphics-view, desktop and worker ports; block shared memory precisely because
  the host omits QSharedMemory.detach and a documented Python byte-buffer API.
  Retain 45 byte-identical assets and original source notices; native acceptance
  remains unexecuted. Two explicit original GPLv3 alternatives are selected;
  fourteen BSD/GPL collection scope reviews remain unresolved.
- Extend existing official ownership/tests/doubles with cancellable Python
  producer/consumer and Mandelbrot delivery, native animation/state relays,
  component geometry, inert screenshot/tray startup, owned asynchronous file
  saving and complete per-port controller checklists. No commit or TODO change.

- 2026-10-14: Implement 18 further official PythonQt ports: drag/drop, lighting,
  item views and address-book parts 1–7, with 15 exact resources. Extend the
  existing manifest, launch table, official tests/doubles and native checklists;
  all new native acceptance states remain unexecuted. Retain per-file BSD source
  notices with the collection GPLv3 terms and unresolved scope.
- Replace stream/wrapper arithmetic, Python model pointers, custom PyQt signals,
  modal dialogs and user-file pickle I/O with native QVariant buffers, numeric
  index IDs, tracked timers/callbacks and owned temporary address-book files.
  Keep failed cleanup guards queued so active drag sources cannot be deleted.

- 2026-10-14: Preserve QMainWindow.centralWidget() in icons and i18n by renaming
  Python fields to _central_widget. Audit all official ports for native slot
  shadowing; add strict double and AST regressions, including inherited methods.

- 2026-10-14: Fix controller-reported official-port failures: remove unsafe Qt
  wrapper arithmetic, release only explicitly declared Python fields, replace
  native constructor keywords with setters, and use QByteArray.data() for bytes.
  Harden doubles to reject wrapper arithmetic, null native properties, constructor
  keywords and implicit QByteArray conversion; add AST and interaction regressions.
  Native reacceptance and licence reconciliation remain pending.

- 2026-10-14: Port 23 official pyqt/examples demos to injected PythonQt, covering
  dialogs, layouts, main windows, painting, tools and widgets. Preserve original
  source identities and 107 byte-identical resources; native acceptance remains
  unexecuted for all 23 and no existing acceptance records are changed.
- Retain the original BSD headers alongside the GPLv3 collection terms and record
  their unresolved scope in the manifest and official-source notice.
- Add tracked asynchronous dialogs, owned temporary settings, scoped styles and
  translations, cancellable chunked file search, dynamic menu disconnection and
  explicit painter cleanup; fix inherited negative layout indexing, regexp
  escaping and false-string boolean conversion. Add per-port native checklists
  and strict exported-member doubles with interaction/failure tests.

- Add original insight ranks 13–18: owned QUiLoader form, cancellable worker
  queue, scoped sample console, idempotent owned menu/action tokens, sample
  QUndoStack commands, and existing compiled wrapper/native slot exposure.
- Expose controller controls, fail clearly for absent host classes, and register
  second-batch native acceptance as unexecuted without changing first-batch states.
- Add tracked dynamic action disconnection, hardened form/menu/undo doubles and
  interaction/failure tests; exercise both glyph-properties toggle directions.

- 2026-10-14: Fix controller-reported insight launch failures: native PythonQt
  wrappers reject new Python attributes. Move controls from windows to
  ExampleHandle, clear them before owner deletion, and seal native doubles while
  allowing Python subclass fields. Audit second-batch ports/editor/chat helpers;
  their custom fields already belong to Python subclasses. Add regression tests.

- 2026-10-14: Survey all 895 PythonQt reference files in 29 manifest source
  entries; add a ranked, categorized guide with numbered citations, licence
  evidence limits, existing coverage and controller native checks.
- Add twelve original Apache-2.0 insight examples with named launch/inspect/close,
  tracked disconnection and rollback for partial owned builds. Cover models,
  timers, contour painting, scoped input, properties, persistence, errors, docks
  and scenes; no runtime dependencies or changes to reference/catalog inputs.
- Register insights separately with native acceptance unexecuted; test owned
  interactions, manifest citations, build failures and disconnect-before-delete.

- Track and disconnect every port-owned PythonQt signal before native teardown,
  including gallery string-signature connections, editor prompts/actions, chat
  timers/input/destruction, and the existing Signals and Slots port.
- Stop timers/workers first; release callbacks, inspection/model references,
  gallery child attributes and editor/chat subclass closure cells before closing
  alerts and the native owner. Add connection inventories and teardown-order tests
  following the controller-reported gallery SIGSEGV; native reacceptance pending.

- Port numbered examples 02, 07, 09, 10, all three 11 entrypoints, 12, 13 and
  14 to injected PythonQt QtCore/QtGui; native acceptance remains unexecuted.
- Add explicit blocked QML (06), fbs/PyQt6 executable (08) and QtSql/database
  (15 plus initializer) records, with exact catalog identities and host reasons.
- Preserve five required assets byte-for-byte; retain gallery BSD notice with
  unresolved license review. Record painter sound capability limitation.
- Scope styles to owned UI; add asynchronous editor prompts, UTF-8 file actions,
  GUI-thread chat delivery and worker join cleanup. Extend boundary/hash tests.

- Exclude deferred function, async-function, method and lambda bodies from
  entrypoint evidence; retain definition-time expressions and class execution,
  with complete imports/API/capability extraction unchanged.
- Return portable inventory errors for output directory/file failures. The
  complete pinned catalog, classifications, hash and four-port state are unchanged.

- Read both launcher catalogs explicitly as UTF-8 in FontLab's ASCII-default
  embedded Python; preserve all Unicode metadata and source/resource bytes.
- Close/delete the Designer QFile when QUiLoader construction fails, with
  regression checks for constructor cleanup and ASCII-default Unicode lookup.

- Implement four original numbered examples as direct PythonQt ports: QLabel,
  QVBoxLayout, Signals and Slots and Qt Designer; preserve required UI bytes.
- Add import-safe named host launcher, retained native handles, JSON snapshots,
  scoped `OwnedWidget` cleanup and an ordinary Remopy example.
- Record individual MIT review, source IDs/hashes and pending native acceptance
  in a separate manifest without altering the complete static catalog.

- Catalog both complete pinned collections: 1,569 original files, 465 Python
  files, every resource and both case-distinct matplotlib source names.
- Add deterministic stdlib inventory tools, static source/API/resource analysis,
  conservative license evidence, planned port mappings and categorized navigation.
- Verify receipt/source mismatch failures and complete catalog coverage with
  19 tests; retain pending implementation, license review and native acceptance.

- Verified the first four source-loaded ports in actual FontLab, including alert dismissal/repeat, Designer results and observed owned-object teardown; preserved complete remaining collection scope.

- Removed the three PyQt Thread chat ports and their network helper (owner decision); they contacted a third-party chat server.

- 2026-10-15: Repair native official-port interaction boundaries: explicit sender
  bindings across every port, coordinate-owned spreadsheet formulas, exact native
  state-transition signals, checked localhost UDP addresses/writes, document
  modification notifications and destruction-aware delegate editor inspection.
  Retain/resolve Python graphics objects after native item retrieval and expose
  Elastic Nodes' center control. Preserve original CounterLabel offset semantics.
  Add 22 regression cases with stricter native doubles; native reacceptance pending.

## 2026-10-15 — workspace plan and checklist reconciliation

Completed repository scope archived after reading WORK.md and checking the
workspace evidence. Workspace release/integration gates remain in the parent
PLAN.md. Historical verification limits below remain part of the record.

### Archived PLAN.md

# Plan

No open work; completed items are in CHANGELOG.md.

Standing scope notes: blocked records stay in the denominator (R004). Removed as not
feasible (workspace DECISIONS.md D8): implementing the missing Qt modules in FontLab's
PythonQt (QML/Quick, WebEngine, Charts, multimedia/GStreamer, QtSql drivers, D-Bus,
matplotlib's Qt backend), and interactions that would use the user's clipboard,
screen capture or system tray.

### Archived TODO.md

# Tasks

No open tasks.

- Add all13 packaged GetGo lessons with99licensed fixtures and shared App detached reports; source/artifact checks pass, native acceptance remains pending.

- GetGo candidate: correct sixteen-menu guide, matching App prerequisite and distributed native-checker namespace. Native verification remains pending.

Issue120 W1 integration candidate: 16 practical and 494 preserved-source menu facades consolidated without copying/executing archive bodies. Native and distribution acceptance remain pending.


## Issue120 current documentation Z5

The current 510-menu source catalogue is separate from the historical 42-page export. Retained manifests are validated before replacing accepted output, without running legacy exporters. Eighteen first-party Apache-2.0 insight listings are frozen inert text with hash/licence manifests. D21 intentional legacy deletions are preserved. Safe hash-named build snapshots prevent parenthesized filenames disappearing through codeinclude.


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

## Unreleased — Issue120 Z16

- Adapt the complete part2 Calendar Controls workflow to current-font modification dates through Fly and shared App UI. Keep all original controls; synchronize defaults/limits and repair dark date-surface readability. Preserve the distinct part3 source and all original bytes. Native qualification remains pending.

## Unreleased — Issue120 Z17

- Adapt the distinct complete part3 calendar to current-font dates via Fly and App. Preserve every locale, seven week starts, source ranges/styles and independent first-Friday/May1 rules; clear stale owned marks. Share mechanics and lifecycle while retaining the full part2 policy/public paths. Native qualification remains pending.


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

- Retain full reviewed MaterialX/Lunr MIT texts beside Apache-2.0; complete transitive frontend notice/publication review remains pending.

## Issue120 Z23 — complete editable glyph-tree pair

Implement both original editable-tree controllers over full local glyph metadata. Retain distinct sibling/child/column positions, text/QVariant values, header/default labels, part3 key sequences/mnemonics/separators, selection action enablement/status and ordinary delegate editing. Shared App model/view/editor/signal mechanics stage complete replacement views before releasing the current draft. Refresh refuses edited-draft discard; Reset Draft explicitly requests reload; capture/setup faults preserve the prior draft. Failed disconnects retain exact owners. Close button retries control/editor failures; terminal failures retain the destruction tombstone and use window Close. Every ordinary completion, parent destruction, constructor fault and queued callback is fenced. No original body/resource is executed or bundled. Requires reviewed unpublished App>=0.2.66.dev0 through Fly. Native PythonQt and full font/getter/cache/history/dirty/save/reopen, integration/distribution/docs/release/publication gates remain pending D25.

## Issue120 Z24 — browser notices

Add source-bound full texts and provenance for named frontend components, including transitive JavaScript dependencies, icons, shared theme inputs and external font responses. Keep the full transitive/publication review explicitly open; runtime assets and retained archives are unchanged.

## Issue120 Z26

Preserve exact upstream notice bytes through Git filters, fresh checkout and archives; add a CRLF distribution regression. Source manifests and pending publication scope remain unchanged.

## Unreleased — isolate temporary notice repositories

- Clear Git's documented repository-local environment for temporary notice
  distribution commands and bound each child call to10seconds.
- Exercise inherited hook context with both default and alternate parent indexes;
  require byte-exact preservation of parent config, refs, index, objects, files
  and caller environment. Keep every notice/filter/checkout/archive assertion.
- Preserve all upstream notice payloads and existing attributes/manifests.
  Source-only correction awaits fresh independent review; no new commit/push.


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


## Issue120 N40 — spacing worksheet menus in the curated tree

Add exactly the reviewed framed and frameless Glyph Spacing Worksheet facades to
the curated 28: 30 current menus, 14 mapped adaptations and 480 historical source
identities still awaiting implementation. Preserve the original 28 menu bytes,
all Lessons sources and provenance, the 494-identity rescue index and existing
licence bytes. Append the complete reviewed worksheet source attribution and
licence; include the exact source guide and regenerated current source pages.

These lazy Fly facades require App>=0.2.70.dev0 and are verified with the private
combined App0.2.73.dev0 artifact. Native acceptance remains 0/432 pending; no
FontLab execution, live installation, release or publication occurs here.


## Issue120 N56 — complete glyph-name pattern laboratory candidate

Retain the complete clean-room Pattern Matching Inspector as a useful modeless glyph-name rule authoring tool: editable native histories, four QRegExp syntaxes, case/minimal matching, escaped literals, UTF-16 positions/lengths and all captures. Add complete captured glyph names and ordered batch capture inspection through existing owned capture mechanics. Share only injected native Qt evaluation, controls and owned lifetime in App. Drafts remain local; no font/selection/history/preferences/file/Output writer or live install is added. Source/artifact/standalone checks are distinct from native PythonQt/getter/cache/history/dirty/save/reopen acceptance, which remains pending.


## N79: both elastic-node component dependency graphs (.83 candidate)

Retain the distinct part2/part3 force laws, fixed nine-node graphs, node/edge
geometry/paint, keyboard/wheel controls and timer policies. Current-font mode
reads all current-master glyph component names twice; repeated/cyclic/missing
references and isolated/unencoded glyphs remain in source order. Drag/shuffle
change only local coordinates. Refresh clears stale captures, Stop Motion stops
both timer forms, and actual drag state guards Close. No font writer runs.

Focused tests first failed with the missing new module; subsequent pure-model,
SDK-shaped rejection and actual standalone Qt widget tests pass. Exact expanded
commands/results and final ordinary artifact/whole-module evidence are retained
in workspace verification/issue-120/elastic-component-graphs-z32. Existing source
bytes and both original hashes remain preserved. Native FontLab acceptance is
pending; no canonical write, live install, push, tag, release or publication.
