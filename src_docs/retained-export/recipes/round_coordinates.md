# Round coordinates to grid

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, now preserved under `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

**Purpose.** Scaling, interpolation and imports leave fractional coordinates. This
snaps every node (on- and off-curve), anchor and advance width of the current master
to a grid (`grid=1` for whole units, `grid=10` for coarse sketches). Halves round away
from zero. Run layer_backup first: Edit > Undo does not restore script edits in FontLab 9.0.9783 (see ../README.md).

```python
run()  # all glyphs, whole units
run(glyph_names=["a", "b"], grid=5, anchors=False, width=False)
```

**FontLab API.** `flLayer.getContours`, `flContour.nodes()`, writable `flNode.x/y`,
`flPinPoint.point`, `flLayer.advanceWidth`, `flItems.notifyChangesApplied`.

**Native check** (`native.py`, owned font): fractional nodes, an anchor and the width
end on the grid; an already-integer glyph is left alone.

**Provenance.** Written from scratch for this repository. FontLab's own
Contour > Coordinates > Apply Rounding rounds interactively; this recipe scripts the
same idea across many glyphs, with anchors and widths.

**Licence.** Apache-2.0, as the repository.
