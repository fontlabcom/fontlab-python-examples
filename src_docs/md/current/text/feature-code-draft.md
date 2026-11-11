---
this_file: src_docs/md/current/text/feature-code-draft.md
tags: ["Text"]
categories: ["Text"]
---

# Feature Code Draft

What: Edit a local OpenType feature-code draft with syntax colour.

How: Mark keywords, quoted strings and comments. Keep all edits in the text
editor. Colour gives lexical guidance; it does not compile the feature code.

Why: Experimental code needs a separate workspace before use in a font.

Usage: Edit text or Load a UTF-8 file. Insert Names adds current-font glyph
names as a comment. Copy or Export New transfers the draft for further use.

Benefit: Prepare feature code beside the font without changing its features.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.

Run **Text > Feature Code Draft** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `a6adcf63cc5c607328e86b5c257570bb262ec3a20045559a08229b765b0c1697`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Text/Feature%20Code%20Draft.py)
