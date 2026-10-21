---
this_file: src_docs/md/current/dialogs/proof-text-coverage-dialog.md
tags: ["Dialogs"]
categories: ["Dialogs"]
---

# Proof Text Coverage Dialog

Check proof text against current-font Unicode assignments.

Setup: Use FontLab 9 with Python 3.11, Fly and fontlabapp.
Click Enter Proof Text to open a modeless standard input dialog. Accept to inspect coverage; Cancel keeps the existing draft. Preview reads the current font again. Duplicate assignments remain visible.
Why: Use a modeless text dialog and normalize Qt UTF-16 text.
Benefit: Find missing characters and ambiguous assignments before proofing.
All windows are modeless. Preview text can be selected and copied with Cmd+C.
Each Preview captures fresh input; results are observations, not a live monitor.
No font, selection, preferences, clipboard or history writer is called.
The App Names panel owns signals, Escape and Close. UI imports are lazy.

Independent behaviour rewrite of the Qt/Riverbank standarddialogs dialog family.
Original idea: Qt examples / Riverbank Computing Limited; Nokia Corporation.
Archived replacements: Apache-2.0 owner grant. Upstream BSD headers and
collection GPL metadata have unresolved scope. No upstream code or assets copied.
The two archived variants consolidate into this FontLab-specific workflow;
original sample controls are not a claim of feature parity. Native acceptance pending.
Source: rescued/part2/ports/dialogs/pyqt-official/standarddialogs-e1a0a829f8f2e311.py
SHA256: 4a705367140cd7600706cf7ab7522523ddc7c5cd3592309c78d316b67cfc0055
Source: rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/standarddialogs-e1a0a829f8f2e311.py
SHA256: 80b66bcc88b46955f88d0b31040a2ea4cdf272aa6de1f825c9ff189abf21af22

Run **Dialogs > Proof Text Coverage Dialog** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/be0b9488ebf9a546113ecd64a95d3a5a584d8cf955a6f24a50296f878cc6c0df.py)
<!--/codeinclude-->
