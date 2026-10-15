---
this_file: examples/recipes/anchors_from_bounds/README.md
---

# Place top and bottom anchors

**Purpose.** Prepare base glyphs for mark attachment: "top" goes above the horizontal
centre of the outline bounds (`offset` units above the highest point), "bottom" on
the baseline at the same x. Existing "top"/"bottom" anchors are moved; any other
anchors stay. Glyphs without outlines are skipped.

```python
run(offset=20)
run(glyph_names=["a", "e", "o"], offset=30)
```

**FontLab API.** `flLayer.boundingBox`, `flLayer.anchors`, `flPinPoint(QPointF)` with
`.name`, `flLayer.addAnchor`, writable `flPinPoint.point`.

**Native check** (`native.py`, owned font): "A" gets both anchors, "n" has its
misplaced "top" moved while its "ogonek" stays, and an empty "space" is skipped.

**Provenance.** Behaviour modelled on the anchor tools of the TypeRig GUI *Anchor*
panel (`typerig-lib/Scripts/TypeRig GUI/Panel/Anchor.py`, MPL-2.0). Written from
scratch; only tool names were consulted.

**Licence.** Apache-2.0, as the repository.
