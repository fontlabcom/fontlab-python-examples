---
this_file: src_docs/md/current/dialogs/fontlab-script-scaffold-wizard.md
tags: ["Dialogs"]
categories: ["Dialogs"]
---

# FontLab Script Scaffold Wizard

Generate a small Python class which reads the current font.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Choose a class name and a title. Use Next to inspect valid Python source. Copy text from the preview into your own script; this tool writes no file.
Why: Generate code as text and quote user titles as data.
Benefit: Start a runnable font-reading script without editing a live font.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank classwizard dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
Archived replacements: Apache-2.0, own earlier work. Upstream BSD headers and
collection GPL metadata have unresolved scope. No upstream code or assets copied.
The two archived variants consolidate into this FontLab-specific workflow;
original sample controls are not a claim of feature parity. Native acceptance pending.
Historical source: rescued/part2/ports/dialogs/pyqt-official/classwizard-035f3fbd2b81479a.py
SHA256: 1d69f1113b8c0a1eb508ee108639dea5bd114fd384ae132c3dd767efa45909fb
Historical source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/classwizard-035f3fbd2b81479a.py
SHA256: 93b55b89157b47b8676db5ce9e9a64641bf7d6290bc576f2c5af16079beef92d

Run **Dialogs > FontLab Script Scaffold Wizard** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/842606c55822c188b4b8d13191f2482d76e31bf12c8510277a8283114dac06f9.py)
<!--/codeinclude-->
