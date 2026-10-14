# this_file: tests/test_official_slot_shadowing.py
"""Reject instance-field names that PythonQt reserves for native methods."""

import ast

import pytest

from tests.test_official_batch import official_qt as official_qt  # noqa: PLC0414 - pytest fixture re-export
from tests.test_official_native_regressions import SOURCES


def test_port_assignments_and_release_fields_do_not_shadow_native_slots(official_qt):
    qt, _ = official_qt
    collisions = []
    for path in SOURCES:
        tree = ast.parse(path.read_text())
        native_classes = {}
        for cls in ast.walk(tree):
            if not isinstance(cls, ast.ClassDef) or not cls.bases:
                continue
            base = getattr(qt.QtGui, ast.unparse(cls.bases[0]), None)
            if base is None:
                continue
            native_classes[cls.name] = base
            names = {
                n.attr
                for n in ast.walk(cls)
                if isinstance(n, ast.Attribute)
                and isinstance(n.ctx, ast.Store)
                and ast.unparse(n.value) == "self"
            }
            for call in (n for n in ast.walk(cls) if isinstance(n, ast.Call)):
                if ast.unparse(call.func) == "demo.track":
                    names.update(arg.value for arg in call.args[1:])
                if (
                    ast.unparse(call.func) == "setattr"
                    and ast.unparse(call.args[0]) == "self"
                ):
                    names.add(call.args[1].value)
            collisions.extend(
                (path.name, cls.name, name)
                for name in names
                if base._fields.get(name) == "method"
            )

        # Also cover fields assigned outside constructors, e.g. child._subwindow.
        bindings = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                bases = {
                    native_classes[call.func.id]
                    for call in ast.walk(node.value)
                    if isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id in native_classes
                }
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        bindings.setdefault(target.id, set()).update(bases)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.ctx, ast.Store)
                and isinstance(node.value, ast.Name)
            ):
                for base in bindings.get(node.value.id, ()):
                    if base._fields.get(node.attr) == "method":
                        collisions.append((path.name, node.value.id, node.attr))
    assert not collisions, f"Native slots cannot be instance fields: {collisions}"


@pytest.mark.parametrize("name", ["centralWidget", "show"])
def test_doubles_reject_own_and_inherited_native_slot_shadowing(name, official_qt):
    qt, _ = official_qt

    class Window(qt.QtGui.QMainWindow):
        pass

    for window in (qt.QtGui.QMainWindow(), Window()):
        assert callable(getattr(window, name))
        with pytest.raises(
            AttributeError, match=f"Slot '{name}' can not be overwritten"
        ):
            setattr(window, name, None)
        assert callable(getattr(window, name))
