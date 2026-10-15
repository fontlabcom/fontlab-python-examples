---
this_file: examples/recipes/contour_direction/README.md
---

# Correct contour direction and start points

**Purpose.** Give every closed contour of the current master PostScript direction:
outer contours counter-clockwise, counters clockwise (y-up). Nesting decides which
is which, so a counter inside a counter turns outward again. Each contour then
starts at its lowest, then leftmost on-curve node, which keeps start points
compatible across masters.

```python
run()                          # all glyphs
run(glyph_names=["O", "Q"])
```

**FontLab API.** `flContour.reverse()` (keeps the first node, reverses the rest),
`flContour.setStartPoint(index)`, `flNode.isOn()`. Orientation is computed from the
node positions with the shoelace formula: in this FontLab 9 build `flContour.clockwise`
reported `False` for a contour that runs clockwise in y-up coordinates, so the recipe
doesn't rely on it.

**Native check** (`native.py`, owned font): an "O" drawn with both contours wrong
ends with a counter-clockwise outer contour and a clockwise counter, both starting
bottom-left, with the same points; a correct glyph is left alone.

**Provenance.** The kind of task done by the clockwise/counter-clockwise and
start-point (bottom-left) buttons of the TypeRig GUI *Contour* panel
(`typerig-lib/Scripts/TypeRig GUI/Panel/Contour.py`, MPL-2.0). Written from scratch: only the panel's button labels and tooltips were consulted, never its implementation.

**Licence.** Apache-2.0, as the repository.
