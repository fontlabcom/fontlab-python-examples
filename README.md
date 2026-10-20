---
this_file: README.md
---

# FontLab Python examples

`Scripts/` contains 33 practical practical facades in one category level: Forms,
Models, Tools, Widgets and GetGo Fonts. Install their matching reviewed Fly, App
and fontlab-python-lessons packages in FontLab 9 Python 3.11; each script states
its setup and limitations. GetGo mutation lessons require an owned font and a
dedicated no-document session. Do not modify a live installation during setup.

The matching runtime package source is included under [`lessons/`](lessons/README.md).
Run `uv build lessons` from this repository to build it; its sixteen packaged
menus, form resource, 99 licensed GetGo fixtures and provenance are included.
The root `pyproject.toml` remains the separate documentation project.

The canonical source now includes the reviewed issue120 facade and package work. Offline
verification does not establish native FontLab compatibility. Original workflow,
lifecycle, whole-font/history and save/reopen acceptance remain pending where
stated; nothing was accepted merely by removing an archived menu wrapper.

## Preserved sources

The local `rescued/` tree retains all original bodies, resources and attribution.
The frozen `rescue-index.json` retains all 494 historical source identities.
`menu-adaptations.json` maps 17 practical practical replacements, with original
workflow acceptance still pending. The other 477 identities remain migration
backlog. All 494 old runtime dispatchers are outside active `Scripts`; their
exact previous bytes are retained in a private recovery snapshot.

## Documentation and verification

Documentation lives in `src_docs/md/`; `src_docs/current_menus.py` generates the
current menu index and source pages from actual `Scripts` files. The source-only
exporter reads reviewed static catalogue pages without running preserved code.
Run `./build.sh` to build locally, or `--serve` for a preview. Site publication has
separate whole-branch, route, accessibility and deployment gates.

Run `uv run --locked python -m pytest -q tests`. Hash checks read the local
preserved sources without importing or executing them. When testing an isolated
checkout, set `FONTLAB_PRESERVED_ROOT` to the existing matching archive root.

The Lessons tests run separately using the documented Python3.11 candidate
command and environment in [`lessons/README.md`](lessons/README.md). Namespace
checks require `EXAMPLES_LEGACY_API_SOURCE` pointing at the existing reviewed
first-party API checkout; they permit only its API/launcher, never archived
script bodies. Keep both documentation/menu and Lessons suites in acceptance.

Glyph Spacing Worksheet and Glyph Spacing Worksheet - Frameless add the two
reviewed numeric delegate profiles through Fly and App>=0.2.70.dev0 (combined
App0.2.73.dev0 candidate). They show four local factor recipes against all
captured selected-layer advances, without applying metrics. All 432 native
artifact/scenario bindings remain pending. Read
[the worksheet guide](src_docs/md/spacing-worksheets.md).

Glyph Name Pattern Lab authors complete native Qt5 QRegExp rules against captured whole-font glyph names. Editable pattern/input histories, all four syntaxes, case/minimal matching and complete native captures remain. Refresh keeps drafts; no font writer is used. Requires reviewed App0.2.76.dev0 via Fly; native qualification pending.

Both complete elastic-node variants are available as current-font dependency
graphs, retaining separate physics and controls plus fixed-graph oracles. Read
[the graph guide](src_docs/md/elastic-component-graphs.md). Native pending.
