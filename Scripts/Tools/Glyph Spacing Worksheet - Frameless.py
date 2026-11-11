# this_file: Scripts/Tools/Glyph Spacing Worksheet - Frameless.py
# SPDX-License-Identifier: Apache-2.0
"""Compare four local spacing recipes against every selected glyph-layer advance.

Purpose:
    Keep the complete preserved part3 Spin Box Delegate lesson useful in FontLab.
    A is a font-unit increment. B is its repeat count. Edit all eight cells.
Original profile setup:
    Use FontLab 9, Python 3.11, Fly and App>=0.2.70.dev0.
    Use matching artifacts. No automatic installation is performed.
Run:
    Select glyph layers, then open this modeless worksheet from Tools.
    Edit factors even without a font. Refresh Selection reads a complete snapshot.
    Reset Factors restores original values and types. Close cancels pending input.
Result:
    Read each captured baseline and all four baseline-plus-A-times-B candidates.
    Candidates change no font metrics. Failed refresh retains the prior report.
Compatibility:
    Independent behavior implementation; no preserved body/helper is executed.
    Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/spinboxdelegate-ddb20b1b68b18a91.py


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Metrics Controls Lab; opens the Glyph Spacing Worksheet - Frameless profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E03", profile='Glyph Spacing Worksheet - Frameless')


if __name__ == "__main__":
    main()
