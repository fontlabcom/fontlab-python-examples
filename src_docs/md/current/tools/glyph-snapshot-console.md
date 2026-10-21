---
this_file: src_docs/md/current/tools/glyph-snapshot-console.md
tags: ["Tools"]
categories: ["Tools"]
---

# Glyph Snapshot Console

Query current-font name, Unicode and modification data with trusted Python.

What: Evaluate short expressions or statements on detached glyph records.
How: Capture once on the UI thread with a glyph-count-scaled deadline and a
Scanning label (at most 120 seconds). Build the namespace once. No worker or conversion timer is used.
Why: Test report expressions without giving the query namespace native handles.
Usage: Capture, enter Python, then Run or press Return. For example,
[g['name'] for g in glyphs if not g['unicode']]. The unicode field is a string
such as "U+0041 U+00C1"; modified is "yyyy-MM-dd HH:mm:ss", or empty if unset.
Select output and copy to a script or report. Capture resets local variables.
Choose the query deadline: 5 seconds by default, at most 60 seconds. A Python
trace guard stops Python loops and restores the earlier host trace. A loop in
native code without Python line events cannot be stopped by this guard.
Code that catches every exception can outlive the time limit.
Benefit: Experiment with real glyph data and keep complete query results.
This runs trusted code in the host process, not a security sandbox. User code
can change detached data. The panel itself calls no font writer.
Setup: FontLab 9, Python 3.11, Fly and App glyph_catalog/draft_signals/scripting.
Independent rewrite of timer-batch and owned-repl.
Based on the author's own FontLab sample, Apache-2.0.
No original source body is redistributed.

Run **Tools > Glyph Snapshot Console** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0c19f3a5ea7d6a42f1d48709c90b095c27ad5787a321238381dd3100250259d7.py)
<!--/codeinclude-->
