# this_file: tests/_wp09_routes.py
"""Resolve retained identity bytes separately from live migrated profile code."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT.parent / 'fontlab-fontlabapp/src/fontlabapp/fontui/core_pythonqt_labs/profiles'
ROWS = {row['source']['path']: row for row in json.loads((ROOT / 'menu-consolidations.json').read_text())['transitions']}
RENAMED = {
    'Expandable Glyph Search': 'expandable_search',
    'Font Units Calculator': 'units_calculator',
    'Calendar Proof Builder': 'calendar_proof',
    'Deferred Glyph Report Drag': 'deferred_glyph_report',
}
SPEC = importlib.util.spec_from_file_location('wp09_historical_layout', ROOT.parent / 'fontlab-python-scriptmix/menu_layout.py')
LAYOUT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAYOUT)


def production_path(path):
    """Read/execute the actual App implementation; never execute identity bytes."""
    path = Path(path)
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError:
        return path
    if relative not in ROWS:
        return path
    name = RENAMED.get(path.stem, path.stem.lower().replace(' ', '_').replace('-', '_'))
    implementation = APP / (name + '.py')
    return implementation if implementation.is_file() else path


def source_bytes(path):
    """Verify an immutable pre-consolidation identity, or read unaffected bytes."""
    path = Path(path)
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.read_bytes()
    row = ROWS.get(relative)
    return LAYOUT.source_bytes(ROOT, row['source']) if row and 'compatibility_launcher' in row else path.read_bytes()


def assert_compat_route(monkeypatch, path, entry, api_module):
    """Check frozen delegate identity and the current selected-profile launch."""
    import ast
    import runpy
    from types import ModuleType

    from module_doubles import install_module

    path = Path(path)
    historical = ast.parse(source_bytes(path), feature_version=(3, 11))
    assert any(
        isinstance(node, ast.ImportFrom)
        and node.module == api_module
        and entry in {alias.name for alias in node.names}
        for node in ast.walk(historical)
    ), 'Keep the exact original API identity as data, never execute its archived body'
    row = ROWS[path.relative_to(ROOT).as_posix()]
    titles = ['Model Filtering Lab', 'Tree Models Lab', 'Metrics Controls Lab',
              'Calendar Lab', 'Completion Lab', 'Drag Drop Lab',
              'Proof Composition Lab', 'Unicode Lab', 'Review Model Lab']
    lab = f'E{titles.index(Path(row["destination"]["path"]).stem) + 1:02d}'
    calls = []
    module = ModuleType('fly.ap.studios.core_pythonqt_labs')
    result = object()
    module.show = lambda key, profile: calls.append((key, profile)) or result
    install_module(monkeypatch, module.__name__, module)
    namespace = runpy.run_path(str(path), run_name='inspection')
    assert calls == [], 'Inspection must remain lazy'
    assert namespace['main']() is result
    runpy.run_path(str(path), run_name='__main__')
    assert calls == [(lab, path.stem), (lab, path.stem)]


def run_profile(path, **kwargs):
    """Run live production code with the pre-existing suite's dependency doubles.

    The migration replaces Fly's aliases with App/native imports. Adapt those
    imports within this module only; real App imports elsewhere stay real.
    """
    import builtins
    import runpy
    import sys
    from types import SimpleNamespace

    target = production_path(path)
    if target == Path(path):
        return runpy.run_path(str(path), **kwargs)
    original = builtins.__import__

    def import_dependency(name, globals=None, locals=None, fromlist=(), level=0):
        fly = sys.modules.get('fly')
        aliases = {'PythonQt': 'qt', 'fontlab': 'fl', 'fontgate': 'fg'}
        if not level and fly is not None and name in aliases and hasattr(fly, aliases[name]):
            return getattr(fly, aliases[name])
        if not level and name.startswith('fontlabapp.'):
            alias = 'fly.ap.' + name.removeprefix('fontlabapp.')
            if alias in sys.modules:
                return sys.modules[alias] if fromlist else sys.modules['fly.ap']
        if name == 'fontlabapp' and '_native' in fromlist and fly is not None:
            actual = original(name, globals, locals, fromlist, level)
            return SimpleNamespace(_native=lambda key: getattr(fly, aliases[key]) if key in aliases and hasattr(fly, aliases[key]) else actual._native(key))
        return original(name, globals, locals, fromlist, level)

    launch = kwargs.get('run_name') == '__main__'
    if launch:
        kwargs['run_name'] = 'inspection'
    namespace = runpy.run_path(str(target), init_globals={'__builtins__': {**vars(builtins), '__import__': import_dependency}}, **kwargs)
    if launch:
        namespace['main']()
    return namespace


def production_relative(path):
    """Return the this_file identity of the live implementation."""
    target = production_path(path)
    root = ROOT.parent / "fontlab-fontlabapp" if target.is_relative_to(APP) else ROOT
    return target.relative_to(root).as_posix()
