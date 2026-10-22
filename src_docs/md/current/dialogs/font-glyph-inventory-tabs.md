---
this_file: src_docs/md/current/dialogs/font-glyph-inventory-tabs.md
tags: ["Dialogs"]
categories: ["Dialogs"]
---

# Font Glyph Inventory Tabs

Inspect glyph counts, names and Unicode assignments in three tabs.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Click Preview after font changes. General gives exact counts, Names keeps font order, and Unicode groups all assigned glyph names. Select and copy text from any tab.
Why: Separate summary, names and Unicode into read-only tabs.
Benefit: Copy a complete font inventory without changing glyph metadata.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank tabdialog dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
The author supplies these first-party samples under Apache-2.0.
The Qt examples carry BSD headers and collection-level GPL metadata.
No code, helper or asset from these examples is included.
The two archived variants consolidate into this FontLab-specific workflow.
Historical source: rescued/part2/ports/dialogs/pyqt-official/tabdialog-dab5fd4c94ec518d.py
SHA256: f0429bb770550780ba27dd2def628e0189a5665595501f32dfb1ebf9ef98c7c0
Historical source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/tabdialog-dab5fd4c94ec518d.py
SHA256: 6fd6f74eddf5d3579fc8b46e70fab7de6444cd70d41a2776c1ca437b345fc2bf

Run **Dialogs > Font Glyph Inventory Tabs** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/797162a922d56b56cf76d3e53c69b43cee37d361fa68462a189a7bb0be437c7d.py)
<!--/codeinclude-->
