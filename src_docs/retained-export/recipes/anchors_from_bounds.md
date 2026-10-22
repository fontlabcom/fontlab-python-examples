# Place top and bottom anchors

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

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

**Provenance.** The kind of task done by the "Add" and "Move" anchor buttons of the
TypeRig GUI *Anchor* panel (`typerig-lib/Scripts/TypeRig GUI/Panel/Anchor.py`,
MPL-2.0). Written from scratch: only the panel's button labels and tooltips were consulted, never its implementation.

**Licence.** Apache-2.0, as the repository.
