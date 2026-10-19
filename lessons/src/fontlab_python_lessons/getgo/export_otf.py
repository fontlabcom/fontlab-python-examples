# this_file: lessons/src/fontlab_python_lessons/getgo/export_otf.py
# SPDX-License-Identifier: Apache-2.0
# MenuTitle: GetGo - Export an OTF Geometry Subset

"""GG Baar (CC0-1.0): export .notdef/space/A/V as a verified CFF OpenType subset.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Native hints/features/kerning are omitted.
"""

from pathlib import Path

from fontlab_python_lessons.getgo._binary import export_subset


def run(destination: str | Path | None = None) -> dict:
    """Build Type 2 charstrings from native segment pens and reopen the OTF."""
    return export_subset(destination, is_ttf=False)
