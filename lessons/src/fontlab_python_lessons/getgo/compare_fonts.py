# this_file: lessons/src/fontlab_python_lessons/getgo/compare_fonts.py
# SPDX-License-Identifier: Apache-2.0
# MenuTitle: GetGo - Compare Two Real Fonts

"""GG Baar (CC0-1.0) and GG Hint (Apache-2.0): normalized glyph-width comparison.
Source fonts: https://code.fontlab.com/getgo-fonts/baar/
https://code.fontlab.com/getgo-fonts/hint/
Original example code: Apache-2.0. Each input has its own temporary copy.
"""

import math

from fontlab_python_lessons.getgo._shared import owned_font


def compare(left: dict, left_upm: float, right: dict, right_upm: float) -> dict:
    """Compare common glyph widths in em, reporting additions and removals."""
    if not all(math.isfinite(n) and n > 0 for n in (left_upm, right_upm)):
        msg = "Units per em must be finite and positive"
        raise ValueError(msg)
    common = sorted(left.keys() & right.keys())
    return {
        "only_left": sorted(left.keys() - right.keys()),
        "only_right": sorted(right.keys() - left.keys()),
        "width_delta_em": {n: round(right[n] / right_upm - left[n] / left_upm, 6) for n in common},
    }


def run() -> dict:
    """Open both fonts together and unwind both contexts even if inspection fails."""
    with owned_font("baar") as (left, lrecord), owned_font("hint") as (right, rrecord):
        widths = [{g.name: float(g.width) for g in package.fgPackage} for package in (left, right)]
        return {
            "sources": [lrecord["page_url"], rrecord["page_url"]],
            **compare(
                widths[0],
                left.info.unitsPerEm,
                widths[1],
                right.info.unitsPerEm,
            ),
        }
