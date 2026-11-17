---
this_file: TODO.md
---

## Next steps (prioritised, 2026-11-17)

1. P0 Task 7: tag and GitHub-release examples (latest v1.2.7 does not contain b281fcc), install the released packages in FontLab 9 and live-test (needs live FontLab).
2. P0 Reconcile WP10/WP11 labs, Lessons entrypoints and compatibility launchers with the current App/Scriptmix/Fly tuple (owner work order 2026-11-14); port the WP10 labs snapshot onto the WP09 routes.
3. P1 Node Table: refresh after native Undo; Stem Blend / Scale With Stem Compensation tolerance (native smoke).
4. P1 Issue 255 native qualification of released Lessons workflows.
5. P2 Lessons (examples/lessons) rows; Task 6/6b native verification.
6. Test-infrastructure and gate rows are deprioritised at the end of this file.

## Task 6b remaining verification

- [ ] Re-run the exact Task 6b uv gate with a writable dependency cache and working package resolution; fallback CPython 3.11 suite passes.
- [ ] Qualify the 66 Task 6b menus and packaged network helper in FontLab: close/reopen, callbacks, workers, saved files, XMLPatterns, sockets, screen capture/tray/drag-drop and hardware OpenGL.

## Task 6 remaining verification

- [ ] Build the cleaned site with the complete hash-locked dependency cache; review generated output before delivery.
- [ ] Install the matching Lessons/App cohort and run all new/restored demos in FontLab 9, checking callbacks, rendering, Close/reopen and editor save persistence.

# Open tasks

- [ ] Reconcile WP10/WP11 labs, Lessons entrypoints and compatibility launchers with the current App/Scriptmix/Fly tuple; defer the complete profile/native matrix after focused route checks.
- [ ] Issue 255: After explicit D43 recovery and admission, qualify released Lessons workflows and the three separately published outer examples in FontLab with matched source paths, native lifecycle/history and saved/reopened font evidence.

- [ ] Task 7: tag and release echopy/examples/python-docs, install in FontLab 9 and live-test (see Next steps).
- [ ] Reconcile WP10 and review the 100-source/25-lab map against the integrated App/Scriptmix cohort; WP09 has nine implemented destinations and 48 retained compatibility launchers.
- [ ] Independently review each WP09 source/destination/runtime profile and current compatibility-launcher hash; retain behavior-parity false until full route review passes.
- [ ] Reconcile the packaged Lessons entrypoints and installed stale-menu cleanup in WP11 before retiring any source launcher.
- [ ] WP11: after the orchestrator commits the reviewed WP09 sources, regenerate catalogue pages only with containing commits whose blobs equal the current launcher bytes; retain historical route pages and redirects separately.
- [ ] Native: qualify all nine WP09 labs and 51 profiles in FontLab PythonQt under WP12, including property getters, sorting/filtering identity, Unicode/IME, deferred MIME, model notifications, read-only/editable differences and dock-refused-Close recovery.

- [ ] Keep all lesson, original-source and destination-hash contracts while updating examples for reviewed App/provider migrations.
- [ ] Qualify the installed cohort, actual owned native workflows, whole-font/history, window priority and save/reopen; keep site and runtime acceptance separate.

- [ ] Repair the audited27direct-panel constructor/parent-death and remaining shared-launcher lifetime gaps without losing controls or failed-Close owners.
- [ ] Native-qualify dock refusal/retry/floating priority with the reviewed App candidate; source/ordinary results are in CHANGELOG.md.

- [ ] Qualify the priority-message candidate with its matching App artifact and native FontLab; source coverage and standalone Qt checks pass, but do not close the host gate.

- [ ] Qualify all current menus in installed FontLab: callbacks, close/reopen, stale snapshots, cancellation, errors and complete font/cache/history preservation.
- [ ] Qualify Models filters, calendars, read-only/editable trees, completers, pattern rules, spinboxes, sliders, elastic graphs and spacing worksheets in native PythonQt.
- [ ] Qualify character-map drawing/copy, Find Files dialogs/desktop opening and image-viewer printing/OS behavior in the native host.
- [ ] Qualify the remaining metadata, contour, kerning and other layer writers with Apply/Undo/Redo and saved/reopened owned fonts. Copy Layers From Font passed live (6 layers as one row, source untouched, reopen equal; hinted glyphs refused with "hints or guides are not transferred").
- [ ] Qualify the thirteen packaged GetGo workflows and reconcile their remaining historical catalogue entries after acceptance.
- [ ] Re-sync corrected GetGo VFJs when supplied; refresh hashes and manifests, then rerun the full corpus and variable exports.
- [ ] Probe whether Node Table writes to __smart_selected queue changes or persist in FontLab.
- [ ] Check Stem Blend and Scale With Stem Compensation read-back with FontLab coordinate rounding enabled.
- [ ] State the decided App minimum `App>=1.2.28` in both Font Reference Image Viewers (now `App>=0.2.156.dev0`; decision and tag evidence in CHANGELOG 2026-11-11, `DECIDED_FLOOR` in tests/test_image_viewer_app_floor.py). Next check: update both docstrings when Image Viewer Lab absorbs them or at the next consolidation-ledger re-baseline; both scripts must stay byte-identical until then.
- [ ] Reconcile and qualify the existing production App route-A zone writer on the chosen current tuple before adopting scripted zone editing. Preserve all-master staging, one history commit, row/Font-window refusals, tags/lock, Undo/Redo, complete-font preservation and save/reopen. Keep the serializer ABI hold and D31 reserved zone/master lane. Native Font Info > Zones remains an alternative; the reviewed final fix4 receipt proves source/offline scope only.
- [ ] Add targeted App auto-layer refusal so kerning imports avoid repeated whole-font scans.
- [ ] Qualify final documentation routes, accessibility and deployment before publication.

- [ ] Verify TypeRig-style stacking for27 independent Tool panels plus shared-App routes using installed artifacts in native FontLab; preserve dock/modal/child-widget policies.

- [ ] Re-review refusal-reporting fixes and pass complete core/TypeRig and per-module80%gates after reviewed source-pin regeneration.

- [ ] Preserve original controls, provenance, unsaved drafts and exact failed owners; qualify real FontLab priority/four-font/history behavior.

- [ ] Check the 130 pyqt-official retirement records recorded as plain `Apache-2.0` (the first-party port's licence) against the upstream BSD headers plus GPL-3.0 collection metadata in NOTICE:158-160, starting with the `schema-1e5d0f7289e1b36e.py` split (part3 `BSD-3-Clause AND GPL-3.0-only`, part2 `Apache-2.0`). Decide whether `license` should name the port or the upstream and make all records agree.
- [ ] Run the App tab literal check for absorbed Scriptmix destinations in CI (`.github/workflows/pin-freshness.yml` skips only that check, because fontlab-fontlabapp is private and no credential is authorized); it runs in the local pre-push gate only for now.
- [ ] After a native Undo the Node Table keeps stale coordinates until Refresh is pressed; refresh it on the host history notification (A2 report 14 section 7, Examples). Blocked in this repository: `Scripts/Contours/Node Table.py` is a proposed consolidation source pinned at 85dda66, so the fix belongs in the App Node Editing Lab "Node table" tab (App follow-up; livetester's r46 patch is the proposal, not live-proven).
- [ ] Standalone Stem Blend and Scale With Stem Compensation still use `COORDINATE_TOLERANCE` 1e-5 and can falsely refuse after Redo (drift 1.5e-5) or reopen (up to 5e-4), per live reports 16 and 17; the App writers were fixed to 1e-3 (App e5b744f, 687b592). They are proposed consolidation sources that must stay byte-identical, so resolve when the Stem Interpolation Lab absorbs them.
- [ ] Port the WP10 Codex labs snapshot (App teaching_* modules plus 20 Examples tests) onto the WP09 routes (`production_path`/`run_profile`); App-level tests must reach 80% per module before landing.
- [ ] Confirm the first scheduled (Monday 05:17 UTC) `Scriptmix pin freshness` run passes on `main`. A manual `workflow_dispatch` run on f6ccc57 (43255331095) already passed; only the scheduled trigger itself is unobserved. Next check: `gh run list -w "Scriptmix pin freshness" --event schedule`.
- [ ] Native check (owner, D46): open the "b" glyph window on an owned copy, with no `FL.fl` setters. Node Table rows must match the native nodes; edit, Undo and Redo must refresh the table; the owned copy must save and reopen exactly. This also decides the Undo-refresh row above.

## Deprioritised test-infrastructure and delivery-paperwork rows

- [ ] Orchestrator: run canonical G-Examples after integration; this local WP09 lane exits 3 for no milestone baseline/upstream merge-base. Prepared full suites pass 2,470 tests with 99 existing skips.
- [ ] Run the exact repository checks on the integrated source, obtain independent review, commit/push the scoped milestone and verify its remote head.
- [ ] After qualified main integration, inventory obsolete branches/files, preserve unique work and remove only proven stale items with recovery evidence.
- [ ] Consolidate the two menu-test processes once their App/Fly loading arrangements can coexist without weakening checks.
- [ ] Complete browser asset provenance, transitive notices and required source availability before site publication.
- [ ] Recheck the complete reviewed package set with clean wheel/sdist installs and all dependent suites before delivery.
- [ ] Independently review the full public-site candidate, verify the current nine-asset English payload and exact primary-source notices, qualify actual main CI/generated output and verify Pages settings/live routes.
- [ ] WP10b/WP10c/WP10port lanes (b803727, dc169b0, f189fe2; f5fe913 GetGo labs UTF-8 manifest + labs.py, 951c6dc require_no_editors fakes, 1e-3 live drift) are unlanded; re-derive the wanted labs port onto main.
