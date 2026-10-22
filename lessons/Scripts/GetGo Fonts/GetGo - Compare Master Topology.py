# MenuTitle: GetGo - Compare Master Topology
# this_file: lessons/Scripts/GetGo Fonts/GetGo - Compare Master Topology.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: fcf75898a46cca80ed0f7e36627864c18a2a9c8e781793fcd70d43fd7a74015e
"""GetGo - Compare Master Topology: run the packaged lesson on verified owned GetGo copies.

Setup: Install fontlab-python-lessons with its packaged GetGo fonts and the
matching Fly/App reports API in FontLab 9 Python 3.11. Pen/export entries also
need the fonttools extra. Mutation lessons require a dedicated no-document
session. Source fonts remain unchanged; owned temporary copies close in finally.

Run: Choose Scripts > GetGo Fonts > GetGo - Compare Master Topology.
Result: A detached, nonmodal read-only report shows the source and computed
values; exports also retain a new geometry subset at the reported path.
Compatibility: Native acceptance of this packaged adaptation is pending.
See the installed GetGo README for this entry's defaults, limits and outputs.
"""

from typing import Any


def main() -> Any:
    """Launch this installed lesson once and retain its report window."""
    from fontlab_python_lessons.getgo import launch

    return launch('master_compatibility')


if __name__ == "__main__":
    main()
