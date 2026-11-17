---
this_file: src_docs/md/current/models/glyph-name-filter.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Name Filter

Filter real glyph names with a Qt list model, then select chosen results.

Open a font and run this script from Models in FontLab's Scripts menu. Enter a
prefix and click Apply Prefix. Choose rows, then click Select Chosen Rows to
change Font window selection. Refresh reads a new font/master/name snapshot.
The panel refuses stale results. It never changes glyph data or preferences.

Install fontlab-python-lessons, fontlab-fly and fontlab-fontlabapp in FontLab's
Python3.11 environment. The package uses fly.ap for shared native access and
owned signal/window cleanup. This keeps the lesson focused on list models.

Run **Models > Glyph Name Filter** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `5dffc5cfb00f5e6c2232a386145ed69c033426a6063a3aad37b2bc335a7c372d`

[Python source at `e8f7809ea85d`](https://github.com/fontlabcom/fontlab-python-examples/blob/e8f7809ea85d8b1725563205d296fb7ebfb55a1b/Scripts/Models/Glyph%20Name%20Filter.py)
