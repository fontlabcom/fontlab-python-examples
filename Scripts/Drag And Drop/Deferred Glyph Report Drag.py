# this_file: Scripts/Drag And Drop/Deferred Glyph Report Drag.py
# SPDX-License-Identifier: Apache-2.0
"""Export the current font's glyph inventory without preparing unused data.

Open a font and run this panel. Refresh captures glyph names and Unicode values.
Drag output into a text field to insert one glyph name per line, or into a JSON
consumer to receive all names and assignments. Copy output copies the JSON.
Each representation is prepared only when requested. Captured data stays stable
during the drag, so the target cannot mix values from different font states.
Font data is read only. No glyph selection or document content is changed.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Deferred Glyph Report Drag profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E06", profile='Deferred Glyph Report Drag')


if __name__ == "__main__":
    main()
