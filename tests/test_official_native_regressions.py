# this_file: tests/test_official_native_regressions.py
"""Regressions for the controller's FontLab crashes and binding failures."""

import ast
import operator
from types import SimpleNamespace

import pytest

from fontlab_python_examples.official import Demo
from tests.official_doubles import CONTRACT
from tests.test_official_batch import ROOT, built, records
from tests.test_official_batch import official_qt as official_qt  # noqa: PLC0414 - pytest fixture re-export

SOURCES = [ROOT / row["target_path"] for row in records()] + [
    ROOT / "fontlab_python_examples/official.py"
]


def test_ports_reject_unary_arithmetic_except_plain_number_literals():
    violations = []
    for path in SOURCES:
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.UnaryOp) or not isinstance(
                node.op, (ast.USub, ast.UAdd)
            ):
                continue
            # Only int/float literals are allowed: never wrappers, calls or names.
            if not isinstance(node.operand, ast.Constant) or type(
                node.operand.value
            ) not in (int, float):
                violations.append(f"{path.name}:{node.lineno}: {ast.unparse(node)}")
    assert not violations, "Unsafe wrapper negation risk: " + "; ".join(violations)


def test_ports_use_no_keywords_for_native_constructors():
    violations = []
    for path in SOURCES:
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Call) or not node.keywords:
                continue
            callee = ast.unparse(node.func)
            name = callee.rsplit(".", 1)[-1]
            if name.startswith("Q") or (name == "__init__" and callee.startswith("Q")):
                violations.append(f"{path.name}:{node.lineno}: {callee}")
    assert not violations, "Unverified native keyword overloads: " + "; ".join(
        violations
    )


def test_explicit_release_fields_exclude_native_properties_and_cover_subclass_fields():
    for path in SOURCES:
        for cls in ast.walk(ast.parse(path.read_text())):
            if not isinstance(cls, ast.ClassDef) or not cls.bases:
                continue
            calls = [
                n
                for n in ast.walk(cls)
                if isinstance(n, ast.Call) and ast.unparse(n.func) == "demo.track"
            ]
            if not calls:
                continue
            name = ast.unparse(cls.bases[0])
            fields = next(types[name] for types in CONTRACT.values() if name in types)
            declared = {arg.value for call in calls for arg in call.args[1:]}
            assigned = {
                n.attr
                for n in ast.walk(cls)
                if isinstance(n, ast.Attribute)
                and isinstance(n.ctx, ast.Store)
                and ast.unparse(n.value) == "self"
            }
            assert not {name for name in declared if fields.get(name) == "value"}, (
                cls.name
            )
            assert assigned <= declared, (cls.name, assigned - declared)


@pytest.mark.parametrize(
    "operation",
    [
        operator.neg,
        operator.pos,
        operator.add,
        operator.sub,
        operator.mul,
        operator.truediv,
    ],
)
def test_double_wrappers_reject_arithmetic(operation, official_qt):
    qt, _ = official_qt
    for cls in (qt.QtCore.QPoint, qt.QtCore.QPointF, qt.QtCore.QSize, qt.QtCore.QRect):
        value = cls()
        args = (value,) if operation in (operator.neg, operator.pos) else (value, value)
        with pytest.raises(TypeError, match="unsafe arithmetic"):
            operation(*args)


def test_double_native_properties_reject_none_even_on_subclasses(official_qt):
    qt, _ = official_qt

    class Window(qt.QtGui.QWidget):
        pass

    for widget in (qt.QtGui.QWidget(), Window()):
        assert "geometry" in widget.__dict__, "Model PythonQt's synthetic dictionary"
        with pytest.raises(TypeError, match="geometry.*NoneType"):
            widget.geometry = None


@pytest.mark.parametrize("name", ["QDialog", "QDialogButtonBox"])
def test_double_native_constructor_rejects_keywords(name, official_qt):
    qt, _ = official_qt
    with pytest.raises(TypeError, match="does not support kwargs"):
        getattr(qt.QtGui, name)(parent=None)


def test_release_preserves_native_and_undeclared_fields_before_delete(official_qt):
    qt, _ = official_qt
    demo = Demo(qt, __file__, "test")

    class Window(qt.QtGui.QMainWindow):
        pass

    window = Window()
    demo.begin(window)
    demo.track(window, "owned_child", "owned_list", "centralWidget")
    window.owned_child = qt.QtGui.QWidget(window)
    window.owned_list = [window.owned_child]
    window.untouched = object()
    geometry, untouched = window.geometry, window.untouched
    handle = demo.finish(window)
    close = handle.owner.close

    def check_then_delete():
        assert window.geometry is geometry and window.untouched is untouched
        assert callable(window.centralWidget), (
            "An unassigned field must not erase an inherited native method"
        )
        assert window.owned_child is None and window.owned_list == []
        assert not handle.connections
        close()

    handle.owner.close = check_then_delete
    handle.close()
    assert handle.owner.closed


def test_tooltip_paint_hit_testing_and_drag_use_components(official_qt, monkeypatch):
    qt, _ = official_qt
    handle = built("tooltips", qt)
    window = handle.widget
    seen = []
    invoke = qt.QtGui.QPainterPath._invoke

    def contains(self, key, *args, **kwargs):
        if key == "contains":
            seen.append((args[0].x(), args[0].y()))
            return True
        return invoke(self, key, *args, **kwargs)

    monkeypatch.setattr(qt.QtGui.QPainterPath, "_invoke", contains)
    item = window.shapeItems[-1]
    item.setPosition(qt.QtCore.QPoint(20, 30))
    assert window.itemAt(qt.QtCore.QPoint(23, 34)) == 2
    assert seen == [(3, 4)]
    window.itemInMotion = item
    window.previousPosition = qt.QtCore.QPoint(23, 34)
    window.moveItemTo(qt.QtCore.QPoint(28, 32))
    assert (item.position().x(), item.position().y()) == (25, 28)
    window.paintEvent(SimpleNamespace())  # All wrapper operators raise in doubles.
    handle.close()


def test_flow_minimum_size_uses_components(official_qt):
    qt, _ = official_qt
    handle = built("flowlayout", qt)
    layout = handle.widget.layout()
    size = layout.minimumSize()
    assert size.width() >= 80 and size.height() >= 30
    handle.close()


def test_qbytearray_movie_codec_export_and_settings_display(official_qt, tmp_path):
    qt, _ = official_qt
    data = qt.QtCore.QByteArray(b"abc")
    with pytest.raises(TypeError, match="cannot convert.*QByteArray"):
        bytes(data)
    movie = built("movie", qt)
    assert movie.snapshot()["formats"] == ["gif", "mng"]
    movie.close()
    codecs = built("codecs", qt)
    codecs.widget.textEdit.setPlainText("Ą–字体")
    codecs.widget.save("utf-8")
    box = codecs.controls["active_dialog"]
    path = tmp_path / "output.txt"
    box._extra["selectedFiles"] = [str(path)]
    box.accept()
    assert path.read_bytes() == "Ą–字体".encode()
    codecs.close()
    settings = built("settingseditor", qt)
    delegate = settings.widget.settingsTree._data["itemDelegate"]
    assert delegate.displayText(qt.QtCore.QByteArray(b"\xe9\x00")) == "é\x00"
    settings.close()
