# this_file: tests/test_restored_demos.py
# SPDX-License-Identifier: Apache-2.0
"""Host-free checks for restored demo ownership and pure drawing calculations."""
import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    spec = importlib.util.spec_from_file_location('restored_test', ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_handle_preserves_state_when_owner_refuses_close(monkeypatch):
    class Owner:
        def __init__(self, widget, content):
            self.widget = widget
            self.closed = False

        def close(self):
            return False

    monkeypatch.setitem(sys.modules, 'fly.ap.qt.widgets', types.SimpleNamespace(OwnedWidget=Owner))
    module = load('lessons/src/fontlab_python_lessons/qt_demos.py')
    handle = module.ExampleHandle(object(), dict)
    handle.controls['draft'] = 'retained'
    with pytest.raises(RuntimeError, match='refused Close'):
        handle.close()
    assert handle.controls['draft'] == 'retained'


def test_handle_disconnects_before_native_deletion(monkeypatch):
    events = []

    class Owner:
        def __init__(self, widget, content):
            self.widget, self.closed = widget, False

        def close(self):
            events.append('delete')
            self.closed = True
            return True

    class Signal:
        def connect(self, callback):
            events.append('connect')

        def disconnect(self, callback):
            events.append('disconnect')

    monkeypatch.setitem(sys.modules, 'fly.ap.qt.widgets', types.SimpleNamespace(OwnedWidget=Owner))
    module = load('lessons/src/fontlab_python_lessons/qt_demos.py')
    handle = module.ExampleHandle(object(), dict)
    handle.connect(Signal(), lambda: None)
    handle.cleanup.append(lambda: events.append('stop'))
    handle.close()
    assert events == ['connect', 'stop', 'disconnect', 'delete']
    assert handle.controls == {}


def test_clock_variants_keep_offset_and_shaped_behaviour(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'lessons/src'))
    component = load('Scripts/Widgets/Clock Component.py')
    shaped = load('Scripts/Widgets/Shaped Clock.py')
    calls = []
    monkeypatch.setattr(component, 'clock', lambda qt, **kwargs: calls.append(kwargs))
    monkeypatch.setattr(shaped, 'clock', lambda qt, **kwargs: calls.append(kwargs))
    component.build(None)
    shaped.build(None)
    assert calls == [dict(designer=True, shaped=False), dict(designer=False, shaped=True)]
    assert component.angles(3, 30, 0, 2) == (165, 180)


def test_editor_preserves_unsaved_text_and_never_overwrites(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(ROOT / 'lessons/src'))
    module = load('Scripts/Widgets/Text Editor.py')

    class Text:
        def __init__(self, parent):
            self.text, self.modified = 'unsaved draft', True

        def document(self):
            return self

        def isModified(self):
            return self.modified

        def setModified(self, modified):
            self.modified = modified

        def setPlainText(self, text):
            self.text = text

        def toPlainText(self):
            return self.text

    class Session:
        def __init__(self, *args):
            import shutil
            self.temporary = tmp_path / "temporary-dialog-folder"
            self.h = types.SimpleNamespace(
                controls={}, close=lambda: shutil.rmtree(self.temporary)
            )
            self.window = types.SimpleNamespace(setWindowTitle=lambda title: None)
            self.g = types.SimpleNamespace(QPlainTextEdit=Text)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def vertical(self):
            pass

        def add(self, obj):
            pass

        def keep(self, name, obj):
            self.h.controls[name] = obj
            return obj

        def label(self, text):
            return types.SimpleNamespace(setText=lambda text: None)

        def button(self, name, title, callback):
            self.h.controls[name] = callback

        def choose(self, callback, save=False):
            self.temporary.mkdir(exist_ok=True)
            self.h.controls["chooser_directory"] = str(self.temporary)
            return types.SimpleNamespace(
                setDirectory=lambda path: self.h.controls.update(chooser_directory=path)
            )

    monkeypatch.setattr(module.S, 'Session', Session)
    handle = module.build(None)
    controls = handle.controls
    existing = tmp_path / 'existing.txt'
    existing.write_text('original')
    controls['open_file'](str(existing))
    assert controls['text'].text == 'unsaved draft'
    assert controls['can_close']() is False
    controls['save_file'](str(existing))
    assert existing.read_text() == 'original'
    assert controls['can_close']() is False
    created = tmp_path / 'new.txt'
    controls['save_file'](str(created))
    assert created.read_text() == 'unsaved draft'
    assert controls['can_close']() is True
    controls['save']()
    assert controls['chooser_directory'] == str(Path.home())
    assert controls['chooser_directory'] != str(tmp_path / 'temporary-dialog-folder')
    handle.close()
    assert created.read_text() == 'unsaved draft'
