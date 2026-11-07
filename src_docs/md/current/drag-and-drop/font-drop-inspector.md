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

Run **Drag And Drop > Font Drop Inspector** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `74a595b4944c809756c110d16a996cbd7020885bc2b1dd32fe27ad50bbec7296`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Drag%20And%20Drop/Font%20Drop%20Inspector.py)
