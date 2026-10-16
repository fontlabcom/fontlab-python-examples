# Back up master layers

**Purpose.** Before an experiment (remove overlap, rounding, automatic spacing), keep
a copy of each glyph's current master outline in a non-master layer, `Regular backup`
(then `Regular backup 2`...). The master stays the active layer. Run it before the
other recipes: Edit > Undo does not restore script edits in FontLab 9.0.9783 (see the
[recipes README](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/recipes/README.md)).

```python
run()                                  # every glyph of the current font, current master
run(glyph_names=["A", "B"], master="Bold", suffix=" before kerning")
```

**FontLab API.** `flGlyph.findLayer`, `flLayer.clone`, `flGlyph.addLayer`,
`flLayer.setActive`, `flItems.notifyChangesApplied` with the changed layers before
their glyphs.

**Native check** (`native.py`, owned font): both glyphs get a backup with the master
outline, the master stays active, a second run picks `Regular backup 2`, and editing
a master node afterwards leaves the backup unchanged.

**Provenance.** The kind of task done by the "Duplicate" action of the TypeRig GUI
*Layer* panel (`typerig-lib/Scripts/TypeRig GUI/Panel/Layer.py`, MPL-2.0). Written from scratch: only the panel's button labels and tooltips were consulted, never its implementation.

**Licence.** Apache-2.0, as the repository.
