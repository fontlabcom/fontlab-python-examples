---
this_file: src_docs/md/current/models/glyph-review-priorities.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Review Priorities

What: Keep a resumable zero-to-five-star review queue for the current font.
How: A painted five-star delegate sets scores by click and edits existing items.
Export JSON retains
the full queue; Import reloads it after checking glyph names, score ranges,
star consistency, duplicate keys and characters that PythonQt can replace.
Why: A portable queue can be resumed without modifying native glyph metadata.
Usage: Open a font and Refresh. Click within a star cell to set its score; Delete clears it.
Export New before closing. To resume, Refresh the matching font and Import an
exported queue. Import accepts UTF-8 BOM and normalizes CRLF or CR to LF.
Benefit: Carry a review across sessions and reject incompatible queues clearly.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Invalid imports keep the visible queue and current scores.

Independent rewrite of the Qt stardelegate example idea. Based on the author's own FontLab sample,
Apache-2.0.
Source: rescued/part2/ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py
SHA256: ab5c5904d2ca3688def0ad17a8a48ac63f507e7a77778a888f14e04a89b0c079
Source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py
SHA256: d11286ceb3e9b813bbda21d1f820c224694722b2b3476c7b19a0791cd6fcc311

Run **Models > Glyph Review Priorities** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/b06651fb1c3b85d494feeb31954a2495d629f17a9cc92498337e131acc23c572.py)
<!--/codeinclude-->
