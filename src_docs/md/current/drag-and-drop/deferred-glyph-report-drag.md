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


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Deferred Glyph Report Drag profile.

Run **Drag And Drop > Deferred Glyph Report Drag** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `02f30ccf16180b2ee87911f40dcc22061609c45508d67a39230eaf402544c2bc`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Drag%20And%20Drop/Deferred%20Glyph%20Report%20Drag.py)
