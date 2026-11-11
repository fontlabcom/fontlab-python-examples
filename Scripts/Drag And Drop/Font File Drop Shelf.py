# this_file: Scripts/Drag And Drop/Font File Drop Shelf.py
# SPDX-License-Identifier: Apache-2.0
"""Collect font files and open selected entries in FontLab.

Drop local fonts or UFO folders, or enter an absolute path and choose Use input.
Select rows and choose Open in FontLab, or drag their file URLs to another window.
Copy output copies all staged paths for scripts. Clear empties the shelf.
The whole selection is checked before opening starts. A failed open stops the
batch and reports which files already opened. File contents are never changed.
No current font is required. Save repeated trips through the file dialog.
Opening relies on FontLab's own format support.
Requires FontLab 9, Python 3.11, Fly and native font-opening support.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Font File Drop Shelf profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E06", profile='Font File Drop Shelf')


if __name__ == "__main__":
    main()
