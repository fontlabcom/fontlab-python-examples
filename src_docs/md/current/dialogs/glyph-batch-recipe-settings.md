---
this_file: src_docs/md/current/dialogs/glyph-batch-recipe-settings.md
tags: ["Dialogs"]
categories: ["Dialogs"]
---

# Glyph Batch Recipe Settings

Draft a JSON recipe from real glyph names.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Choose a prefix and a batch size on the settings pages. Preview captures the current font and builds a complete JSON recipe. Paste the JSON into Glyph Proof Batch Wizard to generate proof lines. No preferences are saved.
Why: Keep batch settings local and export an explicit glyph list.
Benefit: Reuse the recipe in Glyph Proof Batch Wizard without retyping settings.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank configdialog dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
The author supplies these first-party samples under Apache-2.0.
The Qt examples carry BSD headers and collection-level GPL metadata.
No code, helper or asset from these examples is included.
The two archived variants consolidate into this FontLab-specific workflow.
Historical source: rescued/part2/ports/dialogs/pyqt-official/configdialog-3f5f77c0358d9fef.py
SHA256: a8723ff0df166a67c564237dbf0c11dfe87d4f649b2769c2de409efc1508c33f
Historical source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/configdialog-3f5f77c0358d9fef.py
SHA256: 5ddbb490939e6e767b7603a197b0ec14019611ff4447c04fff97293593cb571d

Run **Dialogs > Glyph Batch Recipe Settings** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4c813f2fe58c3efd6ba797ff205fe4433a94c8f7f969dcebf94477cd5ad6dae1.py)
<!--/codeinclude-->
