# this_file: Scripts/Models/Glyph Coverage Grid.py
# SPDX-License-Identifier: Apache-2.0
"""What: Inspect Unicode coverage as a sixteen-column grid of glyph names.
How: Group every captured Unicode assignment into rows of sixteen scalars.
Keep all names when several glyphs share a scalar. Leave absent cells blank.
Why: A name grid reveals gaps and collisions without substituting font previews.
Usage: Open a font and Refresh. Combine each row label with the column digit.
Copy or export JSON to record the complete coverage grid.
Benefit: Locate duplicate assignments and missing positions during font review.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Refresh stages results before replacing the visible grid.

Independent rewrite of the Qt pixelator example idea. Based on the author's own FontLab sample,
Apache-2.0.
Historical source: rescued/part2/ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py
SHA256: 9b8e6b6e8c542817876e897eef2d9d5a503c40eea8486dc6ef975621e123444c
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py
SHA256: dcffd1f6ddaf3cbbe1b72fa90816d42892ce5abccf5ff0098e7e5cc50c9270bb


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Unicode Lab; opens the Glyph Coverage Grid profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E08", profile='Glyph Coverage Grid')


if __name__ == "__main__":
    main()
