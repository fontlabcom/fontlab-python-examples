# MenuTitle: GetGo - Outline Pens and Intersections
# this_file: Scripts/GetGo Fonts/GetGo - Outline Pens and Intersections.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: b6084952d02dcad932da450f300bb20aa7fb470ab36ba389a3c9f1ea13ace0d7
"""GetGo - Outline Pens and Intersections: run the packaged lesson on verified owned GetGo copies.

Setup: Install fontlab-python-lessons with its packaged GetGo fonts and the
matching Fly/App reports API in FontLab 9 Python 3.11. Pen/export entries also
need the fonttools extra. Mutation lessons require a dedicated no-document
session. Source fonts remain unchanged; owned temporary copies close in finally.

Run: Choose Scripts > GetGo Fonts > GetGo - Outline Pens and Intersections.
Result: A detached, nonmodal read-only report shows the source and computed
values; exports also retain a new geometry subset at the reported path.
Compatibility: Uses FontLab's supplied PythonQt.
See the installed GetGo README for this entry's defaults, limits and outputs.
"""

from typing import Any


def main() -> Any:
    """Launch this installed lesson once and retain its report window."""
    from fontlab_python_lessons.getgo import launch

    return launch('outline_pens')


if __name__ == "__main__":
    main()
