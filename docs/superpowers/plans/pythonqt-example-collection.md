---
this_file: docs/superpowers/plans/pythonqt-example-collection.md
---
# Complete PythonQt example collection

Authority: user requested all of pyqt/examples and eyllanesc/QtExamples ported
to PythonQt and organized in this repository. Repeated pyqt URL counts once.
This plan implements the complete collection; inventory is only the first task.

## Global Constraints

- Include every source example and resource in both pinned collections; no
  silent omission or selected-subset completion.
- Keep source bytes recoverable and map every port back to its exact original.
- Preserve per-file licenses/attribution; existing Apache license does not
  relicense upstream GPL code or differently licensed resources.
- Never load PyQt, PySide or another Qt runtime into running FontLab.
- Reuse FontLab's existing application/event loop and native PythonQt semantics.
- No user font edits, no user settings changes, no corpus execution in inventory.
- No private paths/prompts/credentials in public catalog/code/documentation.
- Work on issue-101-pythonqt-examples; preserve unrelated work and .DS_Store.
- Every new source/document has a repository-relative this_file record.
- Use rtk proxy commands. Implementers/reviewers do not spawn subagents.

## Task 1: Complete source catalog and port map

Own this repository's tools/, tests/, catalog/, README/PLAN/TODO/WORK/CHANGELOG/
DEPENDENCIES updates only. Do not change this controller-owned plan, private
recovery archives or sibling repositories. You are not alone in the workspace.

Read README.md, WORK.md, PLAN.md, TODO.md, LICENSE and the root private receipts:
verification/issue-101-ecosystem/evidence/examples-upstream-trees.json and
examples-source-recovery.json. Source receipts pin two revisions, 1,569 exact
files total, with 465 Python source files. A case-insensitive filename collision
exists in QtExamples others/matplotlib/Subplot.py and subplot.py; the receipt
maps both logical source names to distinct verified storage paths. Use only
the verified source directories and these mappings. Original archives unchanged.

Build a reproducible stdlib inventory tool plus checked-in portable catalog/index
for every original file. Distinguish source files from executable example roots;
infer entrypoints/categories using actual source/README and record ambiguity.
Extract Python imports/Qt bindings/observable API usage, parse outcomes,
UI/QML/qrc/assets/dependency/license associations and exact original hashes.
Inspect actual source, not only extension counts. Preserve auxiliary Python
modules as well as executable entries; keep complete denominators. Include QML,
WebEngine, multimedia/GStreamer, matplotlib, database/network/platform entries.
Cross-repository duplicates may share a future implementation only with every
original mapping retained. Do not collapse the two matplotlib names by case.

For each candidate example give an organized target port path, original identities,
runtime state unexecuted, port state pending and observable dependency/capability
needs. The tool must take explicit source-root/receipt arguments and output no
private absolute paths. A clean repeated run must yield byte-identical output.
Provide readable categorized index/navigation and clear usage. Do not manufacture
ports or native support evidence in this inventory task. License unknowns stay
visible; verify README terms and actual license files before assigning licenses.
Do not copy unreviewed third-party source/resources into public distribution.

Tests first: complete accounting, deterministic bytes, both case-colliding names,
source/hash mismatch failures, malformed Python classified rather than omitted,
auxiliary/entrypoint distinction, path portability and category/source mappings.
Use minimal stdlib tooling and pytest for tests; no Qt binary dependencies.
Run tests, scoped lint and diff checks. Record exact commands/results/full
denominators, source receipts and remaining port/native gaps in progress docs.
Commit owned files only; no pushes or releases. Report to the named task report
with implementation/coverage/tests/commits/self-review/remaining concerns.

## Task 2: Complete PythonQt ports and resource organization

Port every indexed example, with clear direct PythonQt code and retained original
mapping. Implement shared binding/property/enum/event-loop/ownership adaptation
where needed. Resolve observed native Qt5 capability gaps with measured routes;
do not replace behavior with fake output or mark unavailable entries complete.
Preserve licensed resources and source attribution, simple in-host/external
launches, categorized catalog and exact status for every entry. Derive bounded
implementation batches from the complete Task1 catalog without dropping entries.

## Task 3: Native acceptance and documentation integration

Execute every port with owned data/UI in FontLab. Verify real interaction/render
outputs/callbacks/errors/teardown and exact original source recovery; retain full
denominators and per-example receipts. Review all implementation batches, resolve
findings, incorporate the complete categorized collection in rebuilt ecosystem
documentation and perform final complete-collection acceptance before publication.

## Task 2 execution preparation

The private examples-implementation-batches.json receipt allocates every315
candidate record across28provisional categories and retains all1569file IDs.
Directory-based catalog associations overlap heavily (977cross-category file
associations); inspect actual imports/resources and refine ownership before
assigning a bounded port batch. Keep the69unassociated repository/shared files
in the denominator. Categories are navigation aids, not proven dependencies.

A fresh FontLab export probe records Python3.11.6/Qt5.15.19 and selected native
widget/network/SVG/UI-loading exports. SQL/Multimedia/QML/Quick/WebEngine/Charts/
RemoteObjects namespaces are absent under probed names; QThread and
QAbstractTableModel are absent from QtCore. Measure alternate routes/native
extensions; do not substitute omitted examples or fake behavior. The numbered
Designer example's reviewed original dialog.ui loads through native QUiLoader
into a197x72QDialog with buttonBox. This is prerequisite evidence only, with
cleanup scheduled in the first probe. A follow-up independently verifies native
OK/Cancel signal routing and destruction of all three owned objects, with removed
probe state and live host. The PythonQt port itself remains unimplemented.

First concrete port batches should share an actual source directory or verified
small dependency group, retain fixed original IDs and resources, and include
source mapping/license review plus owned launch/cleanup acceptance. Fix the two
deferred catalog minors in the first batch touching its tools. Review numbered
example source terms separately from screenshot/resource terms: the pinned README
permits MIT or GPLv3 for numbered source1–15 except otherwise indicated; official
demos use GPL and screenshots have separate attribution/noncommercial terms.
All remaining official/additional examples and native API gaps stay required.
