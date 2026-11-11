---
this_file: src_docs/md/current/drag-and-drop/font-file-drop-shelf.md
tags: ["Drag And Drop"]
categories: ["Drag And Drop"]
---

# Font File Drop Shelf

Collect font files and open selected entries in FontLab.

Drop local fonts or UFO folders, or enter an absolute path and choose Use input.
Select rows and choose Open in FontLab, or drag their file URLs to another window.
Copy output copies all staged paths for scripts. Clear empties the shelf.
The whole selection is checked before opening starts. A failed open stops the
batch and reports which files already opened. File contents are never changed.
No current font is required. Save repeated trips through the file dialog.
Opening relies on FontLab's own format support.
Requires FontLab 9, Python 3.11, Fly and native font-opening support.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).


Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Consolidated in Labs > Drag Drop Lab; opens the Font File Drop Shelf profile.

Run **Drag And Drop > Font File Drop Shelf** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `909a5643b8c1536ddeb4463051c11a426a4ea68ac8d48c078fc14289aff82370`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Drag%20And%20Drop/Font%20File%20Drop%20Shelf.py)
