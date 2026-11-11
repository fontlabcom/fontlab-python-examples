---
this_file: src_docs/md/current/tools/font-info-snapshot.md
tags: ["Tools"]
categories: ["Tools"]
---

# Font Info Snapshot

What: Save and compare current-master naming and credit settings as JSON.
How: Capture package naming, version, PostScript and credit text. Export a versioned
snapshot. Load a previous snapshot and compare it against fresh current data.
Why: Explicit files make name-setting changes visible across font revisions.
Usage: Refresh and Export New to save. Enter a saved snapshot's absolute path
and Compare Saved to inspect each changed field. No settings are applied.
Benefit: Reuse the saved JSON in this tool or a font build check.
Only the current master is read. Comparisons across masters are refused.
This naming snapshot is not a whole-font backup. UTF-8 BOM and CR line endings
are detected from input bytes; only actual conversions are reported.

Setup: FontLab 9, Python 3.11, Fly and App draft_signals/qt_properties.
Modeless panel; font data, selection and application preferences stay unchanged.

Independent rewrite of the Qt settingseditor example idea (Qt/Riverbank Computing;
Nokia Corporation). Based on the author's own FontLab sample, Apache-2.0.
Historical source: rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/settingseditor-9e41e71c41b116a8.py
SHA256: 1a35d9d5b3989ba7728ce129fea1bcc98cce4b221f59cf8916788ffe0ab53475
Historical source: rescued/part2/ports/tools/pyqt-official/settingseditor-9e41e71c41b116a8.py
SHA256: 1433012d1ff11a45c6414df8c625c99fc9e17cd93a91d7bc4e518ebfac5dd890

Run **Tools > Font Info Snapshot** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `5cabadec4f590122e5e6f37b332e2f28cd3f812b809721861ce3ea9dfc0f869e`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Tools/Font%20Info%20Snapshot.py)
