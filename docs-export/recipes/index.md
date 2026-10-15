# FontLab 9 recipes

Small scripts for everyday glyph work, each tested in FontLab on a font it creates and
throws away. Run a `recipe.py` from FontLab's Scripting panel or put it in the Scripts
folder; every recipe has a `run(font_id=None, glyph_names=None, ...)` function you can
call from your own scripts, and works on the current font and master by default.

| Recipe | What it does | Built on |
|---|---|---|
| [layer_backup](layer_backup.md) | Copy master layers to "Regular backup" layers | FontLab API |
| [round_coordinates](round_coordinates.md) | Snap nodes, anchors and widths to a grid | FontLab API |
| [contour_direction](contour_direction.md) | PostScript direction, bottom-left start points | FontLab API |
| [anchors_from_bounds](anchors_from_bounds.md) | Place "top"/"bottom" anchors from the outline | FontLab API |
| [sidebearings_from_reference](sidebearings_from_reference.md) | Copy a reference glyph's sidebearings | FontLab API |
| [kerning_from_text](kerning_from_text.md) | Apply "A V -80" pair lists | FontLab kerning tool |
| [glyph_actions_batch](glyph_actions_batch.md) | Tools > Actions on named glyphs | fontlab-fontlabapp |
| [glyphs_tabular_figures](glyphs_tabular_figures.md) | A Glyphs script, unchanged: centre figures in one width | fontlab-glyport |
| [glyphs_path_report](glyphs_path_report.md) | A Glyphs script, unchanged: report path problems | fontlab-glyport |

Each folder has the script, a README (purpose, API, native check, provenance, licence)
and `native.py`, the FontLab check that `_native.py` runs:

```sh
# from the workspace root, in a FontLab session without open documents
verification/issue-104/fl-native.sh --mutating --lane L6b -- uv run --project fontlab-remopy \
  python fontlab-python-examples/examples/recipes/<name>/native.py [EVIDENCE.json]
```

**Undo.** In FontLab 9.0.9783, Edit > Undo after these script edits names the recipe
but does not restore the outline (measured: `undo_probe.py` in the workspace evidence
`examples-recipes/`). Run `layer_backup` before experimenting.

**Menu use.** Recipes that change only what you name (`round_coordinates`,
`contour_direction`, `anchors_from_bounds`, `sidebearings_from_reference`,
`kerning_from_text`, `glyph_actions_batch`, `glyphs_tabular_figures`) do nothing from the Scripts menu until you fill in the
constant at the end of the file (`GLYPHS`, `PAIRS`...). The menu route was also run
natively: each file, with its constants filled in a temporary copy, executed as a
script (`__name__ == "__main__"`) on an owned font; all nine passed the same checks
(workspace evidence `examples-recipes/menu-*.json`).

The TypeRig-inspired recipes reimplement behaviour only: for TypeRig (MPL-2.0) only
panel button labels and tooltips were consulted, and no TypeRig code is included.
Host-free tests: `tests/test_recipes.py`.
