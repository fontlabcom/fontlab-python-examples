---
this_file: src_docs/md/current/models/glyph-sorting-and-filtering-with-dates.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Sorting and Filtering with Dates

Sort and filter a complete real-font glyph metadata snapshot.

Purpose: Adapt the complete part2 custom source/proxy model lesson to
current-font glyph names, all Unicode assignments and local modification dates.
Setup: FontLab9 Python3.11, fontlab-fly and App>=0.2.54.dev0.
Run: Open a font, then run this Models command. Both read-only views share one
captured model. Enter a regular expression, wildcard or fixed string. Toggle
filter and sorting case independently; click a result header to sort.
Custom matches either name or Unicode. Enable Limit dates for inclusive From/To days. The disabled column selector documents the original ignored control.
Result: Inspect matching real glyph metadata without editing a font, changing
selection or touching preferences/Output. Refresh replaces the complete capture;
missing, unreadable, changed or expired reads clear both views and diagnose.
Close releases models, controls, captured data and callbacks.
Compatibility: Uses FontLab's supplied PythonQt. This replaces one preserved-source dispatcher; the
original remains external and is never executed by this adaptation.

Historical source: rescued/part2/ports/itemviews/pyqt-official/customsortfiltermodel-029ea0dabe87ae57.py
The generic UI and query policy live in App. The part3 official versions have
different contracts and remain separate entries. Custom date filtering
starts unrestricted rather than limiting real fonts to demonstration-only2026.

Run **Models > Glyph Sorting and Filtering with Dates** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/dcd71d55cd5b386fec96d0c0be81b3c696e5b76c0042092128ee4c472210f2d9.py)
<!--/codeinclude-->
