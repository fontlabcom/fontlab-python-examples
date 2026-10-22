# MenuTitle: GetGo - Sidebearings from H
# this_file: Scripts/GetGo Fonts/GetGo - Sidebearings from H.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: 46819ae9909a25291ca3b9558dbe2a1241e7f504fc1ea113a6679047adba3143
"""GetGo - Sidebearings from H: run the packaged lesson on verified owned GetGo copies.

Setup: Install fontlab-python-lessons with its packaged GetGo fonts and the
matching Fly/App reports API in FontLab 9 Python 3.11. Pen/export entries also
need the fonttools extra. Mutation lessons require a dedicated no-document
session. Source fonts remain unchanged; owned temporary copies close in finally.

Run: Choose Scripts > GetGo Fonts > GetGo - Sidebearings from H.
Result: A detached, nonmodal read-only report shows the source and computed
values; exports also retain a new geometry subset at the reported path.
Compatibility: Uses FontLab's supplied PythonQt.
See the installed GetGo README for this entry's defaults, limits and outputs.
"""

from typing import Any


def main() -> Any:
    """Launch this installed lesson once and retain its report window."""
    from fontlab_python_lessons.getgo import launch

    return launch('spacing')


if __name__ == "__main__":
    main()
