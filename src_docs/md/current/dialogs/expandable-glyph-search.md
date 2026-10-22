---
this_file: src_docs/md/current/dialogs/expandable-glyph-search.md
tags: ["Dialogs"]
categories: ["Dialogs"]
---

# Expandable Glyph Search

Find glyph names with optional exact and case matching.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Enter text, expand More Options if required, then click Preview. Results use fresh current-font names. Reverse changes result order only; no glyph is selected.
Why: Hide optional literal-match controls until they are needed.
Benefit: Inspect exact glyph names without changing the Font window selection.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank extension dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
The author supplies these first-party samples under Apache-2.0.
The Qt examples carry BSD headers and collection-level GPL metadata.
No code, helper or asset from these examples is included.
The two archived variants consolidate into this FontLab-specific workflow.
Historical source: rescued/part2/ports/dialogs/pyqt-official/extension-a1c26dbf9f995edb.py
SHA256: 96175cf7e19bcd1dc4f2e6664890436df05a791d47b8442411bd35bb3d32df32
Historical source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/extension-a1c26dbf9f995edb.py
SHA256: d662938fecf32e30d708c02bafce2e7468461be547ab33fd41c6405a6e4f94d9

Run **Dialogs > Expandable Glyph Search** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9a4ff1b05f30320005c281b7010b9171ba48c3c70e763b1f779480d4714e6268.py)
<!--/codeinclude-->
