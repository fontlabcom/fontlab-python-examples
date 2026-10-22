# this_file: Scripts/Widgets/Glyph Modification Calendar with Formats.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: feb734fd0e15a9b4217552e8823ee07beb8ce6d73bd27c21dfa36a537ecd1407
"""Inspect current-font modification dates with the complete part3 calendar.

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
"""


def main() -> None:
    """Open the complete owned part3 calendar through the lazy Fly alias."""
    from fly.ap.glyph_calendar import show_official

    show_official()


if __name__ == "__main__":
    main()
