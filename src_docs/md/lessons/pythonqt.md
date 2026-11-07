---
this_file: src_docs/md/lessons/pythonqt.md
---


# PythonQt examples for FontLab 9

Six short scripts, each focused on one PythonQt technique. They are not menu
tools: they live outside `Scripts/` so the menu catalogue stays unchanged. Copy
one into a FontLab Scripts folder to run it. Each file's header says what it
shows, how to run it and what it needs (FontLab 9, Fly with App).

FontLab 9 embeds MeVisLab PythonQt on Qt 5. Widgets and item models are in
`PythonQt.QtGui` (no QtWidgets). Properties read as attributes, some as methods,
so the examples read them through a small helper. Signals connect with
`signal.connect(callable)`, or with `obj.connect("signal()", callable)`.

| Script | Shows |
|---|---|
| `live_glyph_panel.py` | Modeless tool panel; QTimer watching the current glyph |
| `glyph_table_model.py` | QStandardItemModel, QSortFilterProxyModel, QTableView |
| `canvas_overlay_with_menu.py` | `flCanvas.appendPythonPainter`; menu QAction with a shortcut via `OwnedMenus` |
| `signals_and_timer.py` | Three signal styles, single-shot timers, teardown |
| `saved_settings.py` | QSettings in an own namespace, typed defaults, status check |
| `batch_with_progress.py` | QProgressDialog, chunked work on a copy, cancel |

None writes to a font. Offline tests (`tests/test_pythonqt_examples.py`) prove
compilation, import without FontLab and the pure logic only. They are not native
proof; see CHANGELOG for the native checks still to run.
