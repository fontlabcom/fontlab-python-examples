---
this_file: WORK.md
---

# Current round — guarded documentation comparison (2026-11-14)

The reproducible-docs test now compares a patch against the index, with external
and textconv diffs disabled. Name-only output could falsely flag unchanged file
bytes after a timestamp change when automatic index refresh was disabled. The
original worktree/index comparison boundary and refresh guard are retained.

A real-Git regression covers unchanged bytes with changed timestamps, actual
bytes, deletion, executable mode, and already-staged bytes whose working copy
matches the index after a timestamp change. The scoped old oracle fails its two
stat-only cases; the patched oracle passes all five and preserves each raw index.
The cross-date build retains its complete first/second hashes for all 313 files,
source epoch and generated-commit checks. No assertion or skip is removed.

Final checks on the amended test code:

- Core: 2,017 passed and 92 existing skips (24.12 seconds).
- Separate first-party derived tests: 498 passed and seven existing skips
  (1.81 seconds); Lessons: 204 passed (4.27 seconds), 95.989% combined coverage,
  zero exclusions. All runtime IDs and skip messages match the accepted audit.
- Full documentation pytest: 58 passed, no skips (35.77 seconds), including the
  one added regression. Focused final oracles: two passed (4.606 seconds).
- Changed test Ruff 0.16.7: clean. The full Scripts lint still exits 1 with the
  same 72 diagnostics as the retained baseline; Scripts are unchanged.
- API path audit passes. A genuine-history strict build with the qualified
  release-source epoch reproduces all 313 committed documentation file hashes.

The initial copied-input strict build lacked the Git history required by the
catalogue and failed before building. The successful separate owned clone has
identical Scripts/src_docs inputs; no product code was changed for that setup.
The preliminary HEAD-based proposal exceeded the intended comparison boundary
and was narrowed before these final checks. Its rejected expectations and
receipts are retained separately, not presented as accepted behavior.

No production module, source/destination pin, runtime dependency, installer,
workflow, generated output, source guide or AGENTS instruction changed. No new
production coverage claim is needed. The independent audit's matching reviewed
App/Fly/Scriptmix source tuple and Python environments are used for these checks;
this is not a new ordinary-install or complete-provider admission.

Independent review, controller qualification and current-main/hook/CI delivery
remain pending. Graph context resolves the test exactly, but upstream impact
reports UNKNOWN because test discovery is dynamic; current README, AGENTS and
workflow callers confirm unittest/pytest discovery. Retain whole-flow graph
omissions and the final graph receipts separately from source test results.
Native, installation, provider and publication requirements remain open. Issue123
is paused; exclusions and private Pages holds remain unchanged.

## Prior round record — retained verbatim

# Current round — Issue 255 post-release reconciliation

[fontlab-python-examples v1.2.6](https://github.com/fontlabcom/fontlab-python-examples/releases/tag/v1.2.6) is qualified at `ff5177105afc80eeb2a3e58ebfb03531da5cbbd0`.

Authored native/App/Pens teaching and bounded Lessons successors use Fly; the final source re-audit closes the consumer migration.

Core tests pass 2,013 with 96 inherited skips; derived tests pass 498 with 7 inherited skips; Lessons passes 204 and authored tests 55. All four complete changed-module gates and 57 documentation tests pass, with exact 313-file parity. Main/tag hooks, CI, the public guide and immutable outer example sources are qualified. Genuine Lessons wheel/sdist ordinary installs match all 166 installed files and pass real provider identity and contour geometry checks; actual downloads match reviewed artifacts.

The source, artifact, ordinary external-install, release and download gates above are verified. This round reconciles their progress records after release; it changes no runtime source, installer, dependency declaration, generated documentation or immutable release asset. The three outer examples are published source only and are not included in Lessons wheel/sdist artifacts.

Remaining: After explicit D43 recovery and admission, qualify released Lessons workflows and the three separately published outer examples in FontLab with matched source paths, native lifecycle/history and saved/reopened font evidence.

D43 native acceptance remains held and unproved. Issue 123 remains paused; existing private Pages holds and every unrelated acceptance task remain in PLAN/TODO. Prior WORK bytes are retained exactly in the private external delivery ledger, SHA256 `2388e883100e96a10fc1353e780434372ce8e5b4acff535884fee8638c92ae84`.
