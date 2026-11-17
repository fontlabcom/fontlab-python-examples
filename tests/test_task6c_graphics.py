# this_file: tests/test_task6c_graphics.py
# SPDX-License-Identifier: Apache-2.0
"""Exercise the restored graphics scenes through real offscreen Qt surfaces."""
import importlib.util
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lessons/src'))


def load(path):
    spec = importlib.util.spec_from_file_location(Path(path).stem, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def qt(monkeypatch):
    from PySide6 import QtCore, QtGui, QtWidgets, QtStateMachine, QtTest
    from fontlab_python_lessons import qt_demos
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    class Owner:
        def __init__(self, widget, content):
            self.widget, self.closed = widget, False

        def close(self):
            if self.closed:
                return True
            if not self.widget.close():
                return False
            self.closed = True
            self.widget.deleteLater()
            return True

    def connect(self, obj, signature, callback):
        signal = getattr(obj, signature.split('(')[0])
        signal.connect(callback)
        self.connections.append((signal, None, callback))

    class State(QtStateMachine.QState):
        def addTransition(self, obj, signature, target):
            return super().addTransition(getattr(obj, signature.lstrip('2').split('(')[0]), target)

    core = SimpleNamespace(**{n: getattr(QtCore, n) for n in dir(QtCore)})
    core.QState, core.QStateMachine = State, QtStateMachine.QStateMachine
    gui = SimpleNamespace(**{n: getattr(m, n) for m in (QtGui, QtWidgets)
                             for n in dir(m) if n.startswith('Q')})
    class FileDialog(QtWidgets.QFileDialog):
        AcceptSave = QtWidgets.QFileDialog.AcceptSave
        AcceptOpen = QtWidgets.QFileDialog.AcceptOpen
        def __init__(self, *args):
            super().__init__(*args)
            self.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
    gui.QFileDialog = FileDialog
    monkeypatch.setitem(sys.modules, 'fly.ap.qt.widgets', SimpleNamespace(OwnedWidget=Owner))
    monkeypatch.setattr(qt_demos.ExampleHandle, 'connect_old', connect)
    yield SimpleNamespace(QtCore=core, QtGui=gui, app=app, test=QtTest.QTest)
    app.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
    app.processEvents()


def picture(qt, widget):
    image = qt.QtGui.QImage(widget.size(), qt.QtGui.QImage.Format_ARGB32)
    image.fill(qt.QtGui.QColor('magenta'))
    qt.QtGui.QWidget.render(widget, image)
    assert not image.isNull()
    assert image.pixelColor(image.width() // 2, image.height() // 2) != qt.QtGui.QColor('magenta')
    return image


@pytest.mark.parametrize('title', ['Animated App Chooser', 'Animated States', 'Animated Tiles', 'Moving Blocks'])
def test_state_scenes_transition_and_render(title, qt, monkeypatch):
    from fontlab_python_lessons import qt_demos
    m = load(f'Scripts/Graphics/{title}.py')
    monkeypatch.setattr(qt_demos, 'launch', lambda build, key, title: build(qt))
    h = m.main()
    try:
        c = h.controls
        h.widget.show()
        qt.app.processEvents()
        if title == 'Animated App Chooser':
            for i, choice in enumerate(c['choices']):
                choice.click()
                qt.app.processEvents()
                assert h.inspect_ui()['index'] == i
            assert len(c['scene'].items()) == 4
        elif title == 'Animated States':
            for i in range(1, 4):
                c['cycle'].click()
                qt.app.processEvents()
                assert h.inspect_ui()['state'] == i % 3
            c['editor'].setPlainText('Retained editor draft')
            assert 'Retained' in c['editor'].toPlainText()
        elif title == 'Animated Tiles':
            for name, choice in zip(('Grid', 'Ellipse', 'Figure eight', 'Scatter', 'Center'), c['choices']):
                choice.click()
                qt.app.processEvents()
                assert h.inspect_ui() == {'tiles': 64, 'layout': name}
                assert len(set(m.positions(name))) == 64
        else:
            for expected in (3, 6, 2):
                c['timer'].timeout.emit()
                qt.app.processEvents()
                assert h.inspect_ui()['state'] == expected
            assert len(c['blocks']) == 4
        picture(qt, c['view'])
    finally:
        h.close()
    assert h.owner.closed


def test_stick_figure_poses_keys_constraint_and_lightning(qt, monkeypatch):
    m = load('Scripts/Graphics/Animated Stick Figure.py')
    monkeypatch.setattr(m.random, 'Random', lambda: SimpleNamespace(randrange=lambda n: 0))
    h = m.build(qt)
    try:
        c = h.controls
        for key, name in ((qt.QtCore.Qt.Key_J, 'jump'), (qt.QtCore.Qt.Key_D, 'dance'),
                          (qt.QtCore.Qt.Key_C, 'rest'), (qt.QtCore.Qt.Key_Escape, 'rest')):
            qt.test.keyClick(c['view'], key)
            assert h.inspect_ui()['activity'] == name
        qt.test.keyClick(c['view'], qt.QtCore.Qt.Key_A)
        c['joints'][1].setPos(c['joints'][0].pos())
        c['timer'].timeout.emit()
        first = c['bones'][0].line()
        assert first.length() == pytest.approx(25)
        c['storm'].timeout.emit()
        assert h.inspect_ui()['activity'] == 'dead'
        assert c['flash'].isActive()
        c['storm'].timeout.emit()
        c['flash'].timeout.emit()
        assert c['scene'].backgroundBrush().color() == qt.QtGui.QColor('white')
        picture(qt, c['view'])
        assert m.value(SimpleNamespace(field=3), 'field') == 3
    finally:
        h.close()


def test_easing_gallery_controls_both_motion_paths(qt):
    h = load('Scripts/Graphics/Easing Curve Gallery.py').build(qt)
    try:
        c = h.controls
        assert c['curves'].count() == 47
        for row in (0, 2, 9, 40):
            c['curves'].setCurrentRow(row)
            for name in ('period', 'amplitude', 'overshoot'):
                c[name].setValue(2.0)
            c['timer'].timeout.emit()
            assert c['moving'].pos().y() == 190
        c['path'].setCurrentIndex(1)
        c['timer'].timeout.emit()
        p = c['moving'].pos()
        assert math.hypot(p.x() - 300, p.y() - 190) == pytest.approx(150)
        picture(qt, c['view'])
    finally:
        h.close()


def test_lighting_timer_moves_light_and_shadows(qt):
    h = load('Scripts/Graphics/Scene Lighting Effect.py').build(qt)
    try:
        before = h.inspect_ui()['light']
        h.controls['light_timer'].timeout.emit()
        assert h.inspect_ui()['light'] != before
        assert len(h.controls['scene'].items()) == 26
        effects = [item.graphicsEffect() for item in h.controls['scene'].items() if item.graphicsEffect()]
        assert len(effects) == 25
        assert len({(e.offset().x(), e.offset().y()) for e in effects}) == 25
        picture(qt, h.controls['view'])
    finally:
        h.close()


def test_scene_shapes_main_creates_movable_selectable_items(qt, monkeypatch):
    from module_doubles import install_module
    m = load('Scripts/Graphics/Graphics Scene Shapes.py')
    install_module(monkeypatch, 'PythonQt', SimpleNamespace(QtCore=qt.QtCore, QtGui=qt.QtGui))
    install_module(monkeypatch, 'fly.ap.core.scripting', SimpleNamespace(show_script_dialog=lambda cls, key: cls(None)))
    view = m.main()
    try:
        items = view.shape_scene.items()
        assert len(items) == 3
        for item in items:
            item.setSelected(True)
            item.moveBy(3, 4)
            assert item.isSelected()
            assert item.flags() & qt.QtGui.QGraphicsItem.ItemIsMovable
        assert len(view.shape_scene.selectedItems()) == 3
        picture(qt, view)
    finally:
        view.close()


@pytest.mark.parametrize('kind', ['mice', 'elastic'])
def test_colliding_scene_simulation_input_zoom_and_edges(kind, qt, monkeypatch):
    m = load('Scripts/Graphics/Colliding Scene Mice.py')
    monkeypatch.setattr(m, 'KIND', kind)
    h = m.build(qt)
    try:
        c, state = h.controls, h.controls['controller'].state
        c['simulation'].stop()
        c['nodes'][0].setPos(270, 220)
        c['nodes'][1].setPos(270, 220)
        c['tick']()
        assert state['ticks'] == 1
        assert all(-275 <= n.pos().x() <= 275 for n in c['nodes'])
        before = [(n.pos().x(), n.pos().y()) for n in c['nodes']]
        for key in (qt.QtCore.Qt.Key_Space, qt.QtCore.Qt.Key_Return,
                    qt.QtCore.Qt.Key_Plus, qt.QtCore.Qt.Key_Minus,
                    qt.QtCore.Qt.Key_Left, qt.QtCore.Qt.Key_A):
            qt.test.keyClick(c['view'], key)
        assert [(n.pos().x(), n.pos().y()) for n in c['nodes']] != before
        c['zoom'](100)
        assert state['zoom'] < 5
        wheel = qt.QtGui.QWheelEvent(qt.QtCore.QPointF(20, 20), qt.QtCore.QPointF(20, 20),
                                     qt.QtCore.QPoint(0, 0), qt.QtCore.QPoint(0, 120),
                                     qt.QtCore.Qt.NoButton, qt.QtCore.Qt.NoModifier,
                                     qt.QtCore.Qt.NoScrollPhase, False)
        c['view'].wheelEvent(wheel)
        assert state['zoom'] > 1
        if kind == 'elastic':
            c['nodes'][1].setPos(c['nodes'][0].pos())
            c['shuffle']()
            c['tick']()
            assert len(c['edges']) == 12
            assert any(edge[2].line().length() > 0 for edge in c['edges'])
        else:
            assert len(c['decorations']) == 7
            assert c['decorations'][0].boundingRect().width() == 60
        picture(qt, c['view'])
    finally:
        h.close()


@pytest.mark.parametrize('kind', ['circles', 'basic', 'paths', 'transformations'])
def test_concentric_painter_all_retained_modes_and_controls(kind, qt, monkeypatch):
    m = load('Scripts/Drawing/Concentric Circles.py')
    monkeypatch.setattr(m, 'KIND', kind)
    h = m.build(qt)
    try:
        c, state = h.controls, h.controls['controller'].state
        if kind == 'circles':
            c['animation'].timeout.emit()
            assert state['frame'] == 2
        elif kind == 'transformations':
            for i in range(3):
                c[f'Operation {i + 1}'].setCurrentIndex(i + 1)
            assert state['operations'] == [1, 2, 3]
            for i in range(4):
                c['Shape'].setCurrentIndex(i)
                picture(qt, c['canvas'])
        else:
            for key in ('Pen', 'Cap', 'Join', 'Brush', 'Fill rule', 'color1', 'color2'):
                for index in range(c[key].count()):
                    c[key].setCurrentIndex(index)
                    picture(qt, c['canvas'])
            c['Line width'].setValue(8)
            c['Rotation'].setValue(20)
            c['Antialias'].click()
            c['Transform'].click()
            for index in range(c['Shape'].count()):
                c['Shape'].setCurrentIndex(index)
                picture(qt, c['canvas'])
        image = picture(qt, c['canvas'])
        assert state['paints'] > 0
        assert len({image.pixel(x, 80) for x in range(20, min(image.width(), 300))}) > 1
    finally:
        h.close()


@pytest.mark.parametrize('path', ['Scripts/Drawing/Concentric Circles.py', 'Scripts/Graphics/Colliding Scene Mice.py'])
def test_scene_session_helpers_and_failed_build_clean_up(path, qt, monkeypatch, tmp_path):
    m = load(path)
    s = m.Session(qt, 'helper operations', main=True)
    try:
        assert s.window.centralWidget() is s.panel
        assert m.value(SimpleNamespace(x=7), 'x') == 7
        s.state['dragging'] = True
        event = qt.QtGui.QCloseEvent()
        s.window.closeEvent(event)
        assert not event.isAccepted()
        with pytest.raises(RuntimeError, match='Finish the drag'):
            s.prepare_close()
        s.state['dragging'] = False
        calls = []
        s.before_close = lambda: calls.append('before')
        s.window.closeEvent(event)
        assert calls == ['before']
        s.before_close = None
        b = s.button('act', lambda: calls.append('clicked'))
        b.click()
        s.combo('pick', ['a', 'b'], lambda i: calls.append(i)).setCurrentIndex(1)
        timer = s.timer('idle', lambda: calls.append('tick'), 100, start=False, once=True)
        timer.timeout.emit()
        menu = qt.QtGui.QMenu(s.window)
        s.action(menu, 'action', lambda: calls.append('action'), check=True).trigger()
        assert calls == ['before', 'clicked', 1, 'tick', 'action']
        root = s.root()
        assert s.path(str(root / 'new.txt')) == (root / 'new.txt').resolve()
        assert s.root() == root
        for bad in (str(root), str(tmp_path / 'outside.txt')):
            with pytest.raises(ValueError):
                s.path(bad)
        s.message('Useful message')
        s.choose(False, lambda name: calls.append(name))
        s.pending[-1].fileSelected.emit(str(root / 'selected.txt'))
        assert calls[-1].endswith('selected.txt')
        def fail(name):
            raise OSError('refused file')
        s.choose(True, fail)
        s.pending[-1].fileSelected.emit(str(root / 'failed.txt'))
        assert s.state['error'] == 'refused file'
        routed = s.connect(b, 'clicked()', lambda: calls.append('late'))
        s.closing = True
        routed()
        assert calls[-1] != 'late'
    finally:
        s.state['dragging'] = False
        s.handle.close()
    assert not root.exists()
    monkeypatch.setattr(m, 'configure', lambda session: (_ for _ in ()).throw(ValueError('build failed')))
    with pytest.raises(ValueError, match='build failed'):
        m.build(qt)


def test_painted_editor_marks_pixels_and_file_safety(qt, tmp_path):
    h = load('Scripts/Multimedia/Painted Text Editor.py').build(qt)
    try:
        c = h.controls
        editor = c['text']
        editor.insertPlainText('A draft Ω')
        assert not c['can_close']()
        first = tmp_path / 'first.txt'
        c['save_file'](str(first))
        assert first.read_text() == 'A draft Ω'
        assert c['can_close']()
        editor.selectAll()
        editor.insertPlainText('changed')
        c['save_file'](str(first))
        assert first.read_text() == 'A draft Ω'
        c['open_file'](str(first))
        assert editor.toPlainText() == 'changed'
        c['discard'].click()
        c['open_file'](str(first))
        assert editor.toPlainText() == 'A draft Ω'
        c['open_file'](str(tmp_path / 'missing'))
        bad = tmp_path / 'invalid.txt'
        bad.write_bytes(b'\xff')
        c['open_file'](str(bad))
        editor.show()
        qt.test.mouseClick(editor.viewport(), qt.QtCore.Qt.LeftButton, pos=qt.QtCore.QPoint(30, 40))
        assert c['holes'] == [(30, 40)]
        image = picture(qt, editor)
        assert image.width() > 30
        assert editor.viewport().grab().toImage().pixelColor(30, 40) == qt.QtGui.QColor('#885522')
        c['clear_marks'].click()
        assert c['holes'] == []
        for name in ('open', 'save'):
            c[name].click()
            assert c['file_dialog'].directory().absolutePath() == str(Path.home())
    finally:
        h.close()


def test_raster_and_opengl_surfaces_share_animation(qt, monkeypatch):
    # Offscreen cannot allocate a GL context; keep the real QWidget paint device.
    class SoftwareGL(qt.QtGui.QWidget):
        def setFormat(self, format):
            self.samples = format.samples()
    monkeypatch.setattr(qt.QtGui, 'QOpenGLWidget', SoftwareGL, raising=False)
    m = load('Scripts/OpenGL/Raster And OpenGL Painting.py')
    h = m.build(qt)
    try:
        c = h.controls
        assert c['opengl'].samples == 4
        first = picture(qt, c['raster'])
        c['timer'].timeout.emit()
        assert h.inspect_ui() == {'phase': 1, 'circles': 30}
        second = picture(qt, c['raster'])
        assert first != second
        # paintGL uses the same painter code; route it to a live QImage.
        image = qt.QtGui.QImage(300, 240, qt.QtGui.QImage.Format_ARGB32)
        image.fill(qt.QtGui.QColor('magenta'))
        real_painter = qt.QtGui.QPainter
        monkeypatch.setattr(qt.QtGui, 'QPainter', type('PainterFactory', (), {
            'Antialiasing': real_painter.Antialiasing,
            '__new__': lambda cls, canvas: real_painter(image)}))
        c['opengl'].paintGL()
        assert image.pixelColor(0, 0) == qt.QtGui.QColor('#f6f2e8')
    finally:
        h.close()


@pytest.mark.parametrize('path', ['Scripts/Graphics/Animated Stick Figure.py',
    'Scripts/Graphics/Easing Curve Gallery.py', 'Scripts/Graphics/Scene Lighting Effect.py',
    'Scripts/Graphics/Colliding Scene Mice.py', 'Scripts/Drawing/Concentric Circles.py',
    'Scripts/OpenGL/Raster And OpenGL Painting.py', 'Scripts/Multimedia/Painted Text Editor.py'])
def test_graphics_menu_entrypoint_launches_behaviour(path, qt, monkeypatch):
    from fontlab_python_lessons import qt_demos
    m = load(path)
    if 'OpenGL' in path:
        class GL(qt.QtGui.QWidget):
            def setFormat(self, format):
                pass
        monkeypatch.setattr(qt.QtGui, 'QOpenGLWidget', GL, raising=False)
    monkeypatch.setattr(qt_demos, 'launch', lambda build, key, title: build(qt))
    h = m.main()
    assert h.widget.windowTitle()
    assert h.controls
    h.close()
    assert h.owner.closed
