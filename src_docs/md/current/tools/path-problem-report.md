---
this_file: src_docs/md/current/tools/path-problem-report.md
tags: ["Tools"]
categories: ["Tools"]
---

# Path Problem Report

What: Report contour problems on the current font's current master.
How: Inspect each glyph's contours once. List open contours, closed contours with fewer
than three on-curve nodes, equal adjacent nodes and small node extents.
Why: A combined report gives one repair checklist before overlap removal.
Usage: Open a font. Set the minimum extent, then Refresh. Enter an absolute
new JSON filename and Export to save the complete captured checklist.
Benefit: A build check or another FontLab script can consume the JSON file.

Small extents use node coordinates, including control points, in shape space.
They are a diagnostic heuristic, not exact curve bounds. The report does not
flatten components. Missing master layers are listed separately. No font data
changes. Use Select glyphs with findings after activating the Font window.
Scriptmix Reports > Open Contours is the master-wide variant that selects glyphs.
This tool adds a combined checklist and complete JSON export for build checks.
Scanning runs in small UI-thread steps; Cancel discards the entire unfinished
report. Font, master, glyph order and modification-date changes reject the scan.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Based on the author's own FontLab sample, Apache-2.0.
Sources: recipe.py and path_report.py (Path Problem Report).

Run **Tools > Path Problem Report** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/04fd01b7f682f215bbeaf583651c6ec80aa14d6bed7aa09a8d6c8139ef45c561.py)
<!--/codeinclude-->
