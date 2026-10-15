---
this_file: examples/recipes/glyphs_path_report/README.md
---

# Path problem report (a Glyphs script run in FontLab)

**Purpose.** Find outline problems before export: open paths, closed paths with fewer
than three on-curve points, repeated consecutive points and tiny paths (narrower or
lower than 4 units). Read-only. `path_report.py` is an ordinary Glyphs 3/4 script (in
Glyphs it checks the selected glyphs, or all); `recipe.py` runs the same file
unchanged in FontLab through [glyport](https://github.com/fontlabcom/fontlab-glyport).

```python
run()                              # every glyph of the current font
run(glyph_names=["a", "b"])["problems"]
```

**What glyport needs and provides here.** `font.glyphs` iteration, `glyph.layers[master.id]`,
`layer.paths`, `path.closed`, `path.nodes` with `x`, `y` and `type`. Coordinates
FontLab returns as `-0.0` are printed as `0`.

**Native check** (`native.py`, owned font, glyport commit recorded in the evidence):
exactly the three planted problems are reported (a repeated point, a 2 × 2 path, a
two-point path) and nothing in a clean "O"; the outlines are unchanged afterwards.

**Provenance.** Written from scratch for this repository. The behaviour follows the
common "path problem finder" scripts for Glyphs, such as those in the public
mekkablue Glyphs scripts (https://github.com/mekkablue/Glyphs-Scripts, Paths folder);
their code was not read or copied.

**Licence.** Apache-2.0, as the repository.
