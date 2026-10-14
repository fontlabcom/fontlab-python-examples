# this_file: tests/test_port_errors.py
"""Boundary failure ownership and external example contracts, using doubles."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


def test_host_when_owner_dependency_missing_then_clear_error_before_widget(
    native_boundary, monkeypatch
):
    import fontlab_python_examples as examples

    monkeypatch.setitem(sys.modules, "fontlabapp.widgets", None)
    with pytest.raises(RuntimeError, match="fontlab-fontlabapp"):
        examples.launch("QLabel")
    assert native_boundary[1] == []


def test_host_when_native_module_missing_then_host_error(native_boundary, monkeypatch):
    import fontlab_python_examples as examples

    monkeypatch.setitem(sys.modules, "fontlab", None)
    with pytest.raises(RuntimeError, match="inside FontLab"):
        examples.launch("QLabel")


@pytest.mark.parametrize(
    "name, target",
    [
        ("QVBoxLayout", "QVBoxLayout"),
        ("Qt Designer", "setModal"),
        ("Signals and Slots", "connect"),
    ],
)
def test_build_when_composition_fails_then_widget_ownership_closed(
    native_boundary, monkeypatch, name, target
):
    from qt_doubles import Signal

    import fontlab_python_examples as examples

    def fail(*args):
        raise RuntimeError("composition failed")

    qt, owners = native_boundary
    if target == "QVBoxLayout":
        monkeypatch.setattr(qt.QtGui, target, fail)
    elif target == "connect":
        monkeypatch.setattr(Signal, target, fail)
    else:
        monkeypatch.setattr(qt.QtGui.QWidget, target, fail)
    with pytest.raises(RuntimeError, match="composition failed"):
        examples.launch(name)
    assert owners[-1].closed is True
    assert examples.inspect(name)["launched"] is False


def test_remopy_example_when_run_with_json_inputs_then_host_calls_and_retained_state(
    native_boundary, monkeypatch, capsys
):
    import fontlab_python_examples as examples

    calls = []

    class Controller:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def run(self, code, **variables):
            calls.append(variables)
            namespace = dict(variables)
            exec(code, namespace)  # noqa: S102 - execute the owned example template
            return SimpleNamespace(value=namespace.get("result"))

    monkeypatch.setitem(
        sys.modules, "fontlab_remopy", SimpleNamespace(FontLab=Controller)
    )
    path = Path(__file__).resolve().parents[1] / "examples/remopy.py"
    for action in ("launch", "inspect", "close"):
        monkeypatch.setattr(sys, "argv", [str(path), action, "QLabel"])
        runpy.run_path(str(path), run_name="__main__")
        assert examples.inspect("QLabel")["closed"] is (action == "close")
    assert [call["action"] for call in calls] == ["launch", "inspect", "close"]
    assert "Hello World!" in capsys.readouterr().out
