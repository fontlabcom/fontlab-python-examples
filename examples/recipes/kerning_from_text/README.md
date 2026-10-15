---
this_file: examples/recipes/kerning_from_text/README.md
---

# Kerning pairs from text

**Purpose.** Paste a pair list, from a proofing session or another tool, and apply
it to the current master:

```text
# left right value
A V -80
@O_left T -40
```

`@name` is a FontLab kerning class. Values are rounded to whole units (FontLab stores
whole units; halves round away from zero, as FontLab does) and the stored values are
reported. Unreadable lines are listed, not guessed at. `glyph_names` limits the run to
pairs that involve those glyphs.

```python
run(text=open("pairs.txt").read())
run(text=pairs, glyph_names=["A"], master="Bold")
```

**FontLab API.** `fontpr.call("set_kerning_pair", ...)`, FontLab's MCP kerning tool
(undoable), from FontLab's own Python.

**Native check** (`native.py`, owned font): three pairs, read back with
`list_kerning_pairs`, carry the values −80, −76 (from −75.5) and −60; the bad line is
reported.

**Provenance.** Behaviour modelled on the pair import of the TypeRig GUI *Kerning*
manager (`typerig-lib/Scripts/TypeRig GUI/Manager/Kerning.py`, MPL-2.0). Written from
scratch; only tool names were consulted.

**Licence.** Apache-2.0, as the repository.
