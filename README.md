---
this_file: README.md
---

# FontLab Python examples

One hundred menu scripts show useful Python and PythonQt workflows in FontLab 9.
They inspect fonts, build proofs, edit selected data and show modeless panels.
Each script states its setup, scope and limits. Some scripts change fonts;
read the script's Usage and Setup text before running it.

The menu tree has one category level. The runtime code for the sixteen original
Models, Forms and GetGo menus is a separate package, `fontlab-python-lessons`,
under [lessons/](lessons/README.md). Other menus use shared App helpers through
Fly. The root Python project builds documentation; it is not the runtime package.

## Requirements and installation

Use FontLab 9 with its embedded **Python 3.11 arm64** and supplied PythonQt.
Install `fontlab-fly`, `fontlab-fontlabapp` and `fontlab-python-lessons` in
FontLab's embedded Python environment. Each menu's Setup line states its App
minimum; the Lessons package minimum does not cover every menu. Install the
Lessons `fonttools` extra for pen and export lessons. TypeRig is not required
for the rewritten TypeRig tools. See [DEPENDENCIES.md](DEPENDENCIES.md) for
package versions and documentation dependencies.

Put the required category folders from `Scripts/` in a FontLab Scripts location. Keep the category names
and one-level layout. The Lessons wheel also supplies its sixteen entrypoints
under `share/fontlab-python-lessons/Scripts`; use one copy of each menu.
FontLab loads the package code when a menu runs. Never add a QApplication,
start a second application event loop or install an alternate Qt binding in
FontLab. PySide6 is used only for separate, offscreen tests.

## Use the tools

Open an owned copy of a font. Run a menu from a category below. Where a panel
has Refresh, use it after changing the font, master or selection. A stale
snapshot can refuse Apply. Close the panel when finished.

- **Models > Glyph Name Filter:** enter a prefix, inspect the filtered names,
  then use Select Chosen Rows. Selection changes require an active Font window.
- **Dialogs > Glyph Batch Recipe Settings:** copy a recipe, then paste its JSON
  into Glyph Proof Batch Wizard to produce proof text. Invalid or stale recipes
  are refused.
- **Tools > Kerning Copy Rules:** `A|V A|W = T|o @ -5` builds two pairs from the
  current-master T/o value minus five units. Copy the result into Import Kerning
  Pair List, inspect the preview, then Apply. The edit is recorded as one Undo step.
- **Contours > Node Table:** inspect the current layer's own nodes and edit X/Y.
  The coordinate edit is recorded as one Undo step. Stem Blend and Scale With Stem
  Compensation instead create named layers; inspect those layers before saving.
- **GetGo Fonts > GetGo - Audit a Real Font:** inspect a detached report from a
  packaged, hash-checked fixture. GetGo lessons use temporary copies, not the
  current font. Mutation lessons require a dedicated session with no other
  documents. Export lessons retain new geometry subsets; they omit native hints,
  features and kerning. See the [GetGo guide](lessons/src/fontlab_python_lessons/getgo/README.md).

An offline test pass does not prove native FontLab behavior. Current rewritten
menus still need installed-host checks for callbacks, lifecycle, complete font
state, Undo/Redo and save/reopen. Earlier GetGo source receipts do not accept the
expanded packaged workflows.

## Menu map

| Category | Main workflows |
| --- | --- |
| Contours | Node Table; Node Slope And Handles. |
| Designer | Em Star Polygon preview and one-step contour creation. |
| Dialogs | Scaffold, glyph search, coverage, inventory and proof recipes. |
| Drag And Drop | File shelf, glyph names, proof words and pair boards. The shelf opens staged fonts. |
| Drawing | Outline SVG, SVG reference, Stem Blend and stem-compensated scaling. |
| Forms | Packaged Designer form for hypothetical glyph metrics. |
| GetGo Fonts | Thirteen reports and edits on licensed real-font fixtures. |
| Graphics | Proof layouts, variant graph, review cards, proof pad and mark-colour board. |
| Models | Filters, calendars, trees, encoding, metrics, notes, marks, XML and review queues. |
| Text | Calendar proofs, handoff letters, feature drafts, notes and snippet drafts. |
| Tools | File search, naming, snapshots, kerning recipes, Unicode maps and cross-font layer copies. |
| Widgets | Unit calculator, proof groups, icon browser, palette roles and SVG sketch pad. |
| Windows | Unicode issues dock and glyph snapshot differences. |

For per-menu source and limits, see the [current menu catalogue](src_docs/md/current/index.md).
Detailed guides cover [spacing worksheets](src_docs/md/spacing-worksheets.md),
[elastic graphs](src_docs/md/elastic-component-graphs.md),
[slider previews](src_docs/md/slider-spacing-offsets.md) and
[character maps](src_docs/md/glyph-character-map.md).

## Source map

| Path | Contents |
| --- | --- |
| `Scripts/<Category>/*.py` | Current menu entrypoints and script-specific logic. |
| `lessons/src/fontlab_python_lessons/` | Lazy entrypoints, detached records, Qt models, panels and forms. |
| `lessons/src/fontlab_python_lessons/getgo/` | Real-font algorithms, reports, binary exports and 99 licensed fixtures. |
| `lessons/provenance/` | Lesson source and licence records. |
| `tests/` | Menu, algorithm, lifecycle, provenance and catalogue checks. |
| `lessons/candidate_tests/models_candidate/` | Independent runtime-package tests. |
| `tests_docs/` | Documentation build, literal-source and notice distribution checks. |
| `src_docs/md/` | Authored site pages and current menu pages. |
| `src_docs/current_menus.py` | Menu index and source-page generator. |
| `src_docs/build.py` | Static retained-catalogue export and strict site build. |
| `docs/` | Retained authored guides. Generated site output goes to `.build/site/`. |
| `rescue-index.json`, `menu-adaptations.json`, `NOTICE` | Historical paths, hashes, dispositions and credits. |

Put general UI and native FontLab helpers in `fontlabapp`. Keep `fontport` for
fontParts/UFO compatibility and `glyport` for Glyphs.app compatibility. Scripts
access App through `fly.ap`; do not copy shared UI code into each menu.

## Tests and lint

Run from this repository root. Prerequisites: uv; an available CPython 3.11
arm64 interpreter; reviewed sibling checkouts `../fontlab-fontlabapp`,
`../fontlab-fly` and `../fontlab-python-scriptmix`. uv needs a writable cache
and access to the required packages, or a populated cache for offline use.
Set `FONTLAB_REFERENCE_ROOT` to the reviewed workspace containing the Echopy Qt
stub and API documentation repositories. This is independent of the archive root.

Core tests use App source from the sibling checkout. Run them separately from
the TypeRig-derived tool tests, which need an installed App and real Fly:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest python -B -m pytest -q -p no:cacheprovider tests --ignore-glob='tests/test_issue122_R*.py'
SETUPTOOLS_SCM_PRETEND_VERSION=0.2.150.dev0 PYTHONPATH="$PWD/../fontlab-fly/src" uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest --with ../fontlab-fontlabapp python -B -m pytest -q -p no:cacheprovider tests/test_issue122_R*.py
uv run --no-project --python cpython-3.11-macos-aarch64-none --with ruff ruff check --no-cache Scripts
```

The version override supplies build metadata for the isolated App test install;
it does not select an App release. The script lint command checks `Scripts/`
only. It is not a lint result for the whole repository.

Lessons tests also need the reviewed first-party legacy API checkout at
`../legacy-api-28bc505`. Namespace checks read only its API and launcher; they
must never execute archived script bodies. Run separately with offscreen Qt:

```sh
export EXAMPLES_APP_SOURCE="$PWD/../fontlab-fontlabapp/src/fontlabapp"
export EXAMPLES_LEGACY_API_SOURCE="$PWD/../legacy-api-28bc505"
QT_QPA_PLATFORM=offscreen uv run --no-project --python cpython-3.11-macos-aarch64-none --with PySide6-Essentials --with pytest --with pytest-cov --with fonttools python -B -m pytest -p pytest_cov --confcutdir lessons/candidate_tests/models_candidate -q -p no:cacheprovider lessons/candidate_tests/models_candidate --cov=lessons/src/fontlab_python_lessons --cov-branch --cov-fail-under=80
```

Set pytest's `--basetemp` and `COVERAGE_FILE` to an owned external scratch
location when keeping test output outside the checkout.

Provenance tests use recorded historical paths and SHA256 values by default.
For optional source-byte audits, set `FONTLAB_AUDIT_ARCHIVED_SOURCES=1` and set
`FONTLAB_PRESERVED_ROOT` to an extracted archive root containing `rescued/`.
Only an absent archive root skips. When `rescued/` exists, missing or mismatched
files fail. The full-archive audit collects all missing, unreadable and
mismatched files before failing. Retired thread and SQL sources are also parsed
in this opt-in mode. No archived source is executed.

## Documentation build

The root `pyproject.toml` requires **Python 3.12 or later** for the documentation
project. This is separate from the Python 3.11 FontLab runtime. Prepare the root
`.venv` with `uv sync --locked` before running docs tests. The locked project
includes pytest and the required documentation plugins. Put Homebrew Git on PATH
for the notice distribution tests; the system Git may fail through Xcode.
Those tests create isolated fixture repositories and preserve the caller's Git
state.

```sh
PATH="/opt/homebrew/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider tests_docs
./build.sh
./build.sh --offline
./build.sh --serve
```

Docs tests use the prepared 3.12+ `.venv`; the 3.11 selector above is for runtime
checks. The build verifies static source hashes and generates menu pages without
running archived code. Site publication still needs route, accessibility,
licence and deployment checks. Build the separate runtime distribution with
`uv build lessons`; it includes sixteen menus, the form, fixtures and provenance.

## Historical sources and licence

The 494 historical menu identities remain in `rescue-index.json`.
`menu-adaptations.json` records 222 adaptations and 259 retirements. For 10 of them,
the retirement reason names the native FontLab command that does the job.
The remaining thirteen are packaged GetGo workflows.
Another 42 rescued TypeRig files never had a menu identity. Their records have
no `source_menu` key: 9 adaptations and 33
retirements, 4 of which name a native FontLab command.
These records describe source ancestry and workflow disposition.

`rescued/...` paths identify an external archive, not files shipped here:
`fontlab-python-examples-rescued.tar.gz`, SHA256
`f49848d39bdac1a6a973864500afe56af635871e5001ae94ee36cd95370a8266`.
Previous dispatcher bytes also have a private recovery snapshot. Keep historical
paths and hashes; do not restore archived launchers into the active menu tree.

First-party code uses [Apache-2.0](LICENSE-APACHE-2.0). Read [NOTICE](NOTICE) and
[lesson provenance](lessons/provenance/) for credits and independent rewrites.
GetGo fonts retain their own Apache-2.0, CC0-1.0 or OFL-1.1 licences and bundled
licence texts. Browser asset notices and the remaining transitive review are
listed on the [frontend notices page](src_docs/md/frontend-notices.md).
