---
this_file: src_docs/md/current/tools/glyph-name-completion.md
tags: ["Tools"]
categories: ["Tools"]
---

# Glyph Name Completion

Draft text with current-font glyph-name completions.

Purpose: Adapt the complete part2 custom-completer workflow to FontLab.
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
Compatibility: Actual PythonQt/font/cache/history/dirty/save/reopen acceptance
is pending. This command edits no font, selection, preference, file or Output.
Original: rescued/part2/ports/tools/pyqt-official/customcompleter-10ef4dacb4db4080.py
Original source/resources stay preserved and are not bundled by this facade.

Run **Tools > Glyph Name Completion** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a48476bc1d90a730e40213ae1b4e127e00a6c4d57992433ed2331af7b253e242.py)
<!--/codeinclude-->
