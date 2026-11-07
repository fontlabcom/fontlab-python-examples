---
this_file: src_docs/md/current/drawing/glyph-outline-svg.md
tags: ["Drawing"]
categories: ["Drawing"]
---

# Glyph Outline SVG

What: Export the current glyph outline as reusable SVG artwork.
How: Capture its current-master Qt path, including transformed components.
Choose winding or odd-even fill to diagnose counters and overlaps.
Why: Keep curves in a vector proof without changing font data.
Usage: Open a glyph, Capture, choose a fill rule and Update Proof.
Copy SVG or enter a new absolute .svg path and Save SVG.
Benefit: Keep rendered artwork for an external vector editor.
The frame includes the origin, advance, ascender, descender and ink bounds.
One SVG user unit equals one font unit. SVG y increases downward; baseline is y=0.

SVG is a visual proof. It contains no anchors, metrics, hints or raw node flags.
Snapshots remain detached. Capture again after changing the current font.
Setup: FontLab 9, Python 3.11, Fly, fontlabapp and QtSvg.QSvgGenerator.
Independent rewrite of the Qt painterpaths, basicdrawing and transformations
example ideas (Qt/Nokia, Riverbank). Consolidated into one outline exporter.
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.

Run **Drawing > Glyph Outline SVG** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `8411e650253aa79bd74b432e9fceb74bc921f745714acddad7ca63277f727171`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Drawing/Glyph%20Outline%20SVG.py)
