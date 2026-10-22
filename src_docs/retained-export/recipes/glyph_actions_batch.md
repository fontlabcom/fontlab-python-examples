# Batch Tools > Actions on named glyphs

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

**Purpose.** Run steps from FontLab's Tools > Actions catalogue (Remove Overlap, Add
Extremes, Shift...) on a list of glyphs from a script, using the Pythonic tree of
`fontlab-fontlabapp`:

```python
from fontlabapp import host

dir(host.glyph_actions)  # 72 actions, e.g. remove_overlap
host.glyph_actions.remove_overlap(["X"])  # FontLab's own run_actions
host.actions.search("overlap")  # related menu commands (read-only)
```

`run(glyph_names=["X"], steps=("remove_overlap",))` wraps that and returns FontLab's
own result (contour counts before and after) plus the related menu commands. It
never triggers a menu command. Needs `fontlab-fontlabapp` installed in FontLab.

**Native check** (`native.py`, owned font): two overlapping squares in "X" become one
8-point contour spanning 0–600; "Y", not named, keeps both squares; the search finds
the overlap commands in the menus.

**Provenance.** Written for this repository on fontlabapp's `host.glyph_actions` and
`host.actions` (issue 104). FontLab's Tools > Actions catalogue comes from
`fontpr.list_actions`.

**Licence.** Apache-2.0, as the repository.
