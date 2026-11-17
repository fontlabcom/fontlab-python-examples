# SPDX-License-Identifier: Apache-2.0
# this_file: tests/test_restored_ui.py
"""Offscreen smoke and small behavior checks for restored UI examples."""
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATHS = sorted(p for category in ('Desktop', 'Drag And Drop', 'Item Views')
               for p in (ROOT / 'Scripts' / category).glob('*.py'))


def load(path):
    spec = importlib.util.spec_from_file_location('restored_ui', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def qt(monkeypatch):
    from PySide6 import QtCore, QtGui, QtWidgets
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    monkeypatch.syspath_prepend(str(ROOT / 'lessons/src'))
    from fontlab_python_lessons import qt_demos

    class Owner:
        def __init__(self, widget, content):
            self.widget, self.closed = widget, False

        def close(self):
            if not self.widget.close():
                return False
            self.widget.deleteLater()
            self.closed = True
            return True

    def connect(self, obj, signature, callback):
        signal = getattr(obj, signature.split('(')[0])
        signal.connect(callback)
        self.connections.append((signal, None, callback))

    monkeypatch.setitem(sys.modules, 'fly.ap.qt.widgets', SimpleNamespace(OwnedWidget=Owner))
    monkeypatch.setattr(qt_demos.ExampleHandle, 'connect_old', connect)
    gui = SimpleNamespace(**{name: getattr(module, name) for module in (QtGui, QtWidgets)
                             for name in dir(module) if name.startswith('Q')})
    gui.QAbstractTableModel = QtCore.QAbstractTableModel
    gui.QItemSelectionModel = QtCore.QItemSelectionModel
    yield SimpleNamespace(QtCore=QtCore, QtGui=gui)
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
    app.processEvents()


@pytest.mark.parametrize('path', PATHS, ids=lambda path: str(path.relative_to(ROOT)))
def test_restored_ui_builds_and_closes(path, qt):
    module = load(path)
    assert callable(module.main)
    handle = module.build(qt)
    assert handle.widget is not None
    handle.close()
    assert handle.owner.closed


def test_human_size_scales_boundaries(qt):
    module = load(ROOT / 'Scripts/Item Views/Mounted Storage.py')
    assert module.human_size(0) == '0.0 B'
    assert module.human_size(1024) == '1.0 KiB'
    assert module.human_size(1024 ** 4) == '1.0 TiB'


def test_drag_puzzle_rejects_occupied_cells_and_returns_tile(qt):
    handle = load(ROOT / 'Scripts/Drag And Drop/Tile Puzzle.py').build(qt)
    try:
        controls = handle.controls
        assert controls['place'](0, 0)
        assert not controls['place'](1, 0)
        assert not controls['place'](-1, 1)
        controls['return_tile'](0)
        assert controls['positions'] == {}
        assert sorted(controls['order']) == list(range(25))
    finally:
        handle.close()


def test_incremental_listing_fetches_all_files(qt):
    handle = load(ROOT / 'Scripts/Item Views/Fetch More Files.py').build(qt)
    try:
        for _ in range(11):
            handle.controls['prepare']()
        model = handle.controls['model']
        while model.canFetchMore(qt.QtCore.QModelIndex()):
            model.fetchMore(qt.QtCore.QModelIndex())
        assert model.rowCount() == 205
        assert model.data(model.index(0, 0)) == 'entry-000.txt'
    finally:
        handle.close()


def test_item_puzzle_moves_without_duplicate_tiles(qt):
    handle = load(ROOT / 'Scripts/Item Views/Tile Puzzle.py').build(qt)
    try:
        controls = handle.controls
        assert controls['move'](0, 0)
        assert not controls['move'](1, 0)
        assert controls['move'](0, None)
        assert sorted(controls['unplaced']) == list(range(25))
        assert controls['board_cells'] == [None] * 25
    finally:
        handle.close()


def test_drag_payload_rejects_malformed_offsets(qt):
    handle = load(ROOT / 'Scripts/Drag And Drop/Draggable Text.py').build(qt)
    try:
        mime = qt.QtCore.QMimeData()
        mime.setData('application/x-fontlab-owned-tile', b'{"offset": ["bad", 2]}')
        assert handle.controls['payload'](mime)[1] == [0, 0]
        mime.setData('application/x-fontlab-owned-tile', b'not JSON')
        assert handle.controls['payload'](mime) == ({}, [0, 0])
    finally:
        handle.close()


def test_drag_puzzle_contains_paint_errors_and_ends_painter(qt, monkeypatch, capsys):
    handle = load(ROOT / 'Scripts/Drag And Drop/Tile Puzzle.py').build(qt)
    ended = []

    class Painter:
        def __init__(self, widget):
            pass

        def fillRect(self, *args):
            raise RuntimeError('paint failed')

        def end(self):
            ended.append(True)

    monkeypatch.setattr(qt.QtGui, 'QPainter', Painter)
    try:
        handle.controls['board'].paintEvent(qt.QtGui.QPaintEvent(qt.QtCore.QRect()))
        assert ended == [True]
        assert 'Puzzle drawing failed: paint failed' in capsys.readouterr().out
    finally:
        handle.close()


def test_tray_window_actions_target_enclosing_panel(qt):
    events = []

    class Outer(qt.QtGui.QWidget):
        def showMinimized(self):
            events.append('minimize')

        def showMaximized(self):
            events.append('maximize')

        def showNormal(self):
            events.append('restore')

    outer = Outer()
    handle = load(ROOT / 'Scripts/Desktop/Tray Notifications.py').build(qt)
    try:
        handle.widget.setParent(outer)
        for action in handle.controls['tray_menu'].actions()[:3]:
            action.trigger()
        assert events == ['minimize', 'maximize', 'restore']
    finally:
        handle.close()
        outer.deleteLater()
