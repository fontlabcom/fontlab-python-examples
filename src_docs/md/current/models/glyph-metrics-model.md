---
this_file: src_docs/md/current/models/glyph-metrics-model.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Metrics Model

Inspect real selected-glyph metrics with a read-only Qt table model.

Select glyphs in FontLab's Font window, then run this Models menu entry. The
table shows their current-master names, advances and outline left sidebearings
in font order. Zero remains zero; an em dash marks unavailable layer/outline
data. Refresh explicitly reads the current selection and master after edits.

No glyph fallback or edit occurs. Install fontlab-python-lessons and its fly/App
dependencies in FontLab's Python3.11 environment. Shared fly.ap lifetime helpers
keep the modeless panel owned and disconnect callbacks before destruction.

Run **Models > Glyph Metrics Model** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `c515c98b3de9b8d60ac973ee12c59f8d5624f5b4aa118c202057c8e1f2614b40`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Models/Glyph%20Metrics%20Model.py)
