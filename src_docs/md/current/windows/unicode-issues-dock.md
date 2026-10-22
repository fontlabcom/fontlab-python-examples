---
this_file: src_docs/md/current/windows/unicode-issues-dock.md
tags: ["Windows"]
categories: ["Windows"]
---

# Unicode Issues Dock

What: Find unencoded glyphs and glyphs that share a Unicode in the current font.
How: Read the public glyph catalogue. Count owners of each Unicode scalar, then
filter and page only the issue rows. Double-click uses App scripting.select_glyphs;
its Font-window guard refuses a Glyph window or a changed current font (fl#8528).
Why: Keep an actionable Unicode checklist beside the Font window.
Usage: Activate the Font window, run this script, and double-click an issue row.
Type a name, issue or U+ value to filter. Refresh reads the current font again.
If the status line asks for the Font window, click it and double-click the row again.
The default dock area is right. show(..., area="left") chooses the left area;
top and bottom are also valid. Drag the dock title to float it or dock it again.
App widgets.create_panel floats the registered dock automatically when FontLab's
macOS multi-window profile hides MainWindow. No separate main window is created.
Close or the dock X calls handle.close_owned(): disconnect callbacks first, then
OwnedWidget.close() removes the dock and schedules its widget for deletion.
Benefit: Select the exact glyph that needs an encoding decision, without changing
its Unicode values or geometry. Counts cover every issue, even on other pages.
Setup: FontLab 9, Python 3.11, Fly and App with widgets, scripting, glyph_catalog,
draft_signals and qt_properties.
Independent rewrite of the Qt dockwidgets, menus, separations, basiclayouts and
borderlayout example ideas (Qt/Nokia, Riverbank). Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.

Historical source: rescued/part3/pyqt-official-ports/ports/layouts/pyqt-official/basiclayouts-2f94fe07de765888.py
SHA256: b53b4e5e158d8046220bde8de76c0af424ab90c8a96e362f29906349a5a19d35
Historical source: rescued/part3/pyqt-official-ports/ports/layouts/pyqt-official/borderlayout-f48955d43ed6196c.py
SHA256: 658638cfc0891ae0a6ffabb4024cbe2aa63bec688958a28cfa46da47df90fd37
Historical source: rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/dockwidgets-4efac54bae01fc62.py
SHA256: b14d351359ef448ca38eba7a8fcf66dbdf162dbd45f63f00718ac50096000cff
Historical source: rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py
SHA256: 95fe3a5c2f8bb6eb3528403bcc0433ffac2550cc8cdbab52deaff372f17c4deb
Historical source: rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py
SHA256: f5e1af92ebcf6d666477dc2b3f6d85cd324bc39ea1940982913b60b15c7285c6
Historical source: rescued/part2/ports/layouts/pyqt-official/basiclayouts-2f94fe07de765888.py
SHA256: 6fa0e1268b7c81dbf6c373ae9ebb98ef86ffa0d7c8207ab78a003e65fc49a00d
Historical source: rescued/part2/ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py
SHA256: 5db7de5bb81c11df39be0c6e83c9a39d1f42463982413e62eb27253f0efb58a6
Historical source: rescued/part2/ports/layouts/pyqt-official/borderlayout-f48955d43ed6196c.py
SHA256: 61dce583b8707e5724dc6e28f4f86b2b32884dd9af5f4a25a3a145a54d146dd4
Historical source: rescued/part2/ports/mainwindows/pyqt-official/dockwidgets-4efac54bae01fc62.py
SHA256: 20ab7a5fd5b64e7c3b0cf66bfb80fbca9f8301317b314bb95e66d76b4475fc8d
Historical source: rescued/part2/ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py
SHA256: fedecc268d265622812e43e61b3d80d9c4dbbb812411cc177a2f37d58ad1b039

Run **Windows > Unicode Issues Dock** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/512683abd58e65c361c62336ca3548c19dc63e495a05713b49737cb2aba8097c.py)
<!--/codeinclude-->
