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
[Python source](../../../../.build/menu-sources/a16d69daf12c6ab9adea7ad8ec4eda210b2a171f21f29f0d97eb35c6e6bcd4bb.py)
<!--/codeinclude-->
