---
this_file: src_docs/md/current/widgets/script-palette-roles.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Script Palette Roles

What: Inspect the live FontLab theme palette for script-panel colours.
How: Read this panel's own palette on Refresh. List all twenty colour roles
for Active, Inactive and Disabled, plus six text/background contrast pairs.
A role missing by name is listed as unavailable; its contrast pairs are omitted.
Why: Role-based colours follow the host theme. Fixed hexadecimal themes do not.
Usage: Refresh after a theme change. Copy the report for diagnosis, or copy the
code below into a panel method. The code reads roles from that panel's palette.
Benefit: Choose readable script colours without changing FontLab preferences.
Contrast composites foreground alpha over opaque backgrounds. A translucent
background has no single ratio and is reported explicitly. Ratios describe
palette values; widget styles can render differently.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only panel.
Independent rewrite of the Qt Styles and Style Sheet example ideas
(Riverbank Computing, Nokia). Based on the author's own FontLab sample,
Apache-2.0. Idea only; no upstream code or assets included.

Run **Widgets > Script Palette Roles** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/746ece8fb2074b3890325d357936d5c2e281646fa3bb889b0038f18d7f25da64.py)
<!--/codeinclude-->
