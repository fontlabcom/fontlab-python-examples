---
this_file: src_docs/md/current/tools/layer-metric-comparison.md
tags: ["Tools"]
categories: ["Tools"]
---

# Layer Metric Comparison

What: Compare selected glyph-layer measurements with one reference cell.
How: Read complete equal passes of advances, outline bounds and sidebearings.
Calculate signed differences or percentages. Zero denominators stay undefined;
empty outlines keep unavailable dimensions and margins. Never substitute one.
Why: Relative measurements expose proportion and spacing differences directly.
Usage: Select layers in a Font or Glyph window. Choose Advance, Width, Height,
Left or Right. Enter a reference glyph and layer, or leave both blank to use
the first selected occurrence. Choose Difference or Percent. Copy the table.
Benefit: Compare actual selected layers without switching the active master.
The table is tab-separated text. Selection controls the compared layers;
this tool does not add unselected masters, scan named glyph lists or provide
an independent selected-node part/whole calculator.
View > Metrics Table edits metrics; this comparison reports relative values.

Independent behaviour-only rewrite of the metric-comparison idea from Stats.py.
Credit: Vassil Kateliev and Karandash Type Foundry; kateliev/TypeRig, MPL-2.0.
No TypeRig code, comments, icons or resources are included.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Run **Tools > Layer Metric Comparison** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/df145a203ba17854b926f4310eb3198fc3c703d9048a7660b4c859619a8c91be.py)
<!--/codeinclude-->
