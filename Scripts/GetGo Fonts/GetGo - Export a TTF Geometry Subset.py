# MenuTitle: GetGo - Export a TTF Geometry Subset
# this_file: Scripts/GetGo Fonts/GetGo - Export a TTF Geometry Subset.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: f06122a7a4d65a3d410057339fa5fc7c2b19312d69e355c0a225f4ca29446de0
"""GetGo - Export a TTF Geometry Subset: run the packaged lesson on verified owned GetGo copies.

Setup: Install fontlab-python-lessons with its packaged GetGo fonts and the
matching Fly/App reports API in FontLab 9 Python 3.11. Pen/export entries also
need the fonttools extra. Mutation lessons require a dedicated no-document
session. Source fonts remain unchanged; owned temporary copies close in finally.

Run: Choose Scripts > GetGo Fonts > GetGo - Export a TTF Geometry Subset.
Result: A detached, nonmodal read-only report shows the source and computed
values; exports also retain a new geometry subset at the reported path.
Compatibility: Native acceptance of this packaged adaptation is pending.
See the installed GetGo README for this entry's defaults, limits and outputs.
"""

from typing import Any


def main() -> Any:
    """Launch this installed lesson once and retain its report window."""
    from fontlab_python_lessons.getgo import launch

    return launch('export_ttf')


if __name__ == "__main__":
    main()
