# this_file: tests/test_restored_remaining.py
"""Pure boundaries and real offscreen UI checks for the remaining restorations."""
import importlib.util
import queue
from pathlib import Path
import sys
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lessons/src'))


def load(path):
    spec = importlib.util.spec_from_file_location(Path(path).stem, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('title', ['Local Fortune Client', 'Local Fortune Server'])
def test_local_fortune_frames_handle_partial_and_invalid_data(title):
    m = load(f'Scripts/IPC/{title}.py')
    encoded = m.packet('A curve — 曲線')
    assert m.decode(encoded) == 'A curve — 曲線'
    for end in range(len(encoded)):
        assert m.decode(encoded[:end]) is None
    with pytest.raises(ValueError):
        m.decode(encoded + b'x')
    with pytest.raises(ValueError):
        m.decode(b'\x00\x01x')
    with pytest.raises(ValueError):
        m.packet('x' * 40000)


@pytest.mark.parametrize('title', ['Semaphore Transfer', 'Condition Variable Transfer'])
def test_transfer_preserves_order_and_stops_under_backpressure(title):
    m = load(f'Scripts/Threads/{title}.py')
    m.TOTAL = 1024
    worker = m.Transfer()
    worker.start()
    chunks = []
    deadline = time.monotonic() + 3
    try:
        while sum(map(len, chunks)) < m.TOTAL and time.monotonic() < deadline:
            try:
                chunks.append(worker.messages.get(timeout=.1))
            except queue.Empty:
                pass
    finally:
        worker.stop()
    assert ''.join(chunks) == 'ACGT' * 256
    m.TOTAL = 100000
    worker = m.Transfer()
    worker.start()
    worker.stop()
    assert not any(t.is_alive() for t in worker.threads)


def test_fractal_scanline_separates_interior_and_exterior():
    m = load('Scripts/Threads/Mandelbrot Explorer.py')
    assert m.scanline(2, 2, 1, (0, 0), 0, 24) == [0, 0]
    assert all(m.scanline(3, 2, 1, (3, 3), .01, 24))


def test_schema_examples_and_external_references():
    m = load('Scripts/XML/Schema Validation.py')
    for i in range(3):
        for text in m.documents(i):
            assert m.safe_xml(text) is not None
    for text in ['<!DOCTYPE a><a/>', '<a xmlns:x="x"><x:include/></a>', '<a schemaLocation="https://example.com/x"/>']:
        with pytest.raises(ValueError):
            m.safe_xml(text)


@pytest.mark.parametrize('title', ['Build Word Form', 'Load Word Form', 'Load Word Form With Actions'])
def test_word_form_add_clear_and_cleanup(title, monkeypatch):
    from types import SimpleNamespace
    from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools
    from fontlab_python_lessons import qt_demos as support
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    class Owner:
        def __init__(self, widget, content):
            self.widget, self.closed = widget, False
        def close(self):
            self.closed = True
            self.widget.deleteLater()
            return True
    monkeypatch.setitem(sys.modules, 'fly.ap.qt.widgets', SimpleNamespace(OwnedWidget=Owner))
    def connect_old(self, obj, signature, slot):
        assert QtCore.QObject.connect(obj, QtCore.SIGNAL(signature), slot)
        self.callbacks.append(slot)
    monkeypatch.setattr(support.ExampleHandle, 'connect_old', connect_old)
    gui = SimpleNamespace(**{name: getattr(QtGui, name) for name in dir(QtGui)})
    for name in dir(QtWidgets):
        if name.startswith('Q'): setattr(gui, name, getattr(QtWidgets, name))
    qt = SimpleNamespace(QtCore=QtCore, QtGui=gui, QtUiTools=QtUiTools)
    m = load(f'Scripts/UI Loading/{title}.py')
    handle = m.build(qt)
    try:
        handle.controls['Add'].click()
        assert handle.controls['items'].count() == len(m.WORDS)
        handle.controls['Clear'].click()
        assert handle.controls['items'].count() == 0
    finally:
        handle.close()
        app.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
