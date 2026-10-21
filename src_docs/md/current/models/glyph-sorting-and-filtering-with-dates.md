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
Compatibility: Native PythonQt callbacks, real metadata/getter/cache/history and
complete persistence/UI acceptance remain pending. Standalone Qt tests do not
qualify the FontLab host. This replaces one preserved-source dispatcher; the
original remains external and is never executed by this adaptation.

Original: rescued/part2/ports/itemviews/pyqt-official/customsortfiltermodel-029ea0dabe87ae57.py
The generic UI and query policy live in App. The part3 official versions have
different contracts and remain separate pending entries. Custom date filtering
starts unrestricted rather than limiting real fonts to demonstration-only2026.

Run **Models > Glyph Sorting and Filtering with Dates** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/87bb3fa1f47a0a80ad217ac9e3047c05e2eb11100b23ef714f1278b4b6ec5e14.py)
<!--/codeinclude-->
