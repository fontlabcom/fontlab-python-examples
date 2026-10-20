---
this_file: src_docs/md/current/tools/component-dependency-graph-degree-forces.md
tags: ["Tools"]
categories: ["Tools"]
---

# Component Dependency Graph - Degree Forces

Inspect complete current-master component dependencies in a moving local graph.

Purpose:
    Retain the complete part3 elastic-node lesson as a FontLab dependency view.
Setup:
    FontLab 9, Python 3.11, Fly and reviewed App>=0.2.83.dev0. Install matching
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
    Native PythonQt virtuals, painting and complete font/cache/history/dirty/
    reopen preservation remain pending. No original helper/body is executed.
    Preserved source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/elasticnodes-fff97a435b73d548.py

Run **Tools > Component Dependency Graph - Degree Forces** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4f6bd173fbb68426700b8f41a6693cf33c9ce6c7e9fd0fadd820feb915a6c900.py)
<!--/codeinclude-->
