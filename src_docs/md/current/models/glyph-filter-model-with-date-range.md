---
this_file: src_docs/md/current/models/glyph-filter-model-with-date-range.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Filter Model with Date Range

Inspect and filter whole-font glyph metadata with typed Qt dates.

Purpose: Adapt the complete part3 official custom source/proxy model lesson.
Show every glyph name, all Unicode assignments and local modification datetimes.
Both read-only views share one captured model with native QDateTime cells.
Original profile setup: FontLab9 Python3.11, fontlab-fly and App>=0.2.55.dev0.
Run: Open a font and run this Models command. Use regular expressions, wildcards
or fixed strings, and click result headers to sort.
Match either name or Unicode with Qt QRegExp, then optionally limit inclusive calendar days. Text sorting stays case-sensitive; email-shaped values use the original extracted-token comparator.
Result: Complete captured glyph metadata replaces the demonstration mail data.
Refresh reads the current font again. Empty, stale, unreadable or expired reads
clear both views and diagnose; cells never edit the font. Close releases models,
virtual callbacks, captured data and signals. No selection/history/preferences
or Output writer is called.
Compatibility: Uses FontLab's supplied PythonQt. This replaces one preserved-source dispatcher; its original bytes
remain external and are never executed by this adaptation.

Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/customsortfiltermodel-029ea0dabe87ae57.py
The two part2 workflows retain their separate Python matching/string-date rules.
Demo-specific text and2006/2007date defaults become a complete font snapshot with
empty initial pattern and optional observed date limits. Shared policy lives in App.


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Model Filtering Lab; opens the Glyph Filter Model with Date Range profile.

Run **Models > Glyph Filter Model with Date Range** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `47eba445887f407fdff60be3567b23324316a5a7888d79e6d60f912dc1530073`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Models/Glyph%20Filter%20Model%20with%20Date%20Range.py)
