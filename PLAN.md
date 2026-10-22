---
this_file: PLAN.md
---

# Current goals

Keep the 100-menu collection useful in FontLab 9, with shared helpers in App
and sixteen runtime menus packaged as Lessons. Use Python 3.11 arm64 for host
code. Keep the separate documentation project on its declared Python 3.12+
runtime. Current source and artifact checks do not close native acceptance.

## Native acceptance

Qualify installed artifacts on owned fonts in a dedicated host session. Cover
all current panels, model/view policies, callbacks, close/reopen, cancellation,
stale snapshots and failure paths. Include pattern rules, calendars, trees,
completers, numeric controls, elastic graphs and spacing worksheets.

Check character-map drawing/copy, file dialogs and desktop activation, image
viewers and native printing separately. Check every writer with Apply, Undo,
Redo and save/reopen. Compare complete font state and modification dates across
successive edits, including unrelated glyphs. For cross-font copies, prove that
the source stays unchanged.

Probe Node Table selection-property side effects. Verify fresh-wrapper reads
and selection restoration. Prove Stem Blend's new layers remain ordinary and
non-auto after history and reopen. Test both stem-compensated writers under
coordinate rounding.

Qualify the thirteen packaged GetGo workflows before reconciling their remaining
catalogue entries. When corrected fixture VFJs are supplied, update manifests
and hashes, then rerun corpus and variable-export checks. Keep earlier receipts
as evidence for their exact source version only.

## Small fixes and shared App work

Add missing selection-restoration coverage and cross-repository destination
hash checks. Reconcile retirement licence fields, make collections count tests
independent of line wrapping and check the image viewers' App floors. Combine
the separate menu-test runs only after their import arrangements are compatible.

Request a public App zone writer before adding scripted zone edits. Native
Font Info > Zones remains the alternative. Add targeted auto-layer refusal to
avoid duplicate whole-font scans in kerning imports. Keep generic UI and host
helpers in App, fontParts/UFO adapters in Fontport and Glyphs.app adapters in
Glyport; menus use App through Fly.

## Delivery and publication

Check the final reviewed sibling package set, destination hashes, clean installs
and dependent suites. Complete browser asset provenance, transitive notices and
source availability. Then qualify site routes, accessibility and deployment.
Owner-managed editable installs and publication remain separate delivery steps.

## Done

The practical menu collection, TypeRig-inspired tools, explicit historical
source dispositions and archive-independent default tests are integrated.
Documentation generation and offline runtime checks are present. See CHANGELOG
for verified changes and historical acceptance limits; see TODO for open work.
