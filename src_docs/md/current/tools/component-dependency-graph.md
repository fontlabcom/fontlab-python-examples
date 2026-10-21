---
this_file: src_docs/md/current/tools/component-dependency-graph.md
tags: ["Tools"]
categories: ["Tools"]
---

# Component Dependency Graph

Inspect complete current-master component dependencies in a moving local graph.

Purpose:
    Retain the complete part2 elastic-node lesson as a FontLab dependency view.
Setup:
    FontLab 9, Python 3.11, Fly and App>=0.2.83.dev0. Install matching
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

Run **Tools > Component Dependency Graph** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/2cb374326cd8aecdb04db8c60a6f3e386b3538790e42518621f9a1090ecc6053.py)
<!--/codeinclude-->
