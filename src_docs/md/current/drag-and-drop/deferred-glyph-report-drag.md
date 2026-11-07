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

## Source identity

SHA256: `138a809f419d024f95e499da5b50f2ea8d08fbe2e0a24afd16982c67a82af1fb`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Drag%20And%20Drop/Deferred%20Glyph%20Report%20Drag.py)
