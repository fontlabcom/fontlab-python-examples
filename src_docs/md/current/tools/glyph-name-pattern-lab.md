---
this_file: src_docs/md/current/tools/glyph-name-pattern-lab.md
tags: ["Tools"]
categories: ["Tools"]
---

# Glyph Name Pattern Lab

Author native Qt 5 patterns against complete captured FontLab glyph names.

Purpose:
    Keep the complete Pattern Matching Inspector useful for glyph-name rules.
    Test captures, positions and lengths before using a pattern in another tool.
Setup:
    Use FontLab 9, Python 3.11, Fly and App>=0.2.76.dev0.
    Install the prerequisites yourself. This script installs nothing.
Run:
    Open this modeless lab from Tools. Edit the pattern and test-text histories.
    Choose Regular expression, Regular expression 2, Wildcard or Fixed string.
    Toggle case sensitivity or minimal matching. Every edit updates the result.
    Refresh Glyph Names captures the complete current-font vocabulary.
    Choose a captured name to use it as test text; both authored drafts survive Refresh.
Result:
    Inspect the escaped pattern, native position/length and every capture.
    Inspect all matching captured glyph names and their individual captures.
    Positions and lengths use Qt UTF-16 units. The lab changes no font data.
Compatibility:
    Native PythonQt, complete getter/cache/history/dirty/reopen acceptance pending.
    Independent implementation; no original body or source helper is executed.
    Preserved source: rescued/part2/ports/tools/pyqt-official/regexp-626fd0acec74fd91.py

Run **Tools > Glyph Name Pattern Lab** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/b7f966b9251b68b735648be2b03b8c759631503ae1f1023a2c28227838bb5829.py)
<!--/codeinclude-->
