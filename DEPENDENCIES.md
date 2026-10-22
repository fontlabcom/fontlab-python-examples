---
this_file: DEPENDENCIES.md
---

# Dependencies

## FontLab menus

| Package or runtime | Version floor | Purpose |
| --- | --- | --- |
| FontLab | 9, embedded Python 3.11 arm64 | Runs the menu scripts. |
| PythonQt | Supplied with FontLab | Uses the host widgets and existing application instance. |
| fontlab-fly | 0.2.1 | Exposes shared App helpers through `fly.ap`. |
| fontlab-fontlabapp | 0.2.26.dev0 for Lessons; each menu's Setup line can require more | Supplies font access, UI ownership, models and edit helpers. |
| fontlab-python-lessons | No numeric floor declared by the menus | Supplies the sixteen packaged Models, Forms and GetGo entrypoints, form and font fixtures. |
| fonttools | 4.59, optional Lessons extra | Supplies pen and binary-font export operations. |

Install these packages in FontLab's embedded Python environment. Use the
`fonttools` extra on `fontlab-python-lessons` for pen and export lessons.
TypeRig is not a runtime dependency of the rewritten tools. Fontport is for
fontParts/UFO compatibility; Glyport is for Glyphs.app compatibility.

## Documentation

The root project requires Python 3.12 or later. `uv sync --locked` installs the
following documentation packages at the versions recorded in `uv.lock`.

| Package | Version requirement | Purpose |
| --- | --- | --- |
| properdocs | ==1.6.7 | Static site builder. |
| mkdocs-materialx | ==10.1.5 | Site theme. |
| mkdocstrings | ==1.0.7 | API documentation rendering. |
| mkdocstrings-python | ==2.0.9 | Python API inspection. |
| mkdocs-autorefs | ==1.4.4 | Cross-page API links. |
| griffe | ==2.3.2 | Python source analysis. |
| pymdown-extensions | >=10.2 | Markdown extensions. |
| mkdocs-codeinclude-plugin | ==0.3.1 | Literal source inclusion. |
| mkdocs-awesome-nav | ==3.3.0 | Navigation generation. |
| mkdocs-live-edit-plugin | ==0.4.1 | Source edit links. |
| mkdocs-categories-plugin | ==0.6.0 | Category pages. |
| mkdocs-print-site-plugin | ==2.9 | Printable site output. |
| mkdocs-include-markdown-plugin | ==7.3.0 | Markdown file inclusion. |

## Development and tests

| Package | Version floor | Purpose |
| --- | --- | --- |
| pytest | 8 in the root project | Runs runtime and documentation tests in separate processes. |
| playwright | 1.55 | Checks browser interactions in documentation tests. |
| pytest-cov | Not pinned | Measures optional Lessons test coverage. |
| ruff | Not pinned | Checks menu-script style. |
| PySide6-Essentials | Not pinned | Provides Qt for separate offscreen Lessons tests. |
| hatchling | 1.27 | Builds the Lessons distribution. |
| hatch-vcs | 0.4 | Derives the Lessons package version. |

Run development tools outside FontLab. Do not load PySide or PyQt in FontLab or
create a second QApplication. Test source prerequisites and commands are listed
in [README.md](README.md). The inventory tools otherwise use Python's standard
library for parsing, hashes, JSON, XML and file paths.
