---
this_file: DEPENDENCIES.md
---

# Dependencies

The 2026-11-01 priority-message candidate requires App
`qt_dialogs.run_standard_message_box`. App .152 does not contain this helper.
The matching private candidate is `0.2.26.dev153+g44a0d90da`; no package-index
release or native installation acceptance is claimed. No additional runtime dependency is added.

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

## Current documentation dependencies

Python 3.13 runs the exact 31-package hash lock in `src_docs/requirements.txt`: ProperDocs 1.6.7, MkDocs 1.6.1, MaterialX 10.1.8 and Pymdown Extensions 11.0.1. Search uses MkDocs' bundled plugin. No API renderer or source-body inclusion plugin is used. The shared fltheme26/1.0.0 menu/footer is light. Installed licence bytes and 44 generated asset identities are recorded in `src_docs/md/assets/current-docs-inventory.json`; its transitive review remains incomplete. Runtime dependencies and package metadata are unchanged.

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
