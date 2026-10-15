---
this_file: examples/recipes/layer_backup/README.md
---

# Back up master layers

**Purpose.** Before an experiment (remove overlap, rounding, automatic spacing), keep
a copy of each glyph's current master outline in a non-master layer, `Regular backup`
(then `Regular backup 2`...). The master stays the active layer, and the run is a single
Edit > Undo step.

```python
run()                                  # every glyph of the current font, current master
run(glyph_names=["A", "B"], master="Bold", suffix=" before kerning")
```

**FontLab API.** `flGlyph.findLayer`, `flLayer.clone`, `flGlyph.addLayer`,
`flLayer.setActive`, `flItems.notifyChangesApplied` with the changed layers before
their glyphs (one undo step).

**Native check** (`native.py`, owned font): both glyphs get a backup with the master
outline, the master stays active, a second run picks `Regular backup 2`, and editing
a master node afterwards leaves the backup unchanged.

**Provenance.** Behaviour modelled on the layer-duplication tools of the TypeRig GUI
*Layer* panel (`typerig-lib/Scripts/TypeRig GUI/Panel/Layer.py`, MPL-2.0). Written
from scratch: only the panel and tool names were consulted, no TypeRig code was read
for or copied into this recipe.

**Licence.** Apache-2.0, as the repository.
