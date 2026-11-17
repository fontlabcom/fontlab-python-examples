---
this_file: README.md
---

# FontLab Python examples

Runnable FontLab 9 menu scripts for drawing, font inspection and editing,
PythonQt widgets and modeless tools. Each script explains what it shows and
its requirements. Read its instructions before running: some tools edit fonts.

`Scripts/<Category>/*.py` supplies the Scripts menu. `examples/` contains
standalone teaching examples. `lessons/` is the separately packaged
`fontlab-python-lessons` runtime. The root Python project builds this
repository's documentation site, not the runtime package.

## Install

Open `install.vfpy` in FontLab 9 by double-clicking or dropping it onto FontLab.
The stub uses [fontlab-instamix](https://github.com/fontlabcom/fontlab-python-instamix)
to install the packages and menu scripts; it installs Instamix first if needed.
Restart FontLab after installation.

Use FontLab's embedded Python 3.11 arm64 and supplied PythonQt, with
`fontlab-fly`, `fontlab-fontlabapp` and `fontlab-python-lessons` installed.
Each script's Setup text states any additional requirements. The Lessons
`fonttools` extra is needed for pen and export lessons.

For manual menu installation, copy the desired category folders from `Scripts/`
into a FontLab Scripts location. Keep one category level and one copy of each
menu. The Lessons wheel includes its own menu copies. Never create another
QApplication, start an application event loop, or load PySide/PyQt in FontLab.

Open a font, choose a script in FontLab's Scripts menu, and follow its panel
instructions. Drawing demonstrations that use only sample geometry need no font.
Use Refresh after switching fonts or layers when the panel offers it.

## Menu categories

- **Contours:** nodes, slopes and handles.
- **Designer:** polygon previews and contour construction.
- **Dialogs:** modeless dialog examples.
- **Drawing:** QPainter techniques, paths, outlines and drawing surfaces.
- **Forms:** packaged glyph metrics form.
- **GetGo Fonts:** lessons using bundled licensed font fixtures.
- **Graphics:** graphics scenes, proof previews and visual demonstrations.
- **Labs:** filtering, trees, metrics, calendars, completion, drag and drop,
  proof composition, Unicode and review models.
- **Layouts:** flowing widget arrangements.
- **Models:** packaged glyph list and metrics models.
- **Text:** text documents and proof drafts.
- **Tools:** font inspection, naming, kerning and other font utilities.
- **Widgets:** reusable control demonstrations.
- **Windows:** font snapshot comparisons.

## Development

Compile and test without importing FontLab's native modules:

```sh
uv run --no-project --python cpython-3.11-macos-aarch64-none --with pytest python -m pytest -q tests
./build.sh --offline
```

Some tests require the reviewed App/Fly source checkouts or optional Qt test
bindings. For a non-sibling App checkout, set `EXAMPLES_APP_SOURCE` to its
`src/fontlabapp` directory and add its `src` directory to `PYTHONPATH`.
The docs build uses its separate hash-locked environment; see
[src_docs/requirements.txt](src_docs/requirements.txt). Offline tests and builds
do not verify native FontLab behaviour.

## Licence

First-party examples use [Apache-2.0](LICENSE-APACHE-2.0). Restored examples
retain their individual SPDX and attribution headers; MIT and BSD examples
keep their own terms. See [NOTICE](NOTICE) and [lesson provenance](lessons/provenance/)
for credits. Bundled fonts retain their own licences and licence texts.
