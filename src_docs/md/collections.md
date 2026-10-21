---
this_file: src_docs/md/collections.md
tags:
- Python
categories:
- Guides
---

# Choose an example collection

The retained catalogue contains 299 entrypoint records. It records 148
implementations and 151 cases blocked by a host capability. These are historical
catalogue states, not the result of this documentation build.

The 18 insight examples explain individual PythonQt idioms. Their source is
included directly on each page. The retained recipes cover everyday font tasks;
the GetGo examples use real font fixtures. Do not run a font-editing example on
the only copy of your work.

## Run code in FontLab

Use FontLab's existing `QApplication` and `PythonQt.QtGui`. Do not create another
application or load PyQt or PySide binaries into FontLab. Read the whole example
and its imports before you run it. The previous `fontlab_python_examples`
launcher is archived; the current checkout does not install that package.

Current migrated menu scripts are documented in
[Scriptmix](https://fontlabcom.github.io/fontlab-python-scriptmix/).
Keep an archived example's resources beside its source when inspecting it.
The archive is retained for migration and recovery; it is not installed by this site.

## Current practical scripts

[Current Scripts](current/index.md) lists every active facade and includes its
actual source. The 79 entries require the matching App, Fly and Lessons
packages. Each entry states its setup, behavior and acceptance limits. A shared
package or facade passing offline tests does not prove native FontLab acceptance.

The 494 historical source identities remain in `rescue-index.json`; the 135
hash-bound adaptations and 51 retirements are recorded in `menu-adaptations.json`. The other 308
identities remain migration backlog. Their original bodies and resources stay
unchanged under the local `rescued/` tree. Archived runtime wrappers are retained
privately for recovery and are no longer advertised as working menu tools.

The matching Lessons package source now lives in the repository's `lessons/`
folder. It includes all sixteen packaged menu entries, the form resource and99
licensed GetGo fonts with provenance. Root documentation dependencies remain
separate from that Python3.11 runtime package. No live FontLab install is changed
by building or verifying either project.
