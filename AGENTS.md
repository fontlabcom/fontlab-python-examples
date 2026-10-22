---
this_file: AGENTS.md
---

# FontLab Python examples

Provide useful FontLab menu examples and a separately packaged Lessons runtime.

## Runtime and shared code

- Target embedded Python 3.11 arm64. Request `--python cpython-3.11-macos-aarch64-none`; plain `3.11` can select x86_64.
- Keep `Scripts/<Title Case Category>/*.py` one level deep. Read each Setup line for its App minimum.
- General UI and native FontLab helpers belong in `fontlabapp`. `fontport` is fontParts/UFO only; `glyport` is Glyphs.app compatibility only. Scripts use App through `fly.ap`.
- The root project is documentation-only and requires Python 3.12+. Runtime packaging is in `lessons/pyproject.toml`.

## Checks

Run from the root. Use reviewed sibling App, Fly and Scriptmix checkouts. Set
`FONTLAB_REFERENCE_ROOT` to the reviewed workspace with Echopy Qt stubs and API
docs. uv needs a writable package cache. Core and TypeRig-derived tests require
separate processes because they use different App/Fly loading arrangements.

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest python -B -m pytest -q -p no:cacheprovider tests --ignore-glob='tests/test_issue122_R*.py'
SETUPTOOLS_SCM_PRETEND_VERSION=0.2.150.dev0 PYTHONPATH="$PWD/../fontlab-fly/src" uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest --with ../fontlab-fontlabapp python -B -m pytest -q -p no:cacheprovider tests/test_issue122_R*.py
uv run --no-project --python cpython-3.11-macos-aarch64-none --with ruff ruff check --no-cache Scripts
export EXAMPLES_APP_SOURCE="$PWD/../fontlab-fontlabapp/src/fontlabapp"
export EXAMPLES_LEGACY_API_SOURCE="$PWD/../legacy-api-28bc505"
QT_QPA_PLATFORM=offscreen uv run --no-project --python cpython-3.11-macos-aarch64-none --with PySide6-Essentials --with pytest --with pytest-cov --with fonttools python -B -m pytest -p pytest_cov --confcutdir lessons/candidate_tests/models_candidate -q -p no:cacheprovider lessons/candidate_tests/models_candidate --cov=lessons/src/fontlab_python_lessons --cov-branch --cov-fail-under=80
PATH="/opt/homebrew/bin:$PATH" .venv/bin/python -B -m pytest -q -p no:cacheprovider tests_docs
```

Docs tests need the prepared root 3.12+ `.venv` from `uv sync --locked`.
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
