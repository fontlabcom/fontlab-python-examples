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


BATCH_FOUR_IDS = {
    "da76600eaea7a121",
    "090c76a87351e771",
    "94ab271d023d1ca3",
    "306c12d5cc1db46c",
    "227efef76ed4ac74",
    "e1f313d96e43adff",
    "878fe9f714df3b5e",
    "f4d9e2927469223c",
    "bb1c114d38fb756a",
    "c98ae8ac71886586",
    "b823a76f79197d84",
    "321f8e535facafde",
    "4d19e62d93dd761c",
    "2719ebb336f3a29e",
    "55bcde890cd77ed7",
    "c5b4e385cc921da4",
    "700e96dec485e7a8",
    "5781fa4ba55c884f",
}
BATCH_FIVE_IDS = {
    "b7283d74afb78218",
    "243ae486f9528e8c",
    "de30d23621025fe6",
    "de35a965dfcfd678",
    "2cd6ffc2b2ed65bb",
    "c1b878b63f80e733",
    "0578c17977b471f1",
    "0788354954c8e613",
    "fcfaf9667206bbd6",
    "b95b687bbc541207",
    "65d15d1fbc1b15e9",
    "29f6a7d0a3bb6813",
    "27709a02d37b9ba9",
    "bd6c8feb783ba845",
    "1cf57c0f2ac8880a",
    "1ca857d797199ecf",
}
IDS |= BATCH_FOUR_IDS | BATCH_FIVE_IDS


def records():
    return [
        r
        for r in json.loads((ROOT / "catalog/ports.json").read_text())["ports"]
        if r["source_id"] in IDS
    ]


def test_official_manifest_covers_exact_batch_and_retains_provenance():
    rows = records()
    assert {r["source_id"] for r in rows} == IDS, "All 57 entries require a result"
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


@pytest.mark.parametrize(
    "row",
    [r for r in records() if r["implementation"] == "implemented"],
    ids=lambda r: r["name"],
)
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


@pytest.mark.parametrize("part", range(1, 8))
def test_addressbook_stage_controls_and_contacts(part, official_qt):
    qt, _ = official_qt
    handle = built(f"addressbook part{part}", qt)
    c = handle.controls
    if part == 1:
        c["nameLine"].setText("Zoë")
        c["addressText"].setPlainText("<A>\nŁódź")
        assert handle.snapshot()["name"] == "Zoë"
        assert handle.snapshot()["address"] == "<A>\nŁódź"
        assert "addButton" not in c
        handle.close()
        return
    c["addButton"].click()
    c["submitButton"].click()
    assert handle.snapshot()["contact_count"] == 0
    assert c["active_dialog"].windowTitle == "Empty Field"
    c["active_dialog"].accept()
    for name in ("Zoë", "Ada", "Łukasz"):
        if name != "Zoë":
            c["addButton"].click()
        c["nameLine"].setText(name)
        c["addressText"].setPlainText("<literal>\n" + name)
        c["submitButton"].click()
        c["active_dialog"].accept()
    assert handle.snapshot()["contacts"] == {
        name: "<literal>\n" + name for name in ("Zoë", "Ada", "Łukasz")
    }
    c["addButton"].click()
    c["nameLine"].setText("Ada")
    c["addressText"].setPlainText("duplicate")
    c["submitButton"].click()
    assert handle.snapshot()["contacts"]["Ada"] == "<literal>\nAda"
    c["active_dialog"].accept()
    c["cancelButton"].click()
    assert handle.snapshot()["name"] == "Łukasz"
    if part >= 3:
        c["nextButton"].click()
        assert handle.snapshot()["name"] == "Ada", "Sorted navigation wraps"
        c["previousButton"].click()
        assert handle.snapshot()["name"] == "Łukasz"
    if part >= 4:
        c["editButton"].click()
        c["nameLine"].setText("Ada")
        c["submitButton"].click()
        assert handle.snapshot()["contact_count"] == 3
        c["active_dialog"].accept()
        c["nameLine"].setText("Renamed")
        c["addressText"].setPlainText("New address")
        c["submitButton"].click()
        c["active_dialog"].accept()
        assert handle.snapshot()["contacts"]["Renamed"] == "New address"
        c["removeButton"].click()
        c["active_dialog"].emit("buttonClicked", qt.QtGui.QMessageBox.No)
        assert handle.snapshot()["contact_count"] == 3
        c["removeButton"].click()
        c["active_dialog"].emit("buttonClicked", qt.QtGui.QMessageBox.Yes)
        assert "Renamed" not in handle.snapshot()["contacts"]
    handle.close()


@pytest.mark.parametrize("part", [5, 6, 7])
def test_addressbook_find_is_async_reusable_and_rejects_empty(part, official_qt):
    qt, _ = official_qt
    handle = built(f"addressbook part{part}", qt)
    c, window = handle.controls, handle.widget
    window.contacts.update(Ada="London", Zoë="Łódź", Charles="Paris")
    window.updateInterface(window.NavigationMode)
    c["findButton"].click()
    assert c["findDialog"].isVisible()
    c["findSubmit"].click()
    assert c["findDialog"].isVisible(), "Empty search must not accept stale text"
    c["active_dialog"].accept()
    c["findLine"].setText("Zoë")
    c["findSubmit"].click()
    assert handle.snapshot()["name"] == "Zoë"
    assert handle.snapshot()["address"] == "Łódź"
    for name in ("missing", "Ada"):
        c["findButton"].click()
        c["findLine"].setText(name)
        c["findSubmit"].click()
    assert handle.snapshot()["name"] == "Ada"
    accepted = [
        link
        for link in handle.connections
        if link[0] is c["findDialog"] and link[1] == "accepted()"
    ]
    assert len(accepted) == 1, "Reopening must not duplicate acceptance callbacks"
    c["findButton"].click()
    c["findDialog"].reject()
    assert handle.snapshot()["name"] == "Ada"
    handle.close()


@pytest.mark.parametrize("part", [6, 7])
def test_addressbook_owned_pickle_roundtrip_corruption_and_path_boundary(
    part, official_qt, tmp_path
):
    import pickle

    qt, _ = official_qt
    handle = built(f"addressbook part{part}", qt)
    c, window = handle.controls, handle.widget
    directory = Path(handle.snapshot()["directory"])
    assert directory.is_dir()
    window.contacts.update({"Zoë": "<literal>\nŁódź"})
    window.updateInterface(window.NavigationMode)
    output = directory / "contacts.abk"
    c["saveButton"].click()
    assert not output.exists(), "Choosing a file or inspecting must not save"
    c["active_dialog"]._extra["selectedFiles"] = [str(output)]
    c["active_dialog"].accept()
    assert pickle.loads(output.read_bytes()) == dict(window.contacts)
    window.contacts.clear()
    c["loadButton"].click()
    c["active_dialog"]._extra["selectedFiles"] = [str(output)]
    c["active_dialog"].accept()
    assert handle.snapshot()["contacts"] == {"Zoë": "<literal>\nŁódź"}
    before = dict(window.contacts)
    for content in (b"broken", b"", pickle.dumps([1]), b"cos\nsystem\n."):
        output.write_bytes(content)
        c["loadContacts"](str(output))
        assert handle.snapshot()["error"]
        assert dict(window.contacts) == before
    external = tmp_path / "untouched.abk"
    external.write_bytes(b"untouched")
    c["saveContacts"](str(external))
    c["loadContacts"](str(external))
    assert external.read_bytes() == b"untouched"
    alias = directory / "escape.abk"
    alias.symlink_to(external)
    c["saveContacts"](str(alias))
    assert external.read_bytes() == b"untouched"
    output.write_bytes(pickle.dumps({}))
    c["loadContacts"](str(output))
    assert handle.snapshot()["contact_count"] == 0
    handle.close()
    assert not directory.exists(), "Named close removes only the owned sandbox"


def test_addressbook_vcard_export_preserves_unicode_and_escapes_address(official_qt):
    qt, _ = official_qt
    handle = built("addressbook part7", qt)
    handle.controls["nameLine"].setText("Zoë Example")
    handle.controls["addressText"].setPlainText("A;B\nŁódź, Poland")
    path = Path(handle.snapshot()["directory"]) / "contact.vcf"
    handle.controls["exportContact"](str(path))
    assert path.read_text() == (
        "BEGIN:VCARD\nVERSION:2.1\nN:Example;Zoë\nFN:Zoë Example\n"
        "ADR;HOME:;A\\;B;Łódź  Poland\nEND:VCARD\n"
    )
    handle.close()


@pytest.mark.parametrize("name", ["simpletreemodel", "editabletreemodel"])
def test_tree_models_have_real_hierarchy_and_numeric_index_identity(name, official_qt):
    qt, _ = official_qt
    handle = built(name, qt)
    model = handle.controls["model"]
    root = model.index(0, 0)
    assert root.isValid() and isinstance(root.internalId(), int)
    assert model.data(root), "Original resource text must populate the model"
    assert not model.parent(root).isValid()
    assert model.rowCount(model.index(0, 1)) == 0
    assert not model.index(-1, 0).isValid()
    assert not model.index(99999, 0).isValid()
    assert not model.index(0, 999).isValid()
    assert model.data(qt.QtCore.QModelIndex()) is None
    child = model.index(0, 0, root)
    if child.isValid():
        assert model.parent(child).internalId() == root.internalId()
    assert handle.snapshot()["tree"]["children"]
    handle.close()


def test_editable_tree_actions_edits_and_invalid_mutations(official_qt):
    qt, _ = official_qt
    handle = built("editabletreemodel", qt)
    c, model = handle.controls, handle.controls["model"]
    before = model.rowCount()
    c["insertChildAction"].trigger()
    assert model.rowCount() == before + 1
    selected = c["view"].selectionModel()._invoke("currentIndex")
    assert model.setData(selected, "New title")
    assert model.data(selected) == "New title"
    for name in ("insertRows", "removeRows", "insertColumns", "removeColumns"):
        for start, count in ((-1, 1), (0, -1), (0, 0), (1000000, 1)):
            assert not getattr(model, name)(start, count), (name, start, count)
    assert not model.setData(qt.QtCore.QModelIndex(), "invalid")
    columns = model.columnCount()
    c["insertColumnAction"].trigger()
    assert model.columnCount() == columns + 1
    c["removeColumnAction"].trigger()
    assert model.columnCount() == columns
    c["removeRowAction"].trigger()
    assert model.rowCount() == before
    handle.close()


def test_interview_views_share_selection_and_lazy_hierarchy(official_qt):
    qt, _ = official_qt
    handle = built("interview", qt)
    c, model = handle.controls, handle.controls["model"]
    assert handle.snapshot()["row_count"] == 1000
    assert handle.snapshot()["column_count"] == 10
    assert handle.snapshot()["shared_selection"]
    parent = model.index(4, 0)
    child = model.index(3, 2, parent)
    assert model.parent(child).internalId() == parent.internalId()
    assert model.data(child) == "Item 3:2"
    c["selection"].select(parent, qt.QtGui.QItemSelectionModel.ClearAndSelect)
    assert handle.snapshot()["selected"] == [[4, 0]]
    assert not model.index(-1, 0).isValid()
    assert not model.index(1000, 0).isValid()
    handle.close()


def test_frozen_column_scroll_resize_and_geometry(official_qt):
    qt, _ = official_qt
    handle = built("frozencolumn", qt)
    c, window = handle.controls, handle.widget
    assert handle.snapshot()["rows"] and handle.snapshot()["column_count"] > 1
    window.horizontalHeader().emit("sectionResized", 0, 100, 173)
    assert handle.snapshot()["frozen_width"] == 173
    window.verticalHeader().emit("sectionResized", 2, 20, 37)
    assert c["frozenTableView"].rowHeight(2) == 37
    c["verticalScrollBar"].setValue(50)
    assert handle.snapshot()["scroll"] == [50, 50]
    c["frozenTableView"].verticalScrollBar().setValue(23)
    assert handle.snapshot()["scroll"] == [23, 23]
    window.resizeEvent(SimpleNamespace())
    assert len(handle.snapshot()["frozen_geometry"]) == 4
    handle.close()


def test_lighting_animates_numeric_offsets_and_stops_before_close(official_qt):
    qt, _ = official_qt
    handle = built("lighting", qt)
    before = handle.snapshot()
    assert before["item_count"] == 25 and before["timer_active"]
    handle.controls["timer"].emit("timeout")
    after = handle.snapshot()
    assert after["angle"] > before["angle"] and after["light"] != before["light"]
    assert after["offsets"] != before["offsets"]
    timer = handle.controls["timer"]
    handle.close()
    assert not timer.isActive() and not handle.connections


def drop_event(qt, mime, x, y, source=None):
    result = {"accepted": False, "ignored": False, "action": None}
    event = SimpleNamespace(
        mimeData=lambda: mime,
        pos=lambda: qt.QtCore.QPoint(x, y),
        source=lambda: source,
        rect=lambda: qt.QtCore.QRect(0, 0, 400, 400),
        accept=lambda: result.update(accepted=True),
        acceptProposedAction=lambda: result.update(accepted=True),
        ignore=lambda: result.update(ignored=True),
        setDropAction=lambda action: result.update(action=action),
    )
    return event, result


def test_native_variant_drag_buffer_roundtrip_and_corrupt_input(official_qt):
    from fontlab_python_examples.official import pack_values, unpack_values

    qt, _ = official_qt
    point = qt.QtCore.QPoint(3, 7)
    pixmap = qt.QtGui.QPixmap(80, 80)
    values = unpack_values(qt, pack_values(qt, ["Łódź", point, pixmap]))
    assert values == ["Łódź", point, pixmap]
    with pytest.raises(ValueError, match="Invalid drag data"):
        unpack_values(qt, qt.QtCore.QByteArray(b"truncated"))


@pytest.mark.parametrize("name", ["draggabletext", "fridgemagnets"])
def test_word_drag_external_text_and_internal_move(name, official_qt, monkeypatch):
    from fontlab_python_examples.official import read

    qt, _ = official_qt
    handle = built(name, qt)
    window = handle.widget
    before = handle.snapshot()["label_count"]
    mime = qt.QtCore.QMimeData()
    mime.setText("Zoë Łódź")
    mime.setData("application/x-hotspot", b"3 4")
    event, result = drop_event(qt, mime, 53, 64)
    window.dropEvent(event)
    labels = handle.snapshot()["labels"]
    assert result["accepted"] and len(labels) == before + 2
    assert [label["text"] for label in labels[-2:]] == ["Zoë", "Łódź"]
    assert labels[-2]["x"] == (50 if name == "draggabletext" else 53)
    if name == "draggabletext":
        mime.setData("application/x-hotspot", b"bad offset")
        window.dropEvent(event)
        assert handle.snapshot()["labels"][-2]["x"] == 53
    label = next(child for child in window.children() if child.inherits("QLabel"))
    invoke = qt.QtGui.QDrag._invoke

    def drag(self, key, *args, **kwargs):
        if key == "exec":
            event, accepted = drop_event(qt, self._data["mimeData"], 103, 104, label)
            window.dropEvent(event)
            assert accepted["accepted"]
            return qt.QtCore.Qt.MoveAction
        return invoke(self, key, *args, **kwargs)

    monkeypatch.setattr(qt.QtGui.QDrag, "_invoke", drag)
    label.mousePressEvent(SimpleNamespace(pos=lambda: qt.QtCore.QPoint(3, 4)))
    assert not label.isVisible()
    assert handle.snapshot()["labels"][-1]["text"] == (
        label.labelText if name == "fridgemagnets" else read(label, "text")
    )
    handle.close()


def test_draggable_icons_copy_move_and_reject_other_mime(official_qt, monkeypatch):
    qt, _ = official_qt
    handle = built("draggableicons", qt)
    left, right = handle.controls["left"], handle.controls["right"]
    invoke = qt.QtGui.QDrag._invoke
    action = [qt.QtCore.Qt.CopyAction]

    def drag(self, key, *args, **kwargs):
        if key == "exec":
            event, result = drop_event(qt, self._data["mimeData"], 80, 90, left)
            right.dropEvent(event)
            assert result["accepted"]
            return action[0]
        return invoke(self, key, *args, **kwargs)

    monkeypatch.setattr(qt.QtGui.QDrag, "_invoke", drag)
    left.mousePressEvent(SimpleNamespace(pos=lambda: qt.QtCore.QPoint(23, 24)))
    assert handle.snapshot()["panels"][1][-1] == {"x": 77, "y": 86, "visible": True}
    assert sum(x["visible"] for x in handle.snapshot()["panels"][0]) == 3
    action[0] = qt.QtCore.Qt.MoveAction
    left.mousePressEvent(SimpleNamespace(pos=lambda: qt.QtCore.QPoint(23, 24)))
    assert sum(x["visible"] for x in handle.snapshot()["panels"][0]) == 2
    event, result = drop_event(qt, qt.QtCore.QMimeData(), 0, 0)
    right.dropEvent(event)
    assert result["ignored"]
    handle.close()


@pytest.mark.parametrize("name", ["draganddrop puzzle", "itemviews puzzle"])
def test_puzzle_drop_cancel_completion_and_restart(name, official_qt):
    from fontlab_python_examples.official import pack_values

    qt, _ = official_qt
    handle = built(name, qt)
    c = handle.controls
    board = c["puzzleWidget"]
    assert handle.snapshot()["piece_count"] == 25 and handle.snapshot()["placed"] == 0

    def place(x, y):
        mime = qt.QtCore.QMimeData()
        mime.setData(
            "application/x-fontlab-puzzle-piece",
            pack_values(qt, [qt.QtGui.QPixmap(80, 80), qt.QtCore.QPoint(x, y)]),
        )
        event, result = drop_event(qt, mime, x * 80 + 4, y * 80 + 6)
        board.dropEvent(event)
        return result

    assert place(0, 0)["accepted"]
    assert handle.snapshot()["in_place"] == 1
    assert place(0, 0)["ignored"], "Occupied cells reject a second piece"
    qt._drag_result = qt.QtCore.Qt.IgnoreAction
    board.mousePressEvent(SimpleNamespace(pos=lambda: qt.QtCore.QPoint(5, 5)))
    assert handle.snapshot()["in_place"] == 1 and handle.snapshot()["placed"] == 1
    qt._drag_result = qt.QtCore.Qt.MoveAction
    board.mousePressEvent(SimpleNamespace(pos=lambda: qt.QtCore.QPoint(5, 5)))
    assert handle.snapshot()["in_place"] == 0 and handle.snapshot()["placed"] == 0
    for y in range(5):
        for x in range(5):
            assert place(x, y)["accepted"]
    assert handle.snapshot()["in_place"] == 25
    board.paintEvent(SimpleNamespace(rect=lambda: qt.QtCore.QRect(0, 0, 400, 400)))
    c["completionTimer"].emit("timeout")
    assert c["active_dialog"].windowTitle == "Puzzle Completed"
    assert handle.snapshot()["in_place"] == 25, "Reset follows the dialog response"
    c["active_dialog"].emit("buttonClicked", qt.QtGui.QMessageBox.Ok)
    assert handle.snapshot()["in_place"] == 0
    assert handle.snapshot()["piece_count"] == 25
    c["openImage"]("/not/a/real/image")
    assert handle.snapshot()["error"] and handle.snapshot()["piece_count"] == 25
    timer = c["completionTimer"]
    handle.close()
    assert not timer.isActive()


def test_puzzle_model_roundtrip_and_row_bounds(official_qt):
    qt, _ = official_qt
    handle = built("itemviews puzzle", qt)
    model = handle.controls["model"]
    mime = model.mimeData([model.index(0, 0)])
    root = qt.QtCore.QModelIndex()
    assert model.dropMimeData(mime, qt.QtCore.Qt.MoveAction, -1, 0, root)
    assert model.rowCount() == 26
    assert model.removeRows(0, 1, root) and model.rowCount() == 25
    for row, count in ((-1, 1), (0, -1), (0, 0), (24, 2), (9999, 1)):
        assert not model.removeRows(row, count, root)
    assert model.rowCount(model.index(0, 0)) == 0
    assert not model.dropMimeData(
        qt.QtCore.QMimeData(), qt.QtCore.Qt.MoveAction, 0, 0, root
    )
    handle.controls["restart"]()
    assert model.rowCount() == 25
    handle.close()


def test_drag_close_guard_retries_before_releasing_source(official_qt, monkeypatch):
    from fontlab_python_examples.official import Demo

    qt, _ = official_qt
    demo = Demo(qt, __file__, "drag-test")
    window = qt.QtGui.QWidget()
    handle = demo.finish(window)
    invoke = qt.QtGui.QDrag._invoke

    def drag(self, key, *args, **kwargs):
        if key == "exec":
            for _ in range(2):
                with pytest.raises(RuntimeError, match="Finish or cancel the drag"):
                    handle.close()
                assert not handle.owner.closed and handle.cleanup
            return qt.QtCore.Qt.IgnoreAction
        return invoke(self, key, *args, **kwargs)

    monkeypatch.setattr(qt.QtGui.QDrag, "_invoke", drag)
    native_drag = qt.QtGui.QDrag(window)
    demo.drag(native_drag, qt.QtCore.Qt.MoveAction)
    assert native_drag.deleted
    handle.close()
    assert handle.owner.closed


def test_chart_edit_selection_file_roundtrip_and_bad_input(official_qt, tmp_path):
    qt, _ = official_qt
    handle = built("chart", qt)
    c, model = handle.controls, handle.controls["model"]
    initial = handle.snapshot()
    assert initial["row_count"] > 0 and initial["total"] > 0
    model.setData(model.index(0, 1), 123.0)
    assert handle.snapshot()["quantities"][0] == 123
    for value in ("not a number", "nan", None, -4):
        model.setData(model.index(0, 1), value)
        assert handle.snapshot()["total"] >= 0
    model.setData(model.index(0, 1), 12.5)
    label = 'Zoë, "quoted"'
    model.setData(model.index(0, 0), label)
    c["selection"].select(
        model.index(0, 0), qt.QtGui.QItemSelectionModel.ClearAndSelect
    )
    assert handle.snapshot()["selected"] == [[0, 0]]
    c["pieChart"].paintEvent(
        SimpleNamespace(rect=lambda: qt.QtCore.QRect(0, 0, 600, 400))
    )
    path = tmp_path / "chart.cht"
    c["writeFile"](str(path))
    assert path.exists() and not handle.snapshot()["error"]
    c["openFile"](str(path))
    assert handle.snapshot()["labels"][0] == label
    assert handle.snapshot()["quantities"][0] == 12.5
    before = handle.snapshot()["labels"]
    path.write_text("invalid\n")
    c["openFile"](str(path))
    assert handle.snapshot()["error"]
    assert handle.snapshot()["labels"] == before, (
        "Parse before replacing a loaded chart"
    )
    handle.close()


@pytest.mark.parametrize(
    "name,control,mime_type",
    [
        ("draggableicons", "left", "application/x-fontlab-dnditemdata"),
        ("fridgemagnets", "board", "application/x-fontlab-fridgemagnet"),
        ("draganddrop puzzle", "puzzleWidget", "application/x-fontlab-puzzle-piece"),
        ("itemviews puzzle", "puzzleWidget", "application/x-fontlab-puzzle-piece"),
    ],
)
def test_invalid_drag_payload_is_rejected_without_losing_owned_ui(
    name, control, mime_type, official_qt
):
    from fontlab_python_examples.official import pack_values

    qt, _ = official_qt
    handle = built(name, qt)
    for payload in (qt.QtCore.QByteArray(b"broken"), pack_values(qt, ["wrong type"])):
        mime = qt.QtCore.QMimeData()
        mime.setData(mime_type, payload)
        event, result = drop_event(qt, mime, 10, 10)
        handle.controls[control].dropEvent(event)
        assert result["ignored"] and not result["accepted"]
        assert handle.snapshot()["error"] and not handle.owner.closed
    handle.close()


@pytest.mark.parametrize(
    "row",
    [r for r in records() if r["source_id"] in BATCH_FOUR_IDS],
    ids=lambda r: r["name"],
)
def test_batch_four_inspect_is_inert_and_build_failure_releases_root(
    row, official_qt, monkeypatch
):
    from fontlab_python_examples.official import Demo

    qt, owners = official_qt
    handle = load_record(row).build(qt)
    state = handle.snapshot()
    directory = Path(state["directory"]) if "directory" in state else None
    before = list(directory.iterdir()) if directory else None
    assert handle.snapshot() == state
    assert (list(directory.iterdir()) if directory else None) == before
    handle.close()
    before_owners = len(owners)

    def fail(self, window, extra=dict):
        raise RuntimeError("injected finish failure")

    monkeypatch.setattr(Demo, "finish", fail)
    with pytest.raises(RuntimeError, match="injected finish failure"):
        load_record(row).build(qt)
    assert owners[before_owners:] and all(
        owner.closed for owner in owners[before_owners:]
    )


def test_batch_four_native_aliases_members_and_resource_literals_match_contract():
    from tests.official_doubles import CONTRACT

    for row in records():
        if row["source_id"] not in BATCH_FOUR_IDS:
            continue
        path = ROOT / row["target_path"]
        tree = ast.parse(path.read_text())
        aliases = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            if not isinstance(node.targets[0], ast.Name):
                continue
            value = ast.unparse(node.value)
            if value.startswith("qt.") and len(value.split(".")) == 3:
                _, module, name = value.split(".")
                assert name in CONTRACT[module], (path, value)
                aliases[node.targets[0].id] = CONTRACT[module][name]
        for cls in (
            n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.bases
        ):
            native = aliases.get(ast.unparse(cls.bases[0]))
            if native is None:
                continue
            own = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
            for call in (
                n
                for n in ast.walk(cls)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            ):
                if ast.unparse(call.func.value) == "self":
                    assert call.func.attr in native or call.func.attr in own, (
                        path,
                        cls.name,
                        call.func.attr,
                    )
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            if ast.unparse(call.func) == "demo.asset" and isinstance(
                call.args[0], ast.Constant
            ):
                assert (
                    path.parent / "assets" / row["source_id"] / call.args[0].value
                ).is_file()


def test_puzzle_view_native_drag_uses_model_mime_and_removes_only_moved_rows(
    official_qt, monkeypatch
):
    qt, _ = official_qt
    handle = built("itemviews puzzle", qt)
    model, view = handle.controls["model"], handle.controls["piecesList"]
    view.selectionModel().select(
        model.index(0, 0), qt.QtGui.QItemSelectionModel.ClearAndSelect
    )
    invoke = qt.QtGui.QDrag._invoke

    def drag(self, key, *args, **kwargs):
        if key == "exec":
            location = model.locations[0]
            event, result = drop_event(
                qt,
                self._data["mimeData"],
                location.x() * 80 + 1,
                location.y() * 80 + 1,
                view,
            )
            handle.controls["puzzleWidget"].dropEvent(event)
            assert result["accepted"]
            with pytest.raises(RuntimeError, match="Finish or cancel"):
                handle.close()
            return qt.QtCore.Qt.MoveAction
        return invoke(self, key, *args, **kwargs)

    monkeypatch.setattr(qt.QtGui.QDrag, "_invoke", drag)
    view.startDrag(qt.QtCore.Qt.MoveAction | qt.QtCore.Qt.CopyAction)
    assert model.rowCount() == 24 and handle.snapshot()["in_place"] == 1
    handle.close()


BATCH_FIVE_IMPLEMENTED = [
    row
    for row in records()
    if row["source_id"] in BATCH_FIVE_IDS and row["implementation"] == "implemented"
]


@pytest.mark.parametrize("row", BATCH_FIVE_IMPLEMENTED, ids=lambda r: r["name"])
def test_batch_five_inspect_is_inert_and_finish_failure_rolls_back(
    row, official_qt, monkeypatch
):
    from fontlab_python_examples.official import Demo

    qt, owners = official_qt
    handle = load_record(row).build(qt)
    assert handle.snapshot() == handle.snapshot(), "Inspect must not drive UI controls"
    handle.close()
    first_owner = len(owners)

    def fail(self, window, extra=dict):
        raise RuntimeError("injected finish failure")

    monkeypatch.setattr(Demo, "finish", fail)
    with pytest.raises(RuntimeError, match="injected finish failure"):
        load_record(row).build(qt)
    assert owners[first_owner:] and all(owner.closed for owner in owners[first_owner:])


def test_batch_five_shared_memory_has_precise_native_blocker(official_qt, monkeypatch):
    import fontlab_python_examples as examples

    row = next(r for r in records() if r["source_id"] == "de35a965dfcfd678")
    assert row["implementation"] == "blocked"
    assert (
        "detach()" in row["blocked_reason"] and "byte-buffer" in row["blocked_reason"]
    )
    qt, owners = official_qt
    assert not hasattr(qt.QtCore.QSharedMemory, "detach")
    with pytest.raises(NotImplementedError, match="detach"):
        load_record(row).build(qt)
    monkeypatch.setattr(
        "fontlab_python_examples.launcher._host",
        lambda: pytest.fail("Blocked launch must not access Qt"),
    )
    with pytest.raises(NotImplementedError, match="detach"):
        examples.launch(row["source_id"])
    assert not owners


@pytest.mark.parametrize("name", ["semaphores", "waitconditions"])
def test_batch_five_ring_workers_complete_stop_and_restart(name, official_qt):
    import time

    qt, _ = official_qt
    handle = built(name, qt)
    c = handle.controls
    assert handle.snapshot()["phase"] == "idle"
    c["start"].click()
    deadline = time.monotonic() + 8
    while handle.snapshot()["phase"] == "running" and time.monotonic() < deadline:
        c["timer"].emit("timeout")
        time.sleep(0.001)
    state = handle.snapshot()
    assert state["phase"] == "done", state
    assert state["received"] == state["data_size"] == 100000
    assert state["prefix"] == state["suffix"] == "ACGT" * 20
    assert not state["worker_alive"] and not state["timer_active"]
    c["start"].click()
    c["stop"].click()
    assert not handle.snapshot()["worker_alive"]
    c["start"].click()
    # No GUI drain: the bounded queue fills; close must cancel blocked publishers.
    time.sleep(0.03)
    timer = c["timer"]
    handle.close()
    assert not timer.isActive() and not handle.connections


def test_batch_five_worker_error_and_join_failure_retain_owned_ui(
    official_qt, monkeypatch
):
    import time

    from fontlab_python_examples.official import Demo, WorkerDelivery

    qt, _ = official_qt
    demo = Demo(qt, __file__, "worker-test")
    root = qt.QtGui.QWidget()
    demo.begin(root)
    received = []
    worker = WorkerDelivery(demo, received.append)

    def broken(stop, publish):
        raise ValueError("worker fixture failure")

    worker.start(broken)
    deadline = time.monotonic() + 2
    while worker.phase == "running" and time.monotonic() < deadline:
        worker.drain()
        time.sleep(0.001)
    assert worker.phase == "error" and demo.error == "worker fixture failure"

    class Stalled:
        def join(self, timeout):
            pass

        def is_alive(self):
            return True

    worker.workers = [Stalled()]
    with pytest.raises(RuntimeError, match="retaining owned UI"):
        demo.handle.close()
    assert not demo.handle.owner.closed and demo.handle.connections
    worker.workers.clear()
    demo.handle.close()
    assert demo.handle.owner.closed


def test_batch_five_mandelbrot_scanlines_are_plain_pixels_and_cancellable(official_qt):
    from threading import Event

    row = next(r for r in records() if r["source_id"] == "0788354954c8e613")
    module = load_record(row)
    stop = Event()
    values = []
    module.render_rows(stop, lambda v: values.append(v) or True, 3, 2, 2.0, 2.0, 0.1)
    assert len(values) == 8 * 2
    assert [v[1] for v in values[::2]] == list(range(8))
    assert all(
        type(pixel) is int and 0xFF000000 <= pixel <= 0xFFFFFFFF
        for v in values
        for pixel in v[3]
    )
    stop.set()
    module.render_rows(
        stop, lambda value: pytest.fail("Cancelled worker published"), 2, 2, 0, 0, 1
    )
    for wavelength in (380, 440, 490, 510, 580, 645, 700, 780):
        assert 0xFF000000 <= module.rgb_from_wave_length(wavelength) <= 0xFFFFFFFF


def test_batch_five_mandelbrot_zoom_scroll_restart_and_close(official_qt):
    import time

    qt, _ = official_qt
    handle = built("mandelbrot", qt)
    c = handle.controls
    handle.widget.resize(8, 6)
    c["start"]()
    time.sleep(0.01)
    c["timer"].emit("timeout")
    original = handle.snapshot()
    c["zoom"](0.8)
    assert handle.snapshot()["scale"] == pytest.approx(original["scale"] * 0.8)
    c["scroll"](20, -20)
    assert handle.snapshot()["center"][0] > original["center"][0]
    for factor in (0, -1, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="positive and finite"):
            c["zoom"](factor)
    c["stop"]()
    assert not handle.snapshot()["worker_alive"]
    handle.widget.paintEvent(SimpleNamespace())
    c["start"]()
    timer = c["timer"]
    handle.close()
    assert not timer.isActive()


def test_batch_five_animated_tiles_native_relays_change_layouts(official_qt):
    qt, _ = official_qt
    handle = built("animatedtiles", qt)
    c = handle.controls
    assert handle.snapshot()["item_count"] == 64
    original = handle.snapshot()["positions"]
    for name in ("ellipse", "figure8", "random", "tiled"):
        button = c[name]
        button.mousePressEvent(SimpleNamespace())
        assert handle.snapshot()["positions"] != original
    c["centered"].mousePressEvent(SimpleNamespace())
    assert handle.snapshot()["positions"] == [[0, 0]] * 64
    machine = c["states"]
    handle.close()
    assert not machine.isRunning()


def test_batch_five_appchooser_selects_original_icon_geometry(official_qt):
    qt, _ = official_qt
    handle = built("appchooser", qt)
    c = handle.controls
    assert handle.snapshot()["item_count"] == 4
    c["items"][1].mousePressEvent(SimpleNamespace())
    assert handle.snapshot()["geometries"][1] == [86, 86, 128, 128]
    c["items"][2].mousePressEvent(SimpleNamespace())
    assert handle.snapshot()["geometries"][2] == [86, 86, 128, 128]
    c["items"][0].paint(qt.QtGui.QPainter(), SimpleNamespace(), None)
    handle.close()


def test_batch_five_states_cycle_button_and_stop_machine(official_qt):
    qt, _ = official_qt
    handle = built("states", qt)
    c = handle.controls
    assert handle.snapshot()["button_text"] == "Switch to state 2"
    for text in ("Switch to state 3", "Switch to state 1", "Switch to state 2"):
        c["button"].click()
        assert handle.snapshot()["button_text"] == text
    c["edit"].setPlainText("Owned scene text")
    assert handle.snapshot()["text"] == "Owned scene text"
    machine = c["machine"]
    handle.close()
    assert not machine.isRunning()


def test_batch_five_moveblocks_chooses_different_states(official_qt):
    qt, _ = official_qt
    handle = built("moveblocks", qt)
    previous = handle.snapshot()
    for _ in range(10):
        handle.controls["advance"]()
        state = handle.snapshot()
        assert state["state_index"] != previous["state_index"]
        assert state["geometries"] != previous["geometries"]
        previous = state
    timer = handle.controls["timer"]
    handle.close()
    assert not timer.isActive()


def test_batch_five_easing_curves_parameters_path_and_paint(official_qt):
    qt, _ = official_qt
    handle = built("easing", qt)
    c = handle.controls
    assert handle.snapshot()["curve_count"] == 47
    c["easingCurvePicker"].setCurrentRow(29)  # InElastic
    assert handle.snapshot()["curve"] == "InElastic"
    assert c["periodSpinBox"].isEnabled()
    c["periodSpinBox"].setValue(0.7)
    c["amplitudeSpinBox"].setValue(2.5)
    c["overshootSpinBox"].setValue(3.2)
    c["circleRadio"].setChecked(True)
    assert handle.snapshot()["path"] == "circle"
    c["animation"].updateCurrentTime(1000)
    assert len(handle.snapshot()["position"]) == 2
    c["item"].paint(qt.QtGui.QPainter(), SimpleNamespace(), None)
    c["circleRadio"].setChecked(False)
    assert handle.snapshot()["path"] == "line"
    handle.close()


def test_batch_five_stickman_real_frames_keys_lightning_and_teardown(official_qt):
    qt, _ = official_qt
    handle = built("stickman", qt)
    c = handle.controls
    assert handle.snapshot()["node_count"] == 16
    assert handle.snapshot()["frames"] == {
        "jumping": 5,
        "dancing": 9,
        "chilling": 25,
        "dead": 1,
    }
    original = handle.snapshot()["positions"]
    c["view"].keyPressEvent(SimpleNamespace(key=lambda: qt.QtCore.Qt.Key_J))
    assert handle.snapshot()["activity"] == "jumping"
    frame = next(s for s in c["machine"].configuration() if s._extra.get("assignments"))
    frame.emit("propertiesAssigned")
    assert handle.snapshot()["positions"] != original
    c["dancing"].click()
    assert handle.snapshot()["activity"] == "dancing"
    # Coincident nodes must not divide by zero, and paint uses no wrapper arithmetic.
    from fontlab_python_examples.official import read

    c["nodes"][0].setPos(read(c["nodes"][1], "pos"))
    c["stickMan"].paint(qt.QtGui.QPainter(), SimpleNamespace(), None)
    c["strike"].click()
    assert handle.snapshot()["dead"] and handle.snapshot()["activity"] == "lightning"
    c["flash"].emit("timeout")
    assert handle.snapshot()["activity"] == "dead"
    c["chilling"].click()
    assert handle.snapshot()["activity"] == "dead", (
        "Dead state cannot restart activities"
    )
    lightning, flash = c["lightning"], c["flash"]
    handle.close()
    assert not lightning.isActive() and not flash.isActive()


def test_batch_five_embedded_dialog_controls_and_hover_timeline(official_qt):
    qt, _ = official_qt
    handle = built("embeddeddialogs", qt)
    c = handle.controls
    assert handle.snapshot()["dialog_count"] == 100
    dialog, proxy = c["dialog"], c["proxies"][-1]
    dialog.ui.spacing.setValue(12)
    assert handle.snapshot()["spacing"] == 12
    dialog.ui.directionPicker.emit("activated", 1)
    dialog.ui.stylePicker.emit("activated", "Fusion")
    proxy.hoverEnterEvent(SimpleNamespace())
    proxy.timeLine.emit("valueChanged", 0.5)
    proxy.hoverLeaveEvent(SimpleNamespace())
    timelines = [item.timeLine for item in c["proxies"]]
    handle.close()
    assert all(
        timeline.state() == qt.QtCore.QTimeLine.NotRunning for timeline in timelines
    )


def test_batch_five_colliding_mice_motion_and_paint_use_component_geometry(official_qt):
    qt, _ = official_qt
    handle = built("collidingmice", qt)
    c = handle.controls
    assert handle.snapshot()["mouse_count"] == 7
    original = handle.snapshot()["positions"]
    for mouse in c["mice"]:
        mouse.timer.emit("timeout")
        mouse.paint(qt.QtGui.QPainter(), SimpleNamespace(), None)
    assert handle.snapshot()["positions"] != original
    timers = [mouse.timer for mouse in c["mice"]]
    handle.close()
    assert all(not timer.isActive() for timer in timers)


def test_batch_five_robot_color_image_drop_and_animation_cleanup(official_qt):
    qt, _ = official_qt
    handle = built("dragdroprobot", qt)
    robot = handle.controls["robot"]
    assert handle.snapshot()["palette_count"] == 10
    mime = qt.QtCore.QMimeData()
    mime.setColorData(qt.QtGui.QColor(220, 30, 40))
    event = SimpleNamespace(mimeData=lambda: mime, setAccepted=lambda value: None)
    robot.headItem.dragEnterEvent(event)
    robot.headItem.dropEvent(event)
    assert not robot.headItem.dragOver
    mime.setImageData(qt.QtGui.QImage(30, 40, qt.QtGui.QImage.Format_RGB32))
    robot.headItem.dropEvent(event)
    assert handle.snapshot()["head_image"]
    for part in (robot.headItem, robot.torsoItem, robot.upperLeftArmItem):
        part.paint(qt.QtGui.QPainter(), SimpleNamespace(), None)
    handle.close()


def test_batch_five_diagram_insert_select_color_scale_and_delete(official_qt):
    qt, _ = official_qt
    handle = built("diagramscene", qt)
    c, window = handle.controls, handle.widget
    scene = c["scene"]
    event = SimpleNamespace(
        button=lambda: qt.QtCore.Qt.LeftButton,
        scenePos=lambda: qt.QtCore.QPointF(100, 100),
    )
    window.buttonGroupClicked(0)
    scene.mousePressEvent(event)
    assert handle.snapshot()["item_count"] == 1
    item = scene.items()[0]
    item.setSelected(True)
    scene.setItemColor(qt.QtGui.QColor(12, 34, 56))
    window.sceneScaleChanged("150%")
    window.bringToFront()
    window.sendToBack()
    window.deleteItem()
    assert handle.snapshot()["item_count"] == 0
    assert len(c["discarded"].items()) == 1, (
        "Deleted graphics items retain native ownership"
    )
    window.buttonGroupClicked(window.InsertTextButton)
    scene.mousePressEvent(event)
    text = scene.items()[0]
    text.setPlainText("Owned diagram text")
    text.focusOutEvent(SimpleNamespace())
    assert handle.snapshot()["item_count"] == 1, "Keep nonempty text"
    text.setPlainText("")
    text.focusOutEvent(SimpleNamespace())
    assert handle.snapshot()["item_count"] == 0
    window.about()
    assert c["active_dialog"].windowTitle == "About Diagram Scene"
    handle.close()


def test_batch_five_screenshot_capture_save_cancel_and_inert_inspect(
    official_qt, monkeypatch
):
    qt, _ = official_qt
    captures = []

    class Screen:
        def grabWindow(self, window_id):
            captures.append(window_id)
            return qt.QtGui.QPixmap(320, 200)

    monkeypatch.setattr(
        qt.QtGui.QApplication, "primaryScreen", lambda: Screen(), raising=False
    )
    handle = built("screenshot", qt)
    c = handle.controls
    assert not handle.snapshot()["has_capture"] and not captures
    assert handle.snapshot() == handle.snapshot() and not captures
    c["delaySpinBox"].setValue(0)
    assert not c["hideThisWindowCheckBox"].isEnabled()
    c["newScreenshotButton"].click()
    assert handle.snapshot()["capture_pending"] and not captures
    c["captureTimer"].emit("timeout")
    assert captures == [0] and handle.snapshot()["has_capture"]
    c["saveScreenshotButton"].click()
    box = c["active_dialog"]
    directory = Path(box._data["directory"])
    output = directory / "capture.png"
    saves = []
    invoke = qt.QtGui.QPixmap._invoke

    def save(self, key, *args, **kwargs):
        if key == "save":
            saves.append(args)
            return True
        return invoke(self, key, *args, **kwargs)

    monkeypatch.setattr(qt.QtGui.QPixmap, "_invoke", save)
    c["saveTo"](str(output))
    assert saves == [(str(output.resolve()), "PNG")]
    c["saveTo"]("/outside/owned.png")
    assert "temporary directory" in handle.snapshot()["error"]
    assert len(saves) == 1
    c["newScreenshotButton"].click()
    timer = c["captureTimer"]
    handle.close()
    assert not timer.isActive() and not directory.exists()


def test_batch_five_systray_explicit_visibility_messages_and_owned_quit(
    official_qt, monkeypatch
):
    qt, owners = official_qt
    messages = []
    invoke = qt.QtGui.QSystemTrayIcon._invoke

    def record(self, key, *args, **kwargs):
        if key == "showMessage":
            messages.append(args)
            return None
        return invoke(self, key, *args, **kwargs)

    monkeypatch.setattr(qt.QtGui.QSystemTrayIcon, "_invoke", record)
    handle = built("systray", qt)
    c = handle.controls
    assert not handle.snapshot()["tray_visible"] and not messages
    c["showIconCheckBox"].setChecked(True)
    assert handle.snapshot()["tray_visible"]
    c["iconComboBox"].setCurrentIndex(2)
    assert handle.snapshot()["icon_index"] == 2
    c["showMessageButton"].click()
    assert len(messages) == 1
    c["trayIcon"].emit("messageClicked")
    assert len(handle.alerts) == 1
    tray = c["trayIcon"]
    c["quitAction"].trigger()
    assert handle.owner.closed and not tray.isVisible()
    assert all(owner.closed for owner in owners)


@pytest.mark.parametrize("row", BATCH_FIVE_IMPLEMENTED, ids=lambda r: r["name"])
def test_batch_five_stops_every_registered_activity_before_native_delete(
    row, official_qt
):
    qt, _ = official_qt
    handle = load_record(row).build(qt)
    activities = [getattr(callback, "__self__", None) for callback in handle.cleanup]
    original_close = handle.owner.close

    def checked_close():
        for activity in activities:
            if hasattr(activity, "_active"):
                assert not activity._active, (
                    "Stop timers/machines/animations before native deletion"
                )
        assert not handle.connections and not handle.controls
        original_close()

    handle.owner.close = checked_close
    handle.close()


def test_batch_five_python_callbacks_are_released_without_clearing_native_methods(
    official_qt,
):
    from fontlab_python_examples.official import Demo

    qt, _ = official_qt
    demo = Demo(qt, __file__, "callback-release")

    class Window(qt.QtGui.QWidget):
        pass

    window = Window()
    demo.begin(window)
    window._callback = lambda: window
    demo.track(window, "_callback")
    handle = demo.finish(window)
    original_close = handle.owner.close

    def checked_close():
        assert window._callback is None
        assert callable(window.close)
        original_close()

    handle.owner.close = checked_close
    handle.close()


def test_batch_five_native_members_resources_and_no_modal_shortcuts():
    from tests.official_doubles import CONTRACT

    sources = {
        r["id"]: r
        for r in json.loads((ROOT / "catalog/sources.json").read_text())["files"]
    }
    for row in records():
        if row["source_id"] not in BATCH_FIVE_IDS:
            continue
        path = ROOT / row["target_path"]
        text = path.read_text()
        assert (
            row["license"]["original_notices"][0]
            .removeprefix("#!/usr/bin/env python\n")
            .strip()
            in text
        )
        tree = ast.parse(text, feature_version=(3, 11))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                parts = ast.unparse(node).split(".")
                if (
                    len(parts) >= 3
                    and parts[0] == "qt"
                    and parts[1] in CONTRACT
                    and parts[2].isidentifier()
                ):
                    assert parts[2] in CONTRACT[parts[1]], (path, parts)
                    if len(parts) == 4:
                        assert parts[3] in CONTRACT[parts[1]][parts[2]], (path, parts)
            if isinstance(node, ast.Call):
                callee = ast.unparse(node.func)
                assert not callee.startswith(
                    (
                        "QMessageBox.about",
                        "QMessageBox.information",
                        "QMessageBox.warning",
                        "QMessageBox.critical",
                        "QFileDialog.get",
                        "QTimer.singleShot",
                    )
                ), (path, callee)
        for resource in row["resources"]:
            source = sources[resource["source_id"]]
            assert resource["source"]["sha256"] == source["sha256"]
            assert resource["source"]["path"] == source["path"]
            assert (
                resource["license"]["basis"] and resource["license"]["reviewed_files"]
            )
            assert not resource["target_path"].endswith("_rc.py")
        assert row["source_id"] in (ROOT / "README.md").read_text()
        assert (
            f"batch-5-{row['source_id']}"
            in (ROOT / "docs/pyqt-official-batch.md").read_text()
        )
