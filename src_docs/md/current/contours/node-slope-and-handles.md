---
this_file: src_docs/md/current/contours/node-slope-and-handles.md
tags: ["Contours"]
categories: ["Contours"]
---

# Node Slope And Handles

Set selected node slopes and cubic handle lengths in a non-modal panel.

What: Copy a slope, use each master's italic angle, flip the slope or pivot at the
top or bottom selected node. Set cubic handle proportions or Hobby tensions.
How: Slope is dx/dy; selected nodes keep y. Each moved on-curve node carries
its adjacent unselected handles by the same offset, including at a closed
contour's wrap. Selected handles use their own slope targets.
Curve modes require both segment endpoints selected. Handle rays stay fixed;
Proportions measures length against the endpoint chord. Hobby uses the two
endpoint tangent angles and independent positive tensions. Copy Proportions
reads exactly one selected cubic. Closing cubics are included; open ends stay.
Why: Contour > Align Points and Contour > Handles > Harmonize serve direct edits. This
panel adds explicit reusable numbers, two handle tensions and a batch preview.
Use: Select nodes, run the tool, choose the mode and inspect the table. Reload
selection after changing glyphs. Each Apply is recorded as one Undo step.
Benefit: Repeat the same numeric rule across selected glyphs and masters.
Selection is read separately in each master. Automatic layers, shared outlines,
scaled or rotated shapes and quadratic contours are kept. No node is inserted,
deleted or retyped. Zero handle rays and zero chords are kept. General node
conversion, retraction and Tunni editing remain native or existing tools.
The preview lists each changed node's old and planned coordinates. Read-back
uses the App comparison epsilon; native coordinate storage remains subject to
FontLab's rounding preference.

Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Credit: Independent behaviour rewrite after Vassil Kateliev and Karandash Type
Foundry, kateliev/TypeRig, MPL-2.0. Ideas: node_slope.py and curve.py toolbars.
Repository: https://github.com/kateliev/TypeRig . No source code copied.

Run **Contours > Node Slope And Handles** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `15bbf0ccb0b9af5c5e980f1e9fd6cbd08ca9ffbb33c54ea28847d5d30dd3fff1`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Contours/Node%20Slope%20And%20Handles.py)
