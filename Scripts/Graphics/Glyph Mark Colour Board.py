# this_file: Scripts/Graphics/Glyph Mark Colour Board.py
# SPDX-License-Identifier: Apache-2.0
"""What: Drop colour swatches onto prefix-matched glyphs to set FontLab marks.
How: Capture current-font glyph identities. A drop makes one metadata Undo step
through App history. Read-back checks individually coloured layer overrides.
Native glyph-to-layer mark propagation is unverified.
Why: Organize a review group with visible glyph marks in the Font window.
Usage: Enter a glyph-name prefix, Refresh, then drag a swatch onto a tile.
Refresh after changing the font or master. None clears the glyph's mark.
Benefit: Flag individual glyphs directly without changing the font selection.
The table and selection swatches edit the same property; this board adds
prefix-scoped, drag-and-drop editing.
Glyphs with auto layers are refused. A partial write reports Edit > Undo.
Original profile setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; each drop edits
one glyph.
Independent rewrite of the Qt dragdroprobot example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Historical source: rescued/part2/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py
SHA256: f1faf59693b2054c207de5811e7d721260755e6a5675f199f3472e3d520204d2
Historical source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py
SHA256: c021aba5ca45ca9cf3b0fde77ceb654ff5077191380d83cef5d84c1aec9c8313


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Review Model Lab; opens the Glyph Mark Colour Board profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E09", profile='Glyph Mark Colour Board')


if __name__ == "__main__":
    main()
