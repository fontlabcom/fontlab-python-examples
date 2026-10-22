# Tabular figures (a Glyphs script run in FontLab)

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

**Purpose.** Give figures one shared advance width and centre each outline in it.
`tabular_figures.py` is written as an ordinary Glyphs 3 script (in Glyphs it would work
on the selected glyphs; its functions were run inside Glyphs 3.5.1 and 4.2 on an
in-memory test font, including the anchor move). `recipe.py` runs the *same
file, unchanged* in FontLab through
glyport (`fontlab-glyport`), whose `GlyphsApp` module is
backed by the current FontLab font.

```python
run()  # zero..nine that exist, width 600
run(glyph_names=["one", "seven"], width=620)
```

Bounds are the real outline extents (cubic and quadratic extrema), not the handles.
Layers with components are refused before any change. It works on the current master
(FontLab's, or Glyphs' selected master), and an empty glyph list does nothing.

**What glyport needs and provides here.** `font.masters`, `font.glyphs[name]`,
`glyph.layers[master.id]`, `layer.paths`/`path.nodes` with writable `node.x`, and
`layer.width`. Glyport has no `layer.bounds` yet, so the script measures the outline
from its nodes (which works in Glyphs too). Glyport cannot move anchors yet
(`GSAnchor.position` write is unsupported), so in FontLab, figures with anchors raise
glyport's `UnsupportedCapability` instead of being left half-moved.

**Native check** (`native.py`, owned font, glyport commit recorded in the evidence):
"one" (100–200 in 350) and "two" (40–540 in 580) end centred in 600 (shifts 150 and
10), "A" is untouched, and the script's own `print` output comes back.

**Provenance.** Written from scratch for this repository. The behaviour is the common
"tabular figures / centre glyphs in width" task, as in the public mekkablue Glyphs
scripts (https://github.com/mekkablue/Glyphs-Scripts, Metrics folder); their code was
not read or copied.

**Licence.** Apache-2.0, as the repository.
