# this_file: tests/test_issue122_E15.py
# SPDX-License-Identifier: Apache-2.0
"""Exercise detached FontLab scripting tools and their owned Qt lifecycle."""

import importlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, ClassVar

import pytest

from historical_sources import recorded_sha256

ROOT = Path(__file__).resolve().parents[1]
TITLES = ("Glyph Snapshot Console", "Saved Proof Sample", "FontLab Qt Slot Reference")
ROWS = (("A", "U+0041", ""), ("space", "U+0020", ""), ("A.alt", "", ""))


def load(title: str) -> dict[str, Any]:
    return runpy.run_path(str(ROOT / "Scripts/Tools" / f"{title}.py"))


@pytest.fixture
def app(monkeypatch: Any) -> None:
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp/src"))
    app_module = importlib.import_module("fontlabapp")
    fly = ModuleType("fly")
    fly.ap = app_module
    monkeypatch.setitem(sys.modules, "fly", fly)
    monkeypatch.setitem(sys.modules, "fly.ap", app_module)
    for name in ("draft_signals", "glyph_catalog", "qt_properties", "scripting"):
        module = importlib.import_module("fontlabapp." + name)
        monkeypatch.setitem(sys.modules, "fly.ap." + name, module)
    monkeypatch.setattr(importlib.import_module("fly.ap.scripting"), "current_package",
                        lambda: SimpleNamespace(glyphsCount=300))


def test_real_app_names(app: None) -> None:
    for module, symbol in (("glyph_catalog", "capture"), ("draft_signals", "Scope"),
                           ("qt_properties", "value"), ("scripting", "current_package")):
        assert callable(getattr(importlib.import_module("fly.ap." + module), symbol))


def test_console_queries_use_detached_rows_and_reset_namespace() -> None:
    module = load(TITLES[0])
    namespace = module["snapshot_namespace"](ROWS)
    assert module["evaluate"]("len(glyphs)", namespace) == "3"
    assert module["evaluate"]("[g['name'] for g in glyphs if not g['unicode']]", namespace) == "['A.alt']"
    assert module["evaluate"]("total = len(glyphs)", namespace) == "Statement complete."
    assert module["evaluate"]("total + 2", namespace) == "5"
    assert "total" not in module["snapshot_namespace"](ROWS)
    assert module["snapshot_namespace"](()) ["glyphs"] == []
    with pytest.raises(SyntaxError):
        module["evaluate"]("[", namespace)
    with pytest.raises(ZeroDivisionError):
        module["evaluate"]("1 / 0", namespace)


def test_proof_coverage_handles_non_bmp_and_unencoded_variants() -> None:
    module = load(TITLES[1])
    rows = ROWS + (("smile", "U+1F600", ""),)
    report = json.loads(module["coverage_report"]("A 😀Ω", rows))
    assert report == {"sample": "A 😀Ω", "glyph_count": 4,
                      "missing": ["U+03A9"], "covered": ["U+0020", "U+0041", "U+1F600"]}
    assert json.loads(module["coverage_report"]("", ())) ["missing"] == []
    for text in ("a\0b", "a\u00a0b", "a\u2028b", "a\u2029b", "\ud800"):
        with pytest.raises(ValueError):
            module["checked"](text)


class Settings:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.failure = False
        self.synced = 0

    def setValue(self, key: str, value: str) -> None:
        self.values[key] = value

    def remove(self, key: str) -> None:
        self.values.pop(key, None)

    def sync(self) -> None:
        self.synced += 1

    def status(self) -> int:
        return int(self.failure)


def test_settings_persist_reset_and_write_failure() -> None:
    module = load(TITLES[1])
    settings = Settings()
    module["persist_sample"](settings, "AΩ", 0)
    assert settings.values == {"proof/sample": "AΩ"} and settings.synced == 1
    module["persist_sample"](settings, None, 0)
    assert settings.values == {} and settings.synced == 2
    settings.failure = True
    with pytest.raises(RuntimeError, match="Settings write failed"):
        module["persist_sample"](settings, "A", 0)


class ByteArray:
    def __init__(self, text: str) -> None:
        self.text = text

    def data(self) -> bytes:
        return self.text.encode("ascii")


def test_slot_report_reads_metadata_without_invoking_slots() -> None:
    module = load(TITLES[2])
    methods = [SimpleNamespace(methodType=lambda k=k: k,
                               methodSignature=lambda s=s: ByteArray(s))
               for k, s in ((1, "changed()"), (2, "clear()"), (2, "move(int,int)"))]
    meta = SimpleNamespace(className=lambda: "FontWindow", methodCount=lambda: 3,
                           method=lambda index: methods[index])
    owner = SimpleNamespace(metaObject=lambda: meta)
    report = json.loads(module["slot_report"](owner, SimpleNamespace(Signal=1, Slot=2)))
    assert report == {"class": "FontWindow", "signals": ["changed()"],
                      "slots": ["clear()", "move(int,int)"], "invoked": False,
                      "availability": "available", "PythonQt rules": list(module["PYTHONQT_RULES"])}
    with pytest.raises(ValueError, match="absent or destroyed"):
        module["slot_report"](None, SimpleNamespace(Signal=1, Slot=2))


NATIVE_NAMES = {"render", "size", "layout", "update", "font", "move", "statusBar",
                "geometry", "objectName", "windowTitle", "children", "parent", "window",
                "show", "hide", "close", "resize", "deleteLater", "setLayout",
                "setFocus", "raise_", "lower", "setVisible", "isVisible", "winId",
                "style", "palette", "cursor"}


class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []
        self.fail = False

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        if self.fail:
            raise RuntimeError("disconnect failure")
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in tuple(self.slots):
            slot(*args)


class Widget:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        assert not NATIVE_NAMES.intersection(cls.__dict__), "Native member collision"

    def __setattr__(self, name: str, value: Any) -> None:
        assert name not in NATIVE_NAMES, f"Native attribute collision: {name}"
        object.__setattr__(self, name, value)

    def __init__(self, *args: Any) -> None:
        self.clicked, self.destroyed, self.timeout = Signal(), Signal(), Signal()
        self.returnPressed = Signal()
        self._value, self.index_value = 0, 0
        self.direct_widgets: list[Any] = []
        self.labels: list[str] = []
        self.meta_value = SimpleNamespace(className=lambda: "Widget", methodCount=lambda: 0)
        self._text = ""
        self.active = self.deleted = self.visible = False
        self.buttons: list[Any] = []
        if args and isinstance(args[0], str):
            self._text = args[0]

    @property
    def text(self) -> str:
        return self._text

    def setText(self, value: str) -> None:
        self._text = value

    setPlainText = setText

    def setWindowTitle(self, value: str) -> None:
        self.title_value = value

    def setAttribute(self, *args: Any) -> None:
        pass

    def setContentsMargins(self, *args: Any) -> None:
        pass

    def setSpacing(self, *args: Any) -> None:
        pass

    def setWordWrap(self, *args: Any) -> None:
        pass

    def resize(self, *args: Any) -> None:
        pass

    def addWidget(self, widget: Any) -> None:
        self.buttons.append(widget)

    def setReadOnly(self, state: bool) -> None:
        self.read_only_value = state

    def show(self) -> None:
        self.visible = True

    def deleteLater(self) -> None:
        assert not self.destroyed.slots, "Disconnect before deleteLater"
        self.deleted = True

    def repaint(self) -> None:
        self.repainted = True

    def children(self) -> list[Any]:
        return self.direct_widgets

    def metaObject(self) -> Any:
        return self.meta_value

    def isWidgetType(self) -> bool:
        return True

    def addItem(self, text: str) -> None:
        self.labels.append(text)

    @property
    def currentIndex(self) -> int:
        return self.index_value

    def setCurrentIndex(self, index: int) -> None:
        self.index_value = index

    @property
    def value(self) -> float:
        return self._value

    def setValue(self, value: float) -> None:
        self._value = value

    def setRange(self, minimum: float, maximum: float) -> None:
        self.range_value = (minimum, maximum)

    def start(self, interval: int) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False


class NativeSettings(Settings):
    NoError = 0
    storage: ClassVar[dict[str, str]] = {}
    instances: ClassVar[list[Any]] = []

    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.values = self.storage
        self.identity = args[:2]
        self.instances.append(self)

    def setFallbacksEnabled(self, value: bool) -> None:
        self.fallback_value = value

    def value(self, key: str, default: str) -> str:
        return self.values.get(key, default)


@pytest.fixture
def qt() -> Any:
    clipboard = Widget()
    NativeSettings.storage = {}
    NativeSettings.instances = []
    gui = SimpleNamespace(**{name: Widget for name in (
        "QWidget", "QLabel", "QLineEdit", "QPlainTextEdit", "QPushButton", "QVBoxLayout",
        "QDoubleSpinBox", "QComboBox")})
    gui.QApplication = SimpleNamespace(clipboard=lambda: clipboard, focusWidget=lambda: clipboard)
    core = SimpleNamespace(Qt=SimpleNamespace(WindowFlags=lambda value: value, Tool=1,
                                              WA_QuitOnClose=2),
                           QTimer=Widget, QSettings=NativeSettings,
                           QMetaMethod=SimpleNamespace(Signal=1, Slot=2))
    return SimpleNamespace(QtGui=gui, QtCore=core, clipboard=clipboard)


class Event:
    def __init__(self) -> None:
        self.accepted = self.ignored = False

    def accept(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.ignored = True


def close_panel(panel: Any) -> None:
    event = Event()
    panel.closeEvent(event)
    assert event.accepted and panel.deleted and panel.scope.records == []


def test_console_capture_once_errors_and_reset(app: None, qt: Any, monkeypatch: Any) -> None:
    catalog = importlib.import_module("fly.ap.glyph_catalog")
    rows = tuple((str(i), "", "") for i in range(300))
    monkeypatch.setattr(catalog, "capture", lambda **kwargs: SimpleNamespace(rows=rows))
    module = load(TITLES[0])
    calls: list[Any] = []
    original = module["show"].__globals__["snapshot_namespace"]

    def counted(records: Any) -> Any:
        calls.append(records)
        return original(records)

    monkeypatch.setitem(module["show"].__globals__, "snapshot_namespace", counted)
    panel = module["show"](qt, Widget())
    panel.capture_rows()
    assert len(calls) == 1 and len(panel.query_namespace["glyphs"]) == 300
    assert not hasattr(panel, "batch_timer"), "No per-tick record conversion"
    panel.query_entry.setText("len(glyphs)")
    panel.query_entry.returnPressed.emit()
    assert panel.output_box.text == "300"
    panel.query_entry.setText("1 / 0")
    panel.query_entry.returnPressed.emit()
    assert "ZeroDivisionError" in panel.output_box.text
    monkeypatch.setattr(catalog, "capture", lambda **kwargs: (_ for _ in ()).throw(TimeoutError("expired")))
    panel.box.buttons[-3].clicked.emit(True)
    assert "expired" in panel.status_line.text and panel.query_namespace is None
    close_panel(panel)


@pytest.mark.parametrize("error", [ValueError("Open a font"), RuntimeError("Changed font"), TimeoutError("expired")])
def test_proof_capture_refusals_clear_stale_output(app: None, qt: Any, monkeypatch: Any, error: Exception) -> None:
    module = load(TITLES[1])
    catalog = importlib.import_module("fly.ap.glyph_catalog")
    monkeypatch.setattr(catalog, "capture", lambda **kwargs: SimpleNamespace(rows=ROWS))
    panel = module["show"](qt, Widget())
    panel.sample_entry.setText("A")
    panel.check_coverage()
    assert json.loads(panel.output_box.text)["covered"] == ["U+0041"]
    monkeypatch.setattr(catalog, "capture", lambda **kwargs: (_ for _ in ()).throw(error))
    panel.box.buttons[-2].clicked.emit(True)
    assert panel.output_box.text == "" and str(error) in panel.status_line.text
    panel.copy_sample()
    assert qt.clipboard.text == "A"
    panel.save_sample()
    assert panel.sample_settings.identity == ("FontLabPythonExamples", "SavedProofSample")
    assert panel.sample_settings.fallback_value is False
    close_panel(panel)
    reopened = module["show"](qt, Widget())
    assert reopened.sample_entry.text == "A"
    reopened.reset_sample()
    assert NativeSettings.storage == {} and reopened.sample_entry.text == module["DEFAULT"]
    close_panel(reopened)


@pytest.mark.parametrize("title", TITLES)
def test_owned_close_retries_and_fences_callbacks(app: None, qt: Any, title: str) -> None:
    module = load(title)
    panel = module["show"](qt, Widget())
    signal, slot, _ = panel.scope.records[-1]
    signal.fail = True
    event = Event()
    panel.closeEvent(event)
    assert event.ignored and not panel.deleted and panel in module["_PANELS"]
    signal.fail = False
    close_panel(panel)
    assert panel not in module["_PANELS"]
    before = panel.status_line.text
    slot()
    assert panel.status_line.text == before, "Closed callbacks must be fenced"


@pytest.mark.parametrize("title", TITLES)
def test_main_uses_existing_application_only(app: None, qt: Any, monkeypatch: Any, title: str) -> None:
    fly = sys.modules["fly"]
    fly.qt, fly.fl = qt, SimpleNamespace(MainWindow=lambda: Widget())
    module = runpy.run_path(str(ROOT / "Scripts/Tools" / f"{title}.py"), run_name="__main__")
    assert len(module["_PANELS"]) == 1
    close_panel(module["_PANELS"][0])



# Freeze the complete source denominator. Sources are read, never executed.
SOURCE_HASHES = {'contour-canvas': '9ec8bcc1c515d3352ef161a2eed90a5ac330f7f50aab2388c584bb82aa713fc7', 'timer-batch': '9bede8e4486e03be3c182cd474084ab6a9200ca2419efb4ae3b2cc70ca78bfaa', 'contour-scene': '39e6092d837e4c50f54d6aa8915d99e2546eb04de358a3ae1443940e41937e7e', 'glyph-list': '6cceb5202a9f4bdec96c993d7cf66d225d7b181e594cfa44d7478d095ff9ecbc', 'signal-lifetime': '3fac71d6f9a70e89b14266dbcc8127d246cbaa3eb4bc69d94d433390b88bc4de', 'sandbox-settings': 'a3dacffc45c2c5e1d1bc83b1a5b672c20db9a3873d0cc98166515ed96d1fd8bb', 'worker-glyph-queue': 'b130173c877a6e69a33dc1bca3d6784d7f043a531b318e8314005dc63fb22731', 'owned-key-filter': '0aa8c7ff06fb6df60726380356cb4282245e3d88188cfb86f65b8e576660ba34', 'loaded-glyph-form': '263c0c6715f4fe22418b6da27ee83cc2a39683e23bcdc58723ab7d60e34b1c87', 'glyph-properties': '7d0b1454d9e2a66e871b398e26ca73a5a696d9a77b0c405cf5da5c8d8e228eab', 'metrics-table': '7966a62e0a1613e3f2f1b0e9ed279224b5a4ae9fe4f0bdca0dd96c10e1218667', 'metrics-undo': 'aaf8d655ed841c54c307a08ae3aee0dfd80b53f976fc9f082fe9242d5f1257c3', 'owned-dock': 'cf9c0cdc8f06d74a7d518c8289aaad32991dd571d9630c2b19f03080c184690f', 'metric-controls': '5d889151cfff9a22cf504b47b5f7185cf3203baccc34f096b0db8b7a0c686174', 'callback-errors': 'b5a363f9169456507ecc8d47fa5bf1e92007a6b7f533dca2c4aec5f86f4423d1', 'compiled-slot-exposure': 'e81955446fce469142051973c7c630cac6d44b88aa46ee1ea5aa8cd5e8805108', 'owned-repl': '3b5fb1184dd28f2caa23b1e90eb53308a0d77ead01f5a0bc4fd3cc62bf7d95df', 'plugin-tokens': 'e4c04bf842585c9dd42bc884785f98bc21ce488ce76fa3c4c0ddc9661b98a169'}


@pytest.mark.parametrize("stem,digest", SOURCE_HASHES.items())
def test_source_identity_bytes_and_first_party_provenance(stem: str, digest: str) -> None:

    source = "rescued/part2/ports/insights/" + stem + ".py"
    index = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    record = next(row for row in index if row["target"] == source)
    assert record["target_sha256"] == digest
    assert recorded_sha256(source) == digest
    assert not (ROOT / record["menu"]).exists(), "Never restore a preserved dispatcher"


@pytest.mark.parametrize("title", TITLES)
def test_script_is_python311_and_has_no_native_writes(title: str) -> None:
    import ast

    source = (ROOT / "Scripts/Tools" / f"{title}.py").read_text()
    tree = ast.parse(source, feature_version=(3, 11))
    forbidden = {"notifyChangesApplied", "commit", "CurrentFont", "exec_", "QApplication"}
    calls = {node.func.attr for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    assert not forbidden.intersection(calls), "New panels never write font data or create an application"
    assert "SPDX-License-Identifier: Apache-2.0" in source
    assert source.splitlines()[0] == "# this_file: Scripts/Tools/" + title + ".py"
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            members = {item.name for item in node.body if isinstance(item, ast.FunctionDef)}
            assert not (NATIVE_NAMES - {"closeEvent"}).intersection(members)


DUPLICATES = {
    "contour-canvas": "fontlab-python-examples/Scripts/Drawing/Glyph Outline SVG.py",
    "contour-scene": "fontlab-python-examples/Scripts/Drawing/Glyph Outline SVG.py",
    "glyph-list": "fontlab-python-examples/Scripts/Models/Glyph Name Filter.py",
    "signal-lifetime": "fontlab-python-examples/Scripts/Forms/Glyph Metrics Form.py",
    "owned-key-filter": "fontlab-python-examples/Scripts/Tools/Glyph Name Completion with Focus.py",
    "loaded-glyph-form": "fontlab-python-examples/Scripts/Forms/Glyph Metrics Form.py",
    "glyph-properties": "fontlab-python-examples/Scripts/Models/Glyph Review Form.py",
    "metrics-table": "fontlab-python-examples/Scripts/Models/Glyph Metrics Model.py",
    "metrics-undo": "fontlab-python-scriptmix/Scripts/Metrics/Scale Advances.py",
    "owned-dock": "fontlab-python-examples/Scripts/Windows/Unicode Issues Dock.py",
    "metric-controls": "fontlab-python-examples/Scripts/Widgets/Glyph Spacing Offset.py",
    "callback-errors": "fontlab-python-examples/Scripts/Forms/Glyph Metrics Form.py",
}
PORTED = {"timer-batch": TITLES[0], "owned-repl": TITLES[0],
          "sandbox-settings": TITLES[1], "compiled-slot-exposure": TITLES[2]}
RETIRED = {"worker-glyph-queue", "plugin-tokens"}


def test_dispositions_cover_all_eighteen_without_overlap() -> None:
    assert len(SOURCE_HASHES) == 18
    assert set(SOURCE_HASHES) == set(DUPLICATES) | set(PORTED) | RETIRED
    assert not set(DUPLICATES).intersection(PORTED) and not RETIRED.intersection(PORTED)
    for destination in DUPLICATES.values():
        path = ROOT.parent / destination
        assert path.is_file(), f"Duplicate destination must exist: {destination}"
        assert "this_file:" in path.read_text(), destination
    for title in PORTED.values():
        assert (ROOT / "Scripts/Tools" / f"{title}.py").is_file()


def test_native_slot_reference_button_and_parent_destruction(app: None, qt: Any) -> None:
    module = load(TITLES[2])
    method = SimpleNamespace(methodType=lambda: 2, methodSignature=lambda: ByteArray("clear()"))
    meta = SimpleNamespace(className=lambda: "FontLab", methodCount=lambda: 1,
                           method=lambda index: method)
    owner = Widget()
    owner.meta_value = meta
    panel = module["show"](qt, owner)
    panel.box.buttons[-1].clicked.emit(True)
    assert json.loads(panel.output_box.text)["slots"] == ["clear()"]
    panel.destroyed.emit()
    assert panel not in module["_PANELS"] and panel.scope.records == []


def test_settings_read_error_cleans_up_owned_panel(app: None, qt: Any, monkeypatch: Any) -> None:
    monkeypatch.setattr(NativeSettings, "status", lambda self: 1)
    module = load(TITLES[1])
    with pytest.raises(RuntimeError, match="Cannot read"):
        module["show"](qt, Widget())
    assert module["_PANELS"] == [], "Failed setup must release the panel owner"


def test_empty_font_finishes_console_capture(app: None, qt: Any, monkeypatch: Any) -> None:
    monkeypatch.setattr(importlib.import_module("fly.ap.glyph_catalog"), "capture",
                        lambda **kwargs: SimpleNamespace(rows=()))
    panel = load(TITLES[0])["show"](qt, Widget())
    panel.capture_rows()
    assert panel.query_namespace["glyphs"] == []
    close_panel(panel)


@pytest.mark.parametrize("title", TITLES[:2])
def test_capture_deadline_scales_with_simulated_per_glyph_cost(app: None, qt: Any, monkeypatch: Any, title: str) -> None:
    module = load(title)
    clock = SimpleNamespace(now=100.0)
    monkeypatch.setitem(module["show"].__globals__, "monotonic", lambda: clock.now)
    scripting = importlib.import_module("fly.ap.scripting")
    catalog = importlib.import_module("fly.ap.glyph_catalog")
    budgets: list[float] = []
    panel = module["show"](qt, Widget())
    for count in (10, 50000):
        monkeypatch.setattr(scripting, "current_package", lambda count=count: SimpleNamespace(glyphsCount=count))

        def expensive(*, deadline: float, count: int = count) -> Any:
            assert "Scanning" in panel.status_line.text
            budgets.append(deadline - clock.now)
            for _ in range(count):
                clock.now += 0.001
                if clock.now >= deadline:
                    raise TimeoutError("fake per-glyph scan cost exceeded budget")
            return SimpleNamespace(rows=tuple((str(i), "U+0041", "") for i in range(count)))

        monkeypatch.setattr(catalog, "capture", expensive)
        if title == TITLES[0]:
            panel.capture_rows()
            assert len(panel.query_namespace["glyphs"]) == count
        else:
            panel.check_coverage()
            assert json.loads(panel.output_box.text)["glyph_count"] == count
    assert budgets[1] == 120.0 and budgets[1] > budgets[0] > 2.0, "Cap time, not font size"
    close_panel(panel)


def test_console_infinite_loop_deadline_chains_local_trace_and_restores() -> None:
    from time import monotonic

    module = load(TITLES[0])
    observed: list[str] = []
    previous = sys.gettrace()

    def old_local(frame: Any, event: str, arg: Any) -> Any:
        if frame.f_code.co_filename == "<glyph-snapshot>":
            observed.append(event)
        return old_local

    def old_global(frame: Any, event: str, arg: Any) -> Any:
        return old_local

    sys.settrace(old_global)
    started = monotonic()
    try:
        with pytest.raises(TimeoutError):
            module["evaluate"]("while True: pass", module["snapshot_namespace"](ROWS), 0.03)
        assert sys.gettrace() is old_global, "Always restore the existing host trace"
    finally:
        sys.settrace(previous)
    assert monotonic() - started < 1.0 and "line" in observed
    assert "opcode" not in observed, "Do not add opcode events to an earlier line-only trace"


def test_console_builtins_print_and_deadline_limits() -> None:
    module = load(TITLES[0])
    namespace = module["snapshot_namespace"](ROWS)
    assert module["evaluate"]("print(any(g['unicode'] for g in glyphs))", namespace) == "True\n"
    for seconds in (0, -1, 61, float("nan")):
        with pytest.raises(ValueError):
            module["evaluate"]("1", namespace, seconds)
    assert namespace["__builtins__"] is module["snapshot_namespace"](())["__builtins__"]


def test_console_timeout_is_visible_in_output(app: None, qt: Any) -> None:
    module = load(TITLES[0])
    panel = module["show"](qt, Widget())
    assert panel.deadline_control.value == 5 and panel.deadline_control.range_value[1] == 60
    panel.query_namespace = module["snapshot_namespace"](ROWS)
    panel.deadline_control.setValue(0.03)
    panel.query_entry.setText("while True: pass")
    panel.query_entry.returnPressed.emit()
    assert "TimeoutError" in panel.output_box.text
    close_panel(panel)


@pytest.mark.parametrize("broken", ["method", "methodType", "methodSignature", "data", "enum"])
def test_slot_enumeration_fallback_keeps_rules_and_discards_partial_rows(broken: str) -> None:
    module = load(TITLES[2])
    method = SimpleNamespace(methodType=lambda: 2, methodSignature=lambda: ByteArray("clear()"))
    meta = SimpleNamespace(className=lambda: "FontLab", methodCount=lambda: 1,
                           method=lambda index: method)
    kinds = SimpleNamespace(Signal=1, Slot=2)
    if broken == "method":
        del meta.method
    elif broken == "methodType":
        del method.methodType
    elif broken == "methodSignature":
        del method.methodSignature
    elif broken == "data":
        method.methodSignature = lambda: object()
    else:
        kinds = None
    report = json.loads(module["slot_report"](SimpleNamespace(metaObject=lambda: meta), kinds))
    assert report["availability"] == "not available on this build"
    assert report["signals"] == report["slots"] == []
    assert len(report["PythonQt rules"]) == 9


def test_reference_targets_main_focus_direct_children_and_destroyed_target(app: None, qt: Any) -> None:
    import gc

    owner, focus, child = Widget(), Widget(), Widget()
    qt.QtGui.QApplication.focusWidget = lambda: focus
    module = load(TITLES[2])
    owner.direct_widgets = [child]
    was_enabled = gc.isenabled()
    targets = module["object_choices"](qt.QtGui, owner)
    assert [item[1] for item in targets] == [owner, focus, child]
    assert gc.isenabled() == was_enabled
    panel = module["show"](qt, owner)
    for index, target in enumerate((owner, focus, child)):
        panel.target_picker.setCurrentIndex(index)
        panel.read_slots()
        assert json.loads(panel.output_box.text)["availability"] == "available"
    child.destroyed.emit()
    assert panel.targets[2] is None
    panel.box.buttons[-1].clicked.emit(True)
    assert "destroyed" in panel.status_line.text
    close_panel(panel)


def test_reference_direct_children_conversion_preserves_gc_state() -> None:
    import gc

    module = load(TITLES[2])
    seen: list[bool] = []

    def children() -> list[Any]:
        seen.append(gc.isenabled())
        raise RuntimeError("conversion refused")

    owner = SimpleNamespace(children=children)
    gui = SimpleNamespace(QApplication=SimpleNamespace(focusWidget=lambda: None))
    was_enabled = gc.isenabled()
    for enable in (True, False):
        gc.enable() if enable else gc.disable()
        try:
            with pytest.raises(RuntimeError, match="conversion refused"):
                module["object_choices"](gui, owner)
            assert gc.isenabled() == enable
        finally:
            gc.enable() if was_enabled else gc.disable()
    assert seen == [False, False]


@pytest.mark.parametrize("title", TITLES[:2])
def test_scan_refuses_absent_font_before_catalog_access(app: None, qt: Any, monkeypatch: Any, title: str) -> None:
    module = load(title)
    monkeypatch.setattr(importlib.import_module("fly.ap.scripting"), "current_package", lambda: None)
    with pytest.raises(ValueError, match="Open a font"):
        module["capture_current"](Widget())


@pytest.mark.parametrize("source", ["1 / 0", "[", "while True: pass"])
def test_console_restores_stdout_and_trace_on_error(source: str) -> None:
    module = load(TITLES[0])
    previous_trace, previous_stdout = sys.gettrace(), sys.stdout
    with pytest.raises((ZeroDivisionError, SyntaxError, TimeoutError)):
        module["evaluate"](source, module["snapshot_namespace"](ROWS), 0.02)
    assert sys.gettrace() is previous_trace and sys.stdout is previous_stdout


def test_console_preserves_a_trace_that_requested_opcodes() -> None:
    module = load(TITLES[0])
    previous = sys.gettrace()
    seen: list[str] = []

    def local(frame: Any, event: str, arg: Any) -> Any:
        if frame.f_code.co_filename == "<glyph-snapshot>":
            seen.append(event)
        return local

    def global_trace(frame: Any, event: str, arg: Any) -> Any:
        frame.f_trace_opcodes = True
        return local

    sys.settrace(global_trace)
    try:
        assert module["evaluate"]("sum(range(10))", module["snapshot_namespace"](ROWS)) == "45"
        assert sys.gettrace() is global_trace
    finally:
        sys.settrace(previous)
    assert "opcode" in seen


def test_reference_fallback_is_displayed_by_the_panel(app: None, qt: Any) -> None:
    owner = Widget()
    owner.meta_value = SimpleNamespace(className=lambda: "FontLab", methodCount=lambda: 1)
    panel = load(TITLES[2])["show"](qt, owner)
    panel.read_slots()
    assert "not available on this build" in panel.output_box.text
    panel.target_picker.setCurrentIndex(-1)
    panel.box.buttons[-1].clicked.emit()
    assert "Choose an available widget" in panel.status_line.text
    assert "PythonQt rules" in panel.output_box.text
    close_panel(panel)


@pytest.mark.parametrize("opaque", [object(), 0])
def test_console_opaque_host_trace_refuses_without_settrace(monkeypatch: Any, opaque: Any) -> None:
    module = load(TITLES[0])
    namespace = module["snapshot_namespace"](ROWS)
    installed: list[Any] = []
    with monkeypatch.context() as patch:
        patch.setattr(sys, "gettrace", lambda: opaque)
        patch.setattr(sys, "settrace", installed.append)
        with pytest.raises(RuntimeError, match="Time limit unavailable: FontLab already traces this call"):
            module["evaluate"]("changed = True", namespace)
    assert installed == [] and "changed" not in namespace


@pytest.mark.parametrize("stored", ["A\0", "A\u00a0", "A\u2028", "A\u2029", "\ud800"])
def test_refused_saved_sample_keeps_panel_open_for_replacement(app: None, qt: Any, stored: str) -> None:
    NativeSettings.storage = {"proof/sample": stored}
    module = load(TITLES[1])
    panel = module["show"](qt, Widget())
    assert panel.visible and panel.sample_entry.text == module["DEFAULT"]
    assert "unusable" in panel.status_line.text.lower()
    assert NativeSettings.storage["proof/sample"] == stored, "Do not silently rewrite settings"
    panel.sample_entry.setText("A")
    panel.save_sample()
    assert NativeSettings.storage["proof/sample"] == "A"
    close_panel(panel)


@pytest.mark.parametrize("request_opcodes", [False, True])
def test_query_frame_opcode_flag_restored_after_yield_and_error(request_opcodes: bool) -> None:
    module = load(TITLES[0])
    namespace = module["snapshot_namespace"](ROWS)
    retained: list[tuple[Any, bool]] = []
    previous = sys.gettrace()

    def prior(frame: Any, event: str, arg: Any) -> Any:
        if frame.f_code.co_filename == "<glyph-snapshot>" and event == "call":
            frame.f_trace_opcodes = request_opcodes
            retained.append((frame, frame.f_trace_opcodes))
        return prior

    sys.settrace(prior)
    try:
        module["evaluate"]("g = (i for i in range(3)); first = g.__next__()", namespace)
        with pytest.raises(ZeroDivisionError):
            module["evaluate"]("1 / 0", namespace)
        assert sys.gettrace() is prior
        assert retained and all(frame.f_trace_opcodes == flag for frame, flag in retained)
    finally:
        sys.settrace(previous)
        retained.clear()


def test_console_catch_all_caveat_and_narrow_pythonqt_rules() -> None:
    console, reference = load(TITLES[0]), load(TITLES[2])
    assert "catches every exception can outlive" in console["HELP"]
    assert "catches every exception can outlive" in console["__doc__"]
    rules = reference["PYTHONQT_RULES"]
    assert "calculator" in rules[2] and "observed" in rules[2].lower()
    assert "setEasingCurve" in rules[4] and "QDialogButtonBox" in rules[4]
    assert "retain ownership" not in rules[6]


def test_console_opaque_trace_message_in_panel_runs_nothing(app: None, qt: Any, monkeypatch: Any) -> None:
    module = load(TITLES[0])
    panel = module["show"](qt, Widget())
    panel.query_namespace = module["snapshot_namespace"](ROWS)
    panel.query_entry.setText("changed = True")
    with monkeypatch.context() as patch:
        patch.setattr(sys, "gettrace", lambda: object())
        panel.query_entry.returnPressed.emit()
    assert "Time limit unavailable: FontLab already traces this call" in panel.output_box.text
    assert "changed" not in panel.query_namespace
    close_panel(panel)


@pytest.mark.parametrize("source,expected", [("len(glyphs)", "3"), ("while True: pass", None)])
def test_console_without_prior_trace_runs_and_restores_none(source: str, expected: str | None) -> None:
    module = load(TITLES[0])
    namespace = module["snapshot_namespace"](ROWS)
    previous = sys.gettrace()
    sys.settrace(None)
    try:
        if expected is None:
            with pytest.raises(TimeoutError):
                module["evaluate"](source, namespace, 0.02)
        else:
            assert module["evaluate"](source, namespace) == expected
        assert sys.gettrace() is None, "Restore the genuinely untraced state"
    finally:
        sys.settrace(previous)


def test_console_panel_without_prior_trace_runs_and_times_out(app: None, qt: Any) -> None:
    module = load(TITLES[0])
    panel = module["show"](qt, Widget())
    panel.query_namespace = module["snapshot_namespace"](ROWS)
    previous = sys.gettrace()
    sys.settrace(None)
    try:
        panel.query_entry.setText("len(glyphs)")
        panel.query_entry.returnPressed.emit()
        assert panel.output_box.text == "3" and sys.gettrace() is None
        panel.deadline_control.setValue(0.02)
        panel.query_entry.setText("while True: pass")
        panel.query_entry.returnPressed.emit()
        assert "TimeoutError" in panel.output_box.text and sys.gettrace() is None
    finally:
        sys.settrace(previous)
        close_panel(panel)
