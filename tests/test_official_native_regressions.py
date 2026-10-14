# this_file: tests/test_official_native_regressions.py
"""Regressions for the controller's FontLab crashes and binding failures."""

import ast
import operator
from types import SimpleNamespace

import pytest

from fontlab_python_examples.official import Demo
from tests.official_doubles import CONTRACT
from tests.test_official_batch import ROOT, built, owned_directory, records
from tests.test_official_batch import (
    official_qt as official_qt,  # noqa: PLC0414 - pytest fixture re-export
)

SOURCES = [ROOT / row["target_path"] for row in records()] + [
    ROOT / "fontlab_python_examples/official.py"
]


@pytest.mark.parametrize("container_name", ["QMenu", "QToolBar", "QWidget"])
def test_add_existing_action_when_native_void_overload_then_returns_none(
    container_name, official_qt
):
    qt, _ = official_qt
    container = getattr(qt.QtGui, container_name)()
    action = qt.QtGui.QAction("Test", container)
    assert container.addAction(action) is None, (
        "Adding an existing QAction returns void"
    )
    assert action in container._items, "Void result must still add the original action"


@pytest.mark.parametrize("container_name", ["QMenu", "QToolBar"])
@pytest.mark.parametrize("with_shortcut", [False, True])
def test_add_action_with_callback_when_native_overload_then_returns_none(
    container_name, with_shortcut, official_qt
):
    qt, _ = official_qt
    container = getattr(qt.QtGui, container_name)()
    calls = []
    args = ["Test", lambda: calls.append("triggered")]
    if with_shortcut:
        args.append(qt.QtGui.QKeySequence("Ctrl+P"))
    assert container.addAction(*args) is None, (
        "Callback convenience overload may return None in PythonQt"
    )
    container._items[-1].trigger()
    assert calls == ["triggered"], (
        "Discarding the native return must not suppress the callback"
    )


@pytest.mark.parametrize("container_name", ["QMenu", "QToolBar"])
def test_add_action_with_receiver_slot_when_native_overload_then_returns_none(
    container_name, official_qt
):
    qt, _ = official_qt
    container = getattr(qt.QtGui, container_name)()
    receiver = qt.QtGui.QWidget()
    assert container.addAction("Close", receiver, "close()") is None
    assert (
        container.addAction(
            "Close", receiver, "close()", qt.QtGui.QKeySequence("Ctrl+Q")
        )
        is None
    )


def test_orderform_print_action_is_retained_and_connected_before_menu_insertion(
    official_qt,
):
    qt, _ = official_qt
    handle = built("orderform", qt)
    action = handle.controls["printAction"]
    assert action is handle.widget.printAction and action._qt_name == "QAction"
    assert action in handle.controls["fileMenu"]._items
    assert any(
        obj is action and signature == "triggered()"
        for obj, signature, _ in handle.connections
    )
    action.trigger()
    assert handle.controls["active_dialog"]._qt_name == "QPrintDialog"
    handle.close()
    assert all(not signal.callbacks for signal in action._signals.values()), (
        "Disconnect before deleting owned widgets"
    )


def test_all_ports_and_official_helper_do_not_consume_unsafe_add_action_returns():
    paths = list((ROOT / "ports").rglob("*.py")) + [
        ROOT / "fontlab_python_examples/official.py"
    ]
    violations = []
    for path in paths:
        tree = ast.parse(path.read_text())
        parents = {
            child: node
            for node in ast.walk(tree)
            for child in ast.iter_child_nodes(node)
        }
        for call in ast.walk(tree):
            if (
                not isinstance(call, ast.Call)
                or not isinstance(call.func, ast.Attribute)
                or call.func.attr != "addAction"
            ):
                continue
            if isinstance(parents[call], ast.Expr):
                continue
            # Only the text-only QAction factory has a reliable return in these ports.
            if (
                len(call.args) == 1
                and not call.keywords
                and isinstance(call.args[0], ast.Constant)
                and isinstance(call.args[0].value, str)
            ):
                continue
            violations.append(
                f"{path.relative_to(ROOT)}:{call.lineno}: {ast.unparse(call)}"
            )
    assert not violations, "Retain an explicit QAction before adding it: " + "; ".join(
        violations
    )


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
        tree = ast.parse(path.read_text())
        bases = {
            c.name: ast.unparse(c.bases[0])
            for c in ast.walk(tree)
            if isinstance(c, ast.ClassDef) and c.bases
        }
        for cls in ast.walk(tree):
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
            while name in bases:
                name = bases[name]
            name = name.rsplit(".", 1)[-1]
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
    path = owned_directory(codecs) / "output.txt"
    box._extra["selectedFiles"] = [str(path)]
    box.accept()
    assert path.read_bytes() == "Ą–字体".encode()
    codecs.close()
    settings = built("settingseditor", qt)
    delegate = settings.widget.settingsTree._data["itemDelegate"]
    assert delegate.displayText(qt.QtCore.QByteArray(b"\xe9\x00")) == "é\x00"
    settings.close()


@pytest.mark.parametrize("curve", ["InOutBack", "SineCurve", "OutElastic"])
def test_easing_setter_requires_constructed_value_not_enum(curve, official_qt):
    qt, _ = official_qt
    animation = qt.QtCore.QPropertyAnimation()
    enum = getattr(qt.QtCore.QEasingCurve, curve)
    for bare in (enum, 35, 43, 30):
        with pytest.raises(TypeError, match="setEasingCurve requires QEasingCurve"):
            animation.setEasingCurve(bare)
    value = qt.QtCore.QEasingCurve(enum)
    animation.setEasingCurve(value)
    from fontlab_python_examples.official import read

    assert read(animation, "easingCurve") is value


@pytest.mark.parametrize("name", ["animatedtiles", "dragdroprobot", "moveblocks"])
def test_native_reported_easing_ports_construct_curve_values(name, official_qt):
    qt, _ = official_qt
    handle = built(name, qt)
    assert handle.snapshot()["title"] and not handle.snapshot()["error"]
    if name == "animatedtiles":
        option = SimpleNamespace(
            state=qt.QtGui.QStyle.State_Sunken | qt.QtGui.QStyle.State_MouseOver
        )
        handle.controls["ellipse"].paint(qt.QtGui.QPainter(), option, None)
    handle.close()
    assert handle.owner.closed and not handle.connections


def test_value_setter_enums_across_all_ports_and_helper_are_explicit():
    paths = sorted((ROOT / "ports").rglob("*.py")) + [
        ROOT / "fontlab_python_examples/official.py"
    ]
    single_values = {
        "setEasingCurve",
        "setFont",
        "setCurrentFont",
        "setShortcut",
        "setKeySequence",
        "setCursor",
        "setPalette",
        "setIconSize",
        "setGridSize",
        "setBackgroundBrush",
        "setDefaultTextColor",
        "setTextColor",
    }
    pen_styles = {
        "NoPen",
        "SolidLine",
        "DashLine",
        "DotLine",
        "DashDotLine",
        "DashDotDotLine",
        "CustomDashLine",
    }
    violations = []
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text())):
            if (
                not isinstance(node, ast.Call)
                or not isinstance(node.func, ast.Attribute)
                or not node.args
            ):
                continue
            method = node.func.attr
            value = node.args[-1]
            if not isinstance(value, (ast.Attribute, ast.Constant)):
                continue
            text = ast.unparse(value)
            enum_owner = text.split(".")[-2] if isinstance(value, ast.Attribute) else ""
            bare = (
                isinstance(value, ast.Constant)
                and type(value.value) in (int, str)
                or isinstance(value, ast.Attribute)
                and enum_owner
                in {"Qt", "QFont", "QEasingCurve", "QKeySequence", "QSizePolicy"}
            )
            if not bare:
                continue
            if (
                method in single_values
                or method in {"setColorAt", "setColor"}
                or method == "fill"
                and ast.unparse(node.func.value) == "pixmap"
                or method == "setSizePolicy"
                and len(node.args) == 1
                or method == "setPen"
                and enum_owner == "Qt"
                and value.attr not in pen_styles
            ):
                violations.append((path.name, node.lineno, ast.unparse(node)))
    assert not violations, f"Value-class setters cannot take bare enums: {violations}"


@pytest.mark.parametrize(
    "kind", ["gradient", "palette", "cursor", "pen", "text", "pixmap"]
)
def test_value_setter_doubles_reject_bare_color_and_cursor_enums(kind, official_qt):
    qt, _ = official_qt
    cases = {
        "pixmap": (
            qt.QtGui.QPixmap(10, 10),
            "fill",
            (),
            qt.QtCore.Qt.white,
            qt.QtGui.QColor(qt.QtCore.Qt.white),
        ),
        "text": (
            qt.QtGui.QGraphicsTextItem(),
            "setDefaultTextColor",
            (),
            qt.QtCore.Qt.black,
            qt.QtGui.QColor(qt.QtCore.Qt.black),
        ),
        "gradient": (
            qt.QtGui.QLinearGradient(),
            "setColorAt",
            (0.5,),
            qt.QtCore.Qt.red,
            qt.QtGui.QColor(qt.QtCore.Qt.red),
        ),
        "palette": (
            qt.QtGui.QPalette(),
            "setColor",
            (qt.QtGui.QPalette.Text,),
            qt.QtCore.Qt.red,
            qt.QtGui.QColor(qt.QtCore.Qt.red),
        ),
        "cursor": (
            qt.QtGui.QWidget(),
            "setCursor",
            (),
            qt.QtCore.Qt.OpenHandCursor,
            qt.QtGui.QCursor(qt.QtCore.Qt.OpenHandCursor),
        ),
        "pen": (
            qt.QtGui.QPainter(),
            "setPen",
            (),
            qt.QtCore.Qt.white,
            qt.QtGui.QColor(qt.QtCore.Qt.white),
        ),
    }
    obj, setter, prefix, bare, wrapped = cases[kind]
    with pytest.raises(TypeError, match=setter):
        getattr(obj, setter)(*prefix, bare)
    getattr(obj, setter)(*prefix, wrapped)


def test_scalar_and_documented_enum_overloads_remain_valid(official_qt):
    qt, _ = official_qt
    font = qt.QtGui.QFont()
    font.setWeight(qt.QtGui.QFont.Bold)
    widget = qt.QtGui.QWidget()
    widget.setFont(font)
    widget.setSizePolicy(qt.QtGui.QSizePolicy.Expanding, qt.QtGui.QSizePolicy.Preferred)
    widget.setSizePolicy(
        qt.QtGui.QSizePolicy(qt.QtGui.QSizePolicy.Fixed, qt.QtGui.QSizePolicy.Fixed)
    )
    painter = qt.QtGui.QPainter()
    painter.setPen(qt.QtCore.Qt.NoPen)
    painter.setBrush(qt.QtCore.Qt.NoBrush)
    action = qt.QtGui.QAction(widget)
    action.setShortcut(qt.QtGui.QKeySequence(qt.QtGui.QKeySequence.Open))
    handle = Demo(qt, __file__, "value-shortcut")
    handle.begin(widget)
    owned = handle.action("Open", widget, shortcut=qt.QtGui.QKeySequence.Open)
    assert owned._data["shortcut"]._qt_name == "QKeySequence"
    handle.handle.close()
