# this_file: tests/test_issue122_R1c.py
# SPDX-License-Identifier: Apache-2.0
"""Check numeric outline controls with real App writers and strict host shapes."""

import ast
import hashlib
import importlib
import importlib.util
import inspect
import json
import math
import os
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any

import pytest
from fontlabapp.layer_selection import LayerSelection

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Scripts/Contours/Node Slope And Handles.py"
TYPERIG = "rescued/part3/sources/kateliev_TypeRig/"
R1C_SOURCES = frozenset(
    TYPERIG + path
    for path in (
        "Lib/typerig/core/algo/matchmaker.py",
        "Lib/typerig/proxy/fl/gui/dialogs.py",
        "Lib/typerig/proxy/fl/objects/sampler.py",
        "Scripts/TypeRig GUI/Manager/FontMetrics.py",
        "Scripts/TypeRig GUI/Manager/Impex.py",
        "Scripts/TypeRig GUI/Manager/KernGroups.py",
        "Scripts/TypeRig GUI/Manager/Kerning.py",
        "Scripts/TypeRig GUI/Toolbar/contour.py",
        "Scripts/TypeRig GUI/Toolbar/curve.py",
        "Scripts/TypeRig GUI/Toolbar/node.py",
        "Scripts/TypeRig GUI/Toolbar/node_align.py",
        "Scripts/TypeRig GUI/Toolbar/node_slope.py",
        "Scripts/TypeRig GUI/typerig-toolbar.py",
        "Scripts/TypeRig Tools/TR-Comparator.py",
        "Scripts/TypeRig Tools/TR-ExportFont.py",
        "Scripts/TypeRig Tools/TR-ExportGlyph.py",
        "Scripts/TypeRig Tools/TR-ImportGlyph.py",
    )
)


def r1c_records() -> dict[str, list[dict[str, Any]]]:
    """Return the 17 R1c records folded into menu-adaptations.json."""
    shared = json.loads((ROOT / "menu-adaptations.json").read_text())
    return {
        section: [row for row in shared[section] if row["source"] in R1C_SOURCES]
        for section in ("adaptations", "retirements")
    }


COLLISIONS = {
    "render",
    "size",
    "layout",
    "update",
    "font",
    "move",
    "statusBar",
    "geometry",
    "close",
    "width",
    "height",
}


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("numeric_outlines", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Node:
    def __init__(self, point: tuple[float, float], *, nodeType: str = "on") -> None:
        self.x, self.y = point
        self.on = nodeType == "on"
        self.selected = True
        self.nodeState = 17 if self.on else 32

    def isOn(self) -> bool:
        return self.on

    def getProperties(self) -> list:
        return []


class Contour:
    def __init__(self, nodes: list[Node], *, closed: bool = False) -> None:
        self._nodes, self.closed, self.isTT = nodes, closed, False

    def nodes(self) -> list[Node]:
        return self._nodes

    def getProperties(self) -> list:
        return []


class Owned:
    def __init__(self, name: str) -> None:
        self.name, self.autoLayer, self.isNull = name, False, False
        self.isMasterLayer, self.isMaskLayer = True, False
        self.histories: list[int] = []
        self.shapes: list = []
        self.lastModified = None

    def checkInitHistoryState(self, index: int) -> None:
        self.histories.append(index)

    def changed(self) -> None:
        pass

    def update(self) -> bool:
        return True


def layer_with(contours: list[Contour], name: str = "Regular") -> Owned:
    layer = Owned(name)
    matrix = NS(
        m11=lambda: 1,
        m22=lambda: 1,
        m12=lambda: 0,
        m21=lambda: 0,
        dx=lambda: 0,
        dy=lambda: 0,
    )
    layer.shapes = [
        NS(
            contours=contours,
            isComponent=False,
            shapeData=NS(referenceCount=1),
            transform=matrix,
        )
    ]
    return layer


def cubic() -> Contour:
    return Contour(
        [
            Node((0, 0)),
            Node((0, 30), nodeType="off"),
            Node((70, 100), nodeType="off"),
            Node((100, 100)),
        ]
    )


@pytest.fixture
def module() -> ModuleType:
    return load()


def app_names_used() -> dict[str, set[str]]:
    """Use the G1 AST form, without importing any script or native host."""
    tree = ast.parse(SCRIPT.read_text())
    aliases = {
        a.asname: a.name
        for n in ast.walk(tree)
        if isinstance(n, ast.Import)
        for a in n.names
        if a.name.startswith("fly.ap.")
    }
    return {
        name: {
            n.attr
            for n in ast.walk(tree)
            if isinstance(n, ast.Attribute)
            and isinstance(n.value, ast.Name)
            and n.value.id == alias
        }
        for alias, name in aliases.items()
    }


def test_real_app_names_when_imported_from_installed_app_then_all_exist() -> None:
    """No App src override: verify the installed package and Fly alias identity."""
    used = app_names_used()
    assert set(used) == {
        "fly.ap.outline_writer",
        "fly.ap.outline_panel",
        "fly.ap.scripting",
        "fly.ap.layer_selection",
        "fly.ap.master_angles",
    }
    app = importlib.import_module("fontlabapp")
    app_root = Path(app.__file__).resolve().parent
    assert "site-packages" in str(app_root), "Required non-editable App install"
    fly = importlib.import_module("fly")
    assert fly.ALIASES["ap"] == "fontlabapp"
    for name, attributes in used.items():
        real = importlib.import_module(name)
        assert real is importlib.import_module(name.replace("fly.ap.", "fontlabapp."))
        assert Path(real.__file__).resolve().is_relative_to(app_root)
        for attribute in attributes:
            assert hasattr(real, attribute), f"{name}.{attribute}"


def test_script_when_parsed_then_typed_public_and_no_native_name_collisions() -> None:
    text = SCRIPT.read_text()
    tree = ast.parse(text, feature_version=(3, 11))
    assert text.startswith("# this_file: Scripts/Contours/Node Slope And Handles.py")
    for word in (
        "What:",
        "How:",
        "Why:",
        "Use:",
        "Benefit:",
        "Vassil Kateliev",
        "MPL-2.0",
    ):
        assert word in ast.get_docstring(tree)
    assert not any(
        word in text.lower()
        for word in ("issue 122", "r1c", "archived", "typerig.core", "typerig.proxy")
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None, node.name
            assert all(
                a.annotation
                for a in node.args.args + node.args.kwonlyargs
                if a.arg not in {"self", "cls"}
            ), node.name
        if isinstance(node, ast.ClassDef):
            assert (
                not {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                & COLLISIONS
            )
        if isinstance(node, ast.Assign):
            assert (
                not {
                    n.attr
                    for target in node.targets
                    for n in ast.walk(target)
                    if isinstance(n, ast.Attribute)
                    and isinstance(n.value, ast.Name)
                    and n.value.id == "self"
                }
                & COLLISIONS
            )


def test_native_fakes_when_optional_arguments_are_positional_then_reject() -> None:
    with pytest.raises(TypeError):
        Node((0, 0), "off")
    with pytest.raises(TypeError):
        Contour([], True)
    assert Node((0, 0)).getProperties() == []
    assert Contour([]).getProperties() == []


def test_slope_when_pivot_or_flip_changes_then_exact_coordinates(module: Any) -> None:
    nodes = [Node((10, 0)), Node((70, 100)), Node((20, 200))]
    assert [(x, y) for _, x, y in module.slope_moves(nodes, 0.2, False, False)] == [
        (30, 100),
        (50, 200),
    ]
    assert [(x, y) for _, x, y in module.slope_moves(nodes, 0.2, True, False)] == [
        (-20, 0),
        (0, 100),
    ]
    assert [(x, y) for _, x, y in module.slope_moves(nodes, 0.2, False, True)] == [
        (-10, 100),
        (-30, 200),
    ]


@pytest.mark.parametrize("nodes", [[], [Node((0, 0))], [Node((0, 1)), Node((20, 1))]])
def test_slope_copy_when_no_vertical_span_then_refused(
    module: Any, nodes: list
) -> None:
    with pytest.raises(ValueError):
        module.slope_of(nodes)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_slope_when_nonfinite_then_refused(module: Any, value: float) -> None:
    with pytest.raises(ValueError):
        module.slope_moves([Node((0, 0)), Node((0, 10))], value, False, False)


def test_curve_when_proportions_change_then_tangents_and_types_stay(
    module: Any,
) -> None:
    curve = cubic()
    moves = module.handle_moves(curve, "Proportions", 0.3, 0.5)
    assert [(x, y) for _, x, y in moves] == pytest.approx(
        [(0, math.sqrt(20000) * 0.3), (100 - math.sqrt(20000) * 0.5, 100)]
    )
    assert module.proportions(curve) == pytest.approx(
        (30 / math.sqrt(20000), 30 / math.sqrt(20000))
    )
    assert [n.nodeState for n in curve.nodes()] == [17, 32, 32, 17]


def test_curve_when_hobby_straight_or_closed_then_defined(module: Any) -> None:
    curve = Contour(
        [
            Node((0, 0)),
            Node((20, 0), nodeType="off"),
            Node((80, 0), nodeType="off"),
            Node((100, 0)),
        ]
    )
    assert [
        v for _, x, y in module.handle_moves(curve, "Hobby", 1, 1) for v in (x, y)
    ] == pytest.approx([100 / 3, 0, 200 / 3, 0])
    curve.closed = True
    assert len(module.handle_moves(curve, "Hobby", 1, 1)) == 2
    curve.isTT = True
    assert module.handle_moves(curve, "Hobby", 1, 1) == []


@pytest.mark.parametrize(
    "mode,a,b",
    [
        ("Proportions", -1, 1),
        ("Hobby", 0, 1),
        ("Hobby", 1, math.nan),
        ("unknown", 1, 1),
    ],
)
def test_curve_when_bad_parameters_then_refused(
    module: Any, mode: str, a: float, b: float
) -> None:
    with pytest.raises(ValueError):
        module.handle_moves(cubic(), mode, a, b)


def test_planner_when_shared_transformed_or_tt_then_kept_rows(module: Any) -> None:
    layer = layer_with([cubic()])
    layer.shapes[0].shapeData.referenceCount = 2
    assert "kept" in module.changes(layer, "Proportions", 0.3, 0.3, False, False)[0].new
    layer.shapes[0].shapeData.referenceCount = 1
    layer.shapes[0].transform.m11 = lambda: 2
    assert "kept" in module.changes(layer, "Proportions", 0.3, 0.3, False, False)[0].new
    layer = layer_with([cubic()])
    layer.shapes[0].contours[0].isTT = True
    assert "kept" in module.changes(layer, "Proportions", 0.3, 0.3, False, False)[0].new


@pytest.fixture
def native(monkeypatch: Any) -> Any:
    host, qt = ModuleType("fontlab"), ModuleType("PythonQt")
    notifications: list = []
    host.flGlyph = NS(updatedFgGlyphs=lambda: ())
    host.flItems = lambda: NS(
        notifyChangesApplied=lambda title, objects: notifications.append(
            (title, objects)
        )
    )
    qt.QtCore = NS(QDateTime=NS(currentDateTimeUtc=lambda: "stamp"))
    qt.QtGui = NS(
        QComboBox=Control, QLabel=Control, QCheckBox=Control, QPushButton=Control
    )
    monkeypatch.setitem(sys.modules, "fontlab", host)
    monkeypatch.setitem(sys.modules, "PythonQt", qt)
    monkeypatch.setitem(sys.modules, "fly.qt", qt)
    monkeypatch.setattr(importlib.import_module("fly"), "qt", qt, raising=False)
    return NS(host=host, qt=qt, notifications=notifications)


def test_writer_when_batch_has_auto_glyph_then_keep_it_and_commit_others_once(
    module: Any, native: Any
) -> None:
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.outline_writer as writer

    glyphs = [Owned("a"), Owned("auto")]
    layers = {g.name: layer_with([cubic()]) for g in glyphs}
    for glyph in glyphs:
        glyph.findLayer = lambda master, name=glyph.name: layers[name]
    facts = history.auto_facts((("auto", True, ()),))
    plan = writer.collect(
        glyphs,
        ["Regular"],
        lambda g, m, l: module.changes(l, "Proportions", 0.4, 0.4, False, False),
        facts,
    )
    assert plan.refused == ["auto"]
    writer.apply_work(plan.work, module.TITLE, facts, module.CoordinateEditor())
    assert len(native.notifications) == 1
    assert native.notifications[0][1] == [layers["a"], glyphs[0]]
    assert glyphs[1].histories == []
    assert layers["a"].histories == glyphs[0].histories == [0]


def test_writer_when_pending_or_partial_failure_then_clear_error(
    module: Any, native: Any
) -> None:
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.outline_writer as writer

    glyph, layer = Owned("a"), layer_with([cubic()])
    rows = module.changes(layer, "Proportions", 0.4, 0.4, False, False)
    work = [(glyph, layer, [row.edit for row in rows if row.edit])]
    facts = history.auto_facts(())
    native.host.flGlyph.updatedFgGlyphs = lambda: (4,)
    with pytest.raises(ValueError, match="pending"):
        writer.apply_work(work, module.TITLE, facts, module.CoordinateEditor())
    assert not glyph.histories and not native.notifications
    native.host.flGlyph.updatedFgGlyphs = lambda: ()
    layer.update = lambda: False
    with pytest.raises(
        RuntimeError, match="Native changes may remain; use Edit > Undo"
    ):
        writer.apply_work(work, module.TITLE, facts, module.CoordinateEditor())
    assert len(native.notifications) == 1


def test_editor_when_readback_differs_then_names_layer(module: Any) -> None:
    layer = layer_with([cubic()])
    rows = module.changes(layer, "Proportions", 0.4, 0.4, False, False)
    steps = [r.edit for r in rows if r.edit]
    assert module.CoordinateEditor().check([(layer, steps)]) == ["Regular: coordinates"]
    module.CoordinateEditor().write(layer, steps)
    assert module.CoordinateEditor().check([(layer, steps)]) == []


def fake_panel_type() -> type:
    class StrictPanel:
        def __init__(self, parent: Any = None) -> None:
            self.recorded_rows: list = []
            self.recorded_spins: list = []
            self.recorded_watches: list = []
            self.package, self.package_id, self.glyphs = None, 1, []
            self.status = Control()
            self.refresh_count = 0

        def __setattr__(self, name: str, value: Any) -> None:
            if name in COLLISIONS:
                raise AttributeError(name)
            object.__setattr__(self, name, value)

        def spin(
            self,
            low: float,
            high: float,
            value: float,
            suffix: str = "",
            decimals: int = 0,
        ) -> Any:
            self.recorded_spins.append((low, high, value, suffix, decimals))
            control = Control(value)
            control.setRange(low, high)
            self.watch(control.valueChanged)
            return control

        def add_row(self, label: str, *widgets: Any) -> None:
            self.recorded_rows.append((label, widgets))

        def watch(
            self, signal: Any, callback: Callable[..., Any] | None = None
        ) -> None:
            self.recorded_watches.append((signal, callback))
            signal.connect(lambda *args: (callback or self.refresh)())

        def refresh(self) -> None:
            self.refresh_count += 1

        def intro(self) -> str:
            if self.package is None:
                return "Open a font first."
            if not self.glyphs:
                return "Select glyphs in the Font window, then press Reload selection."
            return ", ".join(g.name for g in self.glyphs)

    return StrictPanel


def fake_capture(deadline: float) -> LayerSelection:
    return LayerSelection((), tuple(getattr(fake_capture, "occurrences", ())))


def fake_show_script_dialog(dialog_type: Callable[[Any], Any], key: str) -> Any:
    return dialog_type


def test_app_fakes_when_inspected_then_match_real_signatures() -> None:
    for name, fake in (
        ("outline_panel.panel_type", fake_panel_type),
        ("layer_selection.capture", fake_capture),
        ("scripting.show_script_dialog", fake_show_script_dialog),
    ):
        mod, attr = name.split(".")
        real = getattr(importlib.import_module("fontlabapp." + mod), attr)
        expected, got = inspect.signature(real), inspect.signature(fake)
        assert got == expected, name


def test_panel_when_created_then_no_native_member_shadowing(
    module: Any, monkeypatch: Any, native: Any
) -> None:
    import fly.ap.outline_panel as panel

    monkeypatch.setattr(panel, "panel_type", fake_panel_type)
    cls = module.panel_type()
    assert not set(vars(cls)) & COLLISIONS
    instance = cls()
    with pytest.raises(AttributeError):
        instance.layout = None


@pytest.mark.parametrize(
    "error", [ValueError("bad"), RuntimeError("native"), TimeoutError("deadline")]
)
def test_main_when_host_refuses_then_reports_error(
    module: Any, monkeypatch: Any, capsys: Any, error: Exception
) -> None:
    def fail() -> type:
        raise error

    monkeypatch.setattr(module, "panel_type", fail)
    assert module.main() is None
    assert str(error) in capsys.readouterr().out


def test_copy_capture_when_layer_selection_changes_then_refuses_or_reads_current(
    module: Any, monkeypatch: Any
) -> None:
    import fly.ap.layer_selection as selection

    monkeypatch.setattr(selection, "capture", fake_capture)
    with pytest.raises(ValueError, match="one glyph layer"):
        module.selected_contours()
    layer = layer_with([cubic()])
    layer.id = 7
    monkeypatch.setattr(fake_capture, "occurrences", [NS(layer=layer)], raising=False)
    assert module.selected_contours() == layer.shapes[0].contours
    other = layer_with([cubic()])
    other.id = 8
    monkeypatch.setattr(fake_capture, "occurrences", [NS(layer=layer), NS(layer=other)])
    with pytest.raises(ValueError, match="one glyph layer"):
        module.selected_contours()


def test_curves_when_unselected_zero_ray_or_wrapped_then_keep_or_edit_exactly(
    module: Any,
) -> None:
    curve = cubic()
    curve.nodes()[0].selected = False
    assert module.handle_moves(curve, "Proportions", 0.4, 0.4) == []
    curve.nodes()[0].selected = True
    curve.nodes()[1].x = curve.nodes()[1].y = 0
    layer = layer_with([curve])
    rows = module.changes(layer, "Proportions", 0.4, 0.4, False, False)
    assert not any(r.edit for r in rows)
    assert any("zero chord or handle" in r.new for r in rows)
    curve = cubic()
    curve._nodes = curve._nodes[2:] + curve._nodes[:2]
    curve.closed = True
    moves = module.handle_moves(curve, "Proportions", 0.5, 0.5)
    assert len(moves) == 2, "Closing cubic must remain editable"


def test_hobby_when_quarter_circle_then_matches_unit_tension_oracle(
    module: Any,
) -> None:
    curve = Contour(
        [
            Node((1, 0)),
            Node((1, 0.4), nodeType="off"),
            Node((0.4, 1), nodeType="off"),
            Node((0, 1)),
        ]
    )
    moves = module.handle_moves(curve, "Hobby", 1, 1)
    k = 4 * (math.sqrt(2) - 1) / 3
    assert [v for _, x, y in moves for v in (x, y)] == pytest.approx([1, k, k, 1])
    tight = module.handle_moves(curve, "Hobby", 2, 2)
    assert [v for _, x, y in tight for v in (x, y)] == pytest.approx(
        [1, k / 2, k / 2, 1]
    )


def test_horizontal_slope_when_applied_then_named_kept_row(module: Any) -> None:
    contour = Contour([Node((1, 3)), Node((8, 3))])
    rows = module.changes(layer_with([contour]), "Slope", 0.3, 0.3, False, False)
    assert not any(row.edit for row in rows)
    assert "horizontal nodes kept" in rows[0].new


class Signal:
    def __init__(self) -> None:
        self.slots: list = []

    def connect(self, callback: Callable[..., Any]) -> None:
        self.slots.append(callback)

    def emit(self, *args: Any) -> None:
        for slot in self.slots:
            slot(*args)


class Control:
    """Explicit Qt property/method surface for real control construction."""

    def __init__(self, value: float | str = 0) -> None:
        self.value = value if isinstance(value, (int, float)) else 0
        self.currentIndex, self.text = 0, value if isinstance(value, str) else ""
        self.checked, self.enabled = False, True
        self.items: list[str] = []
        self.clicked, self.toggled, self.currentIndexChanged, self.valueChanged = (
            Signal(),
            Signal(),
            Signal(),
            Signal(),
        )

    def addItems(self, items: list[str]) -> None:
        self.items.extend(items)

    def setEnabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def setRange(self, low: float, high: float) -> None:
        self.minimum, self.maximum = low, high

    def setValue(self, value: float) -> None:
        if self.value != value:
            self.value = value
            self.valueChanged.emit(value)

    def setCurrentIndex(self, index: int) -> None:
        if self.currentIndex != index:
            self.currentIndex = index
            self.currentIndexChanged.emit(index)

    def setChecked(self, checked: bool) -> None:
        if self.checked != checked:
            self.checked = checked
            self.toggled.emit(checked)

    def setText(self, text: str) -> None:
        self.text = text

    def isChecked(self) -> bool:
        return self.checked


def fake_current_package(expected_id: int | None = None) -> Any | None:
    return getattr(fake_current_package, "package", None)


def test_copy_slots_when_values_or_errors_then_update_controls_and_keep_errors(
    module: Any, monkeypatch: Any, native: Any
) -> None:
    import fly.ap.outline_panel as panel
    import fly.ap.scripting as scripting  # noqa: PLR0402

    assert inspect.signature(fake_current_package) == inspect.signature(
        scripting.current_package
    )
    monkeypatch.setattr(panel, "panel_type", fake_panel_type)
    monkeypatch.setattr(scripting, "current_package", fake_current_package)
    widget = module.panel_type()()
    widget.build_controls()
    widget.package_id = 1
    widget.refresh = lambda: None
    widget.copy_values("italic")
    assert "Open the bound font" in widget.status.text
    monkeypatch.setattr(
        fake_current_package, "package", NS(italicAngle_value=-45), raising=False
    )
    widget.copy_values("italic")
    assert widget.first_value.value == pytest.approx(1)
    monkeypatch.setattr(module, "selected_contours", lambda: [cubic()])
    widget.copy_values("handles")
    assert widget.mode_box.currentIndex == 1
    assert widget.first_value.value == pytest.approx(30 / math.sqrt(20000))
    assert widget.planner()(Owned("a"), "Regular", layer_with([cubic()]))
    assert widget.intro() == "Open a font first."
    assert isinstance(widget.editor(), module.CoordinateEditor)
    for error in (ValueError("bad"), RuntimeError("native"), TimeoutError("deadline")):

        def fail(error: Exception = error) -> list:
            raise error

        monkeypatch.setattr(module, "selected_contours", fail)
        widget.copy_values("slope")
        assert widget.status.text == str(error)


def test_main_when_host_available_then_uses_shared_registry(
    module: Any, monkeypatch: Any, native: Any
) -> None:
    import fly.ap.outline_panel as panel
    import fly.ap.scripting as scripting  # noqa: PLR0402

    monkeypatch.setattr(panel, "panel_type", fake_panel_type)
    monkeypatch.setattr(scripting, "show_script_dialog", fake_show_script_dialog)
    assert module.main().__name__ == "NumericPanel"


def test_dispositions_when_loaded_then_all_17_frozen_identities_have_exact_rows() -> (
    None
):
    data = r1c_records()
    index = json.loads((ROOT / "rescue-index.json").read_text())
    identities = {r["menu"]: r for r in index["menus"]}
    records = data["adaptations"] + data["retirements"]
    assert len(records) == len({r["source_menu"] for r in records}) == 17
    assert len(data["adaptations"]) == 5 and len(data["retirements"]) == 12
    assert sum(r["disposition"] == "ported" for r in records) == 2
    preserved = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
    for row in records:
        frozen = identities[row["source_menu"]]
        assert row["source"] == frozen["target"]
        assert row["source_sha256"] == frozen["target_sha256"]
        assert (
            hashlib.sha256((preserved / row["source"]).read_bytes()).hexdigest()
            == row["source_sha256"]
        )
        assert not row.get("source_body_redistributed", False)
        assert "MPL-2.0" in row["license"]
        assert not any(
            word in row.get("scope", row.get("reason", "")).lower()
            for word in ("archived", "unresolved", "issue 122", "draft")
        )
        if row in data["adaptations"]:
            destination = (
                ROOT.parent / row["menu"]
                if row["menu"].startswith("fontlab-python-scriptmix/")
                else ROOT / row["menu"]
            )
            assert (
                hashlib.sha256(destination.read_bytes()).hexdigest()
                == row["destination_sha256"]
            )
            if row["menu"] == "Scripts/Contours/Node Slope And Handles.py":
                assert "App>=0.2.150.dev0" in destination.read_text()
            assert row["original_workflow_accepted"] is False


def smooth_contour() -> Contour:
    curve = Contour(
        [
            Node((0, 0)),
            Node((0, 30), nodeType="off"),
            Node((60, 80), nodeType="off"),
            Node((80, 100)),
            Node((100, 120), nodeType="off"),
            Node((200, 160), nodeType="off"),
            Node((220, 200)),
        ]
    )
    for node in curve.nodes():
        node.selected = node.isOn()
    curve.nodes()[3].nodeState = 0x31
    return curve


def planned_moves(module: Any, curve: Contour) -> list:
    return [
        move
        for row in module.changes(layer_with([curve]), "Slope", 0.5, 1, False, False)
        if row.edit
        for move in row.edit
    ]


def test_slope_when_smooth_node_moves_then_both_handles_follow(module: Any) -> None:
    curve = smooth_contour()
    module.CoordinateEditor().write(None, [planned_moves(module, curve)])
    incoming, node, outgoing = curve.nodes()[2:5]
    assert [(n.x, n.y) for n in (incoming, node, outgoing)] == [
        (30, 80),
        (50, 100),
        (70, 120),
    ]
    assert (node.x - incoming.x) * (outgoing.y - node.y) == (node.y - incoming.y) * (
        outgoing.x - node.x
    )
    assert node.nodeState == 0x31


def test_slope_when_handle_itself_selected_then_its_own_target_wins(
    module: Any,
) -> None:
    curve = smooth_contour()
    curve.nodes()[2].selected = True
    moves = planned_moves(module, curve)
    assert sum(n is curve.nodes()[2] for n, _, _ in moves) == 1
    module.CoordinateEditor().write(None, [moves])
    assert (curve.nodes()[2].x, curve.nodes()[2].y) == (40, 80)
    assert (curve.nodes()[4].x, curve.nodes()[4].y) == (70, 120)


@pytest.mark.parametrize("rotation", [0, 1])
def test_slope_when_node_is_first_or_last_then_handles_wrap(
    module: Any, rotation: int
) -> None:
    target, base = Node((80, 100)), Node((0, 0))
    outgoing, incoming = (
        Node((100, 120), nodeType="off"),
        Node((60, 80), nodeType="off"),
    )
    nodes = [
        target,
        outgoing,
        Node((0, 30), nodeType="off"),
        base,
        Node((40, 60), nodeType="off"),
        incoming,
    ]
    for node in nodes:
        node.selected = node.isOn()
    curve = Contour(nodes[rotation:] + nodes[:rotation], closed=True)
    module.CoordinateEditor().write(None, [planned_moves(module, curve)])
    assert (target.x, outgoing.x, incoming.x) == (50, 70, 30)


@pytest.mark.parametrize(
    "mode,a,b", [("Slope", 0.5, 1), ("Proportions", 0.4, 0.6), ("Hobby", 1, 2)]
)
def test_preview_when_edits_planned_then_shows_exact_coordinates(
    module: Any, mode: str, a: float, b: float
) -> None:
    rows = module.changes(layer_with([smooth_contour()]), mode, a, b, False, False)
    edits = [r for r in rows if r.edit]
    assert edits, "Fixture must exercise actual movement"
    for row in edits:
        assert len(row.edit) == 1, "Each preview row identifies one coordinate pair"
        node, x, y = row.edit[0]
        assert tuple(map(float, row.old.split(","))) == (node.x, node.y)
        assert tuple(map(float, row.new.split(","))) == (x, y)


def test_readback_when_gap_then_app_prefix_and_no_duplicate_undo_text(
    module: Any, native: Any
) -> None:
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.outline_writer as writer

    layer = layer_with([cubic()])
    moves = module.handle_moves(layer.shapes[0].contours[0], "Proportions", 0.4, 0.4)
    assert module.CoordinateEditor().check([(layer, [moves])]) == [
        "Regular: coordinates"
    ]

    class LostWrite(module.CoordinateEditor):
        def write(self, layer: Any, steps: list[Any]) -> None:
            pass

    with pytest.raises(RuntimeError) as error:
        writer.apply_work(
            [(Owned("a"), layer, [moves])],
            module.TITLE,
            history.auto_facts(()),
            LostWrite(),
        )
    assert str(error.value).startswith("FontLab did not store")
    assert "Undo" not in str(error.value)
    assert module.READBACK_TOLERANCE == writer.EPSILON


def test_controls_when_built_then_buttons_labels_ranges_and_watches_are_correct(
    module: Any, monkeypatch: Any, native: Any
) -> None:
    import fly.ap.outline_panel as panel

    monkeypatch.setattr(panel, "panel_type", fake_panel_type)
    widget = module.panel_type()()
    widget.build_controls()
    assert widget.mode_box.items == ["Slope", "Proportions", "Hobby"]
    assert len(widget.recorded_spins) == 2
    assert widget.first_label.text == "Slope (dx/dy)"
    assert widget.first_value.minimum == -100
    assert not widget.second_value.enabled
    assert widget.top_pivot.enabled and widget.flip_slope.enabled
    actions: list[str] = []
    widget.copy_values = lambda action: actions.append(action)
    buttons = [
        widgets[0]
        for _, widgets in widget.recorded_rows
        if len(widgets) == 1
        and widgets[0].text in ("Copy Slope", "Use Italic Angles", "Copy Proportions")
    ]
    for button in buttons:
        button.clicked.emit(False)
    assert actions == ["slope", "italic", "handles"], (
        "Clicked bool must not replace the bound action"
    )
    widget.mode_box.setCurrentIndex(1)
    assert widget.first_label.text == "First handle / chord"
    assert widget.second_label.text == "Second handle / chord"
    assert widget.first_value.minimum == 0 and widget.second_value.enabled
    assert not widget.top_pivot.enabled and not widget.flip_slope.enabled
    assert not widget.per_master_italic.enabled
    widget.mode_box.setCurrentIndex(2)
    assert widget.first_label.text == "First Hobby tension"
    assert widget.second_label.text == "Second Hobby tension"
    assert widget.first_value.minimum > 0 and widget.second_value.minimum > 0
    widget.mode_box.setCurrentIndex(0)
    widget.per_master_italic.setChecked(True)
    assert not widget.first_value.enabled
    assert widget.refresh_count >= 4


def test_panel_self_reads_when_parsed_then_use_only_public_base_or_own_names() -> None:
    import fly.ap.outline_panel as panel

    tree = ast.parse(SCRIPT.read_text())
    own = {
        n.attr
        for n in ast.walk(tree)
        if isinstance(n, ast.Attribute)
        and isinstance(n.value, ast.Name)
        and n.value.id == "self"
        and isinstance(n.ctx, ast.Store)
    }
    own.update(n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    read = {
        n.attr
        for n in ast.walk(tree)
        if isinstance(n, ast.Attribute)
        and isinstance(n.value, ast.Name)
        and n.value.id == "self"
        and isinstance(n.ctx, ast.Load)
    }
    assert not read - own - set(panel.MEMBERS) - set(panel.HOOKS), (
        "Unknown native/base member used"
    )


def test_intro_when_font_or_selection_missing_then_base_guidance_stays(
    module: Any, monkeypatch: Any, native: Any
) -> None:
    import fly.ap.outline_panel as panel

    monkeypatch.setattr(panel, "panel_type", fake_panel_type)
    widget = module.panel_type()()
    assert widget.intro() == "Open a font first."
    widget.package = NS(id=1)
    assert (
        widget.intro()
        == "Select glyphs in the Font window, then press Reload selection."
    )
    widget.glyphs = [Owned("a")]
    assert widget.intro().startswith("a · ") and "dx/dy" in widget.intro()


def test_italic_when_all_masters_then_each_angle_drives_its_own_preview_and_write(
    module: Any, monkeypatch: Any, native: Any
) -> None:
    import fly.ap.outline_panel as panel
    import fly.ap.scripting as scripting  # noqa: PLR0402

    monkeypatch.setattr(panel, "panel_type", fake_panel_type)
    monkeypatch.setattr(scripting, "current_package", fake_current_package)
    package = NS(
        id=1, master="Upright", masters=["Upright", "Slanted"], italicAngle_value=0
    )

    def set_master(master: str) -> None:
        package.master = master
        package.italicAngle_value = {"Upright": 0, "Slanted": -45}[master]

    package.setMaster = set_master
    monkeypatch.setattr(fake_current_package, "package", package, raising=False)
    widget = module.panel_type()()
    widget.build_controls()
    widget.package = package
    widget.per_master_italic.setChecked(True)
    planner = widget.planner()
    assert package.master == "Upright" and package.italicAngle_value == 0, (
        "Angle capture must restore the master"
    )
    for master, expected_x in (("Upright", 0), ("Slanted", 100)):
        contour = Contour([Node((0, 0)), Node((50, 100))])
        layer = layer_with([contour], master)
        rows = planner(Owned("a"), master, layer)
        steps = [r.edit for r in rows if r.edit]
        assert tuple(
            map(float, next(r.new for r in rows if r.edit).split(","))
        ) == pytest.approx((expected_x, 100))
        module.CoordinateEditor().write(layer, steps)
        assert contour.nodes()[-1].x == pytest.approx(expected_x)
    package.setMaster("Slanted")
    widget.copy_values("italic")
    assert widget.per_master_italic.isChecked() and not widget.first_value.enabled
    assert widget.first_value.value == pytest.approx(1)


def test_native_menu_wording_when_loaded_then_uses_fontlab9_commands() -> None:
    data = r1c_records()
    rows = {Path(r["source"]).name: r for r in data["retirements"]}
    assert "Contour > Handles > Harmonize" in SCRIPT.read_text()
    assert "File > Open Fonts..." in rows["TR-ExportFont.py"]["reason"]
    assert "File > Open Fonts..." in rows["TR-ImportGlyph.py"]["reason"]
    impex = rows["Impex.py"]["reason"]
    assert (
        "File > Import > Classes..." in impex and "File > Export > Classes..." in impex
    )
    reason = rows["contour.py"]["reason"]
    for command in (
        "Contour > Join",
        "Contour > Remove Overlap",
        "Contour > Overlap > Subtract",
        "Contour > Overlap > Intersect",
        "Contour > Overlap > Exclude",
        "Element > Fusion",
        "Glyph > Set PS Direction",
        "Contour > Reverse Contour",
        "Correct Contour Direction",
    ):
        assert command in reason, command
    assert "close" in reason.lower() and "clockwise" in reason.lower()


class FreshNodeProxy:
    """A fresh wrapper which reads and writes one shared native node record."""

    def __init__(self, state: Node) -> None:
        object.__setattr__(self, "_state", state)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._state, name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._state, name, value)


class FreshContour:
    """Never reuse wrapper identities from nodes or segments getters."""

    def __init__(self, source: Contour) -> None:
        self.state = source.nodes()
        self.closed, self.isTT = source.closed, source.isTT
        self.node_calls, self.segment_calls = 0, 0
        self.returned: list = []

    def nodes(self) -> list:
        self.node_calls += 1
        result = [FreshNodeProxy(node) for node in self.state]
        self.returned.append(result)
        return result

    def segments(self) -> list:
        self.segment_calls += 1
        return [self.nodes()]


@pytest.mark.parametrize(
    "mode,a,b", [("Slope", 0.5, 1), ("Proportions", 0.4, 0.6), ("Hobby", 1, 2)]
)
def test_planning_when_native_getters_return_fresh_wrappers_then_one_snapshot_and_correct_write(
    module: Any, mode: str, a: float, b: float
) -> None:
    expected_curve, fresh = smooth_contour(), FreshContour(smooth_contour())
    first, second = fresh.nodes(), fresh.nodes()
    assert all(x is not y for x, y in zip(first, second)), (
        "Fixture must return fresh wrappers"
    )
    fresh.node_calls = 0
    layer = layer_with([fresh])
    rows = module.changes(layer, mode, a, b, False, False)
    assert fresh.node_calls == 1, "Plan must snapshot each contour's nodes exactly once"
    assert fresh.segment_calls == 0, "Segment discovery must use the node snapshot"
    assert all(r.name.startswith("contour 1 node ") for r in rows if r.edit)
    steps = [r.edit for r in rows if r.edit]
    module.CoordinateEditor().write(layer, steps)
    oracle = module.changes(layer_with([expected_curve]), mode, a, b, False, False)
    module.CoordinateEditor().write(None, [r.edit for r in oracle if r.edit])
    assert [(n.x, n.y) for n in fresh.state] == pytest.approx(
        [(n.x, n.y) for n in expected_curve.nodes()]
    )
    if mode == "Slope":
        assert [fresh.state[i].x for i in (2, 3, 4)] == [30, 50, 70], (
            "Smooth node's two handles must follow"
        )
    assert module.CoordinateEditor().check([(layer, steps)]) == []


def test_italic_when_requested_master_is_not_in_capture_then_clear_value_error(
    module: Any, monkeypatch: Any, native: Any
) -> None:
    import fly.ap.outline_panel as panel
    import fly.ap.scripting as scripting  # noqa: PLR0402

    monkeypatch.setattr(panel, "panel_type", fake_panel_type)
    monkeypatch.setattr(scripting, "current_package", fake_current_package)
    package = NS(id=1, master="Regular", masters=["Regular"], italicAngle_value=0)
    monkeypatch.setattr(fake_current_package, "package", package, raising=False)
    widget = module.panel_type()()
    widget.build_controls()
    widget.per_master_italic.setChecked(True)
    planner = widget.planner()
    with pytest.raises(
        ValueError, match="Missing.*italic angles|italic angles.*Missing"
    ):
        planner(Owned("a"), "Missing", layer_with([cubic()]))


def test_snapshot_positions_when_multiple_contours_then_preview_and_write_do_not_collide(
    module: Any,
) -> None:
    curves = [FreshContour(smooth_contour()), FreshContour(smooth_contour())]
    for n in curves[1].state:
        n.x += 500
    layer = layer_with(curves)
    rows = module.changes(layer, "Proportions", 0.4, 0.6, False, False)
    edited = [r for r in rows if r.edit]
    assert {r.name.split(" node ")[0] for r in edited} == {"contour 1", "contour 2"}
    assert len({r.name for r in edited}) == len(edited)
    steps = [r.edit for r in edited]
    module.CoordinateEditor().write(layer, steps)
    assert curves[0].node_calls == curves[1].node_calls == 1
    for a, b in zip(curves[0].state, curves[1].state):
        assert b.x - a.x == pytest.approx(500)
        assert b.y == a.y
    assert module.CoordinateEditor().check([(layer, steps)]) == []


@pytest.mark.parametrize("action", ["slope", "handles"])
def test_copy_when_getters_return_fresh_wrappers_then_reuses_one_snapshot(
    module: Any, monkeypatch: Any, native: Any, action: str
) -> None:
    import fly.ap.outline_panel as panel

    monkeypatch.setattr(panel, "panel_type", fake_panel_type)
    widget = module.panel_type()()
    widget.build_controls()
    fresh = FreshContour(cubic())
    for node in fresh.state:
        node.selected = node.isOn()
    monkeypatch.setattr(module, "selected_contours", lambda: [fresh])
    widget.copy_values(action)
    assert fresh.node_calls == 1, (
        "Copy must retain the snapshot used to find its segment"
    )
    assert widget.first_value.value == pytest.approx(
        1 if action == "slope" else 30 / math.sqrt(20000)
    )


def test_node_planning_when_parsed_then_never_uses_python_object_identity() -> None:
    tree = ast.parse(SCRIPT.read_text())
    assert not any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "id"
        for n in ast.walk(tree)
    ), "Native getters can return fresh wrappers"
