# this_file: Scripts/Tools/Component Dependency Graph.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect complete current-master component dependencies in a moving local graph.

Purpose:
    Retain the complete part2 elastic-node lesson as a FontLab dependency view.
Setup:
    FontLab 9, Python 3.11, Fly and reviewed App>=0.2.83.dev0. Install matching
    prerequisites yourself; this script installs nothing.
Run:
    Refresh captures all current-font glyphs in font order, including unencoded
    and isolated glyphs. Repeated, cyclic and missing component references remain.
    Hover nodes for exact names; inspect directed glyph → base lines below.
    Select Original Nine-node Graph for the preserved fixed graph and controls.
    Drag nodes, use arrow keys for the centre node, Space and Return to shuffle.
    Plus/Minus and Equal and the wheel zoom with the original part2 policy.
    Stop Motion stops the simulation. Finish a drag before Refresh or Close.
Result:
    The clipped-force 30ms single-arrow scene is local and changes no font data.
    Captured references are a snapshot; Refresh after font/master changes.
Compatibility:
    Native PythonQt virtuals, painting and complete font/cache/history/dirty/
    reopen preservation remain pending. No original helper/body is executed.
    Preserved source: rescued/part2/ports/graphicsview/pyqt-official/elasticnodes-fff97a435b73d548.py
"""
# preserved-source-sha256: d65729560a7b649d21bcffcd176aaba7541920cc427548c6e17c1269c70d6bef


def main() -> None:
    """Launch this complete graph profile through the lazy public Fly namespace."""
    from fly.ap.component_graph import show

    show()


if __name__ == "__main__":
    main()
