---
this_file: src_docs/md/current/contours/node-table.md
tags: ["Contours"]
categories: ["Contours"]
---

# Node Table

What: Inspect all own nodes of the current glyph layer and edit X and Y.
How: Read node order, coordinates, types and canvas selection. Stage numeric
cells in a non-modal table. Apply writes accepted edits through App's outline
writer and history.commit. An Apply that changes coordinates is recorded as
one Undo step.
Why: A complete node table exposes unselected points and keeps refused rows.
Usage: Open a glyph. Refresh reads its active layer and discards local cell
edits. Table selection selects canvas nodes; Read Canvas Selection reads the
other direction without discarding cell edits. Edit X/Y, then press Apply.
Refresh caches auto-layer facts; Apply scans them again. Selection reads only
the current layer and synchronizes own nodes even when coordinate edits are
refused. Selection flags are verified; unsynced rows are named in the status.
Benefit: Inspect and edit exact node coordinates without changing node order.
Coordinates use each shape's local space. Translated shapes remain editable;
components, shared outlines, transformed or locked shapes, locked layers,
auto layers and bases of auto composites stay as named kept rows.
Invalid numeric cells and nodes changed since Refresh are kept independently.
Node types are read-only. Distance and angle columns are outside this table.
Window > Panels > Node edits selected canvas points; this table lists every
own node and synchronizes its row selection with the canvas.

Independent behaviour-only rewrite of the node-table idea from Outline.py.
Credit: Vassil Kateliev and Karandash Type Foundry; kateliev/TypeRig, MPL-2.0.
No TypeRig code, comments, icons or resources are included.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Run **Contours > Node Table** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `1fd13c79c47ae52347782f4f3afb8203378d9cf4220fd479453382b9c0c39b28`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Contours/Node%20Table.py)
