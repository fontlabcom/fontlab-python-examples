---
this_file: src_docs/md/current/widgets/glyph-modification-calendar-with-formats.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Glyph Modification Calendar with Formats

Inspect current-font modification dates with the complete part3 calendar.

Purpose: Adapt the distinct full part3 Calendar Widget workflow to FontLab.
Retain every Qt locale in native order, all seven week starts, both selection
modes, grid/navigation, all headings, date limits and four weekday/weekend colours.
Setup: FontLab 9, Python 3.11, fontlab-fly and App>=0.2.61.dev0.
Run: Open a font and run this Widgets command. Choose a date to inspect complete
captured glyph names, Unicode assignments and local modification times in order.
Set Bold/Italic/Plain headers. Toggle first Friday in blue and May 1 in red
independently. May 1 wins when both marks coincide. Refresh reads the font again.
Result: Read the complete matching glyph snapshot without editing the font.
Missing dates are counted. Failed reads clear results. Close releases ownership.
Design: Share generic date fields, signal/lifetime mechanics and reports in App,
through Fly. Preserve part3's 1900–3000 limits and MMM d yyyy editor format.
Clear only owned date marks after page/year/switch changes; keep named colours
readable on an owned light date surface inside either host theme.
Compatibility: Uses FontLab's supplied PythonQt. The separate part2 calendar keeps its own controls and defaults.
Historical source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/calendarwidget-b91effc45f81fbb0.py
Original source/resources are archived outside this repository; this command does not execute them.

Run **Widgets > Glyph Modification Calendar with Formats** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/2b4be40ee762236f25ab2ef6b0decfb86539e31a9dbc5a18c5a8ca6cf7f78b42.py)
<!--/codeinclude-->
