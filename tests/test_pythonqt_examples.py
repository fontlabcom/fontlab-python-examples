# this_file: tests/test_pythonqt_examples.py
# SPDX-License-Identifier: Apache-2.0
"""Offline checks of the PythonQt examples: they compile, import without FontLab,
state what they show and how to run them, and their pure logic works.

Native behaviour (widgets, painters, menus) is not proven here; see the
examples README for the checks to run inside FontLab.
"""

import importlib.util
import py_compile
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted((ROOT / "examples/pythonqt").glob("*.py"))


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
def test_example_when_run_outside_fontlab_then_fails_loudly(path):
    module = load(path.stem)
    with pytest.raises((ImportError, RuntimeError)):  # RuntimeError when App is installed but FontLab is absent
        module.main()  # no silent success without the host


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
        getattr(FgLayer(), "advanceWidth")


def test_overlay_state_when_module_loaded_again_then_shared_with_earlier_run():
    """FontLab runs a script as a fresh module each time; state must outlive that."""
    first = load("canvas_overlay_with_menu")
    second = load("canvas_overlay_with_menu")
    assert first._STATE is second._STATE, "a later run must see what an earlier run installed"
    closed = []
    first._STATE["menus"] = NS(close=lambda: closed.append(True))
    second.uninstall()
    assert closed == [True] and first._STATE["menus"] is None
