# this_file: Scripts/Drag And Drop/Draggable Glyph Names.py
# SPDX-License-Identifier: Apache-2.0
"""Drag exact current-font glyph names into a FontLab proof.

Open a font, run this panel and Refresh after changing fonts. Enter an optional
name filter and choose Use input. Select rows and drag the slash-name tokens
into a Glyph window text bar. Copy output copies all displayed tokens.
Names retain suffixes and unencoded glyphs, so proof assembly does not depend
on Unicode assignments. Filtering and copy-only dragging leave the font intact.
This panel sends text; it does not accept incoming drops.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Draggable Glyph Names profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E06", profile='Draggable Glyph Names')


if __name__ == "__main__":
    main()
