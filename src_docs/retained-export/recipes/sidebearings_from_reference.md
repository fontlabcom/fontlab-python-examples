# Copy sidebearings from a reference glyph

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

**Purpose.** Spacing by analogy: give "I" the sidebearings of "H", or "h m" those of
"n". Each target's outline and anchors shift so that its left sidebearing equals the
reference's, and its advance width changes so that the right sidebearing matches
too. Glyphs without outlines are skipped. Run layer_backup first: Edit > Undo does not restore script edits in FontLab 9.0.9783 (see ../README.md).

```python
run(glyph_names=["I"], reference="H")
run(glyph_names=["h", "m"], reference="n", master="Bold")
```

**FontLab API.** `flLayer.boundingBox`, writable `flNode.x`, `flPinPoint.point`,
`flLayer.advanceWidth`. Outlines are moved node by node in each shape's own
coordinates; glyphs built from transformed components need FontLab's own metrics tools.

**Native check** (`native.py`, owned font): "I" (x 200–300 in 700 units) gets "H"'s
60/60 sidebearings: outline at 60–160, width 220, anchor moved by the same −140; "H"
and an empty "space" are unchanged.

**Provenance.** The kind of task done by "Copy Metrics" (LSB/RSB) in the TypeRig GUI
*Metrics* panel (`typerig-lib/Scripts/TypeRig GUI/Panel/Metrics.py`, MPL-2.0). Written from scratch: only the panel's button labels and tooltips were consulted, never its implementation.

**Licence.** Apache-2.0, as the repository.
