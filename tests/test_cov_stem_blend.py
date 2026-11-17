# this_file: tests/test_cov_stem_blend.py
# SPDX-License-Identifier: Apache-2.0
"""Cover Stem Blend host-free: blend math, SVG, capture, Create Layer and the panel."""

from __future__ import annotations

import runpy
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any, ClassVar

import pytest
from _cov_support import Event, Signal, Widget, install_fly, make_qt
from module_doubles import install_module

SCRIPT = Path(__file__).resolve().parents[1] / "Scripts/Drawing/Stem Blend.py"
SQUARE = [(0.0, 0.0, True), (50.0, 0.0, True), (50.0, 100.0, True), (0.0, 100.0, True)]
WIDE = [(0.0, 0.0, True), (100.0, 0.0, True), (100.0, 200.0, True), (0.0, 200.0, True)]
STEMS, TARGET, SCALES = (50.0, 100.0, 40.0, 80.0), (75.0, 60.0), (1.0, 1.0)


class Field(Widget):
    """Widget with the combo/line-edit change signals Stem Blend connects."""

    made: ClassVar[list[Field]] = []

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.currentIndexChanged, self.textChanged = Signal(), Signal()
        Field.made.append(self)


class Node:
    def __init__(self, x: float, y: float, on: bool = True) -> None:
        self.x, self.y, self.on = x, y, on

    def isOn(self) -> bool:
        return self.on


class Contour:
    def __init__(self, nodes: list[Node], closed: bool = True, isTT: bool = False) -> None:
        self._nodes, self.closed, self.isTT = nodes, closed, isTT

    def nodes(self) -> list[Node]:
        return self._nodes


class Shape:
    def __init__(self, contours: list[Contour] | None = None, component: bool = False) -> None:
        self.contours, self.isComponent = contours or [], component
        self.transform = NS(isIdentity=lambda: True)

    def addContour(self, contour: Contour, *flags: Any) -> None:
        self.contours.append(contour)


class Layer:
    def __init__(self, name: str = "", points: list | None = None, lid: int = 0) -> None:
        self.name, self.id, self.isNull, self.advanceWidth = name, lid, False, 500.0
        self.shapes = [Shape([Contour([Node(*p) for p in points])])] if points else []

    def addShape(self, shape: Shape) -> None:
        self.shapes.append(shape)


def font() -> NS:
    package = NS(id=1, master="Light", masters=["Light", "Bold"], italicAngle_value=-0.0)
    glyph = NS(id=3, name="H", package=NS(id=1),
               layers=[Layer("Light", SQUARE, 11), Layer("Bold", WIDE, 12)])
    glyph.findLayer = lambda name: next((x for x in glyph.layers if x.name == name), None)
    glyph.addLayer = lambda layer: glyph.layers.append(layer)
    return NS(package=package, glyph=glyph)


@pytest.fixture
def module() -> dict[str, Any]:
    return runpy.run_path(str(SCRIPT))


@pytest.fixture
def env(monkeypatch: Any) -> NS:
    Field.made = []
    qt = make_qt(Field)
    qt.QtGui.QFormLayout = Field
    qt.QtCore.QPointF = lambda x, y: NS(x=x, y=y)
    fly = install_fly(monkeypatch, qt)
    state = font()
    state.mismatch, state.refusal = False, ""
    fly.scripting.current_package = lambda: state.package
    coordinates = ModuleType("fly.ap.contours.nodes.coordinates")
    coordinates.current_glyph = lambda package: state.glyph
    history = ModuleType("fly.ap.core.history.glyphs")
    history.scan_auto_facts = lambda package: "facts"
    history.refusal = lambda facts, name, what: state.refusal
    history.unstored_error = lambda mismatches: "; ".join(mismatches)

    def commit(title, fonts, glyphs, mutate, *, operation, facts, read_back):
        mutate()
        found = read_back()
        return NS(mismatches=found or (["forced"] if state.mismatch else []))

    history.commit = commit
    writer = ModuleType("fly.ap.masters.layers.writer")
    writer.settle = lambda layer: None
    guards = ModuleType("fly.ap.core.edit_guards")
    guards.disclose = lambda result, disclosure: None
    guards.append_note = lambda text, result: text
    for name, mod in (("fly.ap.contours.nodes.coordinates", coordinates),
                      ("fly.ap.core.history.glyphs", history),
                      ("fly.ap.masters.layers.writer", writer),
                      ("fly.ap.core.edit_guards", guards)):
        install_module(monkeypatch, name, mod)
    fly.root.fl = NS(
        MainWindow=lambda: "main-window", flLayer=Layer, flShape=Shape,
        flNode=lambda point, nodeType: Node(point.x, point.y, nodeType == "on"),
        flContour=lambda nodes, closed: Contour(nodes, closed),
    )
    return NS(qt=qt, fly=fly, state=state)


def test_blend_when_valid_then_midpoint_and_refusals(module: dict[str, Any]) -> None:
    blend = module["blend_contours"]
    result = blend([(True, SQUARE)], [(True, WIDE, False)], STEMS, TARGET, SCALES, 0.0)
    assert result == [(True, [(0.0, 0.0, True), (75.0, 0.0, True), (75.0, 150.0, True), (0.0, 150.0, True)], False)]
    slanted = blend([(True, SQUARE)], [(True, WIDE)], STEMS, TARGET, SCALES, 10.0)
    assert slanted[0][1][2][0] == pytest.approx(75.0)
    for args, message in (
        ((STEMS, TARGET, (0.0, 1.0), 0.0), "finite positive"),
        ((STEMS, TARGET, SCALES, 89.0), "between -85 and 85"),
        (((50.0, 50.0, 40.0, 80.0), TARGET, SCALES, 0.0), "must differ"),
        ((STEMS, (500.0, 60.0), SCALES, 0.0), "between the measured"),
    ):
        with pytest.raises(ValueError, match=message):
            blend([(True, SQUARE)], [(True, WIDE)], *args)
    with pytest.raises(ValueError, match="nonempty layers"):
        blend([], [], STEMS, TARGET, SCALES, 0.0)
    with pytest.raises(ValueError, match="node types must match"):
        blend([(True, SQUARE)], [(False, WIDE)], STEMS, TARGET, SCALES, 0.0)


def test_path_and_svg_when_cubic_quadratic_open_then_exact_or_refused(module: dict[str, Any]) -> None:
    path = module["path_text"]
    cubic = [(0, 0, True), (10, 0, False), (20, 10, False), (20, 20, True), (10, 30, False)]
    assert path(True, cubic) == "M 0 0 C 10 0 20 10 20 20 Q 10 30 0 0 Z"
    assert path(True, [(0, 0, False), (10, 0, False)], True).startswith("M 5 0 Q 0 0")
    assert path(False, [(0, 0, True), (5, 5, True)]) == "M 0 0 L 5 5"
    for args, message in (
        ((True, [(0, 0, False)]), "on-curve node"),
        ((True, [(float("nan"), 0, True)]), "finite"),
        ((False, [(0, 0, False), (1, 1, True)]), "begin and end"),
        ((True, [(0, 0, True), (1, 0, False), (2, 0, False), (3, 0, False)]), "More than two"),
    ):
        with pytest.raises(ValueError, match=message):
            path(*args)
    svg = module["svg_text"]("H&", [(True, SQUARE)])
    assert "<title>H&amp;</title>" in svg and 'viewBox="0 -100 50 100"' in svg
    with pytest.raises(ValueError, match="exactly to SVG"):
        module["svg_text"]("a\nb", [(True, SQUARE)])
    with pytest.raises(ValueError, match="no outline"):
        module["svg_text"]("H", [])


def test_helpers_when_bad_input_then_refused(module: dict[str, Any], tmp_path: Path) -> None:
    assert module["numbers"]("1 2.5", 2) == (1.0, 2.5)
    with pytest.raises(ValueError, match="space-separated"):
        module["numbers"]("a b", 2)
    with pytest.raises(ValueError, match="exactly 2"):
        module["numbers"]("1", 2)
    for name, message in (("a@b", "@ or #"), ("|temp|x", "@ or #"), ("light", "master name")):
        with pytest.raises(ValueError, match=message):
            module["checked_layer_name"](name, ("Light",))
    target = tmp_path / "out.svg"
    module["export_new"](str(target), "<svg/>")
    assert target.read_text() == "<svg/>"
    with pytest.raises(FileExistsError):
        module["export_new"](str(target), "<svg/>")
    with pytest.raises(ValueError, match="absolute .svg"):
        module["export_new"]("relative.svg", "<svg/>")
    assert not module["stored_outline_matches"]([], [(True, [], False)])
    assert not module["stored_outline_matches"]([(True, [], False)], [(False, [], False)])


def test_read_contours_when_component_or_deadline_then_refused(module: dict[str, Any]) -> None:
    layer = Layer("x", SQUARE)
    assert module["read_contours"](layer, float("inf")) == [(True, SQUARE, False)]
    with pytest.raises(TimeoutError):
        module["read_contours"](layer, 0.0)
    layer.shapes = [Shape(component=True)]
    with pytest.raises(ValueError, match="plain contour shapes"):
        module["read_contours"](layer, float("inf"))


def test_context_and_capture_when_font_state_wrong_then_refused(module: dict[str, Any], env: NS) -> None:
    state = env.state
    assert module["source_options"]() == (["Light", "Bold"], 0.0)
    label, one, two = module["capture_pair"]("Light", "Bold")
    assert label == "H" and one[0][1] == SQUARE and two[0][1] == WIDE
    with pytest.raises(ValueError, match="Both named layers"):
        module["capture_pair"]("Light", "Missing")
    state.glyph.package = NS(id=2)
    for call in (module["current_context"], lambda: module["capture_pair"]("Light", "Bold")):
        with pytest.raises(ValueError, match="glyph in the current font"):
            call()
    env.fly.scripting.current_package = lambda: None
    for call in (module["current_context"], lambda: module["capture_pair"]("Light", "Bold")):
        with pytest.raises(ValueError, match="Open a font"):
            call()


def test_create_layer_when_plan_current_then_one_step_and_stale_refused(module: dict[str, Any], env: NS) -> None:
    plan = module["prepare_blend"]("Light", "Bold", STEMS, TARGET, SCALES, 0.0)
    assert plan["name"] == "Stem 75x60 (Light)" and plan["advance"] == 500.0
    env.state.refusal = "automatic layer owner"
    with pytest.raises(ValueError, match="Kept H: automatic layer owner"):
        module["create_layer"](plan)
    env.state.refusal = ""
    message = module["create_layer"](plan)
    assert "recorded as one Undo step" in message
    added = env.state.glyph.findLayer("Stem 75x60 (Light)")
    assert module["read_contours"](added, float("inf"))[0][1][1] == (75.0, 0.0, True)
    with pytest.raises(ValueError, match="already exists"):
        module["prepare_blend"]("Light", "Bold", STEMS, TARGET, SCALES, 0.0)
    with pytest.raises(ValueError, match="already exists"):
        module["create_layer"](plan)
    env.state.glyph.layers.pop()
    env.state.glyph.layers[0].advanceWidth = 400.0
    with pytest.raises(ValueError, match="Build again"):
        module["create_layer"](plan)
    env.state.glyph.layers[0].advanceWidth = 500.0
    env.state.mismatch = True
    with pytest.raises(RuntimeError, match="use Edit > Undo. forced"):
        module["create_layer"](plan)


def button(label: str) -> Field:
    return next(w for w in Field.made if w.text() == label)


def test_panel_when_driven_then_build_create_copy_export_and_close(
    module: dict[str, Any], env: NS, tmp_path: Path
) -> None:
    panel = module["show"](env.qt, "main-window")
    fields = panel.fields
    assert fields[0].currentText() == "Light" and fields[1].currentText() == "Bold"
    button("Create Layer").clicked.emit()
    assert panel.status_line.text() == "Build the blend first."
    button("Copy SVG").clicked.emit()
    assert panel.status_line.text() == "Build the blend first."
    for index, text in ((2, "50 100"), (3, "40 80"), (4, "75 60")):
        fields[index].setText(text)
    button("Build Blend").clicked.emit()
    assert "New layer: Stem 75x60 (Light)" in panel.status_line.text() and panel.content
    button("Copy SVG").clicked.emit()
    assert env.qt.clipboard.text() == panel.content
    fields[-1].setText(str(tmp_path / "blend.svg"))
    button("Export SVG").clicked.emit()
    assert "SVG exported" in panel.status_line.text()
    button("Export SVG").clicked.emit()
    assert "partial file" in panel.status_line.text()
    button("Create Layer").clicked.emit()
    assert "recorded as one Undo step" in panel.status_line.text() and panel.plan_data is None
    fields[2].textChanged.emit("1")
    assert panel.content == ""
    fields[2].setText("x")
    button("Build Blend").clicked.emit()
    assert panel.status_line.text() == "Use space-separated numbers."
    env.fly.scripting.current_package = lambda: None
    button("Refresh Sources").clicked.emit()
    assert panel.status_line.text() == "Open a font and a glyph first."
    refused = Event()
    panel.scope.refuse = True
    panel.closeEvent(refused)
    assert refused.ignored and panel in module["_PANELS"]
    panel.scope.refuse = False
    closed = Event()
    panel.closeEvent(closed)
    assert closed.accepted and panel.deleted and panel not in module["_PANELS"]
    again = module["show"](env.qt, "main-window")
    again.release_owner()
    assert again not in module["_PANELS"]


def test_show_and_main_when_show_fails_then_released_and_reported(
    module: dict[str, Any], env: NS, capsys: Any, monkeypatch: Any
) -> None:
    monkeypatch.setattr(Field, "show_error", RuntimeError("no screen"))
    with pytest.raises(RuntimeError, match="no screen"):
        module["show"](env.qt, None)
    assert module["_PANELS"] == []
    module["main"]()
    assert capsys.readouterr().out == "Stem Blend: no screen\n"
