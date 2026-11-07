---
this_file: src_docs/md/current/widgets/font-units-calculator.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Font Units Calculator

What: Calculate font-unit values and their em and point equivalents.
How: Read the current font UPM on each Calculate. Apply one explicit operation.
Why: Keep unit arithmetic separate from stored glyph metrics.
Usage: Enter A, an operation and B. Set the proof size in points. Calculate,
then select and copy the result. No expression evaluation or font writes.
Benefit: Transfer measured values into spacing and proof-size decisions.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Calculator example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.

Run **Widgets > Font Units Calculator** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `595ee84ca7920e5a72b5dbc5120eb2d9ff4d83b5f99363f8a8345e98b29284f1`

[Python source at `1505ea0b53c6`](https://github.com/fontlabcom/fontlab-python-examples/blob/1505ea0b53c62938e842d3b039f4fadf2632a842/Scripts/Widgets/Font%20Units%20Calculator.py)
