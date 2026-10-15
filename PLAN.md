---
this_file: PLAN.md
---

# Plan

Everything else is done and recorded in CHANGELOG.md. One item remains, outside this
repository:

1. **Docs integration: docs lane (L5).** `tools/docs_export.py` writes the
   categorized pages into `docs-export/` with `manifest.json`
   (format `fontlab-python-examples.docs-export.v1`). L5 copies or mounts that folder
   into fontlab-python-docs and adds it to the navigation after its current rebuild;
   only L5 runs that build.

Blocked records stay in the denominator (R004). Removed as not feasible (workspace
DECISIONS.md D8): implementing the missing Qt modules in FontLab's PythonQt
(QML/Quick, WebEngine, Charts, multimedia/GStreamer, QtSql drivers, D-Bus,
matplotlib's Qt backend), and interactions that would use the user's clipboard,
screen capture or system tray.
