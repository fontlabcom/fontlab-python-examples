# this_file: Scripts/Tools/Apply Unicode Map.py
# SPDX-License-Identifier: Apache-2.0
"""What: Add explicit Unicode values to selected glyphs in the current font.
How: Paste a JSON object of glyph names and code points. Integers are decimal;
strings are hexadecimal, with optional U+ or 0x prefix. A value can be a list.
Existing codes stay in place.
Why: Font > Generate Unicodes derives values from names. This map also encodes
custom names and assigns several explicit values to one glyph.
Usage: Select glyphs in the Font window and close Glyph editors. Paste a map,
inspect the live table, then Apply Map. Use Selection reloads the glyph scope.
Each Apply is recorded as one Undo step. Auto-layer owners, bases of automatic
composites, unknown names and conflicting codes remain as named kept rows.
Benefit: Apply a reusable character map without renaming outlines.

Example: {"A": "0041", "space": [32, "00A0"]}. Repeated JSON keys and invalid
Unicode scalars are refused. Several map rows cannot claim the same code.
Only selected glyphs can change. Typing uses a detached font snapshot. Use
Selection
reloads it. Apply scans the font once and compares with the displayed preview;
native read-back checks every changed list. A partial write directs you to
Edit > Undo. JSON is pasted; NAM files and font-library maps are not loaded.
Original profile setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0. Modeless panel.

Independent behaviour rewrite of TR-EncodeGlyphs.py by Vassil Kateliev,
kateliev/TypeRig, MPL-2.0. https://github.com/kateliev/TypeRig
No TypeRig code, private identifiers, comments or resources are copied.


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Unicode Lab; opens the Apply Unicode Map profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E08", profile='Apply Unicode Map')


if __name__ == "__main__":
    main()
