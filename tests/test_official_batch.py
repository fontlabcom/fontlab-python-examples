# this_file: tests/test_official_batch.py
"""Official demos: boundary contracts, never native FontLab acceptance."""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDS = {
    "035f3fbd2b81479a",
    "3f5f77c0358d9fef",
    "a1c26dbf9f995edb",
    "63f2eeefd052f701",
    "e1a0a829f8f2e311",
    "dab5fd4c94ec518d",
    "c0d4a173b261a3e5",
    "2f94fe07de765888",
    "f48955d43ed6196c",
    "675c9f79650d7507",
    "7da7020aa7e2732b",
    "1415facde30a25cf",
    "eba98690c141a070",
    "907f39d8bf387501",
    "19571722ed96aa9c",
    "10ef4dacb4db4080",
    "eca1cd9ef1528607",
    "626fd0acec74fd91",
    "9e41e71c41b116a8",
    "505d60a757bbc177",
    "a3b3cbe51c1506c6",
    "876eab33b6a99e31",
    "e62ce3eb648cfb4c",
}


def records():
    return [
        r
        for r in json.loads((ROOT / "catalog/ports.json").read_text())["ports"]
        if r["source_id"] in IDS
    ]


def test_official_manifest_covers_exact_batch_and_retains_provenance():
    rows = records()
    assert {r["source_id"] for r in rows} == IDS, "All 23 entries require a result"
    sources = {
        r["id"]: r
        for r in json.loads((ROOT / "catalog/sources.json").read_text())["files"]
    }
    for row in rows:
        assert row["native_acceptance"] == "unexecuted"
        assert row["source"]["sha256"] == sources[row["source_id"]]["sha256"]
        assert row["license"]["original_notices"], "Retain the actual source header"
        assert row["license"]["reviewed_files"] and row["license"]["basis"]
        if row["implementation"] == "blocked":
            assert row["blocked_reason"], "A blocker needs specific absent host APIs"
            continue
        path = ROOT / row["target_path"]
        tree = ast.parse(path.read_text(), feature_version=(3, 11))
        assert any(
            isinstance(n, ast.FunctionDef) and n.name == "build" for n in tree.body
        )
        for resource in row["resources"]:
            assert (
                hashlib.sha256(
                    (ROOT / resource["target_path"]).read_bytes()
                ).hexdigest()
                == resource["source"]["sha256"]
            )
            assert not resource["target_path"].endswith("_rc.py")


from importlib import util
from types import SimpleNamespace

import pytest

from tests.official_doubles import official_host
from tests.qt_doubles import fake_host


@pytest.fixture
def official_qt(monkeypatch):
    qt, owners = fake_host(monkeypatch)
    return official_host(qt), owners


def load_record(row):
    spec = util.spec_from_file_location(
        "official_" + row["source_id"], ROOT / row["target_path"]
    )
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("row", records(), ids=lambda r: r["name"])
def test_official_build_inspect_controls_disconnect_and_close(row, official_qt):
    qt, _owners = official_qt
    handle = load_record(row).build(qt)
    assert handle.controls and "window" in handle.controls
    state = handle.snapshot()
    assert state["title"] and state["controls"], row["name"]
    assert not any(getattr(obj, "deleted", False) for obj in handle.controls.values())
    json.dumps(state)
    connections = list(handle.connections)
    original_close = handle.owner.close

    def checked_close():
        assert not handle.connections and not handle.controls, (
            "Disconnect and release before native deletion"
        )
        for obj, signature, slot in connections:
            assert slot not in obj._signals[signature].callbacks
        original_close()

    handle.owner.close = checked_close
    handle.close()
    assert handle.snapshot()["closed"]
    handle.close()


def built(name, qt):
    row = next(r for r in records() if r["name"] == "Official " + name)
    return load_record(row).build(qt)


def test_layouts_controls_and_geometry(official_qt):
    qt, _ = official_qt
    for name in ("basiclayouts", "borderlayout", "flowlayout"):
        handle = built(name, qt)
        window = handle.widget
        if name == "basiclayouts":
            assert (
                handle.controls["bigEditor"]
                .toPlainText()
                .startswith("This widget takes up all")
            )
            assert len(handle.controls["horizontalGroupBox"].layout()._items) == 4
            handle.controls["buttonBox"].emit("accepted")
        else:
            layout = window.layout()
            layout.setGeometry(qt.QtCore.QRect(0, 0, 500, 400))
            assert layout.count() == (6 if name == "borderlayout" else 5)
            assert len(handle.snapshot()["items"]) == layout.count()
            assert layout.itemAt(-1) is None, (
                "Negative indexes must not select a native item"
            )
            if name == "flowlayout":
                assert layout.heightForWidth(120) > layout.heightForWidth(600)
        handle.close()


def test_dialog_controls_change_real_state(official_qt):
    qt, _ = official_qt
    handle = built("extension", qt)
    handle.controls["moreButton"].click()
    assert handle.controls["extension"].isVisible()
    handle.controls["moreButton"].click()
    assert not handle.controls["extension"].isVisible()
    handle.close()
    handle = built("configdialog", qt)
    handle.controls["contentsWidget"].setCurrentRow(2)
    assert handle.snapshot()["current_page"] == 2
    handle.close()
    handle = built("tabdialog", qt)
    assert handle.controls["tabWidget"].count == 3
    assert len(handle.controls["applicationsListBox"]._items) == 30
    handle.controls["buttonBox"].emit("rejected")
    handle.close()


@pytest.mark.parametrize("name,count", [("classwizard", 5), ("trivialwizard", 3)])
def test_wizards_page_controls_and_defaults(name, count, official_qt):
    qt, _ = official_qt
    handle = built(name, qt)
    assert len(handle.snapshot()["page_ids"]) == count
    handle.widget.next()
    assert handle.snapshot()["current_id"] == 1
    handle.widget.back()
    assert handle.snapshot()["current_id"] == 0
    if name == "classwizard":
        handle.controls["protectCheckBox"].setChecked(False)
        assert not handle.controls["macroNameLineEdit"].enabled
        handle.controls["protectCheckBox"].setChecked(True)
        assert handle.controls["macroNameLineEdit"].enabled
    handle.close()


@pytest.mark.parametrize(
    "button,prop,value,label",
    [
        ("integerButton", "intValue", 42, "integerLabel"),
        ("doubleButton", "doubleValue", 12.5, "doubleLabel"),
        ("textButton", "textValue", "Ą–字体", "textLabel"),
        ("itemButton", "textValue", "Winter", "itemLabel"),
    ],
)
def test_standard_dialogs_accept_values_without_modal_loop(
    button, prop, value, label, official_qt
):
    qt, _ = official_qt
    handle = built("standarddialogs", qt)
    handle.controls[button].click()
    box = handle.controls["active_dialog"]
    assert box.isVisible()
    box._data[prop] = value
    box.accept()
    assert str(value).replace(".0", "") in handle.controls[label].text
    handle.close()


def test_standard_file_and_message_dialogs_are_inert_until_accept(
    official_qt, tmp_path
):
    qt, _ = official_qt
    handle = built("standarddialogs", qt)
    for button, label, mode in [
        ("directoryButton", "directoryLabel", "directory"),
        ("openFileNameButton", "openFileNameLabel", "open"),
        ("openFileNamesButton", "openFileNamesLabel", "many"),
        ("saveFileNameButton", "saveFileNameLabel", "save"),
    ]:
        handle.controls[button].click()
        box = handle.controls["active_dialog"]
        assert handle.controls[label].text == ""
        box._extra["selectedFiles"] = [str(tmp_path / "sample.txt")]
        box.accept()
        assert "sample.txt" in handle.controls[label].text
        assert not (tmp_path / "sample.txt").exists(), "Selection must not write a file"
    for button, label, choice in [
        ("criticalButton", "criticalLabel", "Retry"),
        ("informationButton", "informationLabel", "Ok"),
        ("questionButton", "questionLabel", "No"),
    ]:
        handle.controls[button].click()
        handle.controls["active_dialog"].emit(
            "buttonClicked", getattr(qt.QtGui.QMessageBox, choice)
        )
        assert handle.controls[label].text == choice
    handle.close()


@pytest.mark.parametrize("name", ["application", "sdi"])
def test_editor_file_roundtrip_errors_and_unsaved_cancel(name, official_qt, tmp_path):
    from fontlab_python_examples.official import read

    qt, _ = official_qt
    handle = built(name, qt)
    window = handle.widget
    path = tmp_path / "sample.txt"
    path.write_text("Ą–字体", encoding="utf-8")
    assert window.loadFile(str(path))
    assert handle.snapshot()["text"] == "Ą–字体"
    window.textEdit.setPlainText("Changed")
    assert window.saveFile(str(path)) and path.read_text() == "Changed"
    assert not window.loadFile(str(tmp_path / "missing"))
    assert handle.snapshot()["text"] == "Changed" and handle.snapshot()["error"]
    read(window.textEdit, "document").setModified(True)
    accepted = []
    window.maybeSave(lambda: accepted.append(True))
    handle.controls["active_dialog"].emit("buttonClicked", qt.QtGui.QMessageBox.Cancel)
    assert not accepted
    handle.controls["active_dialog"].emit("buttonClicked", qt.QtGui.QMessageBox.Discard)
    assert accepted == [True]
    handle.controls["saveAsAct"].trigger()
    box = handle.controls["active_dialog"]
    box._extra["selectedFiles"] = [str(tmp_path / "saved.txt")]
    box.accept()
    assert (tmp_path / "saved.txt").read_text() == "Changed"
    handle.close()


def test_mdi_creates_documents_and_disconnects_dynamic_menu_actions(official_qt):
    qt, _ = official_qt
    handle = built("mdi", qt)
    window = handle.widget
    handle.controls["newAct"].trigger()
    handle.controls["newAct"].trigger()
    assert len(handle.snapshot()["documents"]) == 2
    for sub in window.mdiArea.subWindowList():
        sub.show()
        document = sub.widget().document
        assert len(document._signals["contentsChanged()"].callbacks) == 1
    window.updateWindowMenu()
    previous = list(window._windowActions)
    window.updateWindowMenu()
    for action, slot in previous:
        assert action.deleted
        assert all(not s.callbacks for s in action._signals.values())
    handle.close()


def test_mdi_close_all_prompts_sequentially_and_cancel_keeps_remaining(official_qt):
    qt, _ = official_qt
    handle = built("mdi", qt)
    for _ in range(2):
        handle.controls["newAct"].trigger()
    first, second = handle.widget.mdiArea.subWindowList()
    for sub in (first, second):
        sub.show()
        sub.widget().document.setModified(True)
    handle.controls["closeAllAct"].trigger()
    prompt = handle.controls["active_dialog"]
    assert first.isVisible() and second.isVisible()
    prompt.emit("buttonClicked", qt.QtGui.QMessageBox.Discard)
    assert not first.isVisible() and second.isVisible()
    next_prompt = handle.controls["active_dialog"]
    assert next_prompt is not prompt
    next_prompt.emit("buttonClicked", qt.QtGui.QMessageBox.Cancel)
    assert second.isVisible()
    handle.close()


def test_stylesheet_loader_constructor_failure_releases_file(official_qt, monkeypatch):
    qt, _ = official_qt
    created = []
    file_class = qt.QtCore.QFile

    def file(*args):
        obj = file_class(*args)
        created.append(obj)
        return obj

    def fail():
        raise RuntimeError("loader constructor failed")

    monkeypatch.setattr(qt.QtCore, "QFile", file)
    monkeypatch.setattr(qt.QtUiTools, "QUiLoader", fail)
    with pytest.raises(RuntimeError, match="loader constructor failed"):
        built("stylesheet", qt)
    assert len(created) == 1 and created[0].deleted


def test_drawing_controls_and_explicit_painter_end(official_qt):
    qt, _ = official_qt
    handle = built("basicdrawing", qt)
    handle.controls["antialiasingCheckBox"].setChecked(True)
    handle.controls["transformationsCheckBox"].setChecked(True)
    assert handle.snapshot()["antialiased"] and handle.snapshot()["transformed"]
    combo = handle.controls["shapeComboBox"]
    combo.setCurrentIndex(0)
    combo.emit("activated", 0)
    assert handle.snapshot()["shape"] == combo.itemData(0, qt.QtCore.Qt.UserRole)
    handle.widget.renderArea.paintEvent(SimpleNamespace())
    handle.close()


def test_tooltips_shape_buttons_and_positions(official_qt):
    qt, _ = official_qt
    handle = built("tooltips", qt)
    assert len(handle.snapshot()["shapes"]) == 3
    handle.controls["newCircleButton"].click()
    assert handle.snapshot()["shapes"][-1]["tooltip"] == "Circle <2>"
    handle.controls["newSquareButton"].click()
    handle.controls["newTriangleButton"].click()
    assert len(handle.snapshot()["shapes"]) == 6
    handle.widget.paintEvent(SimpleNamespace())
    handle.close()


def test_i18n_language_windows_stay_owned(official_qt):
    qt, _ = official_qt
    handle = built("i18n", qt)
    assert len(handle.snapshot()["languages"]) == 15
    assert not any(getattr(obj, "deleted", False) for obj in handle.controls.values())
    handle.widget.showAll()
    assert handle.controls["window"] is handle.widget
    assert len(handle.snapshot()["windows"]) == 15
    assert all(w["visible"] for w in handle.snapshot()["windows"])
    for window in handle.widget.mainWindowForCheckBoxMap.values():
        assert window.centralWidget() is window._central_widget
        assert window.centralWidget().layout() is not None
    handle.widget.hideAll()
    assert not any(w["visible"] for w in handle.snapshot()["windows"])
    handle.close()


def test_movie_controls_and_timer_cleanup(official_qt):
    qt, _ = official_qt
    handle = built("movie", qt)
    handle.controls["speedSpinBox"].setValue(150)
    assert handle.controls["movie"].speed == 150
    handle.controls["fitCheckBox"].click()
    assert handle.controls["movieLabel"]._data["scaledContents"]
    handle.controls["openButton"].click()
    assert handle.controls["active_dialog"].isVisible()
    handle.close()


def test_stylesheet_apply_save_and_isolated_style(official_qt, tmp_path):
    qt, _ = official_qt
    handle = built("stylesheet", qt)
    assert "QWidget" in handle.snapshot()["sheet"]
    handle.controls["styleTextEdit"].setPlainText("QWidget { color: red; }")
    handle.controls["applyButton"].click()
    assert handle.snapshot()["applied"] == "QWidget { color: red; }"
    handle.controls["saveButton"].click()
    box = handle.controls["active_dialog"]
    box._extra["selectedFiles"] = [str(tmp_path / "sample.qss")]
    box.accept()
    assert (tmp_path / "sample.qss").read_text() == "QWidget { color: red; }"
    handle.controls["editStyleAction"].trigger()
    assert handle.snapshot()["editor_visible"]
    handle.close()


def test_regexp_refresh_captures_and_escaping(official_qt):
    qt, _ = official_qt
    handle = built("regexp", qt)
    handle.controls["patternComboBox"].setEditText(r"(A)(\d+)")
    handle.controls["textComboBox"].setEditText("xxA123yy")
    assert handle.controls["indexEdit"].text == "2"
    assert handle.controls["matchedLengthEdit"].text == "4"
    assert handle.widget.captureEdits[1].text == "A"
    assert handle.widget.captureEdits[2].text == "123"
    assert "\\\\d" in handle.controls["escapedPatternLineEdit"].text
    handle.controls["patternComboBox"].setEditText("[")
    assert handle.controls["indexEdit"].text == "-1"
    handle.close()


def test_findfiles_timer_search_results_and_cancel(official_qt, tmp_path):
    qt, _ = official_qt
    handle = built("findfiles", qt)
    (tmp_path / "match.txt").write_text("first\nneedle\n", encoding="utf-8")
    (tmp_path / "other.txt").write_text("nothing", encoding="utf-8")
    handle.controls["directoryComboBox"].setEditText(str(tmp_path))
    handle.controls["fileComboBox"].setEditText("*.txt")
    handle.controls["textComboBox"].setEditText("needle")
    handle.controls["findButton"].click()
    assert handle.snapshot()["searching"]
    for _ in range(4):
        handle.controls["searchTimer"].emit("timeout")
    assert handle.snapshot()["results"] == ["match.txt"]
    assert handle.snapshot()["row_count"] == 1
    handle.controls["findButton"].click()
    handle.controls["stopSearch"]()
    assert not handle.snapshot()["searching"]
    handle.controls["directoryComboBox"].setEditText(str(tmp_path / "missing"))
    handle.controls["findButton"].click()
    assert handle.snapshot()["error"]
    handle.close()


def test_icons_images_and_size_controls(official_qt):
    qt, _ = official_qt
    handle = built("icons", qt)
    assert handle.widget.centralWidget() is handle.controls["centralWidget"]
    assert handle.widget.centralWidget().layout() is not None
    path = (
        ROOT
        / "ports/widgets/pyqt-official/assets/505d60a757bbc177/images/find_normal.png"
    )
    handle.controls["addImagesAct"].trigger()
    box = handle.controls["active_dialog"]
    box._extra["selectedFiles"] = [str(path)]
    box.accept()
    assert handle.snapshot()["image_count"] == 1
    handle.controls["otherSpinBox"].setValue(48)
    assert handle.snapshot()["icon_size"] == 48
    handle.controls["removeAllImagesAct"].trigger()
    assert handle.snapshot()["image_count"] == 0
    handle.close()


def test_codecs_preview_accept_and_cancel(official_qt, tmp_path):
    qt, _ = official_qt
    handle = built("codecs", qt)
    path = tmp_path / "unicode.txt"
    path.write_text("Ą–字体", encoding="utf-8")
    handle.controls["openAct"].trigger()
    box = handle.controls["active_dialog"]
    box._extra["selectedFiles"] = [str(path)]
    box.accept()
    preview = handle.widget.previewForm
    assert preview.isVisible() and handle.snapshot()["text"] == ""
    preview.accept()
    assert handle.snapshot()["text"] == "Ą–字体"
    handle.widget.aboutToShowSaveAsMenu()
    handle.close()


def test_completer_corpus_and_replacement_connection(official_qt):
    qt, _ = official_qt
    handle = built("customcompleter", qt)
    assert handle.snapshot()["word_count"] > 100
    edit = handle.widget.completingTextEdit
    previous = edit.completer()
    replacement = qt.QtGui.QCompleter(handle.widget)
    edit.setCompleter(replacement)
    assert not any(s.callbacks for s in previous._signals.values())
    assert edit.completer() is replacement
    handle.close()


def test_settings_location_selection_and_owned_copy(official_qt, tmp_path):
    qt, _ = official_qt
    handle = built("settingseditor", qt)
    original = tmp_path / "settings.ini"
    original.write_text("[General]\nname=unchanged\n")
    handle.controls["openIniFileAct"].trigger()
    box = handle.controls["active_dialog"]
    box._extra["selectedFiles"] = [str(original)]
    box.accept()
    settings = handle.widget.settingsTree.settings
    assert settings._args[0] != str(original)
    owned = Path(settings._args[0])
    assert owned.read_text() == original.read_text()
    settings.setValue("name", "changed")
    assert original.read_text() == "[General]\nname=unchanged\n"
    handle.controls["autoRefreshAct"].emit("triggered", True)
    assert handle.snapshot()["auto_refresh"]
    timer = handle.widget.settingsTree.refreshTimer
    handle.close()
    assert not timer.isActive() and not owned.exists()


@pytest.mark.parametrize("name", ["extension", "application", "classwizard", "icons"])
def test_partial_build_failure_disconnects_and_closes_owned_root(
    name, official_qt, monkeypatch
):
    qt, owners = official_qt
    cls = {
        "application": qt.QtGui.QTextEdit,
        "icons": qt.QtGui.QTableWidget,
    }.get(name, qt.QtGui.QLineEdit)

    def fail(*args, **kwargs):
        raise RuntimeError("injected constructor failure")

    monkeypatch.setattr(qt.QtGui, cls._qt_name, fail)
    with pytest.raises(RuntimeError, match="injected"):
        built(name, qt)
    assert owners and all(o.closed for o in owners)


def test_missing_native_class_fails_clearly_without_fallback(official_qt):
    qt, _ = official_qt
    del qt.QtGui.QMovie
    with pytest.raises(AttributeError, match="QMovie"):
        built("movie", qt)


def test_classwizard_generates_source_only_on_finish(
    official_qt, tmp_path, monkeypatch
):
    qt, _ = official_qt
    handle = built("classwizard", qt)
    values = {
        "className": "Sample",
        "baseClass": "",
        "macroName": "SAMPLE_H",
        "baseInclude": "",
        "outputDir": str(tmp_path),
        "header": "sample.h",
        "implementation": "sample.cpp",
        "comment": True,
        "protect": True,
        "includeBase": False,
        "qobjectMacro": False,
        "qobjectCtor": False,
        "qwidgetCtor": False,
        "defaultCtor": True,
        "copyCtor": True,
    }
    monkeypatch.setattr(type(handle.widget), "field", lambda self, name: values[name])
    assert not list(tmp_path.iterdir())
    handle.widget.accept()
    assert "#ifndef SAMPLE_H" in (tmp_path / "sample.h").read_text()
    assert "class Sample" in (tmp_path / "sample.h").read_text()
    assert "Sample::Sample()" in (tmp_path / "sample.cpp").read_text()
    assert "Sample &Sample::operator=" in (tmp_path / "sample.cpp").read_text()
    values["outputDir"] = str(tmp_path / "missing")
    handle.widget.accept()
    assert handle.snapshot()["error"]
    assert handle.controls["active_dialog"].isVisible()
    handle.close()


def test_findfiles_cancel_closes_in_progress_file(official_qt, tmp_path):
    qt, _ = official_qt
    handle = built("findfiles", qt)
    (tmp_path / "large.txt").write_bytes(b"a" * 200000)
    handle.controls["directoryComboBox"].setEditText(str(tmp_path))
    handle.controls["textComboBox"].setEditText("missing")
    handle.controls["findButton"].click()
    handle.controls["searchTimer"].emit("timeout")
    stream = handle.widget.searchFile
    assert stream is not None and not stream.closed
    handle.controls["progress"].emit("canceled")
    assert stream.closed and not handle.snapshot()["searching"]
    handle.close()


def test_no_untracked_signals_or_blocking_application_calls_in_ports():
    for row in records():
        tree = ast.parse((ROOT / row["target_path"]).read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = ast.unparse(node.func)
            assert not name.endswith((".exec_", ".exec", ".quit", ".closeAllWindows"))
            assert name != "QApplication" and name != "sys.exit"
            if name.endswith(".connect"):
                assert name == "demo.connect", (
                    f"Untracked signal in {row['target_path']}"
                )
            assert not any(
                name.endswith("." + method)
                for method in (
                    "getOpenFileName",
                    "getSaveFileName",
                    "getOpenFileNames",
                    "getExistingDirectory",
                    "getInt",
                    "getDouble",
                    "getText",
                    "getFont",
                    "getColor",
                )
            )


def test_completer_exact_match_does_not_duplicate_word(official_qt, monkeypatch):
    qt, _ = official_qt
    handle = built("customcompleter", qt)
    edit = handle.widget.completingTextEdit
    inserted = []
    cursor = SimpleNamespace(
        movePosition=lambda *args: None, insertText=inserted.append
    )
    monkeypatch.setattr(type(edit), "textCursor", lambda self: cursor)
    monkeypatch.setattr(type(edit), "setTextCursor", lambda self, value: None)
    edit.completer().setCompletionPrefix("apple")
    edit.insertCompletion("apple")
    assert inserted == []
    edit.completer().setCompletionPrefix("app")
    edit.insertCompletion("apple")
    assert inserted == ["le"]
    handle.close()


def test_painter_ends_even_when_native_draw_raises(official_qt, monkeypatch):
    qt, _ = official_qt
    handle = built("tooltips", qt)
    ended = []
    invoke = qt.QtGui.QPainter._invoke

    def failing(self, key, *args, **kwargs):
        if key == "drawPath":
            raise RuntimeError("draw failed")
        if key == "end":
            ended.append(True)
        return invoke(self, key, *args, **kwargs)

    monkeypatch.setattr(qt.QtGui.QPainter, "_invoke", failing)
    with pytest.raises(RuntimeError, match="draw failed"):
        handle.widget.paintEvent(SimpleNamespace())
    assert ended == [True], "QPainter.end must run in finally"
    handle.close()


def test_settings_delegate_false_string_keeps_boolean_type(official_qt):
    qt, _ = official_qt
    handle = built("settingseditor", qt)
    delegate = handle.widget.settingsTree._data["itemDelegate"]
    editor = qt.QtGui.QLineEdit()
    editor.setText("false")
    editor.setModified(True)
    writes = []
    model = SimpleNamespace(
        data=lambda *args: True, setData=lambda *args: writes.append(args)
    )
    index = SimpleNamespace(model=lambda: model)
    delegate.setModelData(editor, model, index)
    assert writes[-1][1] is False
    handle.close()


def test_transient_icon_editor_disconnects_before_native_deletion(official_qt):
    qt, _ = official_qt
    handle = built("icons", qt)
    delegate = handle.widget.imagesTable._data["itemDelegate"]
    editor = delegate.createEditor(
        handle.widget, None, SimpleNamespace(column=lambda: 1)
    )
    assert handle.controls["comboBox"] is editor
    assert any(signal.callbacks for signal in editor._signals.values())
    delegate.destroyEditor(editor, None)
    assert editor.deleted
    assert "comboBox" not in handle.controls
    assert not any(signal.callbacks for signal in editor._signals.values())
    json.dumps(handle.snapshot())
    handle.close()
