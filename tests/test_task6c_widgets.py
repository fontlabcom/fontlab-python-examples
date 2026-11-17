# this_file: tests/test_task6c_widgets.py
# SPDX-License-Identifier: Apache-2.0
"""Drive restored widget examples with real offscreen Qt controls and events."""
import importlib.util
import sys
from enum import Enum
from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lessons/src'))
from fontlab_python_lessons import qt_demos as S


def load(title, category='Widgets'):
    path = ROOT / 'Scripts' / category / (title + '.py')
    spec = importlib.util.spec_from_file_location('widget_' + title.replace(' ', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def qt(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    class Owner:
        def __init__(self, widget, content):
            self.widget, self.closed = widget, False
        def close(self):
            if not self.closed:
                self.widget.hide()
                self.widget.deleteLater()
                self.closed = True
            return True

    def connect(self, obj, signature, slot):
        signal = getattr(obj, signature.split('(')[0])
        signal.connect(slot)
        self.connections.append((signal, None, slot))

    original_value = S.value
    def value(obj, name):
        result = obj.isChecked() if name == 'checked' else original_value(obj, name)
        return result.value if isinstance(result, Enum) else result

    class FontMetrics(QtGui.QFontMetrics):
        width = QtGui.QFontMetrics.horizontalAdvance

    class DirModel(QtWidgets.QFileSystemModel):
        def __init__(self, parent):
            super().__init__(parent)
            self.setRootPath(str(Path.home()))

    gui = SimpleNamespace(**{name: getattr(mod, name) for mod in (QtGui, QtWidgets)
                             for name in dir(mod) if name.startswith('Q')})
    gui.QStringListModel = QtCore.QStringListModel
    gui.QAbstractTableModel = QtCore.QAbstractTableModel
    gui.QDirModel = DirModel
    gui.QFontMetrics = FontMetrics
    monkeypatch.setitem(sys.modules, 'fly.ap.qt.widgets', SimpleNamespace(OwnedWidget=Owner))
    monkeypatch.setitem(sys.modules, 'PythonQt', SimpleNamespace(QtUiTools=QtUiTools))
    monkeypatch.setattr(S.ExampleHandle, 'connect_old', connect)
    monkeypatch.setattr(S, 'value', value)
    yield SimpleNamespace(QtCore=QtCore, QtGui=gui, private=SimpleNamespace(QObject=QtCore.QObject), app=app)
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
    app.processEvents()


def render(widget):
    widget.resize(360, 240)
    widget.show()
    QtWidgets.QApplication.processEvents()
    image = QtGui.QImage(widget.size(), QtGui.QImage.Format_ARGB32)
    image.fill(QtCore.Qt.transparent)
    widget.render(image)
    assert not image.isNull()
    assert any(image.pixelColor(x, y).alpha() > 0 for x in range(0, image.width(), 10) for y in range(0, image.height(), 10))
    return image


def distinct_colours(image):
    return {image.pixel(x, y) for x in range(0, image.width(), 4) for y in range(0, image.height(), 4)}
    return image


def mouse(kind, x=30, y=30, button=QtCore.Qt.LeftButton, buttons=QtCore.Qt.LeftButton):
    return QtGui.QMouseEvent(kind, QtCore.QPointF(x, y), QtCore.QPointF(x, y), button, buttons, QtCore.Qt.NoModifier)


def key(code):
    return QtGui.QKeyEvent(QtCore.QEvent.KeyPress, code, QtCore.Qt.NoModifier)


@pytest.mark.parametrize('title', ['Analog Clock', 'Clock Component', 'Shaped Clock',
    'Counter Label', 'Animated Checker Player', 'Bubble Canvas', 'Button And Alert',
    'Calculator Form', 'Calculator', 'Dark Theme Editor', 'Date And Time Editor',
    'Digital Clock', 'Falling Blocks', 'Filesystem Tree', 'Group Box Gallery',
    'Hello Label', 'Line Edit Gallery', 'List View', 'Multiple Page Widget',
    'Python Console Widget', 'Rich Text Component', 'Scientist Table',
    'Shape Tooltips', 'Text Editor', 'Vertical Buttons', 'Waving Text'])
def test_widget_launch_builds_real_panel(title, qt, monkeypatch):
    module = load(title)
    calls = []
    def launch(builder, identity, caption):
        calls.append((identity, caption))
        return builder(qt)
    monkeypatch.setattr(S, 'launch', launch)
    handle = module.main()
    try:
        assert calls[0][1] == title
        assert isinstance(handle.widget, QtWidgets.QWidget)
        image = render(handle.widget)
        # Bubble Canvas starts empty by design; bubbles appear on timer ticks (tested separately).
        if title != 'Bubble Canvas':
            assert len(distinct_colours(image)) > 1, f'{title} rendered a blank panel'
        if title in ['Hello Label', 'Vertical Buttons', 'List View', 'Filesystem Tree', 'Scientist Table', 'Button And Alert']:
            assert handle.snapshot()['launched']
    finally:
        handle.close()
    assert handle.owner.closed


@pytest.mark.parametrize('title', ['Analog Clock', 'Clock Component', 'Shaped Clock'])
def test_clock_paints_ticks_offsets_and_shaped_drag(title, qt):
    handle = load(title).build(qt)
    try:
        c = handle.controls
        c['set_offset'](3)
        assert handle.snapshot()['offset'] == 3
        c['clock_timer'].timeout.emit()
        assert 'T' in handle.snapshot()['local_time']
        c['reset']()
        assert handle.snapshot()['offset'] == 0
        render(c['canvas'])
        if title == 'Clock Component':
            assert len(handle.snapshot()['notifications']) >= 2
        if title == 'Shaped Clock':
            face = c['canvas']
            face.mousePressEvent(mouse(QtCore.QEvent.MouseButtonPress, button=QtCore.Qt.RightButton))
            face.mouseMoveEvent(mouse(QtCore.QEvent.MouseMove, buttons=QtCore.Qt.NoButton))
            face.mousePressEvent(mouse(QtCore.QEvent.MouseButtonPress))
            face.mouseMoveEvent(mouse(QtCore.QEvent.MouseMove, 50, 50))
            face.mouseReleaseEvent(mouse(QtCore.QEvent.MouseButtonRelease))
            face.contextMenuEvent(QtGui.QContextMenuEvent(QtGui.QContextMenuEvent.Mouse, QtCore.QPoint(3, 3), QtCore.QPoint(3, 3)))
            assert c['context_menu'].actions()[0].text() == 'Exit'
    finally:
        handle.close()


def test_counter_bounds_notifications_and_font(qt):
    handle = load('Counter Label').build(qt)
    try:
        c = handle.controls
        assert not c['set_minimum'](2)
        assert not c['set_maximum'](0)
        assert c['set_maximum'](5)
        assert c['set_minimum'](0)
        assert c['set_offset'](10)
        assert c['set_value'](3)
        assert c['step_up']() and c['step_down']()
        assert not c['set_value'](9)
        c['set_font'](QtGui.QFont('Sans', 20))
        render(c['canvas'])
        assert handle.snapshot()['notifications'][-1] == [13, '13']
    finally:
        handle.close()


def test_calculator_buttons_precedence_memory_repeat_and_errors(qt):
    handle = load('Calculator').build(qt)
    try:
        c = handle.controls
        def press(sequence):
            for value in sequence:
                c[value].click()
            return c['display'].text()
        assert press(['2', '+', '3', '*', '4', '=']) == '14'
        assert press(['=']) == '56'
        assert press(['C', '8', '/', '2', '-', '1', '=']) == '3'
        assert press(['MS', 'M+', 'MC', 'MR']) == '0'
        assert press(['C', '4', 'MS', '2', 'M+', 'MR']) == '6'
        assert float(press(['sqrt', 'square', '±', '±'])) == pytest.approx(6)
        assert float(press(['1/x'])) == pytest.approx(1 / 6)
        assert press(['C', '1', '2', 'Back']) == '1'
        assert press(['CE', '.', '.', '5']) == '0.5'
        assert press(['C', '0', '1/x']) == 'Error'
        assert press(['2', '+', '-', '1', '=']) == '1'
        assert press(['C', '9', '±', 'sqrt']) == 'Error'
        assert handle.snapshot()['display'] == 'Error'
    finally:
        handle.close()


def test_small_form_calendar_line_edits_and_groups(qt):
    handle = load('Calculator Form').build(qt)
    try:
        handle.controls['first'].setValue(7)
        handle.controls['second'].setValue(12)
        assert handle.controls['result'].text() == '19'
    finally:
        handle.close()
    handle = load('Date And Time Editor').build(qt)
    try:
        for name in ['date', 'datetime']:
            handle.controls['configure_' + name]({'week_start': QtCore.Qt.Sunday, 'grid': True,
                'horizontal': QtWidgets.QCalendarWidget.LongDayNames,
                'vertical': QtWidgets.QCalendarWidget.NoVerticalHeader, 'navigation': False})
            cal = handle.controls[name + '_calendar']
            assert cal.isGridVisible() and not cal.isNavigationBarVisible()
            handle.controls['reset_' + name]()
            assert not cal.isGridVisible() and cal.firstDayOfWeek() == QtCore.Qt.Monday
    finally:
        handle.close()
    handle = load('Line Edit Gallery').build(qt)
    try:
        for name in ['echo', 'validator', 'alignment', 'mask', 'access']:
            choice = handle.controls[name]
            for i in range(choice.count()):
                choice.setCurrentIndex(i)
        assert handle.controls['access_edit'].isReadOnly()
        assert handle.controls['echo_edit'].echoMode() == QtWidgets.QLineEdit.NoEcho
        assert handle.controls['validator_edit'].validator() is handle.controls['decimal_validator']
        assert handle.controls['alignment_edit'].alignment() == QtCore.Qt.AlignRight
        assert 'AAAAA' in handle.controls['mask_edit'].inputMask()
    finally:
        handle.close()
    handle = load('Group Box Gallery').build(qt)
    try:
        handle.controls['toggle'].click()
        handle.controls['group_1'].setChecked(False)
        assert handle.controls['toggle'].isChecked()
        assert handle.controls['flat'].isFlat()
        assert handle.controls['popup'].menu().actions()[0].text() == 'Example'
        assert handle.controls['tri'].isTristate()
    finally:
        handle.close()


def test_digital_clock_blinks_and_timer_updates(qt):
    module = load('Digital Clock')
    assert module.display_time(3, 4, 0) == '03:04'
    assert module.display_time(3, 4, 1) == '03 04'
    handle = module.build(qt)
    try:
        handle.controls['clock_timer'].timeout.emit()
        assert len(handle.snapshot()['display']) == 5
        assert handle.controls['lcd'].digitCount() == 5
    finally:
        handle.close()


def test_bubbles_mouse_growth_motion_colors_and_stop(qt):
    handle = load('Bubble Canvas').build(qt)
    try:
        c = handle.controls
        c['set_count'](3)
        c['motion_timer'].timeout.emit()
        before = handle.snapshot()['bubbles']
        assert len(before) == 3
        face = c['canvas']
        face.mousePressEvent(mouse(QtCore.QEvent.MouseButtonPress))
        c['growth_timer'].timeout.emit()
        c['motion_timer'].timeout.emit()
        assert handle.snapshot()['bubbles'][-1][2] == 4
        face.mouseReleaseEvent(mouse(QtCore.QEvent.MouseButtonRelease))
        c['growth_timer'].timeout.emit()
        c['set_inner']('red')
        c['set_outer']('blue')
        c['set_description']('Own bubbles')
        with pytest.raises(ValueError, match='Invalid bubble color'):
            c['set_inner']('invalid-color')
        render(face)
        c['stop']()
        assert not c['motion_timer'].isActive()
        c['start']()
        assert c['motion_timer'].isActive()
        c['set_count'](-1)
        c['motion_timer'].timeout.emit()
        assert handle.snapshot()['bubbles'] == []
    finally:
        handle.close()


def test_shapes_hover_drag_hit_and_new_buttons(qt):
    module = load('Shape Tooltips')
    handle = module.build(qt)
    try:
        c = handle.controls
        shapes = c['shapes']
        for i, shape in enumerate(shapes):
            shape[1:3] = [50 + i * 100, 70]
        assert module.hit(shapes, 50, 70) == 0
        assert module.hit(shapes, 150, 70) == 1
        assert module.hit(shapes, 250, 70) == 2
        assert module.hit(shapes, -100, -100) is None
        face = c['canvas']
        face.mousePressEvent(mouse(QtCore.QEvent.MouseButtonPress, 50, 70, QtCore.Qt.RightButton))
        face.mouseMoveEvent(mouse(QtCore.QEvent.MouseMove, 50, 70, buttons=QtCore.Qt.NoButton))
        face.mouseMoveEvent(mouse(QtCore.QEvent.MouseMove, -100, -100, buttons=QtCore.Qt.NoButton))
        face.mousePressEvent(mouse(QtCore.QEvent.MouseButtonPress, -100, -100))
        face.mousePressEvent(mouse(QtCore.QEvent.MouseButtonPress, 50, 70))
        face.mouseMoveEvent(mouse(QtCore.QEvent.MouseMove, 70, 90))
        face.mouseReleaseEvent(mouse(QtCore.QEvent.MouseButtonRelease, 70, 90))
        assert shapes[-1][1:3] == [70, 90]
        for kind in ['Circle', 'Square', 'Triangle']:
            c[kind].click()
        assert len(shapes) == 6
        render(face)
    finally:
        handle.close()


def test_pages_validate_indices_rename_remove_and_select(qt):
    handle = load('Multiple Page Widget').build(qt)
    try:
        c = handle.controls
        assert c['insert'](2, 'Third')
        assert c['rename'](2, 'Last')
        assert c['set_index'](2)
        assert c['selector'].currentText() == 'Last'
        assert c['stack'].currentWidget().text() == 'Last'
        for name in ['insert', 'remove', 'rename', 'set_index']:
            args = (-1, 'bad') if name in ['insert', 'rename'] else (-1,)
            assert not c[name](*args)
        assert c['remove'](1)
        assert handle.snapshot()['count'] == 2
    finally:
        handle.close()


def test_expression_entry_history_and_error(qt):
    handle = load('Python Console Widget').build(qt)
    try:
        entry = handle.controls['entry']
        entry.setText('2 + 3')
        entry.returnPressed.emit()
        assert handle.snapshot()['result'] == '5'
        entry.setText('1 / 0')
        entry.returnPressed.emit()
        assert 'ZeroDivisionError' in handle.snapshot()['error']
        entry.keyPressEvent(key(QtCore.Qt.Key_Up))
        assert entry.text() == '2 + 3'
        entry.keyPressEvent(key(QtCore.Qt.Key_Down))
        assert entry.text() == ''
        entry.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_A, QtCore.Qt.NoModifier, 'a'))
        assert entry.text() == 'a'
    finally:
        handle.close()


def test_rich_text_zoom_author_and_waving_text_timer(qt):
    handle = load('Rich Text Component').build(qt)
    try:
        c = handle.controls
        c['set_zoom'](100)
        assert handle.snapshot()['zoom'] == 30
        c['reset_zoom']()
        c['set_author']('Ada')
        assert handle.snapshot()['author'] == 'Ada'
        c['reset_author']()
        assert handle.snapshot()['author'] == 'Example author'
        assert 'Bold ideas' in c['text'].toPlainText()
    finally:
        handle.close()
    handle = load('Waving Text').build(qt)
    try:
        c = handle.controls
        c['receiver'].timerEvent(QtCore.QTimerEvent(c['wave_timer'].timerId()))
        assert handle.snapshot()['phase'] == 1
        render(c['canvas'])
        c['entry'].clear()
        render(c['canvas'])
        assert handle.snapshot()['text'] == ''
    finally:
        handle.close()


@pytest.mark.parametrize('title', ['Text Editor', 'Dark Theme Editor'])
def test_editors_preserve_drafts_and_save_utf8_exclusively(title, qt, tmp_path):
    handle = load(title).build(qt)
    try:
        c = handle.controls
        source = tmp_path / 'source.txt'
        source.write_text('Curve — 曲線', encoding='utf8')
        c['open_file'](str(source))
        assert c['text'].toPlainText() == 'Curve — 曲線'
        c['text'].insertPlainText(' draft')
        assert not c['can_close']()
        c['open_file'](str(tmp_path / 'missing'))
        assert 'draft' in c['text'].toPlainText()
        c['save_file'](str(source))
        assert source.read_text() == 'Curve — 曲線'
        output = tmp_path / 'saved.txt'
        c['save_file'](str(output))
        assert 'draft' in output.read_text()
        assert c['can_close']()
        c['open_file'](str(tmp_path / 'missing'))
        c['discard'].click()
        c['open'].click()
        c['save'].click()
    finally:
        handle.close()


def test_button_alert_replaces_owned_alert(qt):
    handle = load('Button And Alert').build(qt)
    try:
        handle.widget.click()
        first = handle.alerts[0]
        assert first.widget.text() == 'You clicked the button!'
        handle.widget.click()
        assert first.closed and len(handle.alerts) == 1
        assert handle.alerts[0].widget.windowModality() == QtCore.Qt.WindowModal
        assert len(handle.snapshot()['alert_texts']) == 1
    finally:
        handle.close()


def test_scientist_model_invalid_roles_indices_and_headers(qt):
    handle = load('Scientist Table').build(qt)
    try:
        m = handle.model
        assert m.rowCount(m.index(0, 0)) == 0
        assert m.columnCount(m.index(0, 0)) == 0
        assert m.data(QtCore.QModelIndex()) is None
        assert m.data(m.index(0, 0), QtCore.Qt.DecorationRole) is None
        assert m.headerData(-1, QtCore.Qt.Horizontal) is None
        assert m.headerData(0, QtCore.Qt.Vertical) is None
        assert m.data(m.index(2, 0)) == 'Darwin'
        assert handle.snapshot()['rows'][1][0] == 'Einstein'
    finally:
        handle.close()


def test_falling_blocks_keyboard_timer_pause_and_drop(qt):
    module = load('Falling Blocks')
    handle = module.build(qt)
    try:
        c = handle.controls
        game = c['game']
        assert not game.move(1, 0)
        game.lower()
        game.drop()
        assert not game.rotate()
        c['start'].click()
        for code in [QtCore.Qt.Key_Left, QtCore.Qt.Key_Right, QtCore.Qt.Key_Down,
                     QtCore.Qt.Key_Up, QtCore.Qt.Key_D, QtCore.Qt.Key_Space, QtCore.Qt.Key_A]:
            c['canvas'].keyPressEvent(key(code))
        assert game.pieces == 1 and game.score > 0
        c['game_timer'].timeout.emit()
        c['pause'].click()
        assert game.paused
        assert not game.move(1, 0)
        assert not game.rotate()
        game.drop()
        game.lower()
        c['pause'].click()
        render(c['canvas'])
        game.board = [[0] * 10 for _ in range(22)]
        game.kind = 0
        game.shape = [(0, 0)]
        game.x, game.y = 9, 21
        game.board[-1] = [1] * 9 + [0]
        assert not game.rotate()
        game.pieces = 24
        game.lower()
        assert game.lines == 1 and game.level == 2
        game.board[0] = [1] * 10
        game.spawn()
        assert not game.playing
        game.reset()
        game.kind = 2
        game.shape = list(module.SHAPES[2])
        game.y = 5
        assert game.rotate() and game.rotate(False)
        game.x = 0
        game.shape = [(0, 0), (0, 1)]
        assert not game.rotate()
        assert not game.move(-1, 0)
    finally:
        handle.close()


def test_flow_layout_reflows_at_actual_width(qt, monkeypatch):
    module = load('Flow Layout', 'Layouts')
    monkeypatch.setattr(S, 'launch', lambda builder, *args: builder(qt))
    handle = module.main()
    try:
        area = handle.controls['flow']
        area.resize(180, 300)
        area.resizeEvent(QtGui.QResizeEvent(QtCore.QSize(180, 300), QtCore.QSize(640, 300)))
        handle.controls['reflow']()
        narrow = handle.snapshot()['rows']
        area.resize(1000, 300)
        handle.controls['reflow']()
        assert handle.snapshot()['rows'] < narrow
        assert module.arrange(100, [])[0] == []
        assert len(area.findChildren(QtWidgets.QPushButton)) == 5
    finally:
        handle.close()


def test_designer_dialog_buttons_load_ui_and_finish(qt, monkeypatch):
    module = load('Designer Button Dialog', 'Dialogs')
    monkeypatch.setattr(S, 'launch', lambda builder, *args: builder(qt))
    for standard in [QtWidgets.QDialogButtonBox.Ok, QtWidgets.QDialogButtonBox.Cancel]:
        handle = module.main()
        try:
            box = handle.widget.findChild(QtWidgets.QDialogButtonBox, 'buttons')
            box.button(standard).click()
            expected = QtWidgets.QDialog.Accepted if standard == QtWidgets.QDialogButtonBox.Ok else QtWidgets.QDialog.Rejected
            assert handle.snapshot()['result'] == expected
        finally:
            handle.close()


@pytest.mark.parametrize('title', ['Analog Clock', 'Clock Component'])
def test_clock_optional_shaped_builder_handlers(title, qt):
    handle = load(title).clock(qt, designer=True, shaped=True)
    try:
        c = handle.controls
        face = c['canvas']
        render(face)
        face.mousePressEvent(mouse(QtCore.QEvent.MouseButtonPress))
        face.mouseMoveEvent(mouse(QtCore.QEvent.MouseMove, 40, 40))
        face.mouseReleaseEvent(mouse(QtCore.QEvent.MouseButtonRelease))
        face.contextMenuEvent(QtGui.QContextMenuEvent(QtGui.QContextMenuEvent.Mouse, QtCore.QPoint(3, 3), QtCore.QPoint(3, 3)))
        assert c['context_menu'].actions()[0].text() == 'Exit'
        c['clock_timer'].timeout.emit()
        assert handle.snapshot()['notifications']
    finally:
        handle.close()


def test_animation_movie_play_pause_seek_speed_and_bad_file(qt, tmp_path):
    handle = load('Animated Checker Player').build(qt)
    try:
        c = handle.controls
        assert c['movie'].isValid()
        c['play'].click()
        c['pause'].click()
        assert c['movie'].state() == QtGui.QMovie.Paused
        c['pause'].click()
        c['frame'].setValue(1)
        assert c['movie'].currentFrameNumber() == 1
        c['speed'].setValue(150)
        assert c['movie'].speed() == 150
        c['fit'].setChecked(True)
        assert c['preview'].hasScaledContents()
        c['stop'].click()
        assert c['movie'].currentFrameNumber() == 0
        assert not c['load'](str(tmp_path / 'missing.gif'))
        assert 'not a supported animation' in handle.snapshot()['error']
        c['open'].click()
    finally:
        handle.close()


def test_window_flags_update_preview_and_names(qt, monkeypatch):
    class Widget(QtWidgets.QWidget):
        def setWindowFlags(self, flags):
            super().setWindowFlags(QtCore.Qt.WindowType(flags))
    monkeypatch.setattr(qt.QtGui, 'QWidget', Widget)
    module = load('Window Flag Gallery')
    monkeypatch.setattr(S, 'launch', lambda builder, *args: builder(qt))
    handle = module.main()
    try:
        c = handle.controls
        c['FramelessWindowHint'].setChecked(True)
        c['WindowStaysOnTopHint'].setChecked(True)
        assert 'FramelessWindowHint' in handle.snapshot()['flag_names']
        assert c['preview'].windowFlags() & QtCore.Qt.FramelessWindowHint
        for radio in handle.widget.findChildren(QtWidgets.QRadioButton):
            radio.setChecked(True)
        assert handle.snapshot()['flag_names'][0] == 'Popup'
        c['preview'].findChild(QtWidgets.QPushButton).click()
        assert not c['preview'].isVisible()
    finally:
        handle.close()


def test_widget_gallery_progress_palette_disabled_groups(qt, monkeypatch):
    # PythonQt exposes these native properties as values rather than methods.
    class Dialog(QtWidgets.QDialog):
        palette = property(QtWidgets.QDialog.palette)
    class Progress(QtWidgets.QProgressBar):
        value = property(QtWidgets.QProgressBar.value)
        maximum = property(QtWidgets.QProgressBar.maximum)
    monkeypatch.setattr(qt.QtGui, 'QDialog', Dialog)
    monkeypatch.setattr(qt.QtGui, 'QProgressBar', Progress)
    module = load('Widget Gallery')
    monkeypatch.setattr(S, 'launch', lambda builder, *args: builder(qt))
    handle = module.main()
    try:
        w = handle.widget
        render(w)
        w.timer.timeout.emit()
        assert w.progressBar.value == 100
        assert w.controls['table'].rowCount() == 10
        assert 'Twinkle' in w.controls['poem'].toPlainText()
        w.useStylePaletteCheckBox.setChecked(False)
        w.useStylePaletteCheckBox.setChecked(True)
        w.changeStyle('missing style')
        for box in w.findChildren(QtWidgets.QCheckBox):
            if 'Disable widgets' in box.text():
                box.setChecked(True)
        assert not w.topLeftGroupBox.isEnabled()
        assert w.controls['password'].echoMode() == QtWidgets.QLineEdit.Password
    finally:
        handle.close()


def test_designer_loader_failure_reports_error_and_releases_loader(qt, monkeypatch):
    released = []
    class Loader:
        def load(self, source):
            assert source.isOpen()
            return None
        def errorString(self):
            return 'malformed Designer form'
        def deleteLater(self):
            released.append(True)
    monkeypatch.setitem(sys.modules, 'PythonQt', SimpleNamespace(QtUiTools=SimpleNamespace(QUiLoader=Loader)))
    with pytest.raises(RuntimeError, match='malformed Designer form'):
        load('Designer Button Dialog', 'Dialogs')._load(qt)
    assert released == [True]
