---
this_file: src_docs/md/current/models/glyph-filter-model-with-local-dates.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Filter Model with Local Dates

Inspect and filter whole-font glyph metadata with typed Qt dates.

Purpose: Adapt the complete part3 official basic source/proxy model lesson.
Show every glyph name, all Unicode assignments and local modification datetimes.
Both read-only views share one captured model with native QDateTime cells.
Original profile setup: FontLab9 Python3.11, fontlab-fly and App>=0.2.55.dev0.
Run: Open a font and run this Models command. Use regular expressions, wildcards
or fixed strings, and click result headers to sort.
Choose a filter column. Date matching uses the displayed default-locale short datetime, not the ISO capture string. Filter and sorting case switches stay independent.
Result: Complete captured glyph metadata replaces the demonstration mail data.
Refresh reads the current font again. Empty, stale, unreadable or expired reads
clear both views and diagnose; cells never edit the font. Close releases models,
virtual callbacks, captured data and signals. No selection/history/preferences
or Output writer is called.
Compatibility: Uses FontLab's supplied PythonQt. This replaces one preserved-source dispatcher; its original bytes
remain external and are never executed by this adaptation.

Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/basicsortfiltermodel-9dab02b61cebbdb7.py
The two part2 workflows retain their separate Python matching/string-date rules.
Demo-specific text and2006/2007date defaults become a complete font snapshot with
empty initial pattern and optional observed date limits. Shared policy lives in App.


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Model Filtering Lab; opens the Glyph Filter Model with Local Dates profile.

Run **Models > Glyph Filter Model with Local Dates** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `0999fad4aa3303a929ff55084b69a831877905e347661a272f0c48117347bbbb`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Models/Glyph%20Filter%20Model%20with%20Local%20Dates.py)
