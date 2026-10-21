# this_file: tests/test_issue122_E10.py
"""Test Tools algorithms, FontLab refusals, exports and modeless lifetimes."""

import ast
import importlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, ClassVar

import pytest

ROOT = Path(__file__).resolve().parents[1]
TITLES = ("Font Name Encoding Audit", "Localized Font Names", "Font Info Snapshot")
FIELDS = (
    "familyName",
    "styleName",
    "openTypeNamePreferredFamilyName",
    "openTypeNamePreferredSubfamilyName",
    "copyright",
    "trademark",
    "postscriptFontName",
    "postscriptFullName",
    "openTypeNameCompatibleFullName",
    "styleMapFamilyName",
    "styleMapStyleName",
    "openTypeNameDesigner",
    "openTypeNameManufacturer",
    "openTypeNameVersion",
)


def fixture_names(
    family: str = "Family", preferred: str = "Preferred", style: str = "Regular"
) -> dict[str, str]:
    """Supply every declared field, including absent optional text."""
    return dict.fromkeys(FIELDS, "") | {
        "familyName": family,
        "styleName": style,
        "openTypeNamePreferredFamilyName": preferred,
        "openTypeNamePreferredSubfamilyName": "Roman",
    }


def load(title: str) -> dict[str, Any]:
    return runpy.run_path(str(ROOT / "Scripts" / "Tools" / f"{title}.py"))


@pytest.fixture
def app(monkeypatch: Any) -> None:
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp" / "src"))
    import fontlabapp

    fly = ModuleType("fly")
    fly.ap = fontlabapp
    monkeypatch.setitem(sys.modules, "fly", fly)
    monkeypatch.setitem(sys.modules, "fly.ap", fontlabapp)


def test_real_app_imports(app: None) -> None:
    for name, symbol in (("draft_signals", "Scope"), ("qt_properties", "value")):
        assert callable(getattr(importlib.import_module("fontlabapp." + name), symbol))


@pytest.mark.parametrize("title", TITLES)
def test_capture_refuses_missing_switched_and_changed_font(title: str) -> None:
    capture = load(title)["capture_info"]
    values = {
        key: value
        for key, value in fixture_names("Café").items()
        if key in load(title)["FIELDS"]
    }
    package = SimpleNamespace(
        id=7, isNull=False, master="Regular", info=SimpleNamespace(**values)
    )
    workspace = SimpleNamespace(currentPackage=package)
    native = SimpleNamespace(flWorkspace=SimpleNamespace(instance=lambda: workspace))
    assert capture(native) == ("Regular", values)
    for absent in (None, SimpleNamespace(isNull=True)):
        workspace.currentPackage = absent
        with pytest.raises(ValueError, match="Open a font"):
            capture(native)
    workspace.currentPackage = package

    class Changing(SimpleNamespace):
        def __getattribute__(self, key: str) -> Any:
            if key == "familyName":
                self.count += 1
                return str(self.count)
            return super().__getattribute__(key)

    package.info = Changing(**values, count=0)
    with pytest.raises(ValueError, match="changed"):
        capture(native)
    package.info = SimpleNamespace(**values)

    class Switching(SimpleNamespace):
        def __getattribute__(self, key: str) -> Any:
            if key == "familyName":
                workspace.currentPackage = SimpleNamespace(id=8, isNull=False)
            return super().__getattribute__(key)

    package.info = Switching(**values)
    with pytest.raises(ValueError, match="changed"):
        capture(native)


@pytest.mark.parametrize("title", TITLES)
def test_capture_reads_current_master_without_switching(title: str) -> None:
    module = load(title)

    class Package:
        id = 7
        isNull = False
        master = "Light"

        @property
        def info(self) -> Any:
            values = fixture_names(
                style={"Light": "Light", "Bold": "Négrita"}[self.master]
            )
            return SimpleNamespace(**{key: values[key] for key in module["FIELDS"]})

        def setMaster(self, *args: Any) -> None:
            pytest.fail("Capture must never switch masters")

    package = Package()
    native = SimpleNamespace(
        flWorkspace=SimpleNamespace(
            instance=lambda: SimpleNamespace(currentPackage=package)
        )
    )
    first = module["capture_info"](native)
    package.master = "Bold"
    second = module["capture_info"](native)
    assert first[0] == "Light" and first[1]["styleName"] == "Light"
    assert second[0] == "Bold" and second[1]["styleName"] == "Négrita"
    if title == TITLES[2]:
        with pytest.raises(ValueError, match="masters"):
            module["compare_info"](first, second)


def test_encoding_report_has_strict_bytes_and_failure_positions() -> None:
    report = json.loads(
        load(TITLES[0])["encoding_report"](("Regular", {"familyName": "CaféΩ"}))
    )
    rows = {row["encoding"]: row for row in report["records"]}
    assert rows["utf-16-be"]["hex"] == "00430061006600e903a9"
    assert rows["cp1252"]["unencodable"] == [{"index": 4, "codepoint": "U+03A9"}]
    assert rows["ascii"]["unencodable"] == [
        {"index": 3, "codepoint": "U+00E9"},
        {"index": 4, "codepoint": "U+03A9"},
    ]
    assert "utf-8" not in rows
    assert all("roundtrip" not in row for row in rows.values())
    assert report["master"] == "Regular"
    assert rows["mac_roman"]["unencodable"] == []
    assert rows["mac_roman"]["hex"] == "4361668ebd"


def test_localized_name_feature_escaping_and_language_bounds() -> None:
    build = load(TITLES[1])["name_feature"]
    assert build('A"\\😀', "Regular", "0x415", "Regular") == (
        '# Current master: "Regular"\n'
        'table name {\n  nameid 16 3 1 0x0415 "A\\0022\\005c\\d83d\\de00";\n'
        '  nameid 17 3 1 0x0415 "Regular";\n} name;\n'
    )
    for family, style, lang in (
        ("", "R", "0x409"),
        ("A", "", "0x409"),
        ("A", "R", "-1"),
        ("A", "R", "65536"),
        ("A\nB", "R", "0x409"),
    ):
        with pytest.raises(ValueError):
            build(family, style, lang, "Regular")


def test_snapshot_roundtrip_diff_and_schema_refusals(tmp_path: Path) -> None:
    module = load(TITLES[2])
    original = ("Regular", fixture_names("A"))
    encoded = module["snapshot_json"](original)
    source = tmp_path / "info.json"
    source.write_text("\ufeff" + encoded, encoding="utf-8")
    assert module["read_snapshot"](str(source)) == (original, ("UTF-8 BOM removed",))
    changed = (original[0], original[1] | {"familyName": "B"})
    assert json.loads(module["compare_info"](original, changed)) == {
        "master": "Regular",
        "changes": {"familyName": {"saved": "A", "current": "B"}},
    }
    assert json.loads(module["compare_info"](original, original)) == {
        "master": "Regular",
        "changes": {},
    }
    for bad in (
        "[]",
        '{"schema":1,"names":{}}',
        encoded.replace('"familyName": "A"', '"familyName": null'),
        encoded.replace('"schema": 2', '"schema": 2, "schema": 2'),
    ):
        source.write_text(bad)
        with pytest.raises(ValueError):
            module["read_snapshot"](str(source))


@pytest.mark.parametrize("title", TITLES)
def test_exports_refuse_lossy_text_relative_paths_and_overwrites(
    title: str, tmp_path: Path
) -> None:
    module = load(title)
    target = tmp_path / "out.txt"
    for bad in ("\0", "\u00a0", "\u2028", "\u2029", "\ud800", "\r"):
        with pytest.raises(ValueError):
            module["checked"](bad)
    with pytest.raises(ValueError):
        module["export_new"]("relative.txt", "x")
    module["export_new"](str(target), "Ω\n")
    assert target.read_bytes() == "Ω\n".encode()
    with pytest.raises(FileExistsError):
        module["export_new"](str(target), "x")


class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in self.slots[:]:
            slot(*args)


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
        "windowTitle",
        "setFont",
        "pos",
        "children",
        "hide",
        "raise_",
    }

    def __init_subclass__(cls, **kwargs: Any) -> None:
        assert not Widget.native.intersection(cls.__dict__), "Native member collision"

    def __setattr__(self, name: str, value: Any) -> None:
        assert name not in self.native, f"Native member collision: {name}"
        object.__setattr__(self, name, value)

    def __init__(self, *args: Any) -> None:
        self.text = args[0] if args and isinstance(args[0], str) else ""
        self.clicked, self.textChanged, self.destroyed = Signal(), Signal(), Signal()
        self.deleted = False

    def setWindowTitle(self, text: str) -> None:
        pass

    def setAttribute(self, *args: Any) -> None:
        pass

    def resize(self, *args: Any) -> None:
        pass

    def addWidget(self, widget: Any) -> None:
        pass

    def setContentsMargins(self, *args: Any) -> None:
        pass

    def setSpacing(self, value: int) -> None:
        pass

    def setReadOnly(self, value: bool) -> None:
        pass

    def setPlaceholderText(self, text: str) -> None:
        pass

    def setPlainText(self, text: str) -> None:
        self.text = text

    def toPlainText(self) -> str:
        return self.text

    def setText(self, text: str) -> None:
        self.text = text
        self.textChanged.emit(text)

    def show(self) -> None:
        pass

    def close(self) -> None:
        self.closeEvent(SimpleNamespace(accept=lambda: None, ignore=lambda: None))

    def deleteLater(self) -> None:
        self.deleted = True


@pytest.mark.parametrize("title", TITLES)
def test_panel_export_error_and_signal_cleanup(
    title: str, app: None, tmp_path: Path
) -> None:
    module = load(title)
    info = ("Regular", fixture_names("Café"))
    module["show"].__globals__["capture_info"] = lambda: (info[0], info[1].copy())
    gui = SimpleNamespace(
        **{
            name: Widget
            for name in (
                "QWidget",
                "QLabel",
                "QVBoxLayout",
                "QLineEdit",
                "QPlainTextEdit",
                "QPushButton",
            )
        }
    )
    qt = SimpleNamespace(
        QtGui=gui,
        QtCore=SimpleNamespace(
            Qt=SimpleNamespace(
                WindowFlags=lambda value: value, Tool=1, WA_QuitOnClose=2
            )
        ),
    )
    panel = module["show"](qt, None)
    if title == TITLES[1]:
        panel.language_field.setText("0x040c")
    panel.destination.setText(str(tmp_path / "output.txt"))
    panel.save_output()
    assert (tmp_path / "output.txt").exists(), "UI must produce durable workflow output"
    panel.save_output()
    assert "exist" in panel.status_line.text.lower()
    assert panel.scope.records
    panel.scope.records[0][0].emit()
    event = SimpleNamespace(accept=lambda: None, ignore=lambda: None)
    panel.closeEvent(event)
    assert panel.deleted and not panel.scope.records
    assert not module["_PANELS"]


@pytest.mark.parametrize("title", TITLES)
def test_python311_source_has_no_font_writer_or_process_boilerplate(title: str) -> None:
    text = (ROOT / "Scripts" / "Tools" / f"{title}.py").read_text()
    ast.parse(text, feature_version=(3, 11))
    for term in (
        "notifyChangesApplied",
        "history.commit",
        "issue 122",
        "native acceptance",
        "archived",
        "QApplication(",
        "setMaster",
        "CurrentFont(",
    ):
        assert term not in text


def make_panel(title: str) -> tuple[dict[str, Any], Any]:
    """Create explicit widgets around a captured font fixture."""
    module = load(title)
    module["show"].__globals__["capture_info"] = lambda: ("Regular", fixture_names())
    gui = SimpleNamespace(
        **{
            name: Widget
            for name in (
                "QWidget",
                "QLabel",
                "QVBoxLayout",
                "QLineEdit",
                "QPlainTextEdit",
                "QPushButton",
            )
        }
    )
    qt = SimpleNamespace(
        QtGui=gui,
        QtCore=SimpleNamespace(
            Qt=SimpleNamespace(
                WindowFlags=lambda value: value, Tool=1, WA_QuitOnClose=2
            )
        ),
    )
    return module, module["show"](qt, None)


def test_translation_refresh_close_and_export_preserve_draft(
    app: None, tmp_path: Path
) -> None:
    module, panel = make_panel(TITLES[1])
    assert panel.family_field.text == "Preferred"
    panel.family_field.setText("Famille")
    panel.refresh_info()
    assert panel.info is not None and panel.family_field.text == "Famille"
    events: list[str] = []
    event = SimpleNamespace(
        accept=lambda: events.append("accept"), ignore=lambda: events.append("ignore")
    )
    panel.closeEvent(event)
    assert events == ["ignore"] and not panel.deleted
    panel.language_field.setText("bad")
    panel.destination.setText(str(tmp_path / "names.fea"))
    panel.save_output()
    assert not (tmp_path / "names.fea").exists() and panel.unsaved
    panel.language_field.setText("0x40c")
    panel.save_output()
    assert '0x040c "Famille"' in (tmp_path / "names.fea").read_text()
    assert not panel.unsaved
    panel.closeEvent(event)
    assert events[-1] == "accept" and not module["_PANELS"]


@pytest.mark.parametrize("title", TITLES)
def test_failed_refresh_blocks_export_and_close_cleanup_can_retry(
    title: str, app: None, tmp_path: Path
) -> None:
    module, panel = make_panel(title)

    def expired() -> Any:
        raise TimeoutError("capture expired")

    module["show"].__globals__["capture_info"] = expired
    panel.refresh_info()
    assert panel.preview.text == "" and panel.info is None
    assert "expired" in panel.status_line.text
    panel.destination.setText(str(tmp_path / "never.txt"))
    panel.save_output()
    assert not (tmp_path / "never.txt").exists()
    signal = panel.scope.records[0][0]
    original = signal.disconnect

    def fail(slot: Any) -> None:
        raise RuntimeError("disconnect failed")

    signal.disconnect = fail
    events: list[str] = []
    event = SimpleNamespace(
        accept=lambda: events.append("accept"), ignore=lambda: events.append("ignore")
    )
    panel.closeEvent(event)
    assert events == ["ignore"] and not panel.deleted
    assert panel.scope.records
    signal.disconnect = original
    panel.closeEvent(event)
    assert events[-1] == "accept" and panel.deleted


def test_snapshot_compare_panel_refreshes_and_contains_bad_files(
    app: None, tmp_path: Path
) -> None:
    module, panel = make_panel(TITLES[2])
    source = tmp_path / "snapshot.json"
    source.write_text(module["snapshot_json"](("Regular", fixture_names("Old"))))
    panel.reference_field.setText(str(source))
    panel.compare_saved()
    assert json.loads(panel.preview.text) == {
        "master": "Regular",
        "changes": {"familyName": {"saved": "Old", "current": "Family"}},
    }
    source.write_text("not JSON")
    panel.compare_saved()
    assert panel.preview.text == "" and "Expecting" in panel.status_line.text
    panel.closeEvent(SimpleNamespace(accept=lambda: None, ignore=lambda: None))


@pytest.mark.parametrize("title", TITLES)
def test_entry_uses_existing_host_application(title: str, monkeypatch: Any) -> None:
    calls: list[Any] = []
    module = load(title)
    module["main"].__globals__["show"] = lambda qt, parent: calls.append((qt, parent))
    fly = ModuleType("fly")
    fly.qt = object()
    fly.fl = SimpleNamespace(MainWindow=lambda: "host")
    monkeypatch.setitem(sys.modules, "fly", fly)
    module["main"]()
    assert calls == [(fly.qt, "host")]


def test_regexp_duplicate_target_and_all_seven_source_identities() -> None:
    """Bind the duplicate to its existing entry and every source to its bytes."""
    import hashlib
    import os

    target = ROOT / "Scripts/Tools/Glyph Name Pattern Lab.py"
    assert "glyph_pattern" in target.read_text()
    index = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    rows = [
        r
        for r in index
        if "/tools/" in r["target"]
        and any(
            "/" + family + "-" in r["target"]
            for family in ("codecs", "i18n", "settingseditor", "regexp")
        )
        and not ("/part2/" in r["target"] and "/regexp-" in r["target"])
    ]
    assert len(rows) == 7 and target.is_file()
    preserved = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
    for row in rows:
        assert (
            hashlib.sha256((preserved / row["target"]).read_bytes()).hexdigest()
            == row["target_sha256"]
        )


def test_encoding_credits_exact_legacy_bytes_and_required_postscript_ascii() -> None:
    module = load(TITLES[0])
    assert set(module["FIELDS"]) == set(FIELDS), (
        "Audit all declared name and credit fields"
    )
    captured = (
        "Bold",
        fixture_names() | {"copyright": "©", "postscriptFontName": "Café"},
    )
    report = json.loads(module["encoding_report"](captured))
    records = {(row["field"], row["encoding"]): row for row in report["records"]}
    for codec in ("cp1252", "mac_roman"):
        assert records["copyright", codec]["hex"] == "a9"
    assert records["copyright", "utf-16-be"]["hex"] == "00a9"
    failure = records["postscriptFontName", "ascii"]
    assert failure["ascii_required"] and not failure["ascii_valid"]
    assert failure["hex"] is None
    assert failure["unencodable"] == [{"index": 3, "codepoint": "U+00E9"}]
    assert report["scope"] == "Current master: Bold"
    assert records["copyright", "utf-16-be"]["purpose"] == "byte dump"


def test_snapshot_detects_only_actual_input_conversions(tmp_path: Path) -> None:
    module = load(TITLES[2])
    captured = (
        "Light",
        fixture_names()
        | {"openTypeNameVersion": "Version 1.002", "copyright": "© 2026"},
    )
    encoded = module["snapshot_json"](captured)
    data = json.loads(encoded)
    assert data["schema"] == 2 and data["master"] == "Light"
    assert set(data["names"]) == set(FIELDS)
    source = tmp_path / "snapshot.json"
    source.write_bytes(encoded.encode("utf-8"))
    assert module["read_snapshot"](str(source)) == (captured, ())
    source.write_bytes(b"\xef\xbb\xbf" + encoded.replace("\n", "\r\n").encode("utf-8"))
    assert module["read_snapshot"](str(source)) == (
        captured,
        ("UTF-8 BOM removed", "CR line endings normalized"),
    )
    changed = ("Light", captured[1] | {"openTypeNameVersion": "Version 1.003"})
    assert json.loads(module["compare_info"](captured, changed))["changes"] == {
        "openTypeNameVersion": {"saved": "Version 1.002", "current": "Version 1.003"}
    }


def test_snapshot_panel_reports_conversions_and_refuses_other_master(
    app: None, tmp_path: Path
) -> None:
    module, panel = make_panel(TITLES[2])
    source = tmp_path / "snapshot.json"
    encoded = module["snapshot_json"](("Regular", fixture_names()))
    source.write_bytes(encoded.encode("utf-8"))
    panel.reference_field.setText(str(source))
    panel.compare_saved()
    assert (
        "normalized" not in panel.status_line.text
        and "BOM" not in panel.status_line.text
    )
    assert panel.master_line.text == "Current master: Regular"
    source.write_bytes(b"\xef\xbb\xbf" + encoded.replace("\n", "\r\n").encode("utf-8"))
    panel.compare_saved()
    assert "UTF-8 BOM removed" in panel.status_line.text
    assert "CR line endings normalized" in panel.status_line.text
    source.write_text(module["snapshot_json"](("Bold", fixture_names(style="Négrita"))))
    panel.compare_saved()
    assert "across masters" in panel.status_line.text and panel.preview.text == ""
    panel.close()


def test_localized_initial_build_failure_can_be_corrected_and_discarded(
    app: None, tmp_path: Path
) -> None:
    module = load(TITLES[1])
    info = (
        "Empty",
        fixture_names("", "")
        | {"styleName": "", "openTypeNamePreferredSubfamilyName": ""},
    )
    module["show"].__globals__["capture_info"] = lambda: info
    gui = SimpleNamespace(
        **{
            name: Widget
            for name in (
                "QWidget",
                "QLabel",
                "QVBoxLayout",
                "QLineEdit",
                "QPlainTextEdit",
                "QPushButton",
            )
        }
    )
    qt = SimpleNamespace(
        QtGui=gui,
        QtCore=SimpleNamespace(
            Qt=SimpleNamespace(
                WindowFlags=lambda value: value, Tool=1, WA_QuitOnClose=2
            )
        ),
    )
    panel = module["show"](qt, None)
    assert panel.info == info, "A preview error must retain a valid font capture"
    assert panel.language_field.text == "", "Require an explicit target language"
    assert panel.master_line.text == "Current master: Empty"
    panel.family_field.setText("Famille")
    panel.style_field.setText("Gras")
    panel.language_field.setText("0x040c")
    panel.destination.setText(str(tmp_path / "localized.fea"))
    panel.save_output()
    output = (tmp_path / "localized.fea").read_text()
    assert output.startswith('# Current master: "Empty"\n')
    assert '0x040c "Famille"' in output and not panel.unsaved
    panel.family_field.setText("Discard me")
    assert panel.unsaved
    panel.discard_close()
    assert panel.deleted and not panel.scope.records and not module["_PANELS"]


@pytest.mark.parametrize("title", TITLES)
def test_master_change_during_capture_is_refused(title: str) -> None:
    module = load(title)
    package = SimpleNamespace(id=7, isNull=False, master="Light")

    class MasterSwitching(SimpleNamespace):
        def __getattribute__(self, name: str) -> Any:
            if name == "familyName":
                package.master = "Bold"
            return super().__getattribute__(name)

    package.info = MasterSwitching(
        **{key: fixture_names()[key] for key in module["FIELDS"]}
    )
    native = SimpleNamespace(
        flWorkspace=SimpleNamespace(
            instance=lambda: SimpleNamespace(currentPackage=package)
        )
    )
    with pytest.raises(ValueError, match="master changed"):
        module["capture_info"](native)
