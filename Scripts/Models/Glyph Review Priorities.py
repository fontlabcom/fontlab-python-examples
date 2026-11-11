# this_file: Scripts/Models/Glyph Review Priorities.py
# SPDX-License-Identifier: Apache-2.0
"""What: Keep a resumable zero-to-five-star review queue for the current font.
How: A painted five-star delegate sets scores by click and edits existing items.
Export JSON retains
the full queue; Import reloads it after checking glyph names, score ranges,
star consistency, duplicate keys and characters that PythonQt can replace.
Why: A portable queue can be resumed without modifying native glyph metadata.
Usage: Open a font and Refresh. Click within a star cell to set its score; Delete clears it.
Export New before closing. To resume, Refresh the matching font and Import an
exported queue. Import accepts UTF-8 BOM and normalizes CRLF or CR to LF.
Benefit: Carry a review across sessions and reject incompatible queues clearly.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Invalid imports keep the visible queue and current scores.

Independent rewrite of the Qt stardelegate example idea. Based on the author's own FontLab sample,
Apache-2.0.
Historical source: rescued/part2/ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py
SHA256: ab5c5904d2ca3688def0ad17a8a48ac63f507e7a77778a888f14e04a89b0c079
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py
SHA256: d11286ceb3e9b813bbda21d1f820c224694722b2b3476c7b19a0791cd6fcc311


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Review Model Lab; opens the Glyph Review Priorities profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E09", profile='Glyph Review Priorities')


if __name__ == "__main__":
    main()
