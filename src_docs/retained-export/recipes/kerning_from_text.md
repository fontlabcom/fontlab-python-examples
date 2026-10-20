# Kerning pairs from text

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, now preserved under `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

**Purpose.** Paste a pair list, from a proofing session or another tool, and apply
it to the current master:

```text
# left right value
A V -80
@O_left T -40
```

`@name` is a FontLab kerning class. Values are rounded to whole units (FontLab stores
whole units; halves round away from zero, as FontLab does) and the stored values are
reported. Unreadable lines (including `nan`, infinities and values beyond ±32767, the 16-bit
range of OpenType kerning) are listed, not guessed at, before anything is applied. `glyph_names` limits the run to
pairs that involve those glyphs.

```python
run(text=open("pairs.txt").read())
run(text=pairs, glyph_names=["A"], master="Bold")
```

**FontLab API.** `fontpr.call("set_kerning_pair", ...)`, FontLab's MCP kerning tool
from FontLab's own Python.

**Native check** (`native.py`, owned font): three pairs, read back with
`list_kerning_pairs`, carry the values −80, −76 (from −75.5) and −60; the bad line is
reported.

**Provenance.** The kind of task done by "Import Kerning" and "Add new pair" in the
TypeRig GUI *Kerning* manager (`typerig-lib/Scripts/TypeRig GUI/Manager/Kerning.py`,
MPL-2.0). Written from scratch: only the manager's menu labels were consulted, never
its implementation.

**Licence.** Apache-2.0, as the repository.
