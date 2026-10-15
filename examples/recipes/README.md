---
this_file: examples/recipes/README.md
---

# FontLab 9 recipes

Small scripts for everyday glyph work, each tested in FontLab on a font it creates and
throws away. Run a `recipe.py` from FontLab's Scripting panel or put it in the Scripts
folder; every recipe has a `run(font_id=None, glyph_names=None, ...)` function you can
call from your own scripts, and works on the current font and master by default.

| Recipe | What it does | Built on |
|---|---|---|
| [layer_backup](layer_backup/) | Copy master layers to "Regular backup" layers | FontLab API |
| [round_coordinates](round_coordinates/) | Snap nodes, anchors and widths to a grid | FontLab API |
| [contour_direction](contour_direction/) | PostScript direction, bottom-left start points | FontLab API |
| [anchors_from_bounds](anchors_from_bounds/) | Place "top"/"bottom" anchors from the outline | FontLab API |
| [sidebearings_from_reference](sidebearings_from_reference/) | Copy a reference glyph's sidebearings | FontLab API |
| [kerning_from_text](kerning_from_text/) | Apply "A V -80" pair lists | FontLab kerning tool |
| [glyph_actions_batch](glyph_actions_batch/) | Tools > Actions on named glyphs | fontlab-fontlabapp |
| [glyphs_tabular_figures](glyphs_tabular_figures/) | A Glyphs script, unchanged: centre figures in one width | fontlab-glyport |
| [glyphs_path_report](glyphs_path_report/) | A Glyphs script, unchanged: report path problems | fontlab-glyport |

Each folder has the script, a README (purpose, API, native check, provenance, licence)
and `native.py`, the FontLab check that `_native.py` runs:

```sh
# from the workspace root, in a FontLab session without open documents
verification/issue-104/fl-native.sh --mutating --lane L6b -- uv run --project fontlab-remopy \
  python fontlab-python-examples/examples/recipes/<name>/native.py [EVIDENCE.json]
```

The TypeRig-inspired recipes reimplement behaviour only: TypeRig (MPL-2.0) was
consulted for tool names, and no TypeRig code is included. Host-free tests:
`tests/test_recipes.py`.
