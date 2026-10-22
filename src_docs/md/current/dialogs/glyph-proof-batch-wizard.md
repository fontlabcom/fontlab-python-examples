---
this_file: src_docs/md/current/dialogs/glyph-proof-batch-wizard.md
tags: ["Dialogs"]
categories: ["Dialogs"]
---

# Glyph Proof Batch Wizard

Build slash-escaped proof lines from current-font glyph names.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Choose a prefix and a line size, or paste JSON from Glyph Batch Recipe Settings. Use Next to review proof batches. Copy the result into a FontLab text workflow. Back retains your settings. The tool does not open tabs or change selection.
Why: Validate pasted recipes against a fresh font snapshot.
Benefit: Turn the settings recipe into reproducible proof lines without font edits.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank trivialwizard dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
Archived replacements: Apache-2.0, own earlier work. Upstream BSD headers and
collection GPL metadata have unresolved scope. No upstream code or assets copied.
The two archived variants consolidate into this FontLab-specific workflow;
original sample controls are not a claim of feature parity. Native acceptance pending.
Historical source: rescued/part2/ports/dialogs/pyqt-official/trivialwizard-c0d4a173b261a3e5.py
SHA256: 9c74350f548bafb26b39fab1126681762dc20b334036595203ec5126893c96ac
Historical source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/trivialwizard-c0d4a173b261a3e5.py
SHA256: 8ad810ecf2897a079286ed7b7ede6a2259c30c0fe7e6b90dc4141af0912103b5

Run **Dialogs > Glyph Proof Batch Wizard** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0a1cfd94073b4a026e2b6faa1afcd910c2baf0ea7b32044eb1f52794bb0ec2a1.py)
<!--/codeinclude-->
