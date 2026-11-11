# this_file: Scripts/Drag And Drop/Glyph Pair Board.py
# SPDX-License-Identifier: Apache-2.0
"""Build adjacent glyph-pair proof lines from the current font.

Open a font and enter or drop slash names, for example /A/V/A. Choose Use input
to append tiles. Drag rows to reorder them, or select rows and Remove selected.
Copy or drag output into a Glyph window text bar: each line contains one pair.
Names are checked before adding tiles. Repeated names, suffixes and unencoded
glyphs remain valid. Refresh clears the board for the newly captured font.
The board changes only the local proof order, never glyph order or kerning.
Prepare focused pair checks without entering each pair separately.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Glyph Pair Board profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E06", profile='Glyph Pair Board')


if __name__ == "__main__":
    main()
