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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/8350dc77bee604e7bbacf96ebb55e20a00ee1843a5864ffe2fcd308b47f13cb6.py)
<!--/codeinclude-->
