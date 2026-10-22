---
this_file: src_docs/md/current/getgo-fonts/getgo-audit-a-real-font.md
tags: ["GetGo Fonts"]
categories: ["GetGo Fonts"]
---

# GetGo - Audit a Real Font

GetGo - Audit a Real Font: run the packaged lesson on verified owned GetGo copies.

Setup: Install fontlab-python-lessons with its packaged GetGo fonts and the
matching Fly/App reports API in FontLab 9 Python 3.11. Pen/export entries also
need the fonttools extra. Mutation lessons require a dedicated no-document
session. Source fonts remain unchanged; owned temporary copies close in finally.

Run: Choose Scripts > GetGo Fonts > GetGo - Audit a Real Font.
Result: A detached, nonmodal read-only report shows the source and computed
values; exports also retain a new geometry subset at the reported path.
Compatibility: Uses FontLab's supplied PythonQt.
See the installed GetGo README for this entry's defaults, limits and outputs.

Run **GetGo Fonts > GetGo - Audit a Real Font** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/cad7eeef1119a1c0a3ea924c29bb26b6a87b62b189c287ee1b1891ec68c8d743.py)
<!--/codeinclude-->
