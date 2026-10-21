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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/f176204a0e09067557f0da46c651f0e882f5492799def7eba75e79bbc1a132aa.py)
<!--/codeinclude-->
