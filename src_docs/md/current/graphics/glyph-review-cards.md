---
this_file: src_docs/md/current/graphics/glyph-review-cards.md
tags: ["Graphics"]
categories: ["Graphics"]
---

# Glyph Review Cards

What: Stage glyph review status and notes on a graphics canvas.
How: Embed one native form per matching glyph. Status and notes stay local.
Why: Review comments need a scratch space beside a font before handoff.
Usage: Enter a prefix that matches at most six names, then Refresh. Set each
status and note. Copy Result transfers the complete report to the clipboard.
Copy before Refresh or Close; Discard and Close explicitly drops local notes.
Benefit: Prepare a named review handoff without altering glyph notes or history.
Notes are plain text. Unsupported Qt text classes are refused during transfer.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless; no font writes.
Independent rewrite of the Qt embeddeddialogs example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.
Source: rescued/part2/ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py
SHA256: c08d4c310c70b3a0e129085b79f59493472859819fdf1c75e7024345724a83bc
Source: rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py
SHA256: b90e385b1cb4ea7f2f202545920844cba59a825fcdf3986878ebd25d3fce1876

Run **Graphics > Glyph Review Cards** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e8a55e253720d1813189b72058561b6193bb7a5013f67daf808f04a66fb583d7.py)
<!--/codeinclude-->
