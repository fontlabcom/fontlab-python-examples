# this_file: Scripts/Models/Glyph Mark Colours.py
# SPDX-License-Identifier: Apache-2.0
"""What: Edit glyph mark colours in a table of the current FontLab font.
How: Capture scalar glyph identities and marks through App names_edit. Each
colour cell uses a combo delegate with FontLab hue and grey presets. Apply
rechecks the current font and original values, then calls App history.commit
with metadata policy for only changed rows. One Apply creates one Undo step.
Why: Native marks persist with the font and support FontLab colour selection.
Usage: Open a font, double-click colour cells, choose marks and click Apply.
Use Discard Changes to restore local edits. Glyphs with auto layers are
refused.
Benefit: Review many glyph marks without changing names, notes or outlines.
Requires: FontLab 9, Python 3.11, Fly and App names_edit, history,
draft_signals
and qt_properties. Failed writes retain the local plan and show Undo guidance.

Independent rewrite of the Qt coloreditorfactory example idea. Based on the
author's own FontLab sample,
Apache-2.0.
Historical source: rescued/part2/ports/itemviews/pyqt-official/coloreditorfactory-0a3b15766909bdc3.py
SHA256: 06780068bb97fb0b0787dbc5fc5dc5d51b1c2c29cfd053fa0ba6be4be802ce58
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/coloreditorfactory-0a3b15766909bdc3.py
SHA256: 5b4aa3c5c7aaad2b40cb25c868c6aa41f828dbc884021db9fd2d630f5cd64534


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Review Model Lab; opens the Glyph Mark Colours profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E09", profile='Glyph Mark Colours')


if __name__ == "__main__":
    main()
