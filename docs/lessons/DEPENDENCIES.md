---
this_file: docs/lessons/DEPENDENCIES.md
---

# Dependencies

Production uses fontlab-fontlabapp for guarded font access, selection and owned
dialog cleanup, and fontlab-fly for the existing alias route. FontLab supplies
PythonQt. No alternate Qt runtime is installed into FontLab.

Hatchling and hatch-vcs build the small distribution and derive versions from
Git. Tests use pytest, coverage.py, offscreen PySide6 and FontTools in an external
environment. PySide6 is a test dependency only. The historical launcher stays
separate and is exercised without copying it into the new distribution.
