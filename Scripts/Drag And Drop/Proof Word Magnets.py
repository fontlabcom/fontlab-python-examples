# this_file: Scripts/Drag And Drop/Proof Word Magnets.py
# SPDX-License-Identifier: Apache-2.0
"""Arrange proof words for a FontLab Glyph window text bar.

Type words and choose Use input, or drop plain text. Drag rows to reorder them;
select rows and choose Remove selected to delete individual words. Repeated
words remain separate. Copy proof text copies the assembled line to the
clipboard; paste it into a Glyph window text bar, or drag output there.
Refresh checks the current font for missing characters. Without a font, the
local draft still works. The panel uses the UI font and does not render outlines.
Prepare quick proof variations without changing glyphs or metrics.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Proof Word Magnets profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E06", profile='Proof Word Magnets')


if __name__ == "__main__":
    main()
