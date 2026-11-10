---
this_file: AGENTS.md
---

## Current scope — 2026-11-05

Issue 230 documentation reconciliation is current. Issue 123 remains paused. The qualified Issue 207 isolated candidate is separate from canonical source, installed artifacts, native acceptance and publication. Reconcile that candidate with later work before integration. Issue 210 specifies future architecture; Issue 211 retains unfinished follow-up checks. Retained dated receipts describe their original source and acceptance surface only.

Canonical source inspected for this proposal: `7de2bf9120af`. This is a dated source observation, not an installed or native acceptance claim.

Keep all lesson, original-source and destination-hash contracts while updating examples for reviewed App/provider migrations.

Qualify the installed cohort, actual owned native workflows, whole-font/history, window priority and save/reopen; keep site and runtime acceptance separate.

## Organization and checks

`Scripts/` contains examples; `lessons/` is a separate runtime distribution with candidate tests; `tests/` checks menus/provenance; `src_docs/` and `tests_docs/` own the catalogue website.

Use README Tests and lint for separate arm64 Python 3.11 core/TypeRig-derived checks and offscreen lessons tests. Prepare the separate Python 3.13 hash-locked docs environment following README before `tests_docs`. Use real reviewed App artifact versions, never pretend build metadata.

# FontLab Python examples

Provide useful FontLab menu examples and a separately packaged Lessons runtime.

## Runtime and shared code

- Target embedded Python 3.11 arm64. Request `--python cpython-3.11-macos-aarch64-none`; plain `3.11` can select x86_64.
- Keep `Scripts/<Title Case Category>/*.py` one level deep. Read each Setup line for its App minimum.
- General UI and native FontLab helpers belong in `fontlabapp`. `fontport` is fontParts/UFO only; `glyport` is Glyphs.app compatibility only. Scripts use App through `fly.ap`.
- Teach canonical domain imports, such as `fly.ap.core.scripting` and
  `fly.ap.glyphs.catalog.model`. Fontport editors live in `fly.ap.fontui`.
- `python -B tools/migrate_app_paths.py --check` audits API path migration against
  the sibling App alias table; migration fixtures intentionally retain old inputs.
- The root project is documentation-only and requires Python 3.12+. Runtime packaging is in `lessons/pyproject.toml`.

## Checks

Run from the root. Use reviewed sibling App, Fly and Scriptmix checkouts. Set
`FONTLAB_REFERENCE_ROOT` to the reviewed workspace with Echopy Qt stubs and API
docs. uv needs a writable package cache. Core and TypeRig-derived tests require
separate processes because they use different App/Fly loading arrangements.

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest python -B -m pytest -q -p no:cacheprovider tests --ignore-glob='tests/test_issue122_R*.py'
PYTHONPATH="$PWD/../fontlab-fly/src" uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest --with "$EXAMPLES_APP_WHEEL" python -B -m pytest -q -p no:cacheprovider tests/test_issue122_R*.py
uv run --no-project --python cpython-3.11-macos-aarch64-none --with ruff ruff check --no-cache Scripts
export EXAMPLES_APP_SOURCE="$PWD/../fontlab-fontlabapp/src/fontlabapp"
export EXAMPLES_LEGACY_API_SOURCE="$PWD/../legacy-api-28bc505"
QT_QPA_PLATFORM=offscreen uv run --no-project --python cpython-3.11-macos-aarch64-none --with PySide6-Essentials --with pytest --with pytest-cov --with fonttools python -B -m pytest -p pytest_cov --confcutdir lessons/candidate_tests/models_candidate -q -p no:cacheprovider lessons/candidate_tests/models_candidate --cov=lessons/src/fontlab_python_lessons --cov-branch --cov-fail-under=80
PATH="/opt/homebrew/bin:$PATH" .docs-venv/bin/python -B -m pytest -q -p no:cacheprovider tests_docs
```

Docs pipeline tests use the prepared Python 3.13 `.docs-venv` and exact `src_docs/requirements.txt`; legacy pytest checks additionally require pytest.
Lessons namespace tests need the reviewed read-only legacy API checkout.
Use external `--basetemp` and `COVERAGE_FILE` paths for disposable output.
The lint command covers menu scripts only. Archive-byte audits are opt-in;
see README for their failure rules. Current-file checks must remain mandatory.

## Applicable host limits

- PythonQt widgets and item models are in `PythonQt.QtGui`; there is no QtWidgets. QObject is in `PythonQt.private`. Never load PySide/PyQt or create QApplication in FontLab.
- Keep entrypoints lazy: `run_python` has a five-second deadline. A client timeout does not stop host code; long callbacks need an internal deadline and cancellation.
- Native instances reject new Python attributes; subclass fields must not shadow native methods. Call protected event handlers on the native class explicitly, not through `super()`.
- Bind the sender in the callback; `self.sender()` can be None. Wrap native slots to consume signal arguments. Do not mix native-slot and bound-method receivers on a signal that will be disconnected.
- Disconnect owned callbacks before widget deletion. Keep explicit owners through close, failure and queued callbacks. Always end QPainter in `finally`; escaping paint exceptions can crash the host.
- Never negate a QPoint wrapper; negate its components. `bytes(QByteArray)` fails; use `.data()`. Avoid generic native-property reads: an unloaded QSvgRenderer's `currentFrame` can crash.
- Selection writes need a verified active Font window. Successful selection reads do not prove write safety.
- Use public App writers and history helpers. Undo notifications need affected layers and glyphs in one list. Never notify auto layers; that can rebuild unrelated composites.
- Native getters and UpdateAll can change caches and later modification dates. Check the whole font across repeated operations; never clear global update queues to hide a difference.
- Layer role flags are boolean properties, not methods. Clones can lose notes and raw node flags. Verify saved/reopened node types and topology, not coordinates alone. Pass absolute save paths.

## Native proof and safety

Offline tests, offscreen Qt, imports and wheel builds are not native proof.
Qualify installed artifacts in FontLab on owned fonts and widgets. Record the
host build and actual module paths; canonical editable installs can shadow a
worktree. Prove complete font preservation, Apply/Undo/Redo and save/reopen.
Mutation checks need a dedicated no-document session and a restart afterward.
Never mutate user-open fonts, preferences or Output content.

Work only in the requested worktree. Do not change branches, index, refs or
commits without explicit authorization. Do not edit sibling or canonical
checkouts, private source corpora, live installs or the `fontlab-user-folder`
symlink. The owner manages editable installs into FontLab. Retain historical
path/hash records; do not execute or ship archived bodies. Put disposable files
outside the repository and preserve existing owner work.

## Milestones and delivery

Read [PLAN.md](PLAN.md), [TODO.md](TODO.md) and [WORK.md](WORK.md) before work.
Make the smallest complete MVP for one named acceptance task. Find all callers,
tests, fixtures, exports and documentation first. Use graph impact before source
symbol edits; confirm stale or unknown graph results against current source.
Keep product work in isolated successors and preserve the owner's checkout.

Run this repository's exact checks and the unchanged 80% gate for each complete
changed production module. Use an independent review before a milestone commit.
Under the current owner task, commit and push reviewed, passing milestones;
verify remote heads rather than inferring delivery from local tracking refs.
Before main integration, reconcile concurrent work and all consumers, run graph
change analysis and repeat the required acceptance on the combined source.

Before removing obsolete branches or files, prove integration, retain recoverable
unique work and check fresh owner/worktree attachments. Preserve sealed reports,
licences, archives and private data. Do not rewrite history by implication.
Remove verified completed work from PLAN/TODO and record scoped evidence in
CHANGELOG. Keep implemented-only native/artifact checks open in TODO. Issue 123
remains paused; no instruction here authorizes driving the owner's FontLab,
installing into its user folder or publishing a site.

## Public site qualification

Retain the complete 100-menu catalogue and Lessons guides. Source identity links and hashes must remain exact. Keep authored retained guides outside generated `docs/`. Follow README for the current exact-lock build. Independent source/privacy/legal review, actual main CI, immutable generated-output verification, settings readback and live browser checks remain required. The current 31-package/44-asset inventory is scoped evidence; the complete transitive browser licence review remains open.

## Integration rounds

After each round of important changes, integrate it into `main` and upstream:
fetch `origin/main`, build the change on top of it in an isolated branch or
worktree, and resolve conflicts by keeping both our work and teammates' work.
Never discard upstream commits, and never force-push. Run the repository's
checks on the merged result, then push to `origin main`. Record the change in
CHANGELOG.md, move verified-solved TODO.md items into CHANGELOG.md, update
PLAN.md, and continue with the next TODO.md item until the list is clear.
`install.vfpy` is shared: keep it byte-identical in every installer repository.
