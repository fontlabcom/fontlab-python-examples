# this_file: lessons/candidate_tests/models_candidate/test_namespace.py
"""Both public APIs must coexist regardless of checkout/source/import precedence."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LEGACY_ROOT = Path(os.environ.get("LEGACY_EXAMPLES_SOURCE", str(ROOT.parent))).resolve()


@pytest.mark.parametrize("source_first", [False, True])
@pytest.mark.parametrize("lessons_first", [False, True])
def test_legacy_and_lessons_when_path_or_import_order_changes_then_both_apis_remain_distinct(
    source_first, lessons_first
):
    code = """
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace as NS
root = Path(ROOT_PATH)
legacy_root = Path(LEGACY_PATH)
paths = [root / 'src', legacy_root] if SOURCE_FIRST else [legacy_root, root / 'src']
sys.path[:0] = [str(path) for path in paths]
order = ['fontlab_python_lessons', 'fontlab_python_examples'] if LESSONS_FIRST else ['fontlab_python_examples', 'fontlab_python_lessons']
for name in order:
    importlib.import_module(name)
import fontlab_python_examples as legacy
import fontlab_python_lessons as lessons
from fontlab_python_examples import launcher
assert Path(legacy.__file__).resolve() == legacy_root / 'fontlab_python_examples/__init__.py'
assert Path(lessons.__file__).resolve() == root / 'src/fontlab_python_lessons/__init__.py'
assert all(getattr(legacy, name) is getattr(launcher, name) for name in legacy.__all__)
assert {'available', 'close', 'describe', 'get', 'inspect', 'launch'} == set(legacy.__all__)
assert legacy.available() and legacy.describe('QLabel')['name'] == 'QLabel'
assert legacy.inspect('QLabel')['launched'] is False
events = []
handle = NS(owner=NS(closed=False), widget=NS(inherits=lambda name: False, show=lambda: events.append('show')))
handle.snapshot = lambda: {'launched': True, 'closed': handle.owner.closed}
handle.close = lambda: setattr(handle.owner, 'closed', True)
launcher._host = lambda: object()
launcher._builder = lambda record: lambda qt: handle
assert legacy.launch('QLabel') is legacy.get('QLabel') is handle
assert legacy.inspect('QLabel')['launched'] is True
legacy.close('QLabel')
assert handle.owner.closed and events == ['show']
dialog = object()
sys.modules['fly.ap.scripting'] = NS(show_script_dialog=lambda cls, key: (cls, key))
sys.modules['fontlab_python_lessons.ui'] = NS(dialog_type=lambda name: dialog)
assert lessons.launch('glyph-name-filter') == (dialog, 'examples-glyph-name-filter')
assert legacy.launch is not lessons.launch
assert 'PythonQt' not in sys.modules and 'fontlab' not in sys.modules
"""
    code = (
        code.replace("ROOT_PATH", repr(str(ROOT)))
        .replace("LEGACY_PATH", repr(str(LEGACY_ROOT)))
        .replace("SOURCE_FIRST", repr(source_first))
        .replace("LESSONS_FIRST", repr(lessons_first))
    )
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code], capture_output=True, text=True, timeout=10, check=False
    )
    assert result.returncode == 0, result.stderr
