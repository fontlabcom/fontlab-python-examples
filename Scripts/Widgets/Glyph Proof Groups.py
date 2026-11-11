# this_file: Scripts/Widgets/Glyph Proof Groups.py
# SPDX-License-Identifier: Apache-2.0
"""What: Build a glyph-name proof from useful current-font groups.
How: Read a fresh App catalog. Combine encoded and unencoded glyphs in font
order, optionally omit suffix names, then wrap slash names into short lines.
Why: Explicit groups make a compact Metrics proof without changing selection.
Usage: Tick the desired groups and set names per line. Preview, then copy the
plain text into FontLab Metrics. Dots identify suffix names by convention.
Names outside portable slash syntax are omitted and listed in the status line.
Benefit: Compare base glyphs and alternates in repeatable proof groups.

Original profile setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Group Box example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Proof Composition Lab; opens the Glyph Proof Groups profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E07", profile='Glyph Proof Groups')


if __name__ == "__main__":
    main()
