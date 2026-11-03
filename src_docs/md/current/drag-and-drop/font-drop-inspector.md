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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/74a595b4944c809756c110d16a996cbd7020885bc2b1dd32fe27ad50bbec7296.py)
<!--/codeinclude-->
