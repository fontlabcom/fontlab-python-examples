# this_file: Scripts/Drag And Drop/Font Drop Inspector.py
# SPDX-License-Identifier: Apache-2.0
"""Check dropped text against the current font and inspect drag formats.

Open a font and Refresh, then drop text or enter it and choose Use input.
The report lists each nonspace character with every matching glyph name.
Uncovered characters show MISSING. Check at most 5,000 characters at a time.
Drop URLs to inspect paths without opening them. Binary drops show format
names only. Copy or drag the report to document drag/drop behavior in scripts.
Plain-text display avoids interpreting HTML. No font data is changed.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Font Drop Inspector profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E06", profile='Font Drop Inspector')


if __name__ == "__main__":
    main()
