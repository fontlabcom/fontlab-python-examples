# this_file: tests/test_echopy_native_examples.py
"""Offline tests for the Echopy signature-reading and owned-descriptor examples."""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(f"echopy_example_{name}", ROOT / "examples/echopy" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sigs = _load("signature_reading")
owned = _load("owned_descriptors")


class Plain:
    def __init__(self, x, y=0):
        self.x = x

    def move(self):
        return 1


def test_read_signature_when_python_class_then_known_signature():
    assert sigs.read_signature(Plain) == ("(x, y=0)", True)


class _NoSignatureMeta(type):
    """Like a native constructor: ``inspect.signature`` raises ValueError on every Python."""

    @property
    def __signature__(cls):
        raise ValueError("no signature found for builtin type")


class NoSignature(metaclass=_NoSignatureMeta):
    pass


def test_read_signature_when_signature_unavailable_then_fallback_not_invented():
    text, known = sigs.read_signature(NoSignature)
    assert not known and text == sigs.UNAVAILABLE


def test_read_signature_when_not_callable_then_fallback():
    assert sigs.read_signature(3) == (sigs.UNAVAILABLE, False)


def test_public_members_when_class_then_sorted_without_underscores():
    assert sigs.public_members(Plain) == ["move"]


def test_report_when_classes_then_name_constructor_and_member_count():
    assert sigs.report([Plain]) == {"Plain": {"constructor": "(x, y=0)", "members": 1}}


def _fake_echopy(monkeypatch, status):
    class Glyph:
        def __init__(self):
            pass

    fl = types.SimpleNamespace(flGlyph=Glyph, flNode=Plain, flLayer=Plain, flPackage=Plain)
    monkeypatch.setitem(sys.modules, "fly", types.SimpleNamespace(fl=fl))
    ext = types.ModuleType("fontlab_echopy.extensions")
    ext.install_extensions = lambda: status
    ext.get_extension = lambda key, specs=None: (specs or {key: lambda g: ["from-spec"]})[key]
    monkeypatch.setitem(sys.modules, "fontlab_echopy", types.ModuleType("fontlab_echopy"))
    monkeypatch.setitem(sys.modules, "fontlab_echopy.extensions", ext)
    return Glyph


def test_call_owned_when_attribute_exists_then_uses_it(monkeypatch):
    _fake_echopy(monkeypatch, {})
    obj = types.SimpleNamespace(layer_names=lambda: ["Regular"])
    assert owned.call_owned(obj, "layer_names", "k") == ["Regular"]


def test_call_owned_when_attribute_missing_then_uses_extension_function(monkeypatch):
    _fake_echopy(monkeypatch, {})
    assert owned.call_owned(types.SimpleNamespace(), "layer_names", "k") == ["from-spec"]
    assert owned.call_owned(types.SimpleNamespace(), "m", "s", 2, specs={"s": lambda o, n: n * 2}) == 4


def test_main_when_fake_host_then_prints_status_and_signatures(monkeypatch, capsys):
    _fake_echopy(monkeypatch, {"fontlab.flGlyph.layer_names": "immutable; use get_extension", "a.b": "installed"})
    owned.main()
    sigs.main()
    out = capsys.readouterr().out
    assert "fontlab.flGlyph.layer_names -> immutable" in out
    assert "layer_names: ['from-spec']" in out
    assert "Glyph()  [0 public members]" in out and "public members" in out


@pytest.mark.parametrize("name", ["owned_descriptors", "signature_reading"])
def test_example_when_executed_as_script_then_uses_fly_native_alias(monkeypatch, capsys, name):
    import runpy

    _fake_echopy(monkeypatch, {"fontlab.flGlyph.layer_names": "immutable; use get_extension"})
    runpy.run_path(str(ROOT / "examples/echopy" / f"{name}.py"), run_name="__main__")
    assert capsys.readouterr().out
