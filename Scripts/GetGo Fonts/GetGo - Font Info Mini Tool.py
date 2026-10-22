# MenuTitle: GetGo - Font Info Mini Tool
# this_file: Scripts/GetGo Fonts/GetGo - Font Info Mini Tool.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: b2574dfef010e55be3ae347d2695c3c69f0137548a666902d3ce3221902b1c5f
"""GetGo - Font Info Mini Tool: run the packaged lesson on verified owned GetGo copies.

Setup: Install fontlab-python-lessons with its packaged GetGo fonts and the
matching Fly/App reports API in FontLab 9 Python 3.11. Pen/export entries also
need the fonttools extra. Mutation lessons require a dedicated no-document
session. Source fonts remain unchanged; owned temporary copies close in finally.

Run: Choose Scripts > GetGo Fonts > GetGo - Font Info Mini Tool.
Result: A detached, nonmodal read-only report shows the source and computed
values; exports also retain a new geometry subset at the reported path.
Compatibility: Native acceptance of this packaged adaptation is pending.
See the installed GetGo README for this entry's defaults, limits and outputs.
"""

from typing import Any


def main() -> Any:
    """Launch this installed lesson once and retain its report window."""
    from fontlab_python_lessons.getgo import launch

    return launch('font_info_ui')


if __name__ == "__main__":
    main()
