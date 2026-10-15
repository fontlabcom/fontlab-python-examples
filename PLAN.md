---
this_file: PLAN.md
---

# Plan

Completed on 2026-10-15:

- All 148 implemented native records cite exact original files/records and hashes,
  with portable projections in `verification/catalog-native-evidence.json` and
  tests comparing them to the workspace originals when present.
- `catalog/reviews.json` resolves 14 Python candidates, 3 QML candidates and
  ownership of 69 shared files. `inventory.py --reviews` reapplies the decisions
  after verifying source hashes. Raw static observations and every identity remain.
- `catalog/licenses.json` records 112 non-official port source reviews, 15 resource
  reviews and 19 original insight file reviews. Pyqt-official licence records are
  untouched. The gallery's explicit BSD exception is retained; unsupported MIT
  selections for five numbered assets are replaced by unresolved grant records.

Remaining work:

1. **Resource licences.** Confirm individual grants and attribution for the 14
   unresolved resources in `catalog/licenses.json`. Do not infer asset rights
   from directory association or a source-code grant. The nine styleexample
   resources retain the GPL collection notice without an individual grant claim.
2. **Licences (R055).** Resolve per-file licence scope once the owner answers D7
   (BSD-3 file headers vs the GPL-3.0 collection notice for pyqt-official ports);
   then close the unresolved records.
3. **Interactions.** Script native interactions for the remaining ports where it
   does not touch user state (drag/drop inside owned widgets, mouse/key-only and
   visual checks).
4. **Docs.** Integrate the categorized examples with exact status into the rebuilt
   fontlab-python-docs site.

The newly classified mathtext Python launcher and chapter6 QML entrypoint remain
catalog requirements with recorded matplotlib/QML blockers; this review adds no
port implementation or native execution. Plugin roles remain integration
requirements rather than extra standalone widget acceptance.

Blocked records stay in the denominator (R004). Removed as not feasible (workspace
DECISIONS.md D8): implementing the missing Qt modules in FontLab's PythonQt
(QML/Quick, WebEngine, Charts, multimedia/GStreamer, QtSql drivers, D-Bus,
matplotlib's Qt backend), and interactions that would use the user's clipboard,
screen capture or system tray.
