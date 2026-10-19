---
this_file: lessons/README.md
---

# Learn FontLab models, forms and real-font workflows

Sixteen Python3.11 menu entries cover current-font Qt models/forms and thirteen
GetGo font workflows. The package runs inside FontLab's existing application.
It creates no QApplication or second event loop and loads no alternate Qt binding.
The distribution is `fontlab-python-lessons`; import `fontlab_python_lessons`.

## Choose a lesson

| FontLab menu | Result |
| --- | --- |
| Models > Glyph Name Filter | Filter real glyph names by prefix; explicitly select chosen rows. |
| Models > Glyph Metrics Model | Read selected names, advances and left sidebearings in font order. |
| Forms > Glyph Metrics Form | Load a Designer form; compare a hypothetical advance with a real glyph. |
| GetGo Fonts > GetGo - Audit a Real Font | Report fixture metrics, encoding collisions and anchor policy. |
| GetGo Fonts > GetGo - Arabic Text Coverage | Compare a text's Unicode scalars with actual encoding. This does not shape Arabic. |
| GetGo Fonts > GetGo - Outline Pens and Intersections | Inspect contour bounds, areas, points and boundary intersections. |
| GetGo Fonts > GetGo - Name a Disposable Derivative | Rename only the owned fixture copy; retain its license. |
| GetGo Fonts > GetGo - Kerning and Classes Report | Read typed pairs, zero values and native class members. |
| GetGo Fonts > GetGo - Masters Axes and Instances | Report designspace coordinates without changing the active master. |
| GetGo Fonts > GetGo - Compare Master Topology | Compare contour/node types across the fixture's masters. |
| GetGo Fonts > GetGo - Sidebearings from H | Give I the sidebearings of H on the owned copy. |
| GetGo Fonts > GetGo - Widen Two Glyphs | Scale A/V nodes, anchors and advances on the owned copy. |
| GetGo Fonts > GetGo - Export a TTF Geometry Subset | Write and reopen a new TrueType geometry subset. |
| GetGo Fonts > GetGo - Export an OTF Geometry Subset | Write and reopen a new CFF geometry subset. |
| GetGo Fonts > GetGo - Font Info Mini Tool | Show a detached information snapshot after closing its fixture. |
| GetGo Fonts > GetGo - Compare Two Real Fonts | Compare names and widths using each font's own UPM. |

The three model/form lessons use the current font. GetGo lessons use packaged
fixtures, not the current font. All99licensed fonts, the source manifest and
license texts ship beside the GetGo modules. No rescued directory is needed.

## Install the matched candidate packages

The current candidate requires `fontlab-fontlabapp>=0.2.26.dev0` and
`fontlab-fly>=0.2.1`. Older App0.2.22/0.2.23 releases lack the reports API needed
by GetGo. App0.2.26.dev0 and Lessons1.0.4.dev0 are unpublished development
candidates. Review and native acceptance must precede release or normal use.

Use a matched, reviewed wheel collection. Some FontLab packages are supplied as
checkout builds or GitHub artifacts; do not assume a plain PyPI install resolves
all dependencies. The verified candidate collection includes App, Lessons, Fly,
Echopy, pythonqtside, TypeRig, Fontport and Glyport. Record source revisions and
wheel hashes. Install FontTools for pen/export lessons:

```sh
uv venv --python cpython-3.11-macos-aarch64-none .venv-install-check
uv pip install --python .venv-install-check/bin/python --prerelease=allow wheelhouse/*.whl fonttools
uv pip check --python .venv-install-check/bin/python
.venv-install-check/bin/python -I -c 'import fly, fontlabapp; assert fly.ap is fontlabapp; from fly.ap.reports import show_report; from fontlab_python_lessons.getgo import launch'
```

These commands create a disposable external install check. They do not install
into FontLab or launch native panels. Use Python3.11 and the host architecture
for FontLab installations. FontLab supplies PythonQt itself; PySide6/PyQt are
not runtime requirements and must not be installed as alternate host bindings.

After installing reviewed packages in FontLab's Python environment, find the
menu files under that interpreter prefix's `share/fontlab-python-lessons/Scripts`.
Copy **Models**, **Forms** and **GetGo Fonts** into a configured FontLab Scripts
folder. Keep the package installed: menus import it and the form loads a packaged
`.ui` file. The checkout's `Scripts/` contains the same sixteen entrypoints.

## Current-font panels

Open a font, then run a Models or Forms entry. Refresh explicitly captures the
current font, master and relevant selection/data. No polling or background work
runs. Changed font membership/master or displayed metrics refuse stale actions
until Refresh. A failed read clears old data and leaves Close usable.

Glyph Name Filter uses case-insensitive prefixes and keeps font order. Apply
Prefix changes only the view. Select Chosen Rows changes only Font-window
selection after checking every requested name. Empty chosen rows do nothing.
There is no current-glyph fallback; legacy selection writers need an active
Font window, not merely an open font.

Glyph Metrics Model uses an immutable QAbstractTableModel. Advance and LSB stay
numeric, including zero and negative values. An em dash means a missing layer
or unavailable outline sidebearing. Empty selection yields an empty table.
The panel has no setters, sorting or hidden writes.

Glyph Metrics Form starts with the first selected glyph in font order, otherwise
the first glyph. Choose another actual name to inspect current-master data.
Preview Difference compares a hypothetical width in plain Python values. There
is no Apply button. Geometry, metrics, history and preferences remain unchanged.
The input supports three decimals within ±1,000,000,000 units. A missing layer
disables Preview; an empty font invents no rows.

All panels use `fly.ap.scripting` native reads, signal ownership, replacement and
Close handling. Snapshot records keep detached values, not native glyph wrappers.
A missing, corrupt or wrong-type form resource produces a closable error.

## GetGo workflows

Choose a GetGo Fonts entry. Twelve entries show detached read-only nonmodal JSON
snapshots through App. Repeating an entry replaces its owned window. Font Info
Mini Tool retains an InfoTool with `report`, `widget` and `close()`; its App
window uses the same read-only report UI. The active font and Output panel are
not report destinations.

Each entry opens a hash-verified fixture as an absolute temporary copy and closes
only that exact package, including operation/partial-open failures. Naming,
sidebearing and transform lessons require a dedicated session with no other
FontLab documents and discard their edits. A failed close retains the temporary
directory and raises. Export lessons retain new output files, omit native hints,
features and kerning, and verify reopened geometry/cmap/advances/license data.

See [the complete GetGo guide](src/fontlab_python_lessons/getgo/README.md) for
all original calls/defaults, fixture licenses, expected values and limitations.
To obtain an original dictionary, call an entry module's `run(**kwargs)`.
`getgo.launch(name, **kwargs)` instead runs the entry and returns its report
window (or the retained InfoTool for `font_info_ui`). Keep and close returned UI.

## Verification and provenance

The [v1.0.3 release](https://github.com/fontlabcom/fontlab-python-examples/releases/tag/v1.0.3)
contains the original three model/form lessons. Its historical FontLab9784
acceptance does not establish acceptance of this expanded package. All thirteen
packaged GetGo runtime rows remain **pending native acceptance**. Historical9783
GetGo receipts describe the earlier source only.

Current tests cover original algorithms/defaults, fake owned-font operations,
real FontTools binary write/reopen, all menu routes, fixture hashes and offscreen
Qt lifecycle failures. Normal independent wheel/sdist installs establish package
closure and installed behavior; they do not prove native FontLab results.

Build with `uv build lessons` from the repository root. The version comes from
hatch-vcs; a source import without distribution metadata reports `0+uninstalled`.
From `lessons/`, run the candidate tests with reviewed App sources:

```sh
QT_QPA_PLATFORM=offscreen PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --python cpython-3.11-macos-aarch64-none --with PySide6-Essentials --with pytest --with pytest-cov --with fonttools python -m pytest -p pytest_cov --confcutdir candidate_tests/models_candidate -q candidate_tests/models_candidate --cov=src/fontlab_python_lessons --cov-branch --cov-fail-under=80
```

Set `EXAMPLES_APP_SOURCE` to the reviewed `fontlabapp` package directory. Historical
root catalogue tests run separately. Source/license hashes are in
`provenance/models.json`, `provenance/getgo.json` and the packaged fixture manifest.
Code is Apache-2.0; fixture fonts retain Apache-2.0, CC0-1.0 and OFL-1.1 notices.
