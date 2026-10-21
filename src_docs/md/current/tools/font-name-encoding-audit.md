---
this_file: src_docs/md/current/tools/font-name-encoding-audit.md
tags: ["Tools"]
categories: ["Tools"]
---

# Font Name Encoding Audit

What: Audit current-master naming and credit fields for legacy encoding support.
How: Read the package fields and master twice. Test ASCII, Windows-1252 and
Mac Roman; include a UTF-16-BE byte dump. Report each unencodable code point.
PostScript font names are ASCII-required. Only the current master is read.
Why: Silent replacement characters damage legacy name-table exports.
Usage: Open a font, Refresh Current Font, inspect the JSON and Export New.
Benefit: Give font build scripts a reproducible encoding report.
The fields are source metadata, not the compiled binary name table.

Setup: FontLab 9, Python 3.11, Fly and App draft_signals/qt_properties.
Modeless panel; font data, selection and application preferences stay unchanged.

Independent rewrite of the Qt codecs example idea (Qt/Riverbank Computing;
Nokia Corporation). Based on the author's own FontLab sample, Apache-2.0.
Source: rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/codecs-19571722ed96aa9c.py
SHA256: c39fb1bab6762e4b2286af604794547e07de9f5a680b4c671e7882c9a6ac9470
Source: rescued/part2/ports/tools/pyqt-official/codecs-19571722ed96aa9c.py
SHA256: fe2257ea8123a18e3995ca919937fd16a02845c939d2ea695fd99cea327cd3a9

Run **Tools > Font Name Encoding Audit** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5ce1bac9d91fe74cb9c526f36cd334a9a171cb5cdbd4a30001cb5a19e5c25d37.py)
<!--/codeinclude-->
