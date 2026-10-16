# MenuTitle: GetGo - Export a TTF Geometry Subset
# SPDX-License-Identifier: Apache-2.0
# this_file: examples/getgo/export_ttf.py
"""GG Baar (CC0-1.0): export .notdef/space/A/V as a verified TrueType subset.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Native hints/features/kerning are omitted.
"""

from pathlib import Path

from examples.getgo._binary import export_subset


def run(destination: str | Path | None = None) -> dict:
    """Convert native cubic contours to quadratic outlines and reopen the TTF."""
    return export_subset(destination, is_ttf=True)


if __name__ == "__main__":
    print(run())
