---
this_file: src_docs/md/current/text/font-handoff-letter.md
tags: ["Text"]
categories: ["Text"]
---

# Font Handoff Letter

What: Prepare a font handoff letter with a complete glyph-name inventory.

How: Prefill the family and version from the current font. Combine your review
instructions with the current font's glyph names in an HTML letter.

Why: A precise review scope helps the recipient return useful corrections.

Usage: Check the project, enter a recipient and instructions, then select Build.
Use Copy for plain text or Export New for a complete UTF-8 HTML document.

Benefit: Send clear review instructions without changing font data.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.

Run **Text > Font Handoff Letter** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `69daf90c33896c7b030642c067eb18999584d36c790d9abf52aa7dd2ba57ee61`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Text/Font%20Handoff%20Letter.py)
