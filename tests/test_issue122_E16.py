# this_file: tests/test_issue122_E16.py
"""Verify recipe identities, contour diagnostics and durable report output."""

import ast
import hashlib
import importlib
import json
import os
import runpy
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any, ClassVar

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Scripts/Tools/Path Problem Report.py"
PRESERVED = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
SOURCES = {
    "glyph_actions_batch/recipe.py": "5c0ccb08425e3b62fb823346a8a6e16d6d38f2898a4e598b20882c9be6a98675",
    "glyphs_path_report/recipe.py": "7e0de0f7d77af0ca7a33d178001f6c246847e438ec726334d263feb12a06ee2e",
    "anchors_from_bounds/recipe.py": "77ed425e774fcf083348cc28eb07eadf5a9bc1a4d6c5e5e7af9616b44a87479e",
    "glyphs_tabular_figures/tabular_figures.py": "ccd42bf36092bf74bdce47fb6075740aa6f4858bdb25b636f616db73d996856c",
    "kerning_from_text/recipe.py": "84ef14fc8870c3a9eeee1ae8a12c1dc92cc893eae38a517fed8e782865a0f9f9",
    "sidebearings_from_reference/recipe.py": "6aadc9ae8fb5fe615d58cba6b632b599083659c42b2a3f76c01b44814bc4ae42",
    "round_coordinates/recipe.py": "0d8b04e4d93565d202239ad1df2514b150cf24a509b34de32ff08ec99f222b45",
    "contour_direction/recipe.py": "a429b53d76d7f78338b05fa05de2f904d19f794f15aafcee102be5fef5077278",
    "glyphs_tabular_figures/recipe.py": "0b689b4b62fe499d10a073c6b62f8eb6417ebbff8f7f261aae996da3ef1a5dcd",
    "glyphs_path_report/path_report.py": "083be309facb9cfa00a3973785f59c728e3f5d6b506416d9499d4cd21698f98e",
    "layer_backup/recipe.py": "468385b598a60b0dc936e359e989d4105092a1364fdd66cadea17672736c13a2",
}
DUPLICATES = {
    "glyph_actions_batch/recipe.py": ("Contours/Remove Overlap.py",),
    "anchors_from_bounds/recipe.py": ("Anchors/Place From Bounds.py",),
    "glyphs_tabular_figures/tabular_figures.py": ("Metrics/Tabular Width.py",),
    "glyphs_tabular_figures/recipe.py": ("Metrics/Tabular Width.py",),
    "sidebearings_from_reference/recipe.py": (
        "Metrics/Copy Metrics From Reference.py",
    ),
    "round_coordinates/recipe.py": (
        "Contours/Round Coordinates.py",
        "Anchors/Round To Grid.py",
        "Metrics/Round Advances.py",
    ),
    "contour_direction/recipe.py": (
        "Contours/Correct Contour Direction.py",
        "Contours/Optimize Start Points.py",
    ),
    "layer_backup/recipe.py": ("Masters/Duplicate Current Layer.py",),
}


def load() -> dict[str, Any]:
    return runpy.run_path(str(SCRIPT))


def contour(
    points: list[tuple[float, float]], closed: bool = True, on: list[bool] | None = None
) -> Any:
    flags = on if on is not None else [True] * len(points)
    nodes = [
        NS(x=x, y=y, isOn=lambda flag=flag: flag)
        for (x, y), flag in zip(points, flags, strict=True)
    ]
    return NS(closed=closed, nodes=lambda: nodes)


@pytest.fixture
def app(monkeypatch: Any) -> None:
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp/src"))
    import fontlabapp

    fly = ModuleType("fly")
    fly.ap = fontlabapp
    monkeypatch.setitem(sys.modules, "fly", fly)
    monkeypatch.setitem(sys.modules, "fly.ap", fontlabapp)
    for name in (
        "scripting",
        "kerning_batch",
        "history",
        "draft_signals",
        "edit_guards",
    ):
        module = importlib.import_module("fontlabapp." + name)
        monkeypatch.setitem(sys.modules, "fly.ap." + name, module)


def test_real_app_imports(app: None) -> None:
    for module, symbol in (
        ("kerning_batch", "write_kerning"),
        ("kerning_batch", "ensure_snapshot"),
        ("history", "refusal"),
        ("scripting", "current_package"),
        ("draft_signals", "Scope"),
    ):
        assert callable(
            getattr(importlib.import_module("fontlabapp." + module), symbol)
        )


def test_all_recipe_identities_and_duplicate_targets() -> None:
    rows = [
        r
        for r in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
        if "/recipes/" in r["target"]
    ]
    assert len(rows) == 11
    assert {
        r["target"].split("/recipes/")[1]: r["target_sha256"] for r in rows
    } == SOURCES
    for row in rows:
        assert (
            hashlib.sha256((PRESERVED / row["target"]).read_bytes()).hexdigest()
            == row["target_sha256"]
        )
    mix = ROOT.parent / "fontlab-python-scriptmix/Scripts"
    for paths in DUPLICATES.values():
        for path in paths:
            assert (mix / path).is_file(), path
            ast.parse((mix / path).read_text(), feature_version=(3, 11))
    assert set(SOURCES) - set(DUPLICATES) == {
        "glyphs_path_report/recipe.py",
        "glyphs_path_report/path_report.py",
        "kerning_from_text/recipe.py",
    }


def test_diagnostics_exact_results_and_single_node() -> None:
    diagnose = load()["diagnose"]
    assert diagnose([contour([(0, 0), (0, 0), (2, 1)], False)], 4) == [
        {"contour": 1, "kind": "open"},
        {"contour": 1, "kind": "repeated-point", "node": 1, "point": [0.0, 0.0]},
        {"contour": 1, "kind": "small-extent", "width": 2.0, "height": 1.0},
    ]
    assert diagnose([contour([(1, 1)])], 4) == [
        {"contour": 1, "kind": "few-on-curve", "count": 1},
        {"contour": 1, "kind": "small-extent", "width": 0.0, "height": 0.0},
    ]
    assert diagnose([contour([])], 4) == [
        {"contour": 1, "kind": "few-on-curve", "count": 0}
    ]
    assert diagnose([contour([(0, 0), (4, 0), (4, 4)])], 4) == []
    seam = diagnose([contour([(0, 0), (10, 0), (10, 10), (0, 0)])], 4)
    assert seam == [
        {"contour": 1, "kind": "repeated-point", "node": 4, "point": [0.0, 0.0]}
    ]
    assert diagnose([contour([(float("nan"), 0)])], 4) == [
        {"contour": 1, "kind": "nonfinite"}
    ]


@pytest.mark.parametrize("bad", [-1, float("inf"), float("nan")])
def test_threshold_refusal(bad: float) -> None:
    with pytest.raises(ValueError):
        load()["diagnose"]([], bad)


def scan_fixture(count: int = 3, cost: float = 0.0) -> tuple[Any, Any, Any, Any]:
    clock = NS(now=0.0, reads=0)
    glyphs = {
        f"g{i}Ω": NS(
            id=i,
            name=f"g{i}Ω",
            lastModified=NS(toMSecsSinceEpoch=lambda: 1),
            findLayer=lambda master: NS(
                getContours=lambda: [contour([(0, 0), (8, 0)], False)]
            ),
        )
        for i in range(count)
    }

    class Font:
        id = 19

        def __len__(self) -> int:
            return len(glyphs)

        def __getitem__(self, index: int) -> Any:
            clock.now += cost
            clock.reads += 1
            return list(glyphs.values())[index]

    package = NS(id=7, fgId=19, master="Regular", findName=glyphs.get)
    state = NS(package=package, font=Font(), glyphs=glyphs)
    service = NS(
        current_package=lambda expected_id=None: (
            state.package
            if state.package is not None and expected_id in (None, state.package.id)
            else None
        )
    )
    native = NS(CurrentFont=lambda: state.font)
    return state, service, native, clock


def finished(module: dict[str, Any], count: int = 3) -> dict[str, Any]:
    _state, service, native, clock = scan_fixture(count)
    work = module["Scan"](4, service, native, lambda: clock.now)
    result = None
    while result is None:
        result = work.step()
    return result


def test_slow_large_font_has_per_tick_budget_and_complete_output() -> None:
    module = load()
    _state, service, native, clock = scan_fixture(2500, cost=0.01)
    work = module["Scan"](4, service, native, lambda: clock.now)
    result = None
    ticks = 0
    while result is None:
        before = clock.reads
        result = work.step()
        assert 0 < clock.reads - before <= module["GLYPHS_PER_TICK"]
        assert clock.reads - before <= 5, "Each tick must yield at its own deadline"
        ticks += 1
    assert clock.now > 40 and ticks > 100, "The total scan may exceed two seconds"
    assert result["glyphs_scanned"] == len(result["problems"]) == 2500
    assert json.loads(module["report_text"](result)) == result


@pytest.mark.parametrize("kind", ["font", "master", "glyph-count", "glyph-stamp"])
def test_scan_rejects_changes_between_ticks(kind: str) -> None:
    module = load()
    state, service, native, clock = scan_fixture(80)
    work = module["Scan"](4, service, native, lambda: clock.now)
    assert work.step() is None
    if kind == "font":
        state.package = None
    elif kind == "master":
        state.package.master = "Bold"
    elif kind == "glyph-count":
        state.glyphs.pop("g0Ω")
    else:
        state.glyphs["g0Ω"].lastModified = NS(toMSecsSinceEpoch=lambda: 2)
    with pytest.raises(ValueError, match="changed"):
        for _ in range(20):
            work.step()


def test_no_font_empty_font_missing_layers_and_nonfinite_output() -> None:
    module = load()
    state, service, native, _clock = scan_fixture()
    state.package = None
    with pytest.raises(ValueError, match="font"):
        module["Scan"](4, service, native)
    assert finished(module, 0)["glyphs_scanned"] == 0
    state, service, native, _clock = scan_fixture(1)
    state.glyphs["g0Ω"].findLayer = lambda master: None
    work = module["Scan"](4, service, native)
    result = None
    while result is None:
        result = work.step()
    assert result["missing_layers"] == ["g0Ω"] and result["problems"] == {}
    state.glyphs["g0Ω"].findLayer = lambda master: NS(
        getContours=lambda: [contour([(float("inf"), 0)])]
    )
    work = module["Scan"](4, service, native)
    result = None
    while result is None:
        result = work.step()
    assert result["problems"] == {"g0Ω": [{"contour": 1, "kind": "nonfinite"}]}
    assert "Infinity" not in module["report_text"](result)


class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        self.slots.remove(slot)

    def emit(self) -> None:
        for slot in self.slots[:]:
            slot()


class Widget:
    native: ClassVar[set[str]] = {
        "font",
        "layout",
        "size",
        "rect",
        "width",
        "height",
        "update",
        "move",
        "render",
        "statusBar",
        "close",
        "show",
    }

    def __init_subclass__(cls, **kwargs: Any) -> None:
        assert not cls.native.intersection(cls.__dict__), "Native member collision"

    def __setattr__(self, name: str, value: Any) -> None:
        assert name not in self.native, "Native member collision"
        object.__setattr__(self, name, value)

    def __init__(self, *args: Any) -> None:
        self.text = args[0] if args and isinstance(args[0], str) else ""
        self.clicked, self.destroyed, self.textChanged = Signal(), Signal(), Signal()
        self.deleted = False
        self.value = 4.0
        self.enabled = True
        self.cells: dict[Any, Any] = {}

    def __getattr__(self, name: str) -> Any:
        if name in {
            "setWindowTitle",
            "setAttribute",
            "resize",
            "addWidget",
            "setContentsMargins",
            "setSpacing",
            "setReadOnly",
            "setRange",
            "setDecimals",
            "setHorizontalHeaderLabels",
            "setEditTriggers",
            "setAlternatingRowColors",
        }:
            return lambda *args: None
        raise AttributeError(name)

    def setValue(self, value: float) -> None:
        self.value = value

    def setText(self, text: str) -> None:
        self.text = text

    def setPlainText(self, text: str) -> None:
        self.text = text
        self.textChanged.emit()

    def toPlainText(self) -> str:
        return self.text

    def setEnabled(self, value: bool) -> None:
        self.enabled = value

    def setHorizontalHeaderLabels(self, labels: list[str]) -> None:
        self.column_labels = labels

    def setRowCount(self, value: int) -> None:
        self.row_count = value
        self.cells.clear()

    def setColumnCount(self, value: int) -> None:
        self.column_count = value

    def setItem(self, row: int, column: int, item: Any) -> None:
        self.cells[row, column] = item.text

    def show(self) -> None:
        pass

    def deleteLater(self) -> None:
        self.deleted = True


class Timer:
    def __init__(self, *args: Any) -> None:
        self.timeout = Signal()
        self.running = False

    def start(self, interval: int) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def fire(self) -> None:
        if self.running:
            self.timeout.emit()


def fake_qt() -> Any:
    gui = NS(
        **{
            name: Widget
            for name in (
                "QWidget",
                "QLabel",
                "QVBoxLayout",
                "QLineEdit",
                "QPlainTextEdit",
                "QPushButton",
                "QDoubleSpinBox",
                "QTableWidget",
                "QTableWidgetItem",
            )
        }
    )
    gui.QAbstractItemView = NS(NoEditTriggers=1)
    return NS(
        QtGui=gui,
        QtCore=NS(
            QTimer=Timer, Qt=NS(WindowFlags=lambda v: v, Tool=1, WA_QuitOnClose=2)
        ),
    )


def close_panel(panel: Any) -> None:
    panel.closeEvent(
        NS(accept=lambda: None, ignore=lambda: pytest.fail("Close refused"))
    )


def report_panel() -> tuple[dict[str, Any], Any, Any, Any]:
    module = load()
    state, service, native, clock = scan_fixture(80, 0.01)
    scan_type = module["Scan"]
    module["show"].__globals__["Scan"] = lambda threshold: scan_type(
        threshold, service, native, lambda: clock.now
    )
    panel = module["show"](fake_qt(), None)
    return module, panel, state, service


def drain(panel: Any) -> None:
    for _ in range(1000):
        if not panel.scan_timer.running:
            return
        panel.scan_timer.fire()
    pytest.fail("Timer did not finish")


def test_timer_cancel_restart_progress_export_and_close_retry(
    app: None, tmp_path: Path
) -> None:
    module, panel, state, _service = report_panel()
    assert panel.result is None and panel.scan_timer.running
    panel.scan_timer.fire()
    assert "80" in panel.progress_line.text and panel.result is None
    panel.cancel_scan()
    assert (
        panel.result is None
        and not panel.scan_timer.running
        and panel.scan_work is None
    )
    panel.destination.setText(str(tmp_path / "cancelled.json"))
    panel.save_report()
    assert not (tmp_path / "cancelled.json").exists()
    panel.refresh_report()
    drain(panel)
    assert len(panel.result["problems"]) == 80
    panel.destination.setText(str(tmp_path / "report.json"))
    panel.save_report()
    assert json.loads((tmp_path / "report.json").read_text())["glyphs_scanned"] == 80
    panel.save_report()
    assert "exist" in panel.status_line.text.lower()
    state.package.master = "Bold"
    panel.refresh_report()
    state.package = None
    drain(panel)
    assert panel.result is None and panel.preview.text == ""
    owned = [record[0] for record in panel.scope.records]
    original = panel.scan_timer.timeout.disconnect

    def fail(slot: Any) -> None:
        raise RuntimeError("disconnect failed")

    panel.scan_timer.timeout.disconnect = fail
    events: list[str] = []
    event = NS(
        accept=lambda: events.append("accept"), ignore=lambda: events.append("ignore")
    )
    panel.closeEvent(event)
    assert events == ["ignore"] and not panel.deleted and not panel.scan_timer.running
    panel.scan_timer.timeout.disconnect = original
    panel.closeEvent(event)
    assert events[-1] == "accept" and panel.deleted and not module["_PANELS"]
    assert all(not signal.slots for signal in owned)


def test_selection_delegates_bound_names_and_refuses_glyph_window(
    app: None, monkeypatch: Any
) -> None:
    import fontlabapp.scripting as service

    module, panel, _state, _service = report_panel()
    drain(panel)
    calls: list[Any] = []
    monkeypatch.setattr(
        service,
        "select_glyphs",
        lambda names, **kwargs: calls.append((list(names), kwargs)) or list(names),
    )
    panel.select_findings()
    assert calls == [(list(panel.result["problems"]), {"package_id": 7})]

    def refuse(*args: Any, **kwargs: Any) -> Any:
        raise ValueError("Activate the Font window before selecting glyphs.")

    monkeypatch.setattr(service, "select_glyphs", refuse)
    panel.select_findings()
    assert "Activate the Font window" in panel.status_line.text
    close_panel(panel)
    assert not module["_PANELS"]


def test_real_selection_guard_precedes_legacy_writes(
    app: None, monkeypatch: Any
) -> None:
    import fontlabapp.scripting as service

    calls: list[str] = []
    native = NS(
        flWorkspace=NS(
            instance=lambda: NS(
                currentPackage=NS(id=7, isNull=False), activeFontPanel=None
            )
        )
    )
    legacy = NS(
        fl=NS(
            font=[NS(name="A")],
            Unselect=lambda: calls.append("clear"),
            Select=lambda i: calls.append("select"),
        )
    )
    monkeypatch.setattr(
        service, "_native", lambda name: legacy if name == "FL" else native
    )
    with pytest.raises(ValueError, match="Font window"):
        service.select_glyphs(["A"], package_id=7)
    assert calls == [], "fl#8528 guard must run before either unsafe writer"


@pytest.mark.parametrize("bad", ["\0", "\u00a0", "\u2028", "\u2029"])
def test_export_refusals_and_roundtrip(bad: str, tmp_path: Path) -> None:
    module = load()
    report = finished(module)
    with pytest.raises(ValueError, match="Qt"):
        module["export_report"](str(tmp_path / (bad + ".json")), report)
    with pytest.raises(ValueError):
        module["export_report"]("relative.json", report)
    path = tmp_path / "report.json"
    module["export_report"](str(path), report)
    assert json.loads(path.read_text()) == report
    with pytest.raises(FileExistsError):
        module["export_report"](str(path), report)


def kern_module() -> dict[str, Any]:
    return runpy.run_path(str(ROOT / "Scripts/Tools/Import Kerning Pair List.py"))


def test_kerning_parser_exact_comments_rounding_and_errors() -> None:
    parse = kern_module()["parse_pairs"]
    rows = parse(
        "# pairs\nA V -75.5 # comment\n@L_A @R_V 0\nV A 2.5\nbroken\nA V -1\nA T nan\n"
    )
    assert [(r["line"], r["left"], r["right"], r["value"]) for r in rows[:3]] == [
        (2, "A", "V", -76),
        (3, "@L_A", "@R_V", 0),
        (4, "V", "A", 3),
    ]
    assert [r["line"] for r in rows if r["error"]] == [5, 6, 7]
    assert parse(" #nothing\n") == []


@pytest.fixture
def kern_host(app: None, monkeypatch: Any) -> tuple[Any, Any, Any, Any]:
    from copy import deepcopy

    import fontlabapp.history as history  # noqa: PLR0402 - preserve module imports
    import fontlabapp.kerning_batch as batch
    import fontlabapp.scripting as service

    class Kern:
        def __init__(self) -> None:
            self.values = {("A", "V"): -20, ("T", "V"): 0}
            self.groups = {"L_A": (["A"], "KernLeft"), "R_V": (["V"], "KernRight")}
            self.fail = False
            self.drop = False

        def items(self) -> list[Any]:
            def side(name: str) -> Any:
                return NS(
                    id=name.lstrip("@"),
                    mode="groupMode" if name.startswith("@") else "glyphMode",
                )

            return [
                (NS(left=side(a), right=side(b)), value)
                for (a, b), value in self.values.items()
            ]

        def set(self, key: Any, value: int) -> None:
            if self.fail:
                raise RuntimeError("setter failed")
            if value and not self.drop:
                self.values[decode(key)] = value

        def remove(self, key: Any) -> None:
            self.values.pop(decode(key), None)

        def scale(self, value: float) -> None:
            self.values = {key: amount * value for key, amount in self.values.items()}

    def decode(key: Any) -> Any:
        return tuple(("@" if mode == "groupMode" else "") + name for name, mode in key)

    kern = Kern()
    glyphs = {name: NS(name=name, isNull=False) for name in ("A", "V", "T")}
    state = NS(package=None, autos=frozenset(), records=[], inits=[])
    package = NS(
        id=7,
        isNull=False,
        master="Regular",
        masters=["Regular"],
        upm=1000,
        kerning=lambda master: kern,
        findName=glyphs.get,
        mastersContainer=lambda: "masters",
        kerningContainer=lambda: "kerning",
        checkInitHistoryState=lambda flags: state.inits.append(flags),
    )
    state.package = package

    def notify(title: str, items: list[Any]) -> None:
        assert items == [package, "masters", "kerning"], (
            "Never notify glyphs or auto layers for kerning"
        )
        state.records.append((title, items, deepcopy(kern.values)))

    native = NS(
        flWorkspace=NS(instance=lambda: NS(currentPackage=state.package)),
        flItems=NS(notifyChangesApplied=notify),
    )
    monkeypatch.setattr(service, "_native", lambda name: native)
    monkeypatch.setattr(batch, "_native", lambda name: native)
    monkeypatch.setattr(
        history, "scan_auto_facts", lambda package: history.AutoFacts(state.autos, {})
    )
    return package, kern, state, glyphs


def test_kerning_real_writer_checkpoint_shape_zero_and_readback(kern_host: Any) -> None:
    package, kern, state, _glyphs = kern_host
    module = kern_module()
    plan = module["prepare_pairs"]("A V -80\n@L_A @R_V 0")
    assert not any(row["error"] for row in plan["rows"])
    assert module["apply_pairs"](plan, plan["text"]) is True
    assert kern.values == {("A", "V"): -80, ("T", "V"): 0, ("@L_A", "@R_V"): 0}
    assert state.inits == [0] and len(state.records) == 2
    assert [record[0] for record in state.records] == ["Import Kerning Pair List"] * 2
    assert state.records[0][2] == {("A", "V"): -20, ("T", "V"): 0}
    assert state.records[1][2] == kern.values and package.master == "Regular"


@pytest.mark.parametrize(
    "text,reason",
    [
        ("missing V -20", "Unknown glyph"),
        ("@missing V -20", "class"),
        ("@R_V V -20", "class"),
        ("A V inf", "finite"),
        ("A V 40000", "range"),
        ("A V -20\nA V -40", "Repeated"),
    ],
)
def test_kerning_bad_rows_refuse_whole_batch(
    kern_host: Any, text: str, reason: str
) -> None:
    _package, kern, state, _glyphs = kern_host
    module = kern_module()
    plan = module["prepare_pairs"](text)
    assert reason.lower() in " ".join(row["error"] for row in plan["rows"]).lower()
    with pytest.raises(ValueError):
        module["apply_pairs"](plan, text)
    assert not state.records and not state.inits and kern.values[("A", "V")] == -20


@pytest.mark.parametrize("text", ["A V -50", "@L_A V -50"])
def test_auto_layer_rule_applies_to_glyphs_and_class_members(
    kern_host: Any, text: str
) -> None:
    _package, _kern, state, _glyphs = kern_host
    state.autos = frozenset({"A"})
    module = kern_module()
    plan = module["prepare_pairs"](text)
    assert "auto" in plan["rows"][0]["error"]
    with pytest.raises(ValueError, match="rows"):
        module["apply_pairs"](plan, text)
    assert not state.records


@pytest.mark.parametrize(
    "change", ["text", "master", "pairs", "groups", "font", "auto", "glyph"]
)
def test_kerning_stale_preview_never_commits(kern_host: Any, change: str) -> None:
    package, kern, state, glyphs = kern_host
    module = kern_module()
    text = "A V -60"
    plan = module["prepare_pairs"](text)
    if change == "text":
        text = "A V -70"
    elif change == "master":
        package.master = "Bold"
    elif change == "pairs":
        kern.values[("A", "V")] = -30
    elif change == "groups":
        kern.groups["new"] = (["T"], "KernLeft")
    elif change == "font":
        state.package = None
    elif change == "auto":
        state.autos = frozenset({"A"})
    else:
        glyphs.pop("A")
    with pytest.raises(ValueError):
        module["apply_pairs"](plan, text)
    assert not state.records and not state.inits


@pytest.mark.parametrize("failure", ["fail", "drop"])
def test_kerning_failure_and_readback_mismatch_keep_undo_hint(
    kern_host: Any, failure: str
) -> None:
    _package, kern, state, _glyphs = kern_host
    module = kern_module()
    plan = module["prepare_pairs"]("A V -80")
    setattr(kern, failure, True)
    with pytest.raises(RuntimeError, match="Undo") as caught:
        module["apply_pairs"](plan, plan["text"])
    assert str(caught.value).count("Undo") == 1
    assert str(caught.value).startswith("Kerning may be partially changed;")
    assert len(state.records) == 2


def test_pair_list_panel_preview_invalidation_apply_and_cleanup(kern_host: Any) -> None:
    _package, kern, _state, _glyphs = kern_host
    module = kern_module()
    panel = module["show"](fake_qt(), None)
    panel.input_field.setPlainText("A V -80\n@L_A @R_V 0")
    panel.preview_pairs()
    assert panel.preview_table.row_count == 2 and panel.apply_button.enabled
    assert panel.preview_table.cells[0, 4] == "-80"
    assert panel.preview_table.column_labels[3] == "Explicit now"
    panel.input_field.setPlainText("A V -90")
    assert panel.plan_data is None and not panel.apply_button.enabled
    panel.preview_pairs()
    panel.apply_list()
    assert kern.values[("A", "V")] == -90
    signals = [record[0] for record in panel.scope.records]
    close_panel(panel)
    assert (
        panel.deleted
        and all(not signal.slots for signal in signals)
        and not module["_PANELS"]
    )


@pytest.mark.parametrize("filename", ["Path Problem Report.py", "Import Kerning Pair List.py"])
def test_public_source_python311_and_attribution(filename: str) -> None:
    text = (ROOT / "Scripts/Tools" / filename).read_text()
    ast.parse(text, feature_version=(3, 11))
    assert "Based on the author's own FontLab sample, Apache-2.0." in text
    for term in (
        "rescued/",
        "SHA256:",
        "issue 122",
        "archived",
        "QApplication(",
        "core.QObject",
    ):
        assert term not in text


@pytest.mark.parametrize(
    "text", ["A V 1\u2028A T 2", "A V 1\u2029A T 2", "A\u00a0V 2", "A V 2\0"]
)
def test_pair_text_refuses_lossy_characters_before_splitting(text: str) -> None:
    with pytest.raises(ValueError, match="Qt"):
        kern_module()["parse_pairs"](text)


def test_noop_empty_list_and_missing_font_do_not_write(kern_host: Any) -> None:
    _package, _kern, state, _glyphs = kern_host
    module = kern_module()
    plan = module["prepare_pairs"]("A V -20")
    assert module["apply_pairs"](plan, plan["text"]) is False
    empty = module["prepare_pairs"]("# empty")
    with pytest.raises(ValueError, match="rows"):
        module["apply_pairs"](empty, empty["text"])
    state.package = None
    with pytest.raises(ValueError, match="font"):
        module["prepare_pairs"]("A V -30")
    assert not state.records and not state.inits


def test_other_master_and_glyph_inventory_are_preserved(kern_host: Any) -> None:
    from copy import deepcopy

    package, kern, state, glyphs = kern_host
    other = deepcopy(kern)
    other.values[("A", "V")] = -100
    package.masters.append("Bold")
    package.kerning = {"Regular": kern, "Bold": other}.__getitem__
    module = kern_module()
    plan = module["prepare_pairs"]("A V -45")
    original_names = set(glyphs)
    assert module["apply_pairs"](plan, plan["text"])
    assert kern.values[("A", "V")] == -45 and other.values[("A", "V")] == -100
    assert set(glyphs) == original_names and len(state.records) == 2


@pytest.mark.parametrize("filename", ["Path Problem Report.py", "Import Kerning Pair List.py"])
def test_entry_points_use_the_host_window(
    filename: str, monkeypatch: Any, capsys: Any
) -> None:
    module = runpy.run_path(str(ROOT / "Scripts/Tools" / filename))
    fly = ModuleType("fly")
    fly.fl = NS(MainWindow=lambda: "host")
    fly.qt = object()
    monkeypatch.setitem(sys.modules, "fly", fly)
    calls: list[Any] = []
    module["main"].__globals__["show"] = lambda qt, parent: calls.append((qt, parent))
    module["main"]()
    assert calls == [(fly.qt, "host")]

    def fail(qt: Any, parent: Any) -> None:
        raise TimeoutError("capture expired")

    module["main"].__globals__["show"] = fail
    module["main"]()
    assert "capture expired" in capsys.readouterr().out


def test_close_during_scan_stops_timer_before_deletion(app: None) -> None:
    module, panel, _state, _service = report_panel()
    panel.scan_timer.fire()
    assert panel.scan_work is not None and panel.result is None
    close_panel(panel)
    assert not panel.scan_timer.running and not panel.scan_timer.timeout.slots
    assert panel.scan_work is None and panel.result is None and panel.deleted
    panel.scan_timer.fire()
    assert not module["_PANELS"]
