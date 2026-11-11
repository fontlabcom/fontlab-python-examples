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

Original profile setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only tool.
App owns panel lifetime, signals and completion.
Independent rewrite of the Qt Calculator example idea (Riverbank Computing, Nokia).
Based on the author's own FontLab sample, Apache-2.0.
Idea only; no upstream code or assets included.


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Metrics Controls Lab; opens the Font Units Calculator profile.

Run **Widgets > Font Units Calculator** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `3d0c7a743500581ad54a5023415c44426134e7e3a00c5a582af2f069cfb98034`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Widgets/Font%20Units%20Calculator.py)
