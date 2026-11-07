---
this_file: src_docs/md/current/text/script-snippet-notebook.md
tags: ["Text"]
categories: ["Text"]
---

# Script Snippet Notebook

What: Keep named FontLab scripting snippets in a local notebook.

How: Store code as text. Search, browse, edit or remove named records. JSON
stores the collection. Snippet export saves one record as a Python file.

Why: A text notebook keeps reusable code available without executing it.

Usage: Enter a title and code. Select Add or Replace before navigation. Use
Cancel Draft to restore the current record. Load JSON reads a collection.
Export New saves JSON. Export Snippet saves the current record. Copy copies it.

Benefit: Reuse scripting knowledge while keeping the current font unchanged.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.

Run **Text > Script Snippet Notebook** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `b961e496593e17b0fa7dcb17e1af2efbeb7e7814f9635d4570378c6ad1068fac`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Text/Script%20Snippet%20Notebook.py)
