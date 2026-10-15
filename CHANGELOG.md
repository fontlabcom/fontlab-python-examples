---
this_file: CHANGELOG.md
---

# Changelog

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

## Unreleased

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
