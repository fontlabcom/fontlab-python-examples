# this_file: tests/test_pythonqt_examples.py
# SPDX-License-Identifier: Apache-2.0
"""Offline checks of the PythonQt examples: they compile, import without FontLab,
state what they show and how to run them, and their pure logic works.

Native behaviour (widgets, painters, menus) is not proven here; see the
examples README for the checks to run inside FontLab.
"""

import importlib.util
import py_compile
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from typing import ClassVar

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted((ROOT / "examples/pythonqt").glob("*.py"))
HOST_MODULES = {"fly", "PythonQt", "fontlab", "fontlabapp", "echopy", "fontlab_echopy"}


class FgLayer:
    """Mirrors the native fgLayer: a name and shapes, but no advance or width."""

    __slots__ = ("name",)

    def __init__(self, name="Regular"):
        self.name = name


class FgGlyph:
    """Mirrors the native fgGlyph: the advance is `width`, layers are fgLayer objects."""

    __slots__ = ("activeLayer", "layers", "name", "width")

    def __init__(self, name, width, layers=None):
        layers = [FgLayer()] if layers is None else layers
        self.name, self.width, self.layers = name, width, layers
        self.activeLayer = layers[0] if layers else None


def load(name):
    path = ROOT / "examples/pythonqt" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"pythonqt_example_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_examples_when_listed_then_six_exist():
    assert len(EXAMPLES) == 6, "the PythonQt example set is six scripts"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.stem)
def test_example_when_compiled_then_valid_python(path, tmp_path):
    py_compile.compile(str(path), cfile=str(tmp_path / "out.pyc"), doraise=True)


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.stem)
def test_example_when_imported_then_needs_no_fontlab_and_documents_itself(path):
    module = load(path.stem)
    doc = module.__doc__ or ""
    for heading in ("What:", "Shows:", "Run:", "Setup:"):
        assert heading in doc, f"{path.name} header lacks {heading}"
    assert callable(module.main), "each example has a main() entry point"
    assert path.read_text().startswith("# this_file: examples/pythonqt/"), "this_file record"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.stem)
def test_example_when_run_outside_fontlab_then_fails_loudly(path, monkeypatch):
    for name in [n for n in sys.modules if n.split(".")[0] in HOST_MODULES]:
        monkeypatch.delitem(sys.modules, name)  # other tests leave host doubles behind
    module = load(path.stem)
    try:
        module.main()  # no silent success without the host
    except ModuleNotFoundError as error:  # the host modules are absent
        assert error.name in HOST_MODULES, f"unrelated import failed: {error}"
    except RuntimeError as error:  # fontlabapp is installed but FontLab is not running
        assert "native API inside FontLab" in str(error), f"unrelated error: {error}"
    else:
        pytest.fail(f"{path.name} ran without FontLab")


def test_live_glyph_panel_when_summarising_then_reads_properties_and_methods():
    module = load("live_glyph_panel")
    glyph = FgGlyph("A", 512.0, [FgLayer(), FgLayer()])
    text = module.summary(glyph)
    assert "Name: A" in text and "Layers: 2" in text and "Advance width: 512" in text
    assert "No current glyph" in module.summary(None)


def test_glyph_table_when_rows_built_then_numbers_stay_numbers():
    module = load("glyph_table_model")
    font = NS(glyphs=[FgGlyph("a", 600), FgGlyph("b", 0, [])])
    assert module.rows(font) == [("a", 1, 600.0), ("b", 0, 0.0)]


def test_overlay_label_when_name_missing_then_placeholder():
    module = load("canvas_overlay_with_menu")
    assert module.label("A") == "Glyph: A"
    assert module.label(None) == "No glyph"
    assert module.SHORTCUT.startswith("Ctrl+"), "the shortcut is a portable key sequence"


def test_overlay_off_when_nothing_registered_then_noop():
    module = load("canvas_overlay_with_menu")
    module.overlay_off()
    assert module._STATE["token"] is None


def test_stopwatch_when_running_then_done_fires_once_at_threshold():
    module = load("signals_and_timer")
    watch = module.Stopwatch()
    assert watch.tick() is False, "a stopped watch does not count"
    watch.running = True
    fired = [watch.tick() for _ in range(module.DONE_AFTER_TICKS + 5)]
    assert fired.count(True) == 1 and fired[module.DONE_AFTER_TICKS - 1] is True
    assert watch.text() == "5.5 s"


class FakeSettings:
    def __init__(self, status=0):
        self.store, self._status = {}, status

    def value(self, key, default=None):
        return self.store.get(key, default)

    def setValue(self, key, value):
        self.store[key] = value

    def remove(self, key):
        self.store.pop(key, None)

    def sync(self):
        pass

    def status(self):
        return self._status


def test_settings_when_saved_and_loaded_then_round_trip_and_reset():
    module = load("saved_settings")
    settings = FakeSettings()
    values = {"sample": "Aa", "size": 72, "uppercase": True}
    module.save(settings, values)
    assert module.load(settings) == values
    module.reset(settings)
    assert module.load(settings) == module.DEFAULTS


def test_settings_when_store_returns_strings_or_junk_then_coerced_to_types():
    module = load("saved_settings")
    settings = FakeSettings()
    settings.store.update({"size": "36", "uppercase": "true", "sample": 5})
    loaded = module.load(settings)
    assert loaded["size"] == 36 and loaded["uppercase"] is True and loaded["sample"] == "5"
    settings.store["size"] = "not a number"
    assert module.load(settings)["size"] == module.DEFAULTS["size"]


def test_settings_when_status_reports_error_then_save_raises():
    module = load("saved_settings")
    with pytest.raises(OSError):
        module.save(FakeSettings(status=1), dict(module.DEFAULTS))


def test_batch_when_snapshot_processed_then_scaled_and_font_untouched():
    module = load("batch_with_progress")
    glyph = FgGlyph("a", 500)
    font = NS(glyphs=[glyph, FgGlyph("n", 0, [])])
    records = module.snapshot(font)
    assert records == [("a", 500.0), ("n", 0.0)]
    assert list(module.process(records)) == [("a", 550), ("n", 0)]
    assert glyph.width == 500, "the source objects are never modified"


def test_fake_layer_when_asked_for_advance_then_like_native_it_has_none():
    with pytest.raises(AttributeError):
        _ = FgLayer().advanceWidth


def test_overlay_state_when_module_loaded_again_then_shared_with_earlier_run():
    """FontLab runs a script as a fresh module each time; state must outlive that."""
    first = load("canvas_overlay_with_menu")
    second = load("canvas_overlay_with_menu")
    assert first._STATE is second._STATE, "a later run must see what an earlier run installed"
    closed = []
    first._STATE["menus"] = NS(close=lambda: closed.append(True))
    second.uninstall()
    assert closed == [True] and first._STATE["menus"] is None


# --- A fake Qt, enough to run build() the way the host would -------------------------------
SIGNALS = {"timeout", "clicked", "canceled", "destroyed"}


class Signal:
    def __init__(self):
        self.slots, self.error = [], None

    def connect(self, slot):
        self.slots.append(slot)

    def disconnect(self, slot):
        if self.error:
            raise self.error  # like a signal of an already deleted C++ object
        self.slots.remove(slot)

    def emit(self, *args):
        for slot in list(self.slots):
            slot(*args)


class Widget:
    """Records every method call; the names in SIGNALS are signals."""

    made: ClassVar[dict] = {}

    def __init__(self, *args):
        self.__dict__["calls"], self.__dict__["signals"] = [], {}
        Widget.made.setdefault(type(self).__name__, []).append(self)

    def __getattr__(self, name):
        if name in SIGNALS:
            return self.signals.setdefault(name, Signal())
        return lambda *args: self.calls.append((name, args))

    def called(self, name):
        return [args for method, args in self.calls if method == name]


class QTimer(Widget):
    singles: ClassVar[list] = []

    @staticmethod
    def singleShot(delay, callback):
        QTimer.singles.append(callback)


class AnyAttr:
    def __getattr__(self, name):
        return name


class Space:
    """A Qt module: QTimer is fixed, any other Q-name becomes a recording Widget class."""

    def __init__(self):
        self.classes = {"QTimer": QTimer, "Qt": AnyAttr()}

    def __getattr__(self, name):
        return self.classes.setdefault(name, type(name, (Widget,), {}))


@pytest.fixture
def host(monkeypatch):
    """A fake `fly` module with a font of 30 glyphs and a mutable current glyph."""
    import sys
    from types import ModuleType

    Widget.made, QTimer.singles = {}, []
    state = NS(font=NS(glyphs=[FgGlyph(f"g{i}", 100 + i) for i in range(30)]), glyph=FgGlyph("A", 600.0))
    fly = ModuleType("fly")
    fly.fl = NS(CurrentFont=lambda: state.font, CurrentGlyph=lambda: state.glyph)
    fly.qt = NS(QtCore=Space(), QtGui=Space())
    monkeypatch.setitem(sys.modules, "fly", fly)
    return state


def test_batch_when_built_then_dialog_stays_open_after_the_last_slice(host):
    dialog = load("batch_with_progress").build(None)
    assert dialog.called("setAutoReset") == [(False,)], "autoReset would hide the Done text"
    assert dialog.called("setAutoClose") == [(False,)], "autoClose would hide the Done text"
    timer = Widget.made["QTimer"][0]
    timer.timeout.emit()
    assert dialog.called("setValue")[-1] == (25,)
    timer.timeout.emit()
    assert dialog.called("setLabelText")[-1][0].startswith("Done: 30 widths")
    assert dialog.called("setCancelButtonText")[-1] == ("Close",)
    assert dialog.called("close") == [], "the user closes the finished dialog"


def test_batch_when_cancelled_early_then_reports_and_closes_after_the_signal(host, capsys):
    dialog = load("batch_with_progress").build(None)
    Widget.made["QTimer"][0].timeout.emit()
    dialog.canceled.emit()
    assert "Batch cancelled after 25 of 30 glyphs" in capsys.readouterr().out
    assert dialog.called("close") == [], "closing waits for the signal to return"
    assert len(QTimer.singles) == 1
    QTimer.singles[0]()
    assert dialog.called("close") == [()]


def test_batch_when_closed_after_finishing_then_message_says_closed_not_cancelled(host, capsys):
    dialog = load("batch_with_progress").build(None)
    timer = Widget.made["QTimer"][0]
    timer.timeout.emit()
    timer.timeout.emit()
    dialog.canceled.emit()
    out = capsys.readouterr().out
    assert "closed (30 of 30 glyphs done)" in out and "cancelled" not in out


def test_closing_text_when_done_or_not_then_wording_differs():
    module = load("batch_with_progress")
    assert module.closing_text(3, 5).startswith("Batch cancelled after 3 of 5")
    assert module.closing_text(5, 5).startswith("Batch dialog closed (5 of 5")


def test_batch_when_no_font_then_asks_to_open_one(host):
    host.font = None
    with pytest.raises(RuntimeError, match="Open a font"):
        load("batch_with_progress").build(None)


@pytest.mark.parametrize("error", [ValueError("deleted"), RuntimeError("deleted")])
def test_signals_teardown_when_children_already_destroyed_then_nothing_escapes(host, error):
    panel = load("signals_and_timer").build(None)
    Widget.made["QTimer"][0].timeout.error = error
    panel.destroyed.emit()  # an exception here would escape into Qt


def test_signals_teardown_when_children_alive_then_disconnects_what_it_connected(host):
    panel = load("signals_and_timer").build(None)
    timer = Widget.made["QTimer"][0]
    reset = Widget.made["QPushButton"][1]
    assert timer.timeout.slots and reset.clicked.slots, "build connected both"
    panel.destroyed.emit()
    assert timer.timeout.slots == [] and reset.clicked.slots == []
    assert timer.called("stop"), "teardown stops the timer first"


def test_signals_panel_when_start_clicked_then_timer_runs_and_done_is_scheduled(host):
    load("signals_and_timer").build(None)
    timer, (start, _reset) = Widget.made["QTimer"][0], Widget.made["QPushButton"]
    assert timer.called("start") == [], "stopped until Start is pressed"
    on_start = next(args[1] for method, args in start.calls if method == "connect")
    on_start()
    assert timer.called("start") == [()] and start.called("setText")[-1] == ("Stop",)
    for _ in range(50):
        timer.timeout.emit()
    assert len(QTimer.singles) == 1, "the done message is scheduled exactly once"


def test_live_panel_when_only_width_changes_then_label_is_redrawn(host):
    load("live_glyph_panel").build(None)
    label, timer = Widget.made["QLabel"][0], Widget.made["QTimer"][0]
    drawn = len(label.called("setText"))
    assert drawn == 1, "the first tick draws"
    timer.timeout.emit()
    assert len(label.called("setText")) == drawn, "an unchanged glyph is not redrawn"
    host.glyph.width = 640.0  # same name, new advance
    timer.timeout.emit()
    assert len(label.called("setText")) == drawn + 1
    assert "Advance width: 640.0" in label.called("setText")[-1][0]
    host.glyph = FgGlyph("A", 640.0, [FgLayer(), FgLayer()])  # same name and width, new layer count
    timer.timeout.emit()
    assert "Layers: 2" in label.called("setText")[-1][0]
    host.glyph = None
    timer.timeout.emit()
    assert "No current glyph" in label.called("setText")[-1][0]


def test_live_panel_when_reading_glyph_fails_then_label_shows_the_error(host):
    load("live_glyph_panel").build(None)
    label, timer = Widget.made["QLabel"][0], Widget.made["QTimer"][0]
    host.glyph = NS()  # has no name: summary raises
    timer.timeout.emit()
    assert "Refresh failed" in label.called("setText")[-1][0]
