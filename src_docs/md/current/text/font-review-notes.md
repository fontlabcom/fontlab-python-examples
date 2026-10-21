---
this_file: src_docs/md/current/text/font-review-notes.md
tags: ["Text"]
categories: ["Text"]
---

# Font Review Notes

What: Edit Markdown notes beside the current FontLab font.

How: Keep notes in a local text document. Add a font heading or checklist.

Why: Review notes need glyph references without changes to glyph note fields.

Usage: Type notes or Load a UTF-8 file from an absolute path. Select Font Heading
to add current-font names. Copy or Export New transfers the notes.

Benefit: Keep a clear checklist for spacing, accents and other review tasks.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.

Run **Text > Font Review Notes** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/903e2e83663d2591028f39946f8732ef0c7bd4ff3ba4305ce149719d746c55e3.py)
<!--/codeinclude-->
