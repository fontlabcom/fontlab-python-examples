# this_file: Scripts/Widgets/Glyph Modification Calendar.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: 5672f6757f558382ba7c7dce22a8e1effad9a707adcea7d2fa916a776a8e4bbb
"""Inspect current-font glyph modification dates with complete calendar controls.

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
"""


def main() -> None:
    """Open the complete owned local-date glyph report through the lazy Fly alias."""
    from fly.ap.glyph_calendar import show

    show()


if __name__ == "__main__":
    main()
