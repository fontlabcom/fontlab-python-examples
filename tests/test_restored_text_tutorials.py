# this_file: tests/test_restored_text_tutorials.py
"""Exercise restored text workflows with real offscreen Qt and pure parsers."""
import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATHS = sorted(p for folder in ('Main Windows', 'Rich Text', 'Tutorials')
               for p in (ROOT / 'Scripts' / folder).glob('*.py'))


def load(path):
    spec = importlib.util.spec_from_file_location('restored_text_' + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def qt(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(ROOT / 'lessons/src'))
    from PySide6 import QtCore, QtGui, QtWidgets, QtPrintSupport
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    gui = types.SimpleNamespace(**{name: getattr(module, name)
        for module in (QtGui, QtWidgets, QtPrintSupport) for name in dir(module)
        if name.startswith('Q')})

    class Owner:
        def __init__(self, widget, content):
            self.widget, self.closed = widget, False

        def close(self):
            self.closed = True
            self.widget.hide()
            self.widget.deleteLater()
            return True

        def __getattr__(self, name):
            return getattr(self.widget, name)

    monkeypatch.setitem(sys.modules, 'fly.ap.qt.widgets', types.SimpleNamespace(OwnedWidget=Owner))
    from fontlab_python_lessons.qt_demos import ExampleHandle

    def connect(self, obj, signature, slot):
        QtCore.QObject.connect(obj, QtCore.SIGNAL(signature), slot)
        self.connections.append((obj, signature, slot))

    def disconnect(self):
        while self.connections:
            obj, signature, slot = self.connections.pop()
            QtCore.QObject.disconnect(obj, QtCore.SIGNAL(signature), slot)

    monkeypatch.setattr(ExampleHandle, 'connect_old', connect)
    monkeypatch.setattr(ExampleHandle, '_disconnect', disconnect)
    yield types.SimpleNamespace(QtCore=QtCore, QtGui=gui), app
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)


@pytest.mark.parametrize('path', PATHS, ids=lambda p: p.stem)
def test_restored_text_builds_modeless_and_closes(path, qt, monkeypatch, tmp_path):
    module = load(path)
    if hasattr(module, 'mkdtemp'):
        def folder(**kwargs):
            result = tmp_path / 'output'
            result.mkdir(exist_ok=True)
            return str(result)
        monkeypatch.setattr(module, 'mkdtemp', folder)
    handle = module.build(qt[0])
    assert handle.widget is not None
    assert handle.controls
    handle.widget.show()
    qt[1].processEvents()
    handle.close()
    assert handle.owner.closed


def test_order_quantities_validate_and_letter_escapes(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'lessons/src'))
    module = load(ROOT / 'Scripts/Rich Text/Order Letter Form.py')
    assert module.quantities(['0', ' 2 ', '10000']) == [0, 2, 10000]
    for bad in ('-1', '10001', 'abc', ''):
        with pytest.raises(ValueError):
            module.quantities([bad])
    result = module.letter('<Alice>', 'A & B\nC', [1, 2, 0], False)
    assert '&lt;Alice&gt;' in result and 'A &amp; B<br>C' in result
    assert 'Total: 17.00' in result


def test_highlighter_handles_multiline_comments(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'lessons/src'))
    module = load(ROOT / 'Scripts/Rich Text/Source Syntax Highlighter.py')
    spans, inside = module.spans('int x; /* comment')
    assert spans[0] == (0, 3, 'keyword') and inside
    spans, inside = module.spans('end */ return 0;', inside)
    assert spans[0] == (0, 6, 'comment') and not inside
    assert (7, 6, 'keyword') in spans


def test_contact_stages_edit_validate_roundtrip_and_preserve_output(qt, monkeypatch, tmp_path):
    module = load(ROOT / 'Scripts/Tutorials/Address Collection Stage 7.py')
    monkeypatch.setattr(module, 'mkdtemp', lambda **kwargs: str(tmp_path))
    handle = module.build(qt[0])
    controls = handle.controls
    controls['Add'].click()
    controls['name'].setText('Alice')
    controls['address'].setPlainText('One Street\nTown')
    controls['submit']()
    assert controls['contacts'] == {'Alice': 'One Street\nTown'}
    controls['Add'].click()
    controls['name'].setText('Bob')
    controls['address'].setPlainText('Two Street')
    controls['submit']()
    controls['navigate'](-1)
    assert controls['name'].text() == 'Alice'
    output = tmp_path / 'contacts.json'
    controls['save_file'](output)
    bad = tmp_path / 'bad.json'
    bad.write_text('{"name": 4}')
    with pytest.raises(ValueError):
        controls['load_file'](bad)
    assert len(controls['contacts']) == 2
    controls['remove'](True)
    controls['load_file'](output)
    assert len(controls['contacts']) == 2
    card = tmp_path / 'alice.vcf'
    controls['export_file'](card)
    assert b'BEGIN:VCARD' in card.read_bytes()
    handle.close()
    assert output.exists() and card.exists()


def test_rich_editor_guard_and_saved_assets_survive_close(qt, monkeypatch, tmp_path):
    module = load(ROOT / 'Scripts/Rich Text/Rich Text Editor.py')
    monkeypatch.setattr(module, 'mkdtemp', lambda **kwargs: str(tmp_path))
    handle = module.build(qt[0])
    controls = handle.controls
    controls['editor'].insertPlainText('Important draft')
    assert controls['can_close']() is False
    output = tmp_path / 'saved.html'
    assert controls['save_file'](output)
    assert controls['can_close']() is True
    handle.close()
    assert 'Important draft' in output.read_text()
