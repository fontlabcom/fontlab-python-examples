# this_file: Scripts/Text/Calendar Proof Builder.py
# SPDX-License-Identifier: Apache-2.0
"""What: Create a monthly numeral proof for the current font.

How: Read Unicode assignments. Build a Monday-first calendar and report missing
ASCII digits and the space separator. The HTML preview uses a reference font.

Why: Glyph names do not identify Unicode coverage reliably.

Usage: Set year and month. Select Build, then Copy. Paste into FontLab Metrics
to proof the actual font. Export New saves a complete UTF-8 HTML document.

Benefit: Check date spacing with realistic numeral sequences.

Original profile setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Calendar Lab; opens the Calendar Proof Builder profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E04", profile='Calendar Proof Builder')


if __name__ == "__main__":
    main()
