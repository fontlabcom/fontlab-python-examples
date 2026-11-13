---
this_file: lessons/DEPENDENCIES.md
---

# Dependencies

Production uses fontlab-fontlabapp for guarded font access, selection and owned
dialog cleanup, and fontlab-fly>=1.3.0 for App/native aliases and canonical `fly.pens` exports. FontLab supplies
PythonQt. No alternate Qt runtime is installed into FontLab.

Hatchling and hatch-vcs build the small distribution and derive versions from
Git. Tests use pytest, coverage.py, offscreen PySide6 and FontTools in an external
environment. PySide6 is a test dependency only. The historical launcher stays
separate and is exercised without copying it into the new distribution.

GetGo reports require App>=0.2.26.dev0 (unreleased candidate API) through Fly.
Fly supplies standard outline pens through its fontlab-python-pens dependency.
Optional fonttools>=4.59 supplies binary subset export/readback; internal compiler
pens remain FontTools imports. Provider internals keep direct imports to avoid cycles.
All 99 GetGo fixture VFJs and original Apache/CC0/OFL license files are packaged.
