---
this_file: src_docs/md/current/tools/editable-glyph-outline.md
tags: ["Tools"]
categories: ["Tools"]
---

# Editable Glyph Outline

Edit a complete local glyph-metadata tree.

Purpose: Adapt the complete distinct part2 editable-tree workflow to FontLab.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.66.dev0.
Run: Open a font and run this Tools command. Edit local cells, rows and columns.
Result: Explore every glyph, Unicode assignment and local modification date.
Part2 adds siblings before the selection, appends children/columns and keeps
one final column. Part3 adds siblings after it and children first, inserts
columns beside it, and retains all original Ctrl+I/R chord and Ctrl+N/Q keys.
Design: Shared App tree/model/view mechanics retain persistent cells, expanded
rows and separate original menu/selection/status policies. All edits are local.
Refresh keeps edited drafts; Reset Draft explicitly reloads the current font.
Capture/setup failures retain the old draft. Failed disconnections keep exact
owners and refuse deletion for Close retry; terminal faults use window Close.
Close releases owned views, models, selection and callbacks. No original is run.
Compatibility: Actual installed PythonQt/font/cache/history/dirty/save/reopen
acceptance remains pending. No font, selection, preference, file or Output
writer is used. Original source/resources are archived outside this repository and unbundled.
Historical source: rescued/part2/ports/itemviews/pyqt-official/editabletreemodel-227efef76ed4ac74.py

Run **Tools > Editable Glyph Outline** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d7e150f4ea743b1f18ad39de8df5d28e06166a9ad871e77ede2d2fa719e66260.py)
<!--/codeinclude-->
