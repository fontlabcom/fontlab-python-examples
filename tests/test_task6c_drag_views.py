# this_file: tests/test_task6c_drag_views.py
# SPDX-License-Identifier: Apache-2.0
"""Exercise owned drag/drop panels, model protocols and desktop actions offscreen."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_restored_ui import ROOT, load, qt as restored_qt


@pytest.fixture
def qt(restored_qt, monkeypatch):
    # Match the PythonQt enum aliases used by the scripts on the PySide6 host.
    dialog = restored_qt.QtGui.QFileDialog
    for name in ('AcceptOpen', 'AcceptSave'):
        monkeypatch.setattr(dialog, name, getattr(dialog.AcceptMode, name), raising=False)
    return restored_qt

DRAGS = sorted((ROOT / 'Scripts/Drag And Drop').glob('*.py'))
TARGETS = DRAGS + [ROOT / 'Scripts' / folder / (name + '.py') for folder, names in [
    ('Desktop', ['Screen Capture', 'Tray Notifications']),
    ('Item Views', ['Directory Tree', 'Frozen Column', 'Mounted Storage', 'Synchronized Lazy Views', 'Tile Puzzle']),
] for name in names]


def event(qt, mime=None, x=10, y=10, action=None):
    """A PythonQt-style synthetic drop event with observable acceptance."""
    class Drop:
        accepted = False
        ignored = False
        drop_action = None
        def mimeData(self): return mime
        def pos(self): return qt.QtCore.QPoint(x, y)
        def proposedAction(self): return action or qt.QtCore.Qt.MoveAction
        def accept(self): self.accepted = True
        def acceptProposedAction(self): self.accepted = True
        def ignore(self): self.ignored = True
        def setDropAction(self, value): self.drop_action = value
        def button(self): return qt.QtCore.Qt.LeftButton
    return Drop()


def render(widget, qt):
    widget.resize(max(100, widget.width()), max(100, widget.height()))
    image = qt.QtGui.QImage(widget.size(), qt.QtGui.QImage.Format_ARGB32)
    image.fill(qt.QtCore.Qt.transparent)
    widget.render(image)
    assert not image.isNull()
    assert image.pixelColor(image.width() // 2, image.height() // 2).alpha() > 0
    return image


@pytest.mark.parametrize('path', TARGETS, ids=lambda p: str(p.relative_to(ROOT)))
def test_menu_entry_launches_real_owned_widget(path, qt, monkeypatch):
    from fontlab_python_lessons import qt_demos
    launched = []
    def launch(builder, key, title):
        handle = builder(qt)
        launched.append((key, title))
        return handle
    monkeypatch.setattr(qt_demos, 'launch', launch)
    handle = load(path).main()
    try:
        assert launched[0][0].startswith('restored_')
        assert handle.widget.windowTitle()
        assert handle.widget.findChildren(qt.QtCore.QObject), 'menu entry built an empty widget'
    finally:
        handle.close()
    assert handle.owner.closed


@pytest.mark.parametrize('path', DRAGS, ids=lambda p: p.stem)
def test_drag_session_helpers_preserve_paths_signals_dialogs_and_close(path, qt, monkeypatch, tmp_path):
    m = load(path)
    # Each standalone script owns its own identical lifecycle implementation.
    s = m.Session(qt, 'Lifecycle protocol', main=True)
    h = s.handle
    try:
        assert m.value(SimpleNamespace(amount=9), 'amount') == 9
        assert m.value(SimpleNamespace(amount=lambda: 8), 'amount') == 8
        s.state['meaning'] = 42
        assert s.snapshot()['meaning'] == 42
        calls = []
        s.button('Run', lambda: calls.append('button')).click()
        s.combo('Choice', ['first', 'second'], lambda i: calls.append(i)).setCurrentIndex(1)
        timer = s.timer('tick', lambda: calls.append('timer'), 1000, once=True)
        timer.timeout.emit()
        assert calls == ['button', 1, 'timer']
        menu = s.window.menuBar().addMenu('Test')
        action = s.action(menu, 'Mark', lambda: calls.append('action'), check=True)
        action.trigger()
        assert action.isChecked() and calls[-1] == 'action'
        root = s.root().resolve()
        assert s.path(root / 'new.txt') == root / 'new.txt'
        for denied in [root, tmp_path / 'outside.txt']:
            with pytest.raises(ValueError, match='within'):
                s.path(denied)
        dialog = s.choose(True, lambda path: calls.append(path), '*.txt')
        dialog.fileSelected.emit(str(root / 'new.txt'))
        assert calls[-1] == str(root / 'new.txt')
        def bad(path): raise OSError('cannot write')
        dialog2 = s.choose(False, bad)
        dialog2.fileSelected.emit(str(root / 'failed.txt'))
        assert s.state['error'] == 'cannot write'
        assert s.pending[-1].text() == 'cannot write'
        s.state['dragging'] = True
        close = qt.QtGui.QCloseEvent()
        s.window.closeEvent(close)
        assert not close.isAccepted()
        with pytest.raises(RuntimeError, match='Finish the drag'):
            s.prepare_close()
        s.state['dragging'] = False
        s.before_close = lambda: calls.append('before close')
        s.window.closeEvent(qt.QtGui.QCloseEvent())
        assert calls[-1] == 'before close'
        s.before_close = None
        s.prepare_close()
        s.window.closeEvent(close)
        assert close.isAccepted()
        s.handle.controls['Run'].click()
        assert calls[-1] == 'before close'
    finally:
        h.close()
    assert not root.exists()
    assert s.pending == [] and not timer.isActive()


@pytest.mark.parametrize('title', ['Draggable Icons', 'Draggable Text', 'Word Magnets'])
def test_drag_tiles_drop_payloads_and_move_source(title, qt, monkeypatch):
    m = load(ROOT / f'Scripts/Drag And Drop/{title}.py')
    h = m.build(qt)
    c = h.controls
    s = c['controller']
    records = []
    class Drag:
        def __init__(self, parent): self.mime = None
        def setMimeData(self, mime): self.mime = mime
        def setPixmap(self, pix): assert not pix.isNull()
        def setHotSpot(self, point): assert point.x() == 10
        def exec(self, *args):
            records.append(self.mime)
            assert s.state['dragging']
            return qt.QtCore.Qt.MoveAction
        def deleteLater(self): pass
    monkeypatch.setattr(qt.QtGui, 'QDrag', Drag)
    try:
        panel = c['panel0']
        render(panel, qt)
        empty = qt.QtCore.QMimeData()
        e = event(qt, empty)
        panel.dragEnterEvent(e)
        panel.dropEvent(e)
        assert e.ignored
        first = c['labels'][0]
        count = len(c['labels'])
        first.mousePressEvent(event(qt))
        assert len(c['labels']) == count - 1 and not s.state['dragging']
        mime = records[-1]
        assert c['payload'](mime)[1] == [10, 10]
        e = event(qt, mime)
        panel.dragEnterEvent(e)
        panel.dragMoveEvent(e)
        panel.dropEvent(e)
        assert e.accepted and e.drop_action == qt.QtCore.Qt.MoveAction
        assert s.state['drops'] == 1
        copy = event(qt, mime, action=qt.QtCore.Qt.CopyAction)
        panel.dropEvent(copy)
        assert copy.accepted and copy.drop_action is None
        if title != 'Draggable Icons':
            plain = qt.QtCore.QMimeData()
            plain.setText('wide ' * 35)
            panel.dropEvent(event(qt, plain, x=330))
            assert s.state['drops'] == 3
        for payload in [b'bad json', b'null', b'{"offset":[false,2]}', b'{"offset":[10001,2]}', b'{"offset":"bad"}']:
            bad = qt.QtCore.QMimeData()
            bad.setData(m.MIME, payload)
            assert c['payload'](bad)[1] == [0, 0]
        s.state['dragging'] = True
        with pytest.raises(RuntimeError, match='Finish the drag'):
            h.close()
        s.state['dragging'] = False
    finally:
        h.close()


def test_deferred_export_encodes_only_on_demand_and_reuses_png(qt, monkeypatch):
    m = load(ROOT / 'Scripts/Drag And Drop/Deferred Picture Export.py')
    h = m.build(qt)
    c = h.controls
    try:
        mime = c['mime_factory']()
        assert mime.formats() == ['image/png']
        assert mime.hasFormat('image/png') and not mime.hasFormat('text/plain')
        assert mime.retrieveData('text/plain', None).isEmpty()
        assert h.snapshot()['encodings'] == 0
        first = mime.retrieveData('image/png', None).data()
        assert first.startswith(b'\x89PNG')
        assert mime.retrieveData('image/png', None).data() == first
        assert h.snapshot()['encodings'] == 1
        decoded = qt.QtGui.QImage.fromData(first)
        assert decoded.size() == qt.QtCore.QSize(220, 160)
        class Drag:
            def __init__(self, parent): pass
            def setMimeData(self, data): assert data.hasFormat('image/png')
            def setPixmap(self, pixmap): assert not pixmap.isNull()
            def exec(self, *args): assert h.snapshot()['dragging']
            def deleteLater(self): pass
        monkeypatch.setattr(qt.QtGui, 'QDrag', Drag)
        c['Export'].mousePressEvent(event(qt))
        assert not h.snapshot()['dragging']
        c['controller'].state['dragging'] = True
        with pytest.raises(RuntimeError): h.close()
        c['controller'].state['dragging'] = False
    finally:
        h.close()


def test_drop_inspector_displays_each_supported_mime_type(qt):
    h = load(ROOT / 'Scripts/Drag And Drop/Drop Inspector.py').build(qt)
    c = h.controls
    try:
        for kind, expected in [('text', 'plain words'), ('html', '<b>bold</b>'), ('urls', 'file:///sample.txt'), ('binary', 'Binary data received'), ('image', None)]:
            mime = qt.QtCore.QMimeData()
            if kind == 'text': mime.setText(expected)
            elif kind == 'html': mime.setHtml(expected)
            elif kind == 'urls': mime.setUrls([qt.QtCore.QUrl(expected)])
            elif kind == 'binary': mime.setData('application/octet-stream', b'\xffbinary')
            else:
                image = qt.QtGui.QImage(20, 20, qt.QtGui.QImage.Format_ARGB32)
                image.fill(qt.QtCore.Qt.red)
                mime.setImageData(image)
            e = event(qt, mime)
            c['area'].dragEnterEvent(e)
            assert h.snapshot()['highlight']
            c['area'].dragLeaveEvent(e)
            assert not h.snapshot()['highlight']
            c['area'].dropEvent(e)
            assert e.accepted and c['formats'].rowCount() == len(mime.formats())
            if expected is not None: assert c['area'].text() == expected
            else: assert c['area'].pixmap().toImage().pixelColor(0, 0).red() == 255
            c['Clear'].click()
            assert c['formats'].rowCount() == 0 and h.snapshot()['formats'] == []
    finally:
        h.close()


def test_drag_puzzle_moves_renders_restarts_and_opens_images(qt, monkeypatch, tmp_path):
    m = load(ROOT / 'Scripts/Drag And Drop/Tile Puzzle.py')
    h = m.build(qt)
    c = h.controls
    s = c['controller']
    try:
        board, tray = c['board'], c['tray']
        render(board, qt)
        render(tray, qt)
        assert not c['place'](-1, 0) and not c['place'](0, 25)
        assert c['place'](0, 0) and c['place'](0, 1)
        assert c['positions'] == {1: 0}
        assert not c['place'](1, 1)
        mime = qt.QtCore.QMimeData()
        mime.setData('application/x-fontlab-puzzle', json.dumps({'tile': 1}).encode())
        for surface in [board, tray]:
            e = event(qt, mime, x=130, y=10)
            surface.dragEnterEvent(e)
            surface.dragMoveEvent(e)
            assert e.accepted and surface.hover_cell == 2
            render(surface, qt)
            surface.dragLeaveEvent(e)
            assert surface.hover_cell is None
            surface.dropEvent(e)
            assert e.accepted
        assert 1 in c['order']
        for data in [b'bad', b'{"tile":"a"}', b'{"tile":99}', b'{}']:
            mime.setData('application/x-fontlab-puzzle', data)
            e = event(qt, mime)
            board.dropEvent(e)
            assert e.ignored
        rejected = event(qt, qt.QtCore.QMimeData())
        board.dragEnterEvent(rejected)
        assert rejected.ignored
        c['place'](0, 0)
        occupied = event(qt, mime)
        board.dragMoveEvent(occupied)
        assert occupied.ignored
        class Drag:
            def __init__(self, source): pass
            def setMimeData(self, data): assert data.hasFormat('application/x-fontlab-puzzle')
            def setPixmap(self, image): assert image.width() == 64
            def exec(self, *args): assert s.state['dragging']
            def deleteLater(self): pass
        monkeypatch.setattr(qt.QtGui, 'QDrag', Drag)
        board.mousePressEvent(event(qt))
        board.mousePressEvent(event(qt, x=319, y=319))
        tray.mousePressEvent(event(qt))
        assert not s.state['dragging']
        c['Restart'].trigger()
        for i in range(25): assert c['place'](i, i)
        assert h.snapshot()['completed']
        c['completion'].timeout.emit()
        assert s.pending[-1].text().startswith('All twenty-five')
        c['return_tile'](0)
        assert not h.snapshot()['completed']
        c['Restart'].trigger()
        c['Open'].trigger()
        picture = qt.QtGui.QImage(20, 40, qt.QtGui.QImage.Format_ARGB32)
        picture.fill(qt.QtCore.Qt.green)
        path = tmp_path / 'picture.png'
        assert picture.save(str(path))
        s.pending[-1].fileSelected.emit(str(path))
        assert len(c['order']) == 25
        s.pending[-1].fileSelected.emit(str(tmp_path / 'missing.png'))
        assert 'Cannot decode' in s.state['error']
    finally:
        h.close()


def test_item_puzzle_model_drag_drop_protocol_and_image_load(qt, monkeypatch, tmp_path):
    m = load(ROOT / 'Scripts/Item Views/Tile Puzzle.py')
    h = m.build(qt)
    c = h.controls
    core = qt.QtCore
    try:
        pieces, board = c['pieces_model'], c['board_model']
        invalid = core.QModelIndex()
        assert pieces.rowCount() == 25 and board.rowCount() == board.columnCount() == 5
        assert pieces.rowCount(pieces.index(0, 0)) == 0
        assert board.rowCount(board.index(0, 0)) == board.columnCount(board.index(0, 0)) == 0
        for model in [pieces, board]:
            assert model.mimeTypes() == [m.MIME]
            assert model.supportedDropActions() == core.Qt.MoveAction
            assert model.flags(invalid) & core.Qt.ItemIsDropEnabled
            assert model.data(invalid) is None
            assert not model.mimeData([]).hasFormat(m.MIME)
        assert pieces.data(pieces.index(0, 0), core.Qt.DisplayRole)
        assert not pieces.data(pieces.index(0, 0), core.Qt.DecorationRole).isNull()
        assert pieces.data(pieces.index(0, 0), core.Qt.UserRole) is None
        data = pieces.mimeData([pieces.index(0, 0)])
        number = int(data.data(m.MIME).data())
        assert board.dropMimeData(data, core.Qt.MoveAction, 0, 0, invalid)
        assert c['board_cells'][0] == number
        assert not board.data(board.index(0, 0), core.Qt.DecorationRole).isNull()
        assert board.data(board.index(0, 0)) is None
        assert not c['move'](number, 0)
        assert board.dropMimeData(board.mimeData([board.index(0, 0)]), core.Qt.MoveAction, 0, 0, board.index(1, 1))
        assert c['board_cells'][6] == number
        assert pieces.dropMimeData(data, core.Qt.MoveAction, -1, -1, invalid)
        assert not pieces.dropMimeData(data, core.Qt.MoveAction, -1, -1, invalid)
        for raw in [None, b'bad', b'-1', b'25']:
            bad = core.QMimeData()
            if raw is not None: bad.setData(m.MIME, raw)
            assert not pieces.dropMimeData(bad, core.Qt.MoveAction, -1, -1, invalid)
            assert not board.dropMimeData(bad, core.Qt.MoveAction, -1, -1, invalid)
        assert not c['move'](-1, None) and not c['move'](0, 25)
        for i in range(25): assert c['move'](i, i)
        assert h.snapshot()['complete']
        c['action_Restart'].trigger()
        assert pieces.rowCount() == 25 and not h.snapshot()['complete']
        c['action_Open'].trigger()
        dialog = c['file_dialog']
        image = qt.QtGui.QImage(30, 20, qt.QtGui.QImage.Format_ARGB32)
        image.fill(core.Qt.blue)
        path = tmp_path / 'tiles.png'
        assert image.save(str(path))
        dialog.selectFile(str(path))
        dialog.accepted.emit()
        assert pieces.data(pieces.index(0, 0), core.Qt.DecorationRole).toImage().pixelColor(10, 10).blue() == 255
    finally:
        h.close()


def test_lazy_views_share_selection_and_preserve_parent_identity(qt):
    h = load(ROOT / 'Scripts/Item Views/Synchronized Lazy Views.py').build(qt)
    c = h.controls
    core = qt.QtCore
    try:
        model = c['model']
        invalid = core.QModelIndex()
        first = model.index(4, 0)
        child = model.index(5, 2, first)
        assert model.rowCount() == 1000 and model.columnCount() == 10
        assert model.columnCount(first) == 10
        assert model.parent(child) == first and not model.parent(first).isValid()
        assert not model.parent(invalid).isValid()
        assert model.data(child) == 'Entry 6, field 3'
        assert model.data(first, core.Qt.DecorationRole) is not None
        assert model.data(child, core.Qt.DecorationRole) is None
        assert model.data(invalid) is None
        assert model.rowCount(child) == 0
        assert not model.index(0, 0, child).isValid()
        for row, col in [(-1, 0), (1000, 0), (0, 10), (0, -1)]:
            assert not model.index(row, col).isValid()
        assert model.index(4, 0).internalId() == first.internalId()
        c['selection'].setCurrentIndex(first, core.QItemSelectionModel.ClearAndSelect)
        assert all(c[name].selectionModel() is c['selection'] for name in ['tree', 'table', 'list'])
        assert c['table'].currentIndex() == first
        # A foreign identity is rejected rather than linked into this model.
        foreign = model.createIndex(1, 0, 999999)
        assert not model.parent(foreign).isValid()
        assert not model.index(0, 0, foreign).isValid()
    finally:
        h.close()


def test_directory_timer_initializes_real_sample_file(qt):
    h = load(ROOT / 'Scripts/Item Views/Directory Tree.py').build(qt)
    try:
        h.controls['load_timer'].timeout.emit()
        root = Path(h.snapshot()['root'])
        assert (root / 'notes.txt').read_text() == 'One small directory fixture.\n'
        assert h.controls['tree'].model().isReadOnly()
        assert not h.snapshot()['loading']
    finally:
        h.close()
    assert not root.exists()


def test_frozen_column_tracks_geometry_row_height_and_scroll(qt):
    h = load(ROOT / 'Scripts/Item Views/Frozen Column.py').build(qt)
    c = h.controls
    try:
        h.widget.show()
        qt.QtCore.QCoreApplication.processEvents()
        table, frozen = c['table'], c['frozen']
        table.setColumnWidth(0, 163)
        table.setColumnWidth(1, 100)
        table.setRowHeight(0, 37)
        c['geometry_timer'].timeout.emit()
        assert frozen.columnWidth(0) == 163 and frozen.rowHeight(0) == 37
        table.verticalScrollBar().setRange(0, 100)
        frozen.verticalScrollBar().setRange(0, 100)
        table.verticalScrollBar().setValue(7)
        assert frozen.verticalScrollBar().value() == 7
        frozen.verticalScrollBar().setValue(9)
        assert table.verticalScrollBar().value() == 9
        assert all(frozen.isColumnHidden(i) for i in range(1, 5))
        assert frozen.selectionModel() is table.selectionModel()
    finally:
        h.close()


def test_mounted_storage_renders_read_only_volume_rows(qt, monkeypatch):
    m = load(ROOT / 'Scripts/Item Views/Mounted Storage.py')
    volume = SimpleNamespace(**{name: (lambda value=value: value) for name, value in {
        'rootPath':'/fixture', 'displayName':'Fixture', 'device':b'disk', 'fileSystemType':b'apfs',
        'bytesTotal':1024**4, 'bytesFree':1024**3, 'bytesAvailable':1024**2,
        'isReady':True, 'isReadOnly':False, 'isRoot':False,
    }.items()})
    monkeypatch.setattr(qt.QtCore.QStorageInfo, 'mountedVolumes', lambda: [volume])
    h = m.build(qt)
    try:
        h.controls['load_timer'].timeout.emit()
        table = h.controls['volumes']
        assert table.rowCount() == 1
        assert table.item(0, 0).text() == '/fixture'
        assert table.item(0, 4).text() == '1.0 TiB'
        assert not table.item(0, 0).flags() & qt.QtCore.Qt.ItemIsEditable
        assert m.human_size(-1024) == '-1.0 KiB'
    finally:
        h.close()


def test_screen_capture_schedules_captures_and_saves_inside_owned_folder(qt, monkeypatch, tmp_path):
    m = load(ROOT / 'Scripts/Desktop/Screen Capture.py')
    pixmap = qt.QtGui.QPixmap(80, 60)
    pixmap.fill(qt.QtCore.Qt.magenta)
    screens = [SimpleNamespace(grabWindow=lambda *a: pixmap)]
    application = SimpleNamespace(screens=lambda: screens)
    monkeypatch.setattr(qt.QtGui, 'QApplication', SimpleNamespace(instance=lambda: application))
    old_value = m.S.value
    monkeypatch.setattr(m.S, 'value', lambda obj, name: obj.isChecked() if name == 'checked' else old_value(obj, name))
    h = m.build(qt)
    c = h.controls
    try:
        c['save_image'](tmp_path / 'nothing.png')
        assert not (tmp_path / 'nothing.png').exists()
        c['delay'].setValue(1)
        c['hide'].setChecked(True)
        c['new'].click()
        assert h.snapshot()['pending'] and not c['delay'].isEnabled()
        c['capture_timer'].timeout.emit()
        assert h.snapshot()['captured'] and not h.snapshot()['pending']
        assert c['preview'].pixmap().toImage().pixelColor(0, 0).magenta() == 255
        with pytest.raises(ValueError, match='inside'):
            c['save_image'](tmp_path / 'escape.png')
        c['save'].click()
        folder = Path(c['file_dialog'].directory().absolutePath())
        target = folder / 'screen.png'
        c['save_image'](target)
        assert qt.QtGui.QImage(str(target)).size() == pixmap.size()
        screens.clear()
        c['capture']()
        assert c['new'].isEnabled()
    finally:
        h.close()


def test_tray_actions_change_icon_and_send_explicit_notification(qt, monkeypatch):
    m = load(ROOT / 'Scripts/Desktop/Tray Notifications.py')
    old_value = m.S.value
    monkeypatch.setattr(m.S, 'value', lambda obj, name: obj.isChecked() if name == 'checked' else old_value(obj, name))
    messages = []
    class Tray(qt.QtGui.QSystemTrayIcon):
        def showMessage(self, *args): messages.append(args)
    monkeypatch.setattr(qt.QtGui, 'QSystemTrayIcon', Tray)
    h = m.build(qt)
    c = h.controls
    try:
        c['message'].click()
        assert h.snapshot()['error'] == 'Enable the tray icon first'
        old_icon = c['tray'].icon().cacheKey()
        c['icon'].setCurrentIndex(1)
        assert c['tray'].icon().cacheKey() != old_icon
        c['show'].setChecked(True)
        c['type'].setCurrentIndex(2)
        c['duration'].setValue(7)
        c['message'].click()
        assert messages[-1] == ('Example notification', 'A manually requested sample message.', Tray.Critical, 7000)
        assert h.snapshot()['notifications'] == 1
        c['tray'].activated.emit(Tray.Trigger)
    finally:
        h.close()
