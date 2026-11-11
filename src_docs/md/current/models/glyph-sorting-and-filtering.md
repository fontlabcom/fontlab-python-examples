---
this_file: src_docs/md/current/models/glyph-sorting-and-filtering.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Sorting and Filtering

Sort and filter a complete real-font glyph metadata snapshot.

Purpose: Adapt the complete part2 basic source/proxy model lesson to
current-font glyph names, all Unicode assignments and local modification dates.
Original profile setup: FontLab9 Python3.11, fontlab-fly and App>=0.2.54.dev0.
Run: Open a font, then run this Models command. Both read-only views share one
captured model. Enter a regular expression, wildcard or fixed string. Toggle
filter and sorting case independently; click a result header to sort.
Choose a filter column: name, Unicode or modification date. Basic retains native Qt QRegExp matching; Custom has different Python matching semantics.
Result: Inspect matching real glyph metadata without editing a font, changing
selection or touching preferences/Output. Refresh replaces the complete capture;
missing, unreadable, changed or expired reads clear both views and diagnose.
Close releases models, controls, captured data and callbacks.
Compatibility: Uses FontLab's supplied PythonQt. This replaces one preserved-source dispatcher; the
original remains external and is never executed by this adaptation.

Historical source: rescued/part2/ports/itemviews/pyqt-official/basicsortfiltermodel-9dab02b61cebbdb7.py
The generic UI and query policy live in App. The part3 official versions have
different contracts and remain separate entries. Custom date filtering
starts unrestricted rather than limiting real fonts to demonstration-only2026.


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Model Filtering Lab; opens the Glyph Sorting and Filtering profile.

Run **Models > Glyph Sorting and Filtering** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `82fe0a046be08762f07dbabdd001147d1bf8d0441fbf8785ccc76ae56063110c`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Models/Glyph%20Sorting%20and%20Filtering.py)
