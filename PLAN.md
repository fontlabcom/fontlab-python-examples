---
this_file: PLAN.md
---

# Plan

Completed work is summarised in README.md "Status". Remaining work:

1. **Catalog accuracy.** Update `catalog/ports.json` native-acceptance fields from
   the recorded native evidence; resolve the 14 ambiguous Python candidates, 3 QML
   launcher candidates and shared-file ownership in the static catalog.
2. **Licences (R055).** Resolve per-file licence scope once the owner answers D7
   (BSD-3 file headers vs the GPL-3.0 collection notice for pyqt-official ports);
   then close the unresolved records.
3. **Interactions.** Script native interactions for the remaining ports where it
   does not touch user state (drag/drop inside owned widgets, mouse/key-only and
   visual checks).
4. **Docs.** Integrate the categorized examples with exact status into the rebuilt
   fontlab-python-docs site.

Blocked records stay in the denominator (R004). Removed as not feasible (workspace
DECISIONS.md D8): implementing the missing Qt modules in FontLab's PythonQt
(QML/Quick, WebEngine, Charts, multimedia/GStreamer, QtSql drivers, D-Bus,
matplotlib's Qt backend), and interactions that would use the user's clipboard,
screen capture or system tray.
