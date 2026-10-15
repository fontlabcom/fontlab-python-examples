---
this_file: PLAN.md
---

# Plan

Everything else is done and recorded in CHANGELOG.md. Two items remain, and neither
can be closed inside this repository:

1. **Resource licences: owner decision.** 14 resources in `catalog/licenses.json`
   stay `unresolved`; no grant is inferred. Provenance research (2026-10-15,
   workspace evidence `examples-licences/provenance.json` and `provenance.py`):
   - The 9 styleexample resources (`ports/embedded/eyllanesc/assets/631cc1bc310c00b9/`)
     are The Qt Company's own files from `qt/qtbase` `examples/embedded/styleexample`:
     add.png, remove.png, nature_1.jpg, nostyle.qss and stylewidget.ui are
     byte-identical to Qt 5.15 and 6.5; the four other .qss files differ only in
     trailing whitespace. That example's sources carry
     `LicenseRef-Qt-Commercial OR BSD-3-Clause`, and qtbase's REUSE.toml (dev) assigns
     `examples/**` the same licence. The files themselves carry no notice, and the
     REUSE rule post-dates the example's removal.
   - The 5 pyqt/examples assets (three identical `icon.svg`, `bullet.png`, `shot.wav`)
     have no traced origin. The icon uses the Tango template's ids (`svg11300`) but
     matches no traced Tango file. `shot.wav` is not loaded at runtime (QSoundEffect is
     unavailable), and `bullet.png` and the icons are.
   Options for the owner: accept BSD-3-Clause for the 9 Qt files (adding a Qt notice);
   confirm the 5 assets with Michael Herrmann; or replace them with original assets.
   Replacement needs a native re-recording path for non-clean-room ports, because
   `tools/record_native.py` covers clean-room records only.
2. **Docs integration: handoff to the docs lane (L5) and the controller.**
   fontlab-python-docs is not this lane's write set; only L5 runs its build. The
   coverage review on this side is done: 299 records (148 implemented, each with a
   native pass, evidence and an existing file; 151 blocked, each with
   `blocked_reason`), 18 insights and 9 recipes with README and native driver.
   Inputs for the docs: `catalog/INDEX.md`, `catalog/ports.json`, `catalog/insights.json`
   and `examples/recipes/*/README.md`.

Blocked records stay in the denominator (R004). Removed as not feasible (workspace
DECISIONS.md D8): implementing the missing Qt modules in FontLab's PythonQt
(QML/Quick, WebEngine, Charts, multimedia/GStreamer, QtSql drivers, D-Bus,
matplotlib's Qt backend), and interactions that would use the user's clipboard,
screen capture or system tray.
