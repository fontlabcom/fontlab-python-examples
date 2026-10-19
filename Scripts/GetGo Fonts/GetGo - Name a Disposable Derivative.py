# MenuTitle: GetGo - Name a Disposable Derivative
# this_file: Scripts/GetGo Fonts/GetGo - Name a Disposable Derivative.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 923c9109b994eed66c18e4056cc1ed2054748bcb1a3b53083097583f1f909d40
"""GetGo - Name a Disposable Derivative: run the packaged lesson on verified owned GetGo copies.

Setup: Install fontlab-python-lessons with its packaged GetGo fonts and the
matching Fly/App reports API in FontLab 9 Python 3.11. Pen/export entries also
need the fonttools extra. Mutation lessons require a dedicated no-document
session. Source fonts remain unchanged; owned temporary copies close in finally.

Run: Choose Scripts > GetGo Fonts > GetGo - Name a Disposable Derivative.
Result: A detached, nonmodal read-only report shows the source and computed
values; exports also retain a new geometry subset at the reported path.
Compatibility: Native acceptance of this packaged adaptation is pending.
See the installed GetGo README for this entry's defaults, limits and outputs.
"""

from typing import Any


def main() -> Any:
    """Launch this installed lesson once and retain its report window."""
    from fontlab_python_lessons.getgo import launch

    return launch('naming')


if __name__ == "__main__":
    main()
