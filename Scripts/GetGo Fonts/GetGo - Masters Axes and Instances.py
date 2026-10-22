# MenuTitle: GetGo - Masters Axes and Instances
# this_file: Scripts/GetGo Fonts/GetGo - Masters Axes and Instances.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: b66b704bc5d5fa09b1f8d15effa09ba119973672c3db755fff20095116d4394f
"""GetGo - Masters Axes and Instances: run the packaged lesson on verified owned GetGo copies.

Setup: Install fontlab-python-lessons with its packaged GetGo fonts and the
matching Fly/App reports API in FontLab 9 Python 3.11. Pen/export entries also
need the fonttools extra. Mutation lessons require a dedicated no-document
session. Source fonts remain unchanged; owned temporary copies close in finally.

Run: Choose Scripts > GetGo Fonts > GetGo - Masters Axes and Instances.
Result: A detached, nonmodal read-only report shows the source and computed
values; exports also retain a new geometry subset at the reported path.
Compatibility: Native acceptance of this packaged adaptation is pending.
See the installed GetGo README for this entry's defaults, limits and outputs.
"""

from typing import Any


def main() -> Any:
    """Launch this installed lesson once and retain its report window."""
    from fontlab_python_lessons.getgo import launch

    return launch('designspace')


if __name__ == "__main__":
    main()
