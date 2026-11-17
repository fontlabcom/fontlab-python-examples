---
this_file: WORK.md
---

## Task 6 — menu cleanup and drawing examples (2026-11-17)

Removed obsolete issue/provenance tests and ledgers, their dead tooling and 48
compatibility menu launchers. Kept current functional checks and added a compile
smoke check over Scripts, examples and lessons. Removed the unused docs-export
provider while retaining the standalone site and historical authored guides.
README is 76 lines. Current catalogue source pages cover all 122 menu scripts;
uncommitted source bytes have hashes without fabricated immutable links.

Restored 39 licensed visual demos (29 Apache-2.0, 9 MIT, 1 BSD-3-Clause) and added
22 new Apache-2.0 drawing demos. The complete 313-file restore/skip inventory and
all deletion paths are in task-6-report.md. Shared restored controls use the
packaged Lessons runtime and current App ownership. Independent source review
caught and verified fixes for close-time widget disposal and editor save paths.

Verification: full core suite on CPython 3.11 arm64 passed 218 tests; supplemental
docs source/build-invocation checks passed 16. Drawing checks include real
offscreen rendering, PNG encoding, scene items and widget disposal. Required
uv dependency resolution cannot fetch pytest because DNS is unavailable; the
3.11 run reused installed pytest via sys.path. Exact-lock offline site build is
blocked by uncached babel==2.18.0; system-tool fallback failed the unchanged
vendor asset check. Generated docs/ remains the original committed output.
No native FontLab, installation, publication, commit, push or branch change.

## 2026-11-15 — Shared installer source alignment

Copied the reviewed shared installer exactly: dependency constraints and managed origins remain protected; inactive conditional dependencies are filtered before sibling execution in the resolver target Python. FontLab imports remain standard-library-only. Package identity, runtime APIs, dependency declarations, scripts, bundles and legal files are unchanged. The docs root remains non-package; its existing scripts/curated and nested-package distribution contracts are unchanged.

Focused checks: 1 passed in 0.02s. This qualifies the local source candidate only. Independent review, combined-main/full delivery gates, genuine release/downloads, installed provider closure and admitted FontLab/native workflows remain separate. No owner-folder installation or native operation ran.



# Current round — documentation repair delivery ledger (2026-11-14)

Independent source, controller and final delivery reviews accept the guarded
documentation-test repair at source/main/hook/CI scope. Source X is
`fb4cce48c1df2676c0ea52d6428c586f905d84a6`; generated main Y is
`039c3d06c42bc0fc5c8febaa1118645edaf96ace`, whose sole parent is X, changing only
`docs/sitemap.xml` and its gzip. The qualification log binds exact X to Y.
Documentation run 43540339178 and pin-freshness run 43540339165 succeeded for X.
Existing public Pages workflows succeeded for X and Y; these metadata checks
are separate from browser/live-route acceptance and private-site holds.

The source repair retains WORKTREE versus INDEX, the disabled-refresh guard,
all existing assertions and complete 313-file cross-date hashes. No HEAD-based
comparison was accepted. Full controller manual checks passed 2,017 core cases
with 92 skips, 498 derived with seven skips, 204 Lessons and 58 documentation
cases. Runtime total is 2,719 passes/99 existing skips with exact reviewed IDs
and results. Lessons combined coverage is 95.989%, zero exclusions, unchanged
80% gate. Strict generation reproduced 313 files at its qualified dated epoch.
Target Ruff passes; the same 72 inherited Scripts findings remain, exit 1.
The bounded graph response was LOW; whole-flow omissions remain unresolved.

The first ordinary hook passed core 2,013/96, then failed before derived tests
because App's declared local Pens prerequisite was missing. A genuine Pens
1.0.5 clone at `e80672ff2d51e2fec77f4b73f0c7e01d93b9a37f` supplied it.
The unchanged hook retry passed core 2,013/96 and derived 498/7, tests-only with
zero selected changed production modules; the nonforce push succeeded. Hook
individual IDs were not captured: no mapping of the four extra core skips is
claimed. Actual derived origins were regular App `1.2.16.dev1+ge8b012e38`,
editable Pens 1.0.5 and explicit reviewed Fly source `1505b29`. This dated check
context does not qualify the latest provider cohort or ordinary distribution.

The hook clears Git-local environment variables; manual index-refresh guards
are not assumed to survive it. The successful-push source and Pens raw-index
intervals remain FAILED, writers UNKNOWN; App/Fly/Scriptmix matched. No index was
restored. The author's alternate-index write-tree interval remains NOT
RAW-PRESERVED. The controller retained its incorrect conformance hash label
and independently reviewed report-only correction. Matching 1,084 canonical
tracked identities and 29 first-party reference endpoints are bounded snapshot
results, not transient, untracked or global preservation proof.

This round updates only PLAN, TODO, WORK and cumulative CHANGELOG after the
accepted delivery. The complete prior WORK is archived byte-exact in the private
external task packet, SHA256 `194ff85a416b97a4426291e12c5b04fb11919226c5d04838a6e023f936511aca`.
Fresh checks and independent review of this ledger remain controller gates;
no new release, ordinary installation, root installation or native result follows.

All other TODO rows remain open. Root install.sh remains required and unrun in
this task. All seventeen native rows, full GUI/theme/typing/filter/history and
save/reopen checks, the native fence, provider and graph limits, Issue 123 pause,
private Pages holds, excluded repositories, Book restriction and stopped cleanup
remain unchanged. Continue those authorized tasks through their separate gates.
