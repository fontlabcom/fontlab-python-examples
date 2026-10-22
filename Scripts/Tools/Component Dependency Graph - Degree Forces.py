# this_file: Scripts/Tools/Component Dependency Graph - Degree Forces.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect complete current-master component dependencies in a moving local graph.

Purpose:
    Retain the complete part3 elastic-node lesson as a FontLab dependency view.
Setup:
    FontLab 9, Python 3.11, Fly and App>=0.2.83.dev0. Install matching
    prerequisites yourself; this script installs nothing.
Run:
    Refresh captures all current-font glyphs in font order, including unencoded
    and isolated glyphs. Repeated, cyclic and missing component references remain.
    Hover nodes for exact names; inspect directed glyph → base lines below.
    Select Original Nine-node Graph for the preserved fixed graph and controls.
    Drag nodes, use arrow keys for the centre node, Space and Enter to shuffle.
    Plus/Minus and the wheel zoom with the original part3 policy.
    Stop Motion stops the simulation. Finish a drag before Refresh or Close.
Result:
    The degree-weighted 40ms double-arrow scene is local and changes no font data.
    Captured references are a snapshot; Refresh after font/master changes.
Compatibility:
    No original helper/body is executed.
    Historical source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/elasticnodes-fff97a435b73d548.py
"""
# historical source sha256: fa1dc74f37f29a33afd673b5e4a399838797d8cc355079d512769ec6d10e6a99


def main() -> None:
    """Launch this complete graph profile through the lazy public Fly namespace."""
    from fly.ap.component_graph import show_official

    show_official()


if __name__ == "__main__":
    main()
