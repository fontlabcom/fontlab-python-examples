---
this_file: src_docs/md/current/tools/fontlab-qt-slot-reference.md
tags: ["Tools"]
categories: ["Tools"]
---

# FontLab Qt Slot Reference

Read live FontLab widget signals and slots for a scripting reference.

What: Select the main window, the focused widget captured when this panel opens,
or a widget from the main window's direct children. List signals and slots with
signatures, plus fixed PythonQt rules for safe callback wiring.
How: Use direct native accessors. Disable Python GC while converting the one
children list; do not traverse the widget tree or read arbitrary property values.
Read only Qt metadata. If method enumeration is absent, report that limitation
and keep the PythonQt rules visible. No discovered method is invoked.
Why: Inspect the compiled interface before writing a FontLab callback.
Usage: Focus the target widget before running this script. Choose an object,
then Read Reference and copy the JSON. Run again to refresh the object choices.
Destroyed targets are refused. No document is needed and no font is changed.
Benefit: Keep exact signal/slot signatures beside practical PythonQt rules.
A Qt declaration does not prove PythonQt can call every listed overload.
Setup: FontLab 9, Python 3.11, Fly and App draft_signals/qt_properties.
Independent rewrite of compiled-slot-exposure.
Based on the author's own FontLab sample, Apache-2.0.
No original source body is redistributed.

Run **Tools > FontLab Qt Slot Reference** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/544a5d955b2fe05c96a82474c2ab44da4627039d4ccf86ee3758503d1915632a.py)
<!--/codeinclude-->
