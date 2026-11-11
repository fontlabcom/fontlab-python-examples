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
Original profile setup:
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
    Independent implementation; no original body or source helper is executed.
    Historical source: rescued/part2/ports/tools/pyqt-official/regexp-626fd0acec74fd91.py


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Model Filtering Lab; opens the Glyph Name Pattern Lab profile.

Run **Tools > Glyph Name Pattern Lab** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `3ec4acf173cd70589abd088130392d22317acfe73e4290c9cc20399070ee395f`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Tools/Glyph%20Name%20Pattern%20Lab.py)
