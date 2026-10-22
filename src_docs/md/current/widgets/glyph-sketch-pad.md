---
this_file: src_docs/md/current/widgets/glyph-sketch-pad.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Glyph Sketch Pad

What: Sketch construction ideas over a detached current-glyph outline.
How: Capture the current glyph in the current master. Fit its complete Qt path
into an owned canvas. Use its Base and Text palette roles for painting. Store
pen strokes in font units with y increasing upward. SVG keeps a fixed stroke.
Why: A detached sketch protects the glyph while keeping meaningful coordinates.
Usage: Open a glyph, then Capture. Drag to draw. Undo Stroke removes one stroke;
Clear removes the local sketch. SVG Text produces strokes for an external vector
editor, without the reference outline. Copy SVG Text before closing to retain it.
Capture refuses to replace a nonempty sketch. Close drops scratch strokes and
always permits application quit. No font or filesystem writes occur.
Benefit: Explore construction changes beside FontLab and keep reusable SVG lines.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless panel. App owns
signals and completion.
Independent rewrite of the Qt Scribble example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.

Run **Widgets > Glyph Sketch Pad** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/3321caeff0d78f8c20304acdf501e196aa7b6b4cbb6b1a5c2da2601c6c92edf4.py)
<!--/codeinclude-->
