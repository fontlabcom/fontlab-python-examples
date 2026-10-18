---
this_file: lessons/README.md
---

# Learn Qt models and forms with real FontLab data

Three Python3.11 lessons turn list models, table models and Designer forms into
useful current-font panels. They run inside FontLab's existing application.
No new QApplication, event loop or alternate Qt binding is loaded in FontLab.
Install distribution `fontlab-python-lessons`; its Python namespace is
`fontlab_python_lessons`. The historical `fontlab_python_examples` catalogue
launcher keeps its own available/launch/inspect/close API and works alongside it.

| Menu entry | Use |
| --- | --- |
| Models > Glyph Name Filter | Filter actual glyph names by prefix; explicitly select chosen rows. |
| Models > Glyph Metrics Model | Read selected glyph names, advances and left sidebearings in font order. |
| Forms > Glyph Metrics Form | Load a Designer form and compare a hypothetical advance against a real glyph. |

Install the wheel and its `fontlab-fly`/`fontlab-fontlabapp>=0.2.22` dependencies in the
FontLab Python3.11 environment. Find the menu files under the installed Python
prefix's `share/fontlab-python-lessons/Scripts`. Copy its Models and Forms
folders into a configured FontLab Scripts folder. Keep the package installed:
the menu files import it, and the form loads its packaged `.ui` resource.
The source checkout's Scripts folder contains the same three menu files.

The required FontLab packages are currently supplied as reviewed checkout builds
or GitHub release artifacts. A plain install of this wheel from PyPI cannot
resolve the complete set: `fontlab-fly` and `fontlab-echopy` were absent from the
registry in the verified installation run. Fly's latest GitHub release asset was
0.2.0, below this package's minimum; later Git tags alone are not wheel releases.

For a complete installation test outside FontLab, collect these eight reviewed
wheels into one otherwise empty `wheelhouse` directory. The verified collection
uses Lessons1.0.3.dev1+gef544f608, App0.2.23,
Fly0.2.2.dev3+g6cf9dc150, Echopy0.2.3,
pythonqtside0.2.1.dev54+g2777e85cd, TypeRig0.2.1.dev8+gf589189,
Fontport1.0.2 and Glyport1.0.8.dev12+g756df2ac8. Development versions identify
read-only canonical-checkout builds; they are not publication claims. Build a
checkout wheel with `uv build --out-dir /path/to/wheelhouse`; obtain the reviewed
App0.2.23 wheel from its GitHub release. Record every source revision and wheel
hash before installation. Then run:

```sh
uv venv --python cpython-3.11-macos-aarch64-none .venv-install-check
uv pip install --python .venv-install-check/bin/python wheelhouse/*.whl
uv pip check --python .venv-install-check/bin/python
.venv-install-check/bin/python -I -c 'import importlib.resources as r; import fontlab_python_lessons as p; import fly, fontlabapp; assert fly.ap is fontlabapp; assert r.files(p).joinpath("resources/glyph-metrics-form.ui").is_file(); print(p.__version__)'
```

This resolves every declared dependency normally, including public third-party
dependencies. Fly requires all six target packages even though these lessons use
only its App and native Qt aliases. FontLab itself supplies PythonQt; a clean
external environment cannot launch the panels. This verification installs into
the disposable environment only. It does not alter FontLab's live installation.

Open a font before using a lesson. Refresh explicitly adopts the current font,
master and relevant selection/data. No automatic polling or background work runs.
Changed font membership/master or displayed metrics refuse stale actions until
Refresh. Filter and form actions do not silently adopt another font. The metrics
table shows a frozen snapshot and says to Refresh after edits.

Glyph Name Filter uses case-insensitive prefix matching and preserves font order.
Apply Prefix updates only the view. Select Chosen Rows changes only Font window
selection, after every requested name is checked; it never changes font data.
No chosen rows means no selection action. This lesson reads exact Font window
selection and does not invent a current-glyph fallback.

Glyph Metrics Model uses an immutable QAbstractTableModel. Advance and LSB stay
numeric, including zero and negative values. An em dash means a missing layer or
unavailable outline sidebearing. Empty selection yields an empty table.
The table offers no setters, sorting or hidden write behavior.

Glyph Metrics Form starts with the first selected glyph in font order, otherwise
the first glyph. Choose another actual name to inspect its current-master data.
Preview Difference compares a hypothetical width in plain Python values. There
is no Apply button: geometry, metrics, history and preferences remain unchanged.
The form's numeric input supports three decimals within ±1,000,000,000 font units.
Missing current-master layers disable Preview; an empty font invents no rows.

All panels reuse `fly.ap.scripting` native reads, owned signal connections,
registry replacement and Close handling. Snapshot records retain plain immutable
values rather than native glyph wrappers. UI controls and Close/status exist
before font reads; failed reads clear obsolete data and keep Close usable.
Missing/corrupt form resources report an error in a closable dialog.

## Validation

The installed candidate passes all three actual menu workflows and twelve
edge/lifecycle controls in FontLab 9.0.9784 on macOS arm64, with complete font
and history preservation. Final integration/release gates remain open.
Host-free tests use actual offscreen Qt6
widgets behind a PythonQt-shaped facade and App's real lifecycle implementation;
they do not prove native PythonQt/FontLab compatibility. PySide6 is a test-only
dependency, never a production import or FontLab installation requirement.

From this candidate checkout, use the workspace's cached isolated tools:

```sh
QT_QPA_PLATFORM=offscreen PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --offline --no-project --python cpython-3.11-macos-aarch64-none --with PySide6 --with pytest --with pytest-cov python -m pytest -p pytest_cov --confcutdir candidate_tests/models_candidate -q candidate_tests/models_candidate --cov=src/fontlab_python_lessons --cov-branch --cov-fail-under=80
uv build --no-sources
```

The widget tests resolve the sibling fontlab-fontlabapp source checkout to use
its actual dialog lifecycle. Set `EXAMPLES_APP_SOURCE` to its `src/fontlabapp`
directory when testing an extracted distribution outside this workspace.
The coexistence tests also need the unchanged historical checkout; set
`LEGACY_EXAMPLES_SOURCE` to that checkout when testing an extracted sdist. This
does not package or modify the historical launcher.
Only candidate_tests/models_candidate belongs to this new package. Historical root files
remain untouched in this worktree and are explicitly excluded from wheel/sdist.
See provenance/models.json and NOTICE-models.md for original paths/hashes/licence.

Historical tests use the separate root `fontlab_python_examples` launcher.
Keep their process separate from the candidate tests above for scoped checks. The
root README's `pytest -q tests` command remains intact; include its existing
FontTools test dependency to exercise GetGo's pen tests:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest --with fonttools python -m pytest -q tests
```

The 1,886 historical tests and 40 lesson tests pass. All eleven changed
production modules exceed 80% statement, branch and aggregate coverage;
combined coverage is 97.77%. Four independent namespace-order controls and the
actual legacy QLabel panel pass alongside the installed lessons. These results
cover the three lessons; the broader catalogue and eighteen-insight migration
remain open.

The distribution version comes from Git through hatch-vcs. An uninstalled source
import reports `0+uninstalled`; this does not create an installation claim. No
broader catalogue, Scriptmix, GetGo or archive completion follows from these three
lessons. Active Font-window verification in App is required before legacy
selection writers are safe; an open font alone does not establish that context.
App0.2.22 is the minimum reviewed safe release; acceptance uses App0.2.23.
Full dependency resolution was
verified with its actual release wheel and the explicit source-wheel collection
above. The verified clean environment contains 23 compatible packages. The
lesson source documentation lives in `lessons/`, separately from generated
site output in `docs/`, so a site rebuild cannot remove it.

The form validates known control types before retaining the loaded widget.
Missing, malformed or wrong-type resources leave a usable Close button. See
[Qt's loader contract](https://doc.qt.io/archives/qt-5.15/quiloader.html) and
[hatch-vcs configuration](https://github.com/ofek/hatch-vcs).
