---
this_file: src_docs/md/current/drag-and-drop/deferred-glyph-report-drag.md
tags: ["Drag And Drop"]
categories: ["Drag And Drop"]
---

# Deferred Glyph Report Drag

Export the current font's glyph inventory without preparing unused data.

Open a font and run this panel. Refresh captures glyph names and Unicode values.
Drag output into a text field to insert one glyph name per line, or into a JSON
consumer to receive all names and assignments. Copy output copies the JSON.
Each representation is prepared only when requested. Captured data stays stable
during the drag, so the target cannot mix values from different font states.
Font data is read only. No glyph selection or document content is changed.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).

Run **Drag And Drop > Deferred Glyph Report Drag** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0e39090b3239dd586578fe2ea74c0a53e12ae7611486ac335e9a7e40b5f2ef14.py)
<!--/codeinclude-->
