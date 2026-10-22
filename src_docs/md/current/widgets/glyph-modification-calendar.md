---
this_file: src_docs/md/current/widgets/glyph-modification-calendar.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Glyph Modification Calendar

Inspect current-font glyph modification dates with complete calendar controls.

Purpose: Adapt the complete part2 Calendar Controls workflow to FontLab.
Choose a local calendar day. Read every matching glyph name, all its Unicode
assignments and the exact captured modification timestamp in font order.
Setup: FontLab 9, Python 3.11, fontlab-fly and App>=0.2.60.dev0.
Run: Open a font and run this Widgets command. Set locale, week start, selection,
grid, navigation, headings, date limits and weekday/weekend/header colours.
The special switch marks the first Friday and January 1 of the displayed year.
Refresh replaces the whole read-only snapshot. A failure clears all results.
Result: Inspect which glyphs changed on a day without editing font data or
native selection. Undated glyphs are counted explicitly. Close releases signals.
Design: Use generic injected-Qt calendar controls and complete metadata capture
in App, through Fly. Initial options and crossing date limits stay coherent.
The distinct part3 calendar with May 1 and bold/italic headings stays separate.
Compatibility: Native PythonQt/getter/font/cache/history/save/reopen acceptance
is pending. This candidate neither changes preferences nor writes files/Output.
Historical source: rescued/part2/ports/widgets/pyqt-official/calendarwidget-b91effc45f81fbb0.py
Original source/resources are archived outside this repository; this command does not execute them.

Run **Widgets > Glyph Modification Calendar** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/989ee48a51d1cb127df6581b43f2c1ec32e427a515a1b10b686dbd3fbdb49930.py)
<!--/codeinclude-->
