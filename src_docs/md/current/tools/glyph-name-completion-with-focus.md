---
this_file: src_docs/md/current/tools/glyph-name-completion-with-focus.md
tags: ["Tools"]
categories: ["Tools"]
---

# Glyph Name Completion with Focus

Draft text with current-font glyph-name completions.

Purpose: Adapt the complete part3 custom-completer workflow to FontLab.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.63.dev0.
Run: Open a font, run this Tools command, and type at least three characters.
Ctrl+E also offers shorter prefixes. Use Refresh after font changes.
Result: Keep every exact glyph name in the vocabulary, including unencoded and
suffixed names. Draft text and normal text copy stay local to the owned editor.
Design: Shared App completion mechanics use native Qt case-insensitive ordering,
exact QString activation, complete source-fenced reads and safe replacement.
Part2 retains alphabetic triggers, New/Close and Vocabulary. Part3 retains its
separate punctuation/modifier, focus, suffix, popup width and About/Exit policy.
Refresh errors remove old completions but keep the draft. About information is
shown in the modeless status area. A failed disconnect refuses Close for retry.
Close releases owned callbacks and models; no original body is executed.
Compatibility: Uses FontLab's supplied PythonQt. This command edits no font, selection, preference, file or Output.
Historical source: rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/customcompleter-10ef4dacb4db4080.py
Original source/resources are archived outside this repository and are not bundled by this facade.

Run **Tools > Glyph Name Completion with Focus** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `a9b0779d69e988bb6ffa90bb5e3ed39127310f01930a743afd601c763ca9bd82`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Tools/Glyph%20Name%20Completion%20with%20Focus.py)
