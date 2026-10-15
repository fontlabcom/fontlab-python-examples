---
this_file: examples/recipes/round_coordinates/README.md
---

# Round coordinates to grid

**Purpose.** Scaling, interpolation and imports leave fractional coordinates. This
snaps every node (on- and off-curve), anchor and advance width of the current master
to a grid (`grid=1` for whole units, `grid=10` for coarse sketches). Halves round away
from zero. The run is one Edit > Undo step titled "Round Coordinates".

```python
run()                                   # all glyphs, whole units
run(glyph_names=["a", "b"], grid=5, anchors=False, width=False)
```

**FontLab API.** `flLayer.getContours`, `flContour.nodes()`, writable `flNode.x/y`,
`flPinPoint.point`, `flLayer.advanceWidth`, `flItems.notifyChangesApplied`.

**Native check** (`native.py`, owned font): fractional nodes, an anchor and the width
end on the grid; an already-integer glyph is left alone; Edit > Undo offers
"Undo Round Coordinates".

**Provenance.** Behaviour modelled on the node-rounding tools of the TypeRig GUI *Node*
panel (`typerig-lib/Scripts/TypeRig GUI/Panel/Node.py`, MPL-2.0) and FontLab's own
rounding commands. Written from scratch; only tool names were consulted.

**Licence.** Apache-2.0, as the repository.
