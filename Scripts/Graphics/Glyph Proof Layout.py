# this_file: Scripts/Graphics/Glyph Proof Layout.py
# SPDX-License-Identifier: Apache-2.0
"""What: Compare current-master advance widths and geometric side bearings.
How: Read a prefix-matched sample twice and build an anchored spacing strip.
Each tile's width is proportional to its advance. Hover for full measurements;
zero advances use a vertical marker and a separate measurement label.
Why: Compare relative widths at a glance while reviewing spacing in FontLab.
Usage: Open a font, enter a prefix with at most twelve matches, set the strip
width, then Refresh. Copy Result sends slash names to a Glyph window text bar.
Benefit: Spot width outliers without changing outlines or font metrics.
Empty layers have no ink margins; their side bearings show an em dash.

Original profile setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt anchorlayout example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Historical source: rescued/part2/ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py
SHA256: 4de40f5bc168015793f3529ef70f2e69dc46be41b38d17afb29f7e34ef8d717f
Historical source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py
SHA256: 60caa0dacfd8b8e41a4c8a5c83e5aced63a298e574433410c25e529452560ad2


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Proof Composition Lab; opens the Glyph Proof Layout profile.
"""


def main():
    """Open this retained route in its shared lab."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E07", profile='Glyph Proof Layout')


if __name__ == "__main__":
    main()
