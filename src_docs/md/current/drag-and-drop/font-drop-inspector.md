---
this_file: src_docs/md/current/drag-and-drop/font-drop-inspector.md
tags: ["Drag And Drop"]
categories: ["Drag And Drop"]
---

# Font Drop Inspector

Check dropped text against the current font and inspect drag formats.

Open a font and Refresh, then drop text or enter it and choose Use input.
The report lists each nonspace character with every matching glyph name.
Uncovered characters show MISSING. Check at most 5,000 characters at a time.
Drop URLs to inspect paths without opening them. Binary drops show format
names only. Copy or drag the report to document drag/drop behavior in scripts.
Plain-text display avoids interpreting HTML. No font data is changed.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Font Drop Inspector profile.

Run **Drag And Drop > Font Drop Inspector** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `df156bd6c302365e1dd8d6c377beaa7165b65e60d50db2edce81999bfa9d83ef`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Drag%20And%20Drop/Font%20Drop%20Inspector.py)
