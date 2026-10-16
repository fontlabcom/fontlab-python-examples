# MenuTitle: GetGo - Export an OTF Geometry Subset
# SPDX-License-Identifier: Apache-2.0
# this_file: examples/getgo/export_otf.py
"""GG Baar (CC0-1.0): export .notdef/space/A/V as a verified CFF OpenType subset.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Native hints/features/kerning are omitted.
"""

from pathlib import Path

from examples.getgo._binary import export_subset


def run(destination: str | Path | None = None) -> dict:
    """Build Type 2 charstrings from native segment pens and reopen the OTF."""
    return export_subset(destination, is_ttf=False)


if __name__ == "__main__":
    print(run())
