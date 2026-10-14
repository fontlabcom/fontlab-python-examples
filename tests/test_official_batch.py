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

BATCH_SIX_IDS = {
    "4efac54bae01fc62",
    "60d40ce5671653cf",
    "09afeea11be83f4f",
    "2d36e0fe43f5d49a",
    "912e5c751b20ce97",
    "13a6bb9a9d2b9037",
    "b2d717e4d43806d2",
    "c12a2071adbab88b",
    "c56cf1699b07b350",
    "c997677a2bdb4f34",
    "428c50abcef7adfe",
    "b34b2f696a977e74",
    "806fd814a2ea4d46",
    "d6dc56a5318ffe71",
    "356e4e807f1e789f",
    "b91effc45f81fbb0",
    "499e965d86347920",
    "3040b9f6b267a196",
    "f702b62aa47629ad",
    "16456ba02f4b79cc",
    "84cb59e07adfae2c",
    "8e5aa13798c2763c",
    "248e64416b9b218c",
    "36805750b888fba6",
    "468179092748a72e",
    "9e21c6536fda7a23",
    "e63bffc17abf2fde",
    "509e781f1267967f",
    "136c45cc9f97c218",
}
IDS |= BATCH_SIX_IDS

BATCH_SEVEN_IDS = {
    "409f3d46a9555f23",
    "67170c89593ad35e",
    "d8803c2afaabf3d5",
    "9dab02b61cebbdb7",
    "0bba8a80541ab04f",
    "ebf87d5f5390b0fd",
    "a96a7978c0b9f6ee",
    "79f3a23172968ad2",
    "98f207907001ce47",
    "029ea0dabe87ae57",
    "d50ad6638357e669",
    "39de33366209402d",
    "cf15c3e91cdd8ded",
    "fbb4e3c7288fed7c",
    "fff97a435b73d548",
    "4b8851287931abd0",
    "aad57160cfd51894",
    "a58650b5461c0f48",
    "43c6c2f6f5f036d3",
    "90721289b8108c4f",
    "fa6823667fdb918f",
    "dc59f268ee01e364",
    "bf3b39a8c2df8e94",
    "cc95f9719b8e4eda",
    "0a3b15766909bdc3",
    "a59dae9770bfbefb",
    "ddb20b1b68b18a91",
}
IDS |= BATCH_SEVEN_IDS

BATCH_EIGHT_IDS = {
    "7ba49e67588b1329",
    "ad499afe23726248",
    "1ad60855ca28f3cc",
    "6417cdcf1bfd1752",
    "68d664f95f48ce52",
    "b383fecf912548bb",
    "b9660f4ee653ca01",
    "5125860585e98b3a",
    "ab719a6a5c3afe4a",
    "9941e3c752b3a3b7",
    "b7db02f540cc7559",
    "835281a1ab864833",
    "831ac8ea61da03f3",
    "781a3a959215eb81",
    "3cf5db95a691d200",
    "8d5ea81a74e30222",
    "fcada4fff6524fcf",
    "b83377c9b48aec14",
    "74af8d8d2d7774b8",
    "9030a87a532b8d8f",
    "0ad3432ccdca7ac0",
    "47298251b3c83ecf",
    "5a8e48d2a1396cea",
    "738a22ef3062ed51",
    "ca47b83fbf3f31b9",
    "1e5d0f7289e1b36e",
    "e1316fee99c63555",
    "f4000cf8ca288375",
    "b64d66dbce7274fe",
    "333f0272885ca1b7",
    "0a13f60f5f0561db",
    "6ed36280660df7ea",
    "f6d352360ae9bdfb",
    "a14d08fe23965bec",
    "bcfa5de0140286d5",
    "0677ebfd7fa2cc60",
    "2c4c366f259d7d80",
    "ed6d42d4faa7e0bb",
    "960c701fa6221ac5",
    "303ea3ee09c4677d",
    "38465a8f4b1a229f",
    "8847cbce50b72500",
    "4d24cd77c74a8801",
    "8d1557cbfed9c7a0",
    "5941e31267112c98",
    "85a56a1f3c25ccca",
    "75ca5ac77ecefd6d",
    "773db5c24ae98ffb",
    "4dbe92cd1e720dce",
    "de4979a99c6d0bed",
    "5eb4b9eaa2d5c9dc",
    "481c128fba3a714b",
    "27bf65f8b059fd96",
    "a1273c8940d43221",
    "c391afd8516131e1",
    "d0a18273fa604bb6",
    "1321540b04f33117",
    "81a6f0d16c203608",
    "54cbd9afababdf71",
    "ae16288fede27692",
    "2f1e2f679775d89e",
    "6b1f4f5590a5518a",
    "0b0d8d2fae153e5e",
    "34538a4e2600b918",
    "30cfa75ad45b3447",
    "57a381bc8260c85d",
    "b88e7eb0fcb53264",
    "dd226ba9fbb7b330",
    "c82d1af7d1a7b0cf",
    "54c7440bdcdc3dfc",
    "3cd3713a5dc9f6dc",
    "eb7a89f07f63cca7",
    "36246fcbffecdeba",
    "a57a89e523c75b7f",
}
IDS |= BATCH_EIGHT_IDS

# Standalone widgets retain their behavior; their Designer plugin integration is
# separately blocked because the host does not expose QtDesigner.
BATCH_EIGHT_IMPLEMENTED = {
    "27bf65f8b059fd96",
    "4d24cd77c74a8801",
    "9941e3c752b3a3b7",
    "1321540b04f33117",
    "7ba49e67588b1329",
    "de4979a99c6d0bed",
    "773db5c24ae98ffb",
    "bcfa5de0140286d5",
    "5125860585e98b3a",
    "0ad3432ccdca7ac0",
    "a14d08fe23965bec",
    "c82d1af7d1a7b0cf",
    "5a8e48d2a1396cea",
    "b7db02f540cc7559",
    "b9660f4ee653ca01",
    "1e5d0f7289e1b36e",
}


def test_batch_eight_supported_entrypoints_have_real_ports():
    rows = json.loads((ROOT / "catalog/ports.json").read_text())["ports"]
    implemented = {r["source_id"] for r in rows if r["implementation"] == "implemented"}
    assert BATCH_EIGHT_IMPLEMENTED <= implemented, "All 16 supported demos need ports"


def records():
    return [
        r
        for r in json.loads((ROOT / "catalog/ports.json").read_text())["ports"]
        if r["source_id"] in IDS
    ]


def test_official_manifest_covers_exact_batch_and_retains_provenance():
    rows = records()
    assert {r["source_id"] for r in rows} == IDS, (
        "All 187 official entries require a result"
    )
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

    qt._screens = [Screen()]
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


@pytest.mark.parametrize(
    "row",
    [
        r
        for r in records()
        if r["source_id"] in BATCH_SIX_IDS and r["implementation"] == "implemented"
    ],
    ids=lambda r: r["name"],
)
def test_batch_six_inspect_is_inert_and_failure_releases_owned_root(
    row, official_qt, monkeypatch
):
    from fontlab_python_examples.official import Demo

    qt, owners = official_qt
    handle = load_record(row).build(qt)
    before = handle.snapshot()
    assert before["error"] == "", (
        "Every default batch-6 document/resource must load successfully"
    )
    connections = list(handle.connections)
    controls = dict(handle.controls)
    cleanup_count = len(handle.cleanup)
    assert handle.snapshot() == before, "Inspect must only read UI"
    assert handle.connections == connections and handle.controls == controls
    assert len(handle.cleanup) == cleanup_count, (
        "Inspect must not allocate QSettings or callbacks"
    )
    handle.close()
    offset = len(owners)

    def fail(self, window, extra=dict):
        raise RuntimeError("injected finish failure")

    monkeypatch.setattr(Demo, "finish", fail)
    with pytest.raises(RuntimeError, match="injected finish failure"):
        load_record(row).build(qt)
    assert owners[offset:] and all(owner.closed for owner in owners[offset:]), (
        "Failed construction must release every window"
    )


def test_batch_six_textobject_blocker_is_native_interface_absence(official_qt):
    from tests.official_doubles import CONTRACT

    row = next(r for r in records() if r["source_id"] == "806fd814a2ea4d46")
    assert (
        row["implementation"] == "blocked"
        and "QTextObjectInterface" in row["blocked_reason"]
    )
    assert "QTextObjectInterface" not in CONTRACT["QtGui"]
    with pytest.raises(RuntimeError, match="QTextObjectInterface"):
        load_record(row).build(official_qt[0])


@pytest.mark.parametrize(
    "expression,result",
    [("2+3*4=", "14.0"), ("9/0=", "####"), ("0", "0"), ("7=", "7.0")],
)
def test_batch_six_calculator_buttons_preserve_precedence_and_zero_division(
    expression, result, official_qt
):
    qt, _ = official_qt
    h = built("calculator", qt)
    mapping = {
        "+": "plusButton",
        "*": "timesButton",
        "/": "divisionButton",
        "=": "equalButton",
    }
    for key in expression:
        (
            h.widget.digitButtons[int(key)]
            if key.isdigit()
            else h.controls[mapping[key]]
        ).click()
    assert h.snapshot()["display_text"] == result
    h.controls["clearAllButton"].click()
    assert h.snapshot()["display_text"] == "0"
    h.close()


def test_batch_six_clocks_and_circles_have_owned_stoppable_timers(official_qt):
    qt, _ = official_qt
    for name in (
        "analogclock",
        "shapedclock",
        "digitalclock",
        "concentriccircles",
        "styles",
        "wiggly",
    ):
        h = built(name, qt)
        if name == "concentriccircles":
            assert h.snapshot()["frames"] == [0, 0, 0, 0]
            h.controls["timer"].emit("timeout")
            assert h.snapshot()["frames"] == [1, 1, 1, 1]
        elif name == "digitalclock":
            assert h.controls["window"]._data["value"] == "12 34"
        elif name == "wiggly":
            h.controls["lineEdit"].setText("Hello FontLab")
            assert h.snapshot()["text"] == "Hello FontLab"
        elif name == "styles":
            before = h.controls["progressBar"].value
            h.controls["timer"].emit("timeout")
            assert h.controls["progressBar"].value > before
            h.controls["disableWidgetsCheckBox"].setChecked(True)
            assert not h.controls["topLeftGroupBox"].enabled
        timers = [
            obj
            for obj in h.controls.values()
            if getattr(obj, "_qt_name", "") in ("QTimer", "QBasicTimer")
        ]
        if name == "wiggly":
            timers.append(h.widget._wiggly.timer)
        h.close()
        assert timers and all(not t.isActive() for t in timers)


def test_batch_six_menu_actions_and_groupbox_controls(official_qt):
    qt, _ = official_qt
    h = built("menus", qt)
    h.controls["newAct"].trigger()
    assert "File|New" in h.controls["infoLabel"].text
    h.controls["boldAct"].trigger()
    assert "Format|Bold" in h.controls["infoLabel"].text
    h.controls["aboutAct"].trigger()
    assert h.controls["active_dialog"].isVisible()
    h.close()
    h = built("groupbox", qt)
    h.controls["toggleButton"].click()
    assert not h.controls["toggleButton"].checked
    h.controls["tristateBox"].setCheckState(qt.QtCore.Qt.Checked)
    assert h.controls["tristateBox"].checkState() == qt.QtCore.Qt.Checked
    h.close()


def test_batch_six_lineedit_modes_masks_and_access(official_qt):
    qt, _ = official_qt
    h = built("lineedits", qt)
    for control, index in (
        ("echoComboBox", 1),
        ("validatorComboBox", 2),
        ("inputMaskComboBox", 3),
        ("accessComboBox", 1),
    ):
        h.controls[control].emit("activated", index)
    assert h.controls["echoLineEdit"].echoMode == qt.QtGui.QLineEdit.Password
    assert "AAAAA" in h.controls["inputMaskLineEdit"].inputMask
    assert h.controls["accessLineEdit"].readOnly
    h.controls["validatorComboBox"].emit("activated", 0)
    assert h.controls["validatorLineEdit"]._data["validator"] is None
    h.close()


def test_batch_six_slider_and_spinbox_controls(official_qt):
    qt, _ = official_qt
    h = built("sliders", qt)
    h.controls["valueSpinBox"].setValue(12)
    assert h.snapshot()["horizontal"] == h.snapshot()["vertical"] == 12
    h.controls["invertedAppearance"].setChecked(True)
    assert h.widget.horizontalSliders.slider.invertedAppearance
    h.controls["orientationCombo"].emit("activated", 1)
    assert h.controls["stackedWidget"].currentIndex == 1
    h.close()
    h = built("spinboxes", qt)
    h.controls["precisionSpinBox"].setValue(4)
    assert all(
        h.controls[key].decimals == 4
        for key in ("doubleSpinBox", "priceSpinBox", "scaleSpinBox")
    )
    h.controls["formatComboBox"].emit("activated", "hh:mm:ss")
    assert h.controls["meetingEdit"].displayFormat == "hh:mm:ss"
    h.close()


def test_batch_six_calendar_month_year_font_and_widget_options(official_qt):
    qt, _ = official_qt
    h = built("calendar", qt)
    h.controls["monthCombo"].emit("activated", 1)
    h.controls["yearEdit"].setDate(qt.QtCore.QDate(2024, 2, 1))
    h.controls["fontSizeSpinBox"].setValue(18)
    assert h.snapshot()["month"] == 2 and h.snapshot()["year"] == 2024
    assert h.snapshot()["font_size"] == 18 and "February" in h.snapshot()["title"]
    h.close()
    h = built("calendarwidget", qt)
    h.controls["gridCheckBox"].setChecked(True)
    assert h.controls["calendar"].gridVisible
    h.controls["currentDateEdit"].setDate(qt.QtCore.QDate(2025, 5, 1))
    assert h.snapshot()["selected_date"] == "2025-05-01"
    h.controls["weekdayColorCombo"].emit("currentIndexChanged", 1)
    h.close()


def test_batch_six_painterpaths_and_transformations_controls(official_qt):
    qt, _ = official_qt
    h = built("painterpaths", qt)
    h.controls["penWidthSpinBox"].setValue(7)
    h.controls["rotationAngleSpinBox"].setValue(45)
    assert len(h.widget.renderAreas) == 9
    assert all(
        area.penWidth == 7 and area.rotationAngle == 45 for area in h.widget.renderAreas
    )
    h.close()
    h = built("transformations", qt)
    h.controls["shapeComboBox"].emit("activated", 2)
    h.widget.operationComboBoxes[0].setCurrentIndex(1)
    h.widget.operationComboBoxes[0].emit("activated", 1)
    assert h.widget.transformedRenderAreas[0].operations
    assert h.widget.originalRenderArea.shape is h.widget.shapes[2]
    h.close()


def test_batch_six_tetrix_start_pause_keys_and_piece_rotation(official_qt):
    qt, _ = official_qt
    h = built("tetrix", qt)
    h.controls["startButton"].click()
    board = h.widget.board
    assert h.snapshot()["started"] and board.timer.isActive()
    x = board.curX
    board.keyPressEvent(SimpleNamespace(key=qt.QtCore.Qt.Key_Left))
    assert board.curX == x - 1
    assert board.curPiece.rotatedLeft().shape() == board.curPiece.shape()
    h.controls["pauseButton"].click()
    assert h.snapshot()["paused"] and not board.timer.isActive()
    h.controls["pauseButton"].click()
    assert board.timer.isActive()
    timer = board.timer
    h.close()
    assert not timer.isActive()


def test_batch_six_charactermap_size_selection_and_explicit_clipboard(official_qt):
    qt, _ = official_qt
    h = built("charactermap", qt)
    h.controls["sizeCombo"].emit("currentIndexChanged", "16")
    assert h.widget.characterWidget.displayFont.pointSize() == 16
    h.controls["insertCharacter"]("A")
    assert h.snapshot()["text"] == "A"
    assert not h.widget.clipboard.text(), (
        "Inspect and selection must not write the clipboard"
    )
    h.controls["clipboardButton"].click()
    assert h.widget.clipboard.text() == "A"
    h.close()


def test_batch_six_windowflag_preview_is_owned(official_qt):
    qt, owners = official_qt
    h = built("windowflags", qt)
    h.controls["framelessWindowCheckBox"].click()
    assert h.widget.previewWindow.windowFlags() & qt.QtCore.Qt.FramelessWindowHint
    assert h.snapshot()["preview_visible"]
    h.close()
    assert all(owner.closed for owner in owners)


def test_batch_six_docks_and_recentfiles_preserve_documents_and_isolate_settings(
    official_qt, tmp_path
):
    qt, _ = official_qt
    h = built("dockwidgets", qt)
    h.controls["customerList"].emit(
        "currentTextChanged", "Test Customer, 123 Test Street"
    )
    assert "Test Customer" in h.controls["textEdit"].toPlainText()
    target = tmp_path / "letter.html"
    h.controls["saveAct"].trigger()
    dialog = h.controls["active_dialog"]
    dialog._extra["selectedFiles"] = [str(target)]
    assert not target.exists()
    dialog.accept()
    assert "Test Customer" in target.read_text()
    h.close()
    h = built("recentfiles", qt)
    path = tmp_path / "recent.txt"
    h.controls["textEdit"].setPlainText("Owned recent file")
    assert h.controls["saveFile"](str(path))
    assert h.snapshot()["recent_files"] == [str(path)]
    assert path.read_text() == "Owned recent file"
    assert str(h.widget._settings._args[0]).startswith("/"), (
        "QSettings uses an owned INI path"
    )
    h.controls["newAct"].trigger()
    assert len(h.alerts) == 1
    assert h.alerts[0].widget._settings is h.widget._settings
    h.controls["loadFile"](str(tmp_path / "missing.txt"))
    assert h.snapshot()["error"]
    h.close()


def test_batch_six_orderform_accepts_nonblocking_details_and_print_is_inert(
    official_qt,
):
    qt, _ = official_qt
    h = built("orderform", qt)
    assert h.snapshot()["letters"] == 1
    h.controls["openDialog"]()
    dialog = h.controls["active_dialog"]
    dialog.nameEdit.setText("Test Customer")
    dialog.addressEdit.setPlainText("123 Test Street")
    dialog.itemsTable.item(0, 1).setText("2")
    dialog.verify()
    assert h.snapshot()["letters"] == 2
    h.controls["printFile"]()
    box = h.controls["active_dialog"]
    assert box.printer()._data["outputFormat"] == qt.QtGui.QPrinter.PdfFormat
    assert not Path(box.printer()._data["outputFileName"]).exists(), (
        "Open/inspect must not print"
    )
    h.close()


def test_batch_six_syntax_highlighter_rules_and_multiline_comments(
    official_qt, tmp_path
):
    qt, _ = official_qt
    h = built("syntaxhighlighter", qt)
    source = tmp_path / "example.cpp"
    source.write_text("class Example { /* comment */ int number; }; // comment")
    h.controls["openFile"](str(source))
    assert "class Example" in h.controls["editor"].toPlainText()
    h.widget.highlighter.highlightBlock(source.read_text())
    assert h.widget.highlighter._extra["formats"], (
        "Highlight callbacks must apply formats"
    )
    h.widget.highlighter.highlightBlock("/* unfinished")
    assert h.widget.highlighter._data["currentBlockState"] == 1
    h.widget.highlighter.highlightBlock("finished */")
    assert h.widget.highlighter._data["currentBlockState"] == 0
    h.close()


def test_batch_six_textedit_format_save_cancel_preview_and_clipboard_disconnect(
    official_qt, tmp_path
):
    qt, _ = official_qt
    h = built("textedit", qt)
    assert h.snapshot()["file"] == "", "Default resource must never be saved over"
    assert (
        ":/images/logo32.png" in h.controls["textEdit"].document._extra["resources"]
    ), "Original HTML resource URL must resolve without qRegisterResourceData"
    h.controls["actionTextBold"].setChecked(True)
    h.controls["actionTextBold"].trigger()
    assert h.controls["textEdit"]._extra["formats"]
    path = tmp_path / "edited.html"
    h.controls["fileSaveAs"]()
    box = h.controls["active_dialog"]
    box._extra["selectedFiles"] = [str(path)]
    assert not path.exists()
    box.accept()
    assert path.exists() and h.snapshot()["file"] == str(path)
    h.controls["textEdit"].document.setModified(True)
    h.controls["fileNew"]()
    box = h.controls["active_dialog"]
    before = h.controls["textEdit"].toPlainText()
    box.emit("buttonClicked", qt.QtGui.QMessageBox.Cancel)
    assert h.controls["textEdit"].toPlainText() == before
    box.emit("buttonClicked", qt.QtGui.QMessageBox.Discard)
    assert not h.controls["textEdit"].toPlainText()
    h.controls["filePrintPreview"]()
    assert (
        h.controls["active_dialog"].printer()._data["outputFormat"]
        == qt.QtGui.QPrinter.PdfFormat
    )
    clipboard = qt.QtGui.QApplication.clipboard()
    h.close()
    assert all(not signal.callbacks for signal in clipboard._signals.values())


def test_batch_six_svg_native_image_renderers_and_imageviewer_zoom(
    official_qt, tmp_path
):
    qt, _ = official_qt
    h = built("svgviewer", qt)
    assert h.widget.view.svgItem is not None
    h.controls["backgroundAction"].setChecked(True)
    assert h.widget.view.backgroundItem.isVisible()
    h.controls["rendererGroup"].emit("triggered", h.controls["imageAction"])
    assert h.widget.view.renderer == h.widget.view.Image
    h.close()
    h = built("imageviewer", qt)
    path = tmp_path / "image.png"
    path.write_bytes(b"boundary image fixture")
    assert h.controls["loadImage"](str(path))
    h.controls["zoomInAct"].trigger()
    assert h.snapshot()["scale"] == 1.25
    h.controls["fitToWindowAct"].setChecked(True)
    h.controls["fitToWindowAct"].trigger()
    assert h.controls["scrollArea"].widgetResizable
    h.close()


def test_batch_six_separations_inversion_colour_dialog_and_brightness(official_qt):
    qt, _ = official_qt
    h = built("separations", qt)
    screen = h.widget.cyanWidget
    screen.setImage(qt.QtGui.QImage(2, 1, qt.QtGui.QImage.Format_RGB32))
    h.widget.scaledImage = screen.originalImage
    screen.invertImage()
    assert screen.inverted
    screen.setColor()
    assert h.controls["active_dialog"].isVisible()
    h.controls["active_dialog"].accept()
    h.controls["brightnessMenu"].emit("triggered", h.controls["halfBrightness"])
    assert h.snapshot()["brightness"] == 128
    h.close()


def test_batch_six_scribble_drawing_pen_dialogs_and_save_cancel(official_qt, tmp_path):
    qt, _ = official_qt
    h = built("scribble", qt)
    area = h.controls["scribbleArea"]
    area.resizeEvent(SimpleNamespace())
    area.drawLineTo(qt.QtCore.QPoint(10, 20))
    assert area.isModified()
    h.controls["penWidth"]()
    h.controls["active_dialog"].setIntValue(5)
    h.controls["active_dialog"].accept()
    assert area.penWidth() == 5
    h.controls["penColor"]()
    h.controls["active_dialog"].reject()
    h.controls["saveFile"]("png")
    h.controls["active_dialog"].reject()
    assert area.isModified(), "Cancelling save must retain dirty state"
    h.close()


@pytest.mark.parametrize(
    "name",
    [
        "analogclock",
        "shapedclock",
        "digitalclock",
        "concentriccircles",
        "painterpaths",
        "transformations",
        "charactermap",
        "tetrix",
        "wiggly",
        "scribble",
        "svgviewer",
    ],
)
def test_batch_six_virtual_paint_and_resize_paths_do_not_use_wrapper_operators(
    name, official_qt
):
    qt, _ = official_qt
    qt._strict_integer_coordinates = True
    h = built(name, qt)
    event = SimpleNamespace(rect=qt.QtCore.QRect(0, 0, 120, 120))
    if name == "concentriccircles":
        widgets = h.widget._circles
    elif name == "painterpaths":
        widgets = h.widget.renderAreas
    elif name == "transformations":
        widgets = [h.widget.originalRenderArea, *h.widget.transformedRenderAreas]
    elif name == "charactermap":
        widgets = [h.widget.characterWidget]
    elif name == "wiggly":
        widgets = [h.widget._wiggly]
    elif name == "tetrix":
        widgets = [h.widget.board]
    elif name == "scribble":
        widgets = [h.widget.scribbleArea]
    elif name == "svgviewer":
        widgets = [h.widget.view]
    else:
        widgets = [h.widget]
    for widget in widgets:
        if name == "scribble":
            widget.resizeEvent(event)
        widget.paintEvent(event)
    assert all(not painter.isActive() for painter in qt._painters), (
        "Every native painting context ends exactly once"
    )
    h.close()


def test_batch_six_native_exports_and_resource_references_match_captured_stubs():
    from tests.official_doubles import CONTRACT

    for row in records():
        if row["source_id"] not in BATCH_SIX_IDS | BATCH_EIGHT_IDS:
            continue
        path = ROOT / row["target_path"]
        tree = ast.parse(path.read_text(), feature_version=(3, 11))
        aliases = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                pieces = ast.unparse(node).split(".")
                if (
                    len(pieces) in (3, 4)
                    and pieces[0] == "qt"
                    and pieces[1] in CONTRACT
                ):
                    assert pieces[2] in CONTRACT[pieces[1]], (path, pieces)
                    if len(pieces) == 4:
                        assert pieces[3] in CONTRACT[pieces[1]][pieces[2]], (
                            path,
                            pieces,
                        )
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            ):
                value = ast.unparse(node.value).split(".")
                if len(value) == 3 and value[0] == "qt":
                    assert value[2] in CONTRACT[value[1]], (path, value)
                    aliases[node.targets[0].id] = CONTRACT[value[1]][value[2]]
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
            ):
                assert node.attr in aliases[node.value.id], (path, ast.unparse(node))
            if (
                isinstance(node, ast.Call)
                and ast.unparse(node.func) == "demo.asset"
                and isinstance(node.args[0], ast.Constant)
            ):
                asset = (
                    path.parent
                    / "assets"
                    / row["source_id"]
                    / node.args[0].value.removeprefix(":/")
                )
                assert asset.exists(), (path, asset)
        assert not any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr in ("exec", "exec_", "toInt")
            for n in ast.walk(tree)
        ), "No blocking dialog loops or QString-only conversions"


def test_batch_six_python_callback_references_release_before_native_deletion(
    official_qt,
):
    qt, _ = official_qt
    for name, child, callbacks in (
        ("charactermap", "characterWidget", ["characterSelected"]),
        ("tetrix", "board", ["scoreChanged", "levelChanged", "linesRemovedChanged"]),
        ("separations", "cyanWidget", ["imageChanged"]),
    ):
        h = built(name, qt)
        obj = getattr(h.widget, child)
        assert all(callable(getattr(obj, callback)) for callback in callbacks)
        h.close()
        assert all(getattr(obj, callback) is None for callback in callbacks), (
            "Release private Python callbacks before native children"
        )


def test_batch_seven_native_exports_and_no_external_network_shortcuts():
    """All explicit Qt aliases resolve to the captured native host surface."""
    from tests.official_doubles import CONTRACT

    for row in records():
        if row["source_id"] not in BATCH_SEVEN_IDS:
            continue
        path = ROOT / row["target_path"]
        tree = ast.parse(path.read_text(), feature_version=(3, 11))
        aliases = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                parts = ast.unparse(node).split(".")
                if len(parts) in (3, 4) and parts[0] == "qt" and parts[1] in CONTRACT:
                    assert parts[2] in CONTRACT[parts[1]], (path, parts)
                    if len(parts) == 4:
                        assert parts[3] in CONTRACT[parts[1]][parts[2]], (path, parts)
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            ):
                parts = ast.unparse(node.value).split(".")
                if (
                    isinstance(node.value, ast.Attribute)
                    and len(parts) == 3
                    and parts[0] == "qt"
                    and parts[1] in CONTRACT
                ):
                    aliases[node.targets[0].id] = CONTRACT[parts[1]][parts[2]]
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
            ):
                assert node.attr in aliases[node.value.id], (path, ast.unparse(node))
            if isinstance(node, ast.Call):
                fn = ast.unparse(node.func)
                assert fn not in {
                    "QApplication",
                    "sys.exit",
                    "QDesktopServices.openUrl",
                    "QTimer.singleShot",
                }, (path, fn)
                assert not fn.endswith(
                    ("exec_", ".waitForConnected", ".waitForReadyRead")
                ), (path, fn)


BATCH_SEVEN_IMPLEMENTED = [
    r
    for r in records()
    if r["source_id"] in BATCH_SEVEN_IDS and r["implementation"] == "implemented"
]


@pytest.mark.parametrize("row", BATCH_SEVEN_IMPLEMENTED, ids=lambda r: r["name"])
def test_batch_seven_inspection_is_inert_and_failure_rolls_back(
    row, official_qt, monkeypatch
):
    import threading

    from fontlab_python_examples.official import Demo

    qt, owners = official_qt
    before = {t.ident for t in threading.enumerate() if t.name == "official-worker"}
    h = load_record(row).build(qt)
    initial = json.dumps(h.snapshot(), sort_keys=True)
    connections = len(h.connections)
    assert json.dumps(h.snapshot(), sort_keys=True) == initial, (
        "Inspection must not drive UI/network state"
    )
    assert len(h.connections) == connections
    h.close()
    assert {
        t.ident for t in threading.enumerate() if t.name == "official-worker"
    } == before, "Close joins owned workers"
    count = len(owners)

    def fail(*args, **kwargs):
        raise RuntimeError("Owned finish failure")

    monkeypatch.setattr(Demo, "finish", fail)
    with pytest.raises(RuntimeError, match="Owned finish failure"):
        load_record(row).build(qt)
    assert all(o.closed for o in owners[count:]), (
        "Partial builds must close every owner"
    )
    assert {
        t.ident for t in threading.enumerate() if t.name == "official-worker"
    } == before


def spin_until(qt, h, predicate, timeout=3):
    import time

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        qt._pump_network()
        for name, obj in list(h.controls.items()):
            if getattr(obj, "_qt_name", None) == "QTimer" and obj.isActive():
                obj.emit("timeout")
        if predicate():
            return
        time.sleep(0.005)
    pytest.fail("Owned loopback/worker delivery did not complete")


@pytest.mark.parametrize(
    "name",
    [
        "fortuneclient",
        "blockingfortuneclient",
        "fortuneserver",
        "threadedfortuneserver",
    ],
)
def test_batch_seven_fortune_roundtrip_worker_shutdown_and_foreign_peer_rejection(
    name, official_qt
):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        c = h.controls
        action = c.get("requestNewFortune", c.get("probe"))
        action()
        spin_until(qt, h, lambda: bool(h.snapshot()["fortune"]))
        assert h.snapshot()["fortune"] in {
            "You've been leading a dog's life. Stay off the furniture.",
            "You've got to think about tomorrow.",
            "You will be surprised by a loud noise.",
            "You will feel hungry again in another hour.",
            "You might have mail.",
            "You cannot kill time without injuring eternity.",
            "Computers are not intelligent. They only think they are.",
        }
        if "portLineEdit" in c:
            c["portLineEdit"].setText("1")
            action()
            assert "owned" in h.snapshot()["error"]
            assert h.controls["getFortuneButton"].enabled
    finally:
        h.close()


@pytest.mark.parametrize("name", ["broadcastsender", "broadcastreceiver"])
def test_batch_seven_udp_roundtrip_stops_timers_and_releases_port(name, official_qt):
    import socket

    qt, _ = official_qt
    h = built(name, qt)
    address = (h.snapshot()["host"], h.snapshot()["port"])
    h.controls["sendSample"]()
    spin_until(qt, h, lambda: bool(h.snapshot()["received"]))
    assert h.snapshot()["received"] == ["Broadcast message 1"]
    timers = [h.controls["timer"], h.controls["pollTimer"]]
    h.close()
    assert not any(t.isActive() for t in timers)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(address)


def test_batch_seven_http_download_cancel_missing_and_foreign_url(official_qt):
    qt, _ = official_qt
    h = built("http", qt)
    try:
        c = h.controls
        c["urlLineEdit"].setText("https://example.invalid/file")
        c["downloadButton"].click()
        assert "owned" in h.snapshot()["error"] and not h.snapshot()["downloading"]
        endpoint = h.snapshot()["endpoint"]
        url = f"http://127.0.0.1:{endpoint['port']}"
        c["urlLineEdit"].setText(url + "/sample.txt")
        c["downloadButton"].click()
        spin_until(qt, h, lambda: not h.snapshot()["downloading"])
        path = Path(h.snapshot()["output_path"])
        assert path.read_bytes() == b"Owned FontLab PythonQt HTTP download.\n"
        assert h.snapshot()["bytes_read"] == len(path.read_bytes())
        c["downloadButton"].click()
        c["cancelDownload"]()
        qt._pump_network()
        assert h.snapshot()["aborted"] and not path.exists()
        c["urlLineEdit"].setText(url + "/missing")
        c["downloadButton"].click()
        spin_until(qt, h, lambda: not h.snapshot()["downloading"])
        assert h.snapshot()["error"] and not path.exists()
    finally:
        h.close()
    assert not path.parent.exists(), "Owned HTTP output directory is released"


def test_batch_seven_loopback_transfer_and_close_while_active(official_qt):
    qt, _ = official_qt
    h = built("loopback", qt)
    try:
        h.widget.TotalBytes = 128 * 1024
        h.controls["startButton"].click()
        spin_until(qt, h, lambda: h.snapshot()["bytes_received"] == h.widget.TotalBytes)
        assert h.snapshot()["bytes_written"] == h.widget.TotalBytes
        assert h.controls["startButton"].enabled
        h.widget.TotalBytes = 50 * 1024 * 1024
        h.controls["startButton"].click()
    finally:
        h.close()


@pytest.mark.parametrize("name", ["simplewidgetmapper", "combowidgetmapper"])
def test_batch_seven_mapper_navigation_matches_original_data(name, official_qt):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        c = h.controls
        assert c["nameEdit"].text == "Alice"
        assert not c["previousButton"].enabled
        c["nextButton"].click()
        assert c["nameEdit"].text == "Bob" and h.snapshot()["current_index"] == 1
        c["mapper"].toLast()
        assert c["nameEdit"].text == "Emma" and not c["nextButton"].enabled
        c["previousButton"].click()
        assert c["nameEdit"].text == "Donald"
        if name == "simplewidgetmapper":
            assert c["ageSpinBox"].value == 19
        else:
            assert c["typeComboBox"].currentIndex == 0
    finally:
        h.close()


@pytest.mark.parametrize(
    "name,pattern,expected",
    [("basicsortfiltermodel", "Andy", 2), ("customsortfiltermodel", "Sports", 3)],
)
def test_batch_seven_sort_filter_controls_and_dates(
    name, pattern, expected, official_qt
):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        assert h.snapshot()["source_rows"] == 10
        h.controls["filterPatternLineEdit"].setText(pattern)
        assert h.snapshot()["proxy_rows"] == expected
        h.controls["filterPatternLineEdit"].setText("nothing-matches")
        assert h.snapshot()["proxy_rows"] == 0
        h.controls["filterPatternLineEdit"].setText("")
        assert h.snapshot()["proxy_rows"] == 10
    finally:
        h.close()


def test_batch_seven_fetchmore_exact_insertion_and_empty_directory(
    official_qt, tmp_path, monkeypatch
):
    qt, _ = official_qt
    h = built("fetchmore", qt)
    try:
        model = h.controls["model"]
        while h.controls["fixtureTimer"].isActive():
            h.controls["fixtureTimer"].emit("timeout")
        h.controls["scanTimer"].emit("timeout")
        insertions = []
        monkeypatch.setattr(
            type(model),
            "beginInsertRows",
            lambda self, parent, start, end: insertions.append((start, end)),
        )
        h.controls["fetchMore"]()
        assert model.rowCount() == 100 and insertions == [(0, 99)]
        while model.canFetchMore(qt.QtCore.QModelIndex()):
            h.controls["fetchMore"]()
        assert model.rowCount() == 207 and insertions[-1] == (200, 206)
        h.controls["fetchMore"]()
        assert len(insertions) == 3
        h.controls["lineEdit"].setText(str(tmp_path))
        h.controls["scanTimer"].emit("timeout")
        h.controls["fetchMore"]()
        assert model.rowCount() == 2
        assert not model.canFetchMore(qt.QtCore.QModelIndex())
    finally:
        h.close()


def test_batch_seven_dom_preserves_node_types_and_rejects_bad_xml(
    official_qt, tmp_path
):
    qt, _ = official_qt
    h = built("simpledommodel", qt)
    try:
        model = h.controls["model"]
        root = model.index(0, 0)
        assert model.data(root) == "root"
        assert model.data(model.index(0, 1)) == 'label="owned"'
        assert model.rowCount(root) == 3
        comment = model.index(0, 0, root)
        instruction = model.index(1, 0, root)
        child = model.index(2, 0, root)
        assert model.data(comment) == "#comment" and model.data(instruction) == "demo"
        assert (
            model.data(child) == "child"
            and model.parent(child).internalId() == root.internalId()
        )
        assert isinstance(root.internalId(), int)
        bad = tmp_path / "bad.xml"
        bad.write_text("<broken>")
        h.controls["loadXml"](bad)
        assert h.snapshot()["error"] and h.controls["model"] is model
        good = tmp_path / "good.xml"
        good.write_text('<new attribute="value"><a/></new>')
        h.controls["loadXml"](good)
        assert h.snapshot()["root_names"] == ["new"] and not h.snapshot()["error"]
    finally:
        h.close()


def test_batch_seven_spreadsheet_formula_recursion_cycle_division_and_async_dialog(
    official_qt,
):
    qt, _ = official_qt
    h = built("spreadsheet", qt)
    try:
        c = h.controls
        assert h.snapshot()["total"] == 21883
        c["putFormula"]("C2", "200")
        assert h.snapshot()["total"] == 21933
        c["putFormula"]("F2", "= F2")
        assert c["table"].item(1, 5).display() is None
        c["putFormula"]("F2", "/ C2 C1")
        assert c["table"].item(1, 5).display() == "nan"
        c["cell_addAction"].trigger()
        dialog = h.controls["active_dialog"]
        dialog.accept()
        assert "+ " in h.snapshot()["formulas"][2][2]
        with pytest.raises(ValueError, match="Invalid cell"):
            c["putFormula"]("Z100", "bad")
        c["printAction"].trigger()
        preview = h.controls["active_dialog"]
        assert preview._qt_name == "QPrintPreviewDialog"
        printer = preview.printer()
        assert printer._data["outputFormat"] == qt.QtGui.QPrinter.PdfFormat
        assert Path(printer._data["outputFileName"]).name == "spreadsheet.pdf"
        preview.emit("paintRequested", printer)
    finally:
        h.close()


def test_batch_seven_spinbox_delegate_commit_and_geometry(official_qt):
    qt, _ = official_qt
    h = built("spinboxdelegate", qt)
    try:
        c = h.controls
        index = c["model"].index(2, 1)
        option = SimpleNamespace(rect=qt.QtCore.QRect(2, 3, 20, 30))
        editor = c["delegate"].createEditor(h.widget, option, index)
        c["delegate"].setEditorData(editor, index)
        assert editor.value == 6 and editor.minimum == 0 and editor.maximum == 100
        editor.setValue(42)
        c["delegate"].setModelData(editor, c["model"], index)
        assert h.snapshot()["rows"][2][1] == 42
        c["delegate"].updateEditorGeometry(editor, option, index)
        assert editor._position == [2, 3, 20, 30]
    finally:
        h.close()


def test_batch_seven_storage_bytes_tooltips_and_invalid_indices(official_qt):
    qt, _ = official_qt
    h = built("storageview", qt)
    try:
        model = h.controls["model"]
        h.controls["loadTimer"].emit("timeout")
        assert model.data(qt.QtCore.QModelIndex(), qt.QtCore.Qt.DisplayRole) is None
        assert "Device: fixture" in model.data(
            model.index(0, 0), qt.QtCore.Qt.ToolTipRole
        )
        assert model.data(model.index(0, 4), qt.QtCore.Qt.DisplayRole) == "4.00 kB"
        assert model.rowCount(model.index(0, 0)) == 0
    finally:
        h.close()


def test_batch_seven_delayed_png_encodes_only_on_first_data_request(
    official_qt, monkeypatch
):
    from fontlab_python_examples.official import Demo

    qt, _ = official_qt
    requests = []

    def drag(demo, source, *args):
        mime = demo.handle.widget.mimeData
        assert mime.formats() == ["image/png"]
        assert demo.handle.widget.encodingCount == 0
        value = mime.retrieveData("image/png", 0)
        requests.append(value.data())
        mime.retrieveData("image/png", 0)
        assert demo.handle.widget.encodingCount == 1
        assert mime.formats() == ["image/png"]

    monkeypatch.setattr(Demo, "drag", drag)
    h = built("delayedencoding", qt)
    try:
        assert h.snapshot()["encoding_count"] == 0
        h.controls["dragIcon"].emit("pressed")
        assert requests == [b"owned-image-double"]
        assert h.snapshot()["encoding_count"] == 1 and h.widget.mimeData is None
        assert all(not p.isActive() for p in qt._painters)
    finally:
        h.close()


def test_batch_seven_drop_formats_text_and_raw_bytes_then_clear(official_qt):
    qt, _ = official_qt
    h = built("dropsite", qt)
    try:
        mime = qt.QtCore.QMimeData()
        mime.setText("hello")
        mime.setData("text/plain", qt.QtCore.QByteArray(b"hello"))
        mime.setData("application/octet-stream", qt.QtCore.QByteArray(b"\x00\xff"))
        event = SimpleNamespace(
            mimeData=lambda: mime, acceptProposedAction=lambda: None
        )
        h.controls["dropArea"].dragEnterEvent(event)
        h.controls["dropArea"].dropEvent(event)
        assert h.snapshot()["drop_text"] == "hello"
        assert h.snapshot()["formats"] == [
            ["text/plain", "hello"],
            ["application/octet-stream", "00 FF"],
        ]
        h.controls["clearButton"].emit("pressed")
        assert h.snapshot()["formats"] == []
    finally:
        h.close()


def test_batch_seven_color_factory_is_local_and_commits_qcolor(official_qt):
    qt, _ = official_qt
    h = built("coloreditorfactory", qt)
    try:
        delegate = h.controls["delegate"]
        model = qt.QtGui.QStandardItemModel(1, 2, h.widget)
        index = model.index(0, 1)
        model.setData(index, qt.QtGui.QColor("aliceblue"))
        editor = delegate.createEditor(h.widget, None, index)
        delegate.setEditorData(editor, index)
        assert editor.currentText == "aliceblue"
        editor.setColor(qt.QtGui.QColor("aquamarine"))
        delegate.setModelData(editor, model, index)
        assert model.data(index) == qt.QtGui.QColor("aquamarine")
        assert delegate.creator.valuePropertyName().data() == b"currentIndex"
        assert (
            "setDefaultFactory"
            not in (
                ROOT
                / next(
                    r["target_path"]
                    for r in records()
                    if r["name"] == "Official coloreditorfactory"
                )
            ).read_text()
        )
    finally:
        h.close()


def test_batch_seven_star_paint_hit_testing_and_integer_model_commit(official_qt):
    qt, _ = official_qt
    h = built("stardelegate", qt)
    try:
        assert h.snapshot()["ratings"] == [5, 4, 3, 5]
        delegate = h.controls["delegate"]
        model = qt.QtGui.QStandardItemModel(1, 4, h.widget)
        index = model.index(0, 3)
        model.setData(index, 5)
        editor = delegate.createEditor(h.widget, None, index)
        delegate.setEditorData(editor, index)
        assert editor.starAtPosition(50) == 3 and editor.starAtPosition(200) == -1
        editor.mouseMoveEvent(SimpleNamespace(x=lambda: 50))
        editor.paintEvent(None)
        delegate.setModelData(editor, model, index)
        assert model.data(index) == 3 and type(model.data(index)) is int
        assert all(not p.isActive() for p in qt._painters)
    finally:
        h.close()


def test_batch_seven_pixelator_size_delegate_and_owned_print_cancel(official_qt):
    qt, _ = official_qt
    h = built("pixelator", qt)
    try:
        c = h.controls
        c["pixelSizeSpinBox"].setValue(20)
        assert h.snapshot()["pixel_size"] == 20
        c["printAction"].trigger()
        if h.controls["active_dialog"]._qt_name == "QMessageBox":
            h.controls["active_dialog"].emit("buttonClicked", qt.QtGui.QMessageBox.Yes)
        h.controls["active_dialog"].accept()
        timer = h.controls["printTimer"]
        assert timer.isActive()
        h.controls["progress"].emit("canceled")
        assert not timer.isActive() and all(not p.isActive() for p in qt._painters)
    finally:
        h.close()


def test_batch_seven_graphics_topology_controls_and_explicit_timer_stop(official_qt):
    qt, _ = official_qt
    anchor = built("anchorlayout", qt)
    try:
        assert anchor.snapshot()["labels"] == list("ABCDEFG")
        assert all(name in anchor.controls for name in "ABCDEFG")
        assert len(anchor.snapshot()["geometry"]) == 7
    finally:
        anchor.close()
    elastic = built("elasticnodes", qt)
    try:
        assert (
            elastic.snapshot()["node_count"] == 9
            and elastic.snapshot()["edge_count"] == 12
        )
        elastic.controls["step"]()
        elastic.controls["scaleView"](1.2)
        elastic.widget.stopMotion()
        assert not elastic.snapshot()["timer_active"]
    finally:
        elastic.close()


def test_batch_seven_pad_native_form_state_cleanup_and_no_custom_meta_property(
    official_qt,
):
    qt, _ = official_qt
    h = built("padnavigator", qt)
    machine = h.controls["stateMachine"]
    try:
        assert h.snapshot()["icon_count"] == 9 and machine.isRunning()
        assert "hostName" in h.controls
        h.controls["pad"].setFill(True)
        assert h.snapshot()["fill"]
        assert not any(
            b"fill" in getattr(obj, "_args", ()) for obj in h.controls.values()
        )
    finally:
        h.close()
    assert not machine.isRunning()


def test_batch_seven_lightmaps_owned_tiles_pan_city_night_zoom_and_drag(official_qt):
    qt, _ = official_qt
    h = built("lightmaps", qt)
    try:
        map_ = h.controls["map"]
        h.controls["berlinAction"].trigger()
        spin_until(qt, h, lambda: h.snapshot()["tile_count"] > 0)
        assert h.snapshot()["latitude"] == pytest.approx(52.52959)
        before = h.snapshot()["longitude"]
        h.controls["pan"](qt.QtCore.QPoint(20, 0))
        assert h.snapshot()["longitude"] != before
        h.controls["nightModeAction"].trigger()
        assert h.snapshot()["night_mode"]
        h.controls["activateZoom"]()
        assert h.snapshot()["zoomed"]
        map_.paintEvent(SimpleNamespace(rect=lambda: qt.QtCore.QRect(0, 0, 400, 300)))
        map_.mouseReleaseEvent(None)
        map_.pressed = map_.snapped = False
        map_.mouseMoveEvent(
            SimpleNamespace(
                buttons=lambda: qt.QtCore.Qt.LeftButton,
                pos=lambda: qt.QtCore.QPoint(30, 40),
            )
        )
        assert all(not p.isActive() for p in qt._painters)
    finally:
        h.close()


def test_batch_seven_dirview_owned_fixture_is_read_only_and_removed(official_qt):
    qt, _ = official_qt
    h = built("dirview", qt)
    root = Path(h.snapshot()["root_path"])
    h.controls["loadTimer"].emit("timeout")
    assert h.snapshot()["read_only"] and h.snapshot()["column_count"] == 4
    assert (root / "example.txt").is_file()
    h.close()
    assert not root.exists()


@pytest.mark.parametrize("text", ["", "Fortune", "Zażółć 🐈"])
def test_batch_seven_fortune_wire_format_is_qt4_and_fragment_safe(text):
    import struct
    import threading

    from fontlab_python_examples.official import fortune_packet, receive_fortune

    packet = fortune_packet(text)
    assert packet == struct.pack(
        ">HI", len(text.encode("utf-16-be")) + 4, len(text.encode("utf-16-be"))
    ) + text.encode("utf-16-be")
    chunks = list(packet)
    connection = SimpleNamespace(
        recv=lambda n: bytes([chunks.pop(0)]) if chunks else b""
    )
    assert receive_fortune(connection, threading.Event()) == text


@pytest.mark.parametrize("packet", [b"", b"\x00\x08\x00", b"\x00\x04\x00\x00\x00\x04"])
def test_batch_seven_fortune_wire_rejects_truncated_frames(packet):
    import threading

    from fontlab_python_examples.official import receive_fortune

    chunks = bytearray(packet)

    def receive(n):
        result = bytes(chunks[:n])
        del chunks[:n]
        return result

    with pytest.raises(ValueError):
        receive_fortune(SimpleNamespace(recv=receive), threading.Event())


@pytest.mark.parametrize("count", [0, 11])
def test_storageview_launch_defers_native_tuple_scan_and_inspect_never_scans(
    official_qt, monkeypatch, count
):
    qt, _ = official_qt
    volumes = tuple(qt.QtCore.QStorageInfo(f"/volume-{i}") for i in range(count))
    calls = []

    def mounted_volumes():
        calls.append(True)
        return volumes

    monkeypatch.setattr(qt.QtCore.QStorageInfo, "mountedVolumes", mounted_volumes)
    h = built("storageview", qt)
    try:
        model = h.controls["model"]
        timer = h.controls["loadTimer"]
        assert model.volumes == [] and model.rowCount() == 0
        assert timer.isActive() and not calls, "Launch must not enumerate volumes"
        for _ in range(3):
            assert h.snapshot()["loading"] and h.snapshot()["row_count"] == 0
        assert not calls, "Inspection must never enumerate volumes"
        timer.emit("timeout")
        assert calls == [True] and model.volumes == list(volumes)
        assert h.snapshot()["row_count"] == count and not h.snapshot()["loading"]
        assert not timer.isActive(), "Owned single-shot stops before population"
        for _ in range(3):
            h.snapshot()
        assert calls == [True], "Completed inspection uses cached volume state"
    finally:
        h.close()


def test_storageview_scan_failure_finishes_loading_without_leaking_timer(
    official_qt, monkeypatch
):
    qt, _ = official_qt

    def unavailable():
        raise OSError("Volume enumeration failed")

    monkeypatch.setattr(qt.QtCore.QStorageInfo, "mountedVolumes", unavailable)
    h = built("storageview", qt)
    try:
        timer = h.controls["loadTimer"]
        timer.emit("timeout")
        assert not h.snapshot()["loading"] and h.snapshot()["row_count"] == 0
        assert "Volume enumeration failed" in h.snapshot()["error"]
        assert not timer.isActive()
    finally:
        h.close()


@pytest.mark.parametrize(
    "name,timers",
    [
        ("storageview", ["loadTimer"]),
        ("dirview", ["loadTimer"]),
        ("fetchmore", ["scanTimer", "fixtureTimer"]),
    ],
)
def test_deferred_startup_close_before_tick_stops_disconnects_and_guards_callbacks(
    name, timers, official_qt, monkeypatch
):
    qt, _ = official_qt
    h = built(name, qt)
    retained = [h.controls[key] for key in timers]
    callbacks = [slot for obj, _signature, slot in h.connections if obj in retained]
    assert h.snapshot()["loading"], "Launch exposes pending startup work"
    h.close()
    assert all(not timer.isActive() for timer in retained)
    assert all(
        not signal.callbacks for timer in retained for signal in timer._signals.values()
    )

    def stale_native_access(*args):
        pytest.fail("Stale callback accessed a destroyed native timer")

    monkeypatch.setattr(qt.QtCore.QTimer, "stop", stale_native_access)
    for callback in callbacks:
        callback()


def test_fetchmore_launch_defers_fixture_writes_and_directory_scan(
    official_qt, monkeypatch
):
    qt, _ = official_qt
    writes, scans = [], []
    original_write = Path.write_text

    def write(path, *args, **kwargs):
        writes.append(path)
        return original_write(path, *args, **kwargs)

    def entry_list(directory):
        scans.append(True)
        return directory._invoke("entryList")

    monkeypatch.setattr(Path, "write_text", write)
    monkeypatch.setattr(qt.QtCore.QDir, "entryList", entry_list)
    h = built("fetchmore", qt)
    try:
        assert not writes and not scans, "Build must not generate/list sample files"
        model = h.controls["model"]
        assert model.fileList == [] and h.snapshot()["loading"]
        fixture = h.controls["fixtureTimer"]
        fixture.emit("timeout")
        assert 0 < len(writes) <= 32 and not scans
        while fixture.isActive():
            fixture.emit("timeout")
        assert len(writes) == 205 and not scans
        h.controls["scanTimer"].emit("timeout")
        assert len(scans) == 1 and not h.snapshot()["loading"]
        assert len(model.fileList) == 207
    finally:
        h.close()


def test_dirview_launch_defers_filesystem_root_and_sample_creation(
    official_qt, monkeypatch
):
    qt, _ = official_qt
    calls = []

    def set_root(model, path):
        calls.append(path)
        return model._invoke("setRootPath", path)

    monkeypatch.setattr(qt.QtGui.QFileSystemModel, "setRootPath", set_root)
    h = built("dirview", qt)
    try:
        root = Path(h.snapshot()["root_path"])
        assert not calls and not (root / "example.txt").exists()
        h.controls["loadTimer"].emit("timeout")
        assert calls == [str(root)] and (root / "example.txt").exists()
        assert not h.snapshot()["loading"]
    finally:
        h.close()


def batch_eight(id, qt):
    return load_record(next(r for r in records() if r["source_id"] == id)).build(qt)


def test_batch_eight_accounts_for_every_remaining_official_entrypoint():
    rows = [r for r in records() if r["source_id"] in BATCH_EIGHT_IDS]
    assert len(rows) == 74
    assert sum(r["implementation"] == "implemented" for r in rows) == 16
    assert sum(r["implementation"] == "blocked" for r in rows) == 58
    catalog = json.loads((ROOT / "catalog/sources.json").read_text())["files"]
    candidates = {
        r["id"]
        for r in catalog
        if r["path"].startswith("src/pyqt-official/")
        and r.get("python", {}).get("role") == "entrypoint"
    }
    assert candidates == IDS, (
        "No official entrypoint may disappear from the denominator"
    )


@pytest.mark.parametrize(
    "row",
    [
        r
        for r in records()
        if r["source_id"] in BATCH_EIGHT_IDS and r["implementation"] == "blocked"
    ],
    ids=lambda r: r["source_id"],
)
def test_batch_eight_blockers_fail_before_accessing_host(row, monkeypatch):
    from fontlab_python_examples import launcher

    class UntouchedHost:
        def __getattr__(self, key):
            pytest.fail("Blocked build touched host: " + key)

    with pytest.raises(NotImplementedError) as result:
        load_record(row).build(UntouchedHost())
    assert str(result.value) == row["blocked_reason"]

    def forbidden():
        pytest.fail("Blocked launch tried to acquire a FontLab runtime")

    monkeypatch.setattr(launcher, "_host", forbidden)
    with pytest.raises(NotImplementedError, match="not ported"):
        launcher.launch(row["source_id"])


def test_batch_eight_calculator_and_pyuic_declared_connections_are_tracked(official_qt):
    qt, _ = official_qt
    h = batch_eight("27bf65f8b059fd96", qt)
    try:
        h.controls["inputSpinBox1"].setValue(7)
        h.controls["inputSpinBox2"].setValue(8)
        assert h.snapshot()["sum"] == "15"
        assert len(h.connections) == 2
        h.controls["inputSpinBox1"].setValue(0)
        assert h.snapshot()["sum"] == "8"
    finally:
        h.close()
    for id, adds in (
        ("5a8e48d2a1396cea", True),
        ("b7db02f540cc7559", False),
        ("b9660f4ee653ca01", True),
    ):
        h = batch_eight(id, qt)
        try:
            h.controls["button1"].click()
            h.controls["button1"].click()
            assert h.snapshot()["items"] == (
                ["This", "is", "a", "demo"] * 2 if adds else []
            )
            h.controls["button2"].click()
            assert h.snapshot()["items"] == []
            assert len(h.connections) == (3 if adds else 2)
            h.controls["okButton"].click()
            assert not h.widget.isVisible()
        finally:
            h.close()


def test_batch_eight_clock_and_counter_setters_emit_inspected_values(official_qt):
    qt, _ = official_qt
    h = batch_eight("4d24cd77c74a8801", qt)
    try:
        h.controls["setTimeZone"](-3)
        assert h.snapshot()["time_zone"] == -3
        assert h.snapshot()["notifications"]["timeZoneChanged"] == [-3]
        h.controls["timer"].emit("timeout")
        assert isinstance(h.snapshot()["notifications"]["timeChanged"][0], str)
        h.controls["resetTimeZone"]()
        assert h.snapshot()["time_zone"] == 0
    finally:
        h.close()
    h = batch_eight("1321540b04f33117", qt)
    try:
        assert h.snapshot()["value"] == 1, "Original 123 request exceeds default range"
        h.controls["setMaximum"](200)
        h.controls["setOffset"](5)
        h.controls["setValue"](123)
        assert h.snapshot()["notifications"]["valueChanged(int)"] == [128]
        assert h.snapshot()["notifications"]["valueChanged(str)"] == ["128"]
        h.controls["stepDown"]()
        assert h.snapshot()["value"] == 122
        h.controls["setMinimum"](150)
        assert h.snapshot()["value"] == 150
        h.controls["setValue"](-100)
        assert h.snapshot()["value"] == 150
        h.controls["setMaximum"](10)
        assert h.snapshot()["minimum"] == h.snapshot()["value"] == 10
    finally:
        h.close()


def test_batch_eight_polygon_and_viewer_properties(official_qt):
    qt, _ = official_qt
    h = batch_eight("773db5c24ae98ffb", qt)
    try:
        h.controls["setNumberOfSides"](0)
        h.controls["setAngle"](400)
        h.controls["setInnerRadius"](12)
        h.controls["setOuterRadius"](80)
        h.controls["setInnerColor"](qt.QtGui.QColor(1, 2, 3))
        h.controls["setOuterColor"](qt.QtGui.QColor(3, 2, 1))
        s = h.snapshot()
        assert (s["sides"], s["angle"], s["inner_radius"], s["outer_radius"]) == (
            3,
            360,
            12,
            80,
        )
        assert h.widget.getInnerColor().red() == 1, "Repair original max(3, QColor) bug"
    finally:
        h.close()
    h = batch_eight("bcfa5de0140286d5", qt)
    try:
        h.controls["setZoom"](3)
        h.controls["setZoom"](-2)
        assert h.snapshot()["zoom"] == -2
        assert h.snapshot()["notifications"]["zoomChanged"] == [-2]
        h.controls["resetZoom"]()
        h.controls["setAuthor"]("Example Author")
        assert h.snapshot()["author"] == "Example Author"
        h.controls["resetAuthor"]()
        assert h.snapshot()["author"] == "David Boddie"
        assert "PyQt Demonstration Widget" in h.snapshot()["text"]
    finally:
        h.close()


def test_batch_eight_multipage_select_rename_insert_remove(official_qt):
    qt, _ = official_qt
    h = batch_eight("de4979a99c6d0bed", qt)
    try:
        assert h.snapshot()["page_titles"] == ["Page 1", "Page 2"]
        h.controls["comboBox"].emit("activated", 1)
        h.controls["setPageTitle"]("Second")
        assert h.snapshot()["current_page"] == 1
        assert h.snapshot()["page_title"] == "Second"
        page = qt.QtGui.QLabel("Inserted", h.widget)
        h.controls["insertPage"](0, page)
        assert h.snapshot()["page_count"] == 3
        h.controls["removePage"](0)
        assert h.snapshot()["page_count"] == 2
    finally:
        h.close()


def test_batch_eight_date_calendar_options_and_native_protected_handler(official_qt):
    qt, _ = official_qt
    h = batch_eight("7ba49e67588b1329", qt)
    try:
        for name in ("dateEdit", "dateTimeEdit"):
            editor = h.controls[name]
            editor.setGridVisible(True)
            editor.setFirstDayOfWeek(qt.QtCore.Qt.Sunday)
            editor.mousePressEvent(SimpleNamespace())
            assert editor._calendar is editor.calendarWidget()
            assert editor._calendar.gridVisible
            editor.resetGridVisible()
            editor.resetFirstDayOfWeek()
            assert not editor._calendar.gridVisible
            editor.setNavigationBarVisible(False)
            editor.resetNavigationBarVisible()
            editor.setHorizontalHeaderFormat(qt.QtGui.QCalendarWidget.LongDayNames)
            editor.resetHorizontalHeaderFormat()
            editor.setVerticalHeaderFormat(qt.QtGui.QCalendarWidget.NoVerticalHeader)
            editor.resetVerticalHeaderFormat()
        assert h.snapshot()["calendar_popup"]
    finally:
        h.close()


def test_batch_eight_console_explicit_eval_history_and_errors(official_qt):
    qt, _ = official_qt
    h = batch_eight("5125860585e98b3a", qt)
    try:
        assert h.snapshot()["history"] == []
        h.widget.setText("6 * 7")
        h.widget.emit("returnPressed")
        assert h.snapshot()["output"] == "42"
        assert h.snapshot()["history"] == ["6 * 7"]
        h.widget.setText("1 / 0")
        h.controls["execute"]()
        assert "division by zero" in h.snapshot()["evaluation_error"]
        assert h.snapshot()["history"] == ["6 * 7"]
        for key in (qt.QtCore.Qt.Key_Up, qt.QtCore.Qt.Key_Down):
            h.widget.keyReleaseEvent(
                SimpleNamespace(
                    type=lambda: qt.QtCore.QEvent.KeyRelease,
                    key=lambda: key,
                    accept=lambda: None,
                )
            )
        assert h.snapshot()["expression"] == ""
    finally:
        h.close()


def test_batch_eight_bubbles_input_motion_and_timers(official_qt):
    qt, _ = official_qt
    h = batch_eight("9941e3c752b3a3b7", qt)
    try:
        h.controls["setBubbles"](3)
        old = h.snapshot()["positions"]
        h.controls["animation_timer"].emit("timeout")
        assert all(
            new[1] < before[1] for new, before in zip(h.snapshot()["positions"], old)
        )
        event = SimpleNamespace(
            button=lambda: qt.QtCore.Qt.LeftButton,
            pos=lambda: qt.QtCore.QPoint(80, 90),
            accept=lambda: None,
        )
        h.widget.mousePressEvent(event)
        assert h.snapshot()["new_bubble"]
        h.controls["bubbleTimer"].emit("timeout")
        h.widget.mouseMoveEvent(event)
        h.widget.mouseReleaseEvent(event)
        assert h.snapshot()["bubble_count"] == 4
        h.controls["setBubbles"](-3)
        assert h.snapshot()["bubble_count"] == 0
        h.controls["stop"]()
        assert not h.controls["animation_timer"]._active
        h.controls["start"]()
        assert h.controls["animation_timer"]._active
    finally:
        h.close()


@pytest.mark.parametrize(
    "id",
    [
        "4d24cd77c74a8801",
        "9941e3c752b3a3b7",
        "1321540b04f33117",
        "773db5c24ae98ffb",
        "c82d1af7d1a7b0cf",
    ],
)
def test_batch_eight_painting_ends_contexts_without_wrapper_arithmetic(id, official_qt):
    qt, _ = official_qt
    qt._strict_integer_coordinates = True
    h = batch_eight(id, qt)
    try:
        if id == "9941e3c752b3a3b7":
            h.controls["setBubbles"](2)
        if id == "c82d1af7d1a7b0cf":
            h.controls["timer"].emit("timeout")
            assert (
                h.snapshot()["native_elapsed"] == h.snapshot()["opengl_elapsed"] == 50
            )
            canvases = [h.controls["native"], h.controls["openGL"]]
        else:
            canvases = [h.widget]
        event = SimpleNamespace(rect=qt.QtCore.QRect(0, 0, 200, 200))
        for canvas in canvases:
            canvas.paintEvent(event)
        assert qt._painters and all(not painter.isActive() for painter in qt._painters)
    finally:
        timers = [
            obj
            for obj in h.controls.values()
            if getattr(obj, "_qt_name", "") == "QTimer"
        ]
        h.close()
        assert all(not obj._active for obj in timers)


@pytest.mark.parametrize("id", ["0ad3432ccdca7ac0", "a14d08fe23965bec"])
def test_batch_eight_owned_local_ipc_roundtrip_and_cleanup(id, official_qt):
    import time

    from fontlab_python_examples.official import read

    qt, _ = official_qt
    h = batch_eight(id, qt)
    endpoint = Path(read(h.controls["hostLineEdit"], "text"))
    try:
        assert endpoint.is_socket() and h.snapshot()["sent"] == 0
        assert h.controls["hostLineEdit"].readOnly
        h.controls["requestNewFortune"]()
        deadline = time.monotonic() + 1
        while not h.snapshot()["fortune"] and time.monotonic() < deadline:
            qt._pump_network()
        state = h.snapshot()
        assert (
            state["fortune"]
            in load_record(next(r for r in records() if r["source_id"] == id)).FORTUNES
        )
        assert state["sent"] == state["received"] == 1
        assert not state["pending"] and not state["error"]
    finally:
        h.close()
    assert not endpoint.exists() and not endpoint.parent.exists()


def test_batch_eight_xml_deferred_native_validation_and_diagnostics(official_qt):
    qt, _ = official_qt
    h = batch_eight("1e5d0f7289e1b36e", qt)
    try:
        assert h.snapshot()["loading"] and h.snapshot()["valid"] is None
        h.controls["initializeTimer"].emit("timeout")
        assert h.snapshot()["valid"] is True
        assert h.snapshot()["status"] == "validation successful"
        for index in range(3):
            h.controls["schemaSelection"].setCurrentIndex(index)
            assert h.snapshot()["schema_index"] == index
            qt._validation_result = (False, "Owned invalid instance", 3, 2)
            h.controls["instanceSelection"].setCurrentIndex(1)
            assert h.snapshot()["valid"] is False
            assert (h.snapshot()["line"], h.snapshot()["column"]) == (3, 2)
            qt._validation_result = (True, "", 1, 1)
            h.controls["instanceSelection"].setCurrentIndex(0)
            assert h.snapshot()["valid"] is True
        for name in ("schemaHighlighter", "instanceHighlighter"):
            h.controls[name].highlightBlock('<recipe key="value"><!-- unfinished')
        h.controls["instanceEdit"].setPlainText("\n<root>\n <missing>\n</root>")
        h.controls["validate"]()
        assert h.snapshot()["line"] == 4 and h.snapshot()["column"] > 1, (
            "Boundary parse errors must preserve their source location too"
        )
    finally:
        h.close()


@pytest.mark.parametrize(
    "text",
    [
        "",
        "<broken",
        '<!DOCTYPE x SYSTEM "https://example.invalid/x"><x/>',
        '<x xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://example.invalid/x"/>',
        '<x xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="file:///tmp/other.xsd"/>',
    ],
)
def test_batch_eight_xml_rejects_invalid_or_external_input_before_native_validation(
    text, official_qt
):
    qt, _ = official_qt
    h = batch_eight("1e5d0f7289e1b36e", qt)
    try:
        h.controls["initializeTimer"].emit("timeout")
        before = len(qt._schema_requests)
        h.controls["instanceEdit"].setPlainText(text)
        h.controls["validate"]()
        assert h.snapshot()["valid"] is False
        assert len(qt._schema_requests) == before, (
            "Rejected input never reaches native XML networking"
        )
    finally:
        h.close()


@pytest.mark.parametrize("id", ["0ad3432ccdca7ac0", "a14d08fe23965bec"])
def test_batch_eight_ipc_close_with_pending_request_stops_every_timer(id, official_qt):
    from fontlab_python_examples.official import read

    qt, _ = official_qt
    h = batch_eight(id, qt)
    endpoint = Path(read(h.controls["hostLineEdit"], "text"))
    h.controls["requestNewFortune"]()
    assert h.snapshot()["pending"]
    timers = [h.controls[name] for name in ("requestTimer", "retryTimer")]
    h.close()
    assert all(not timer._active for timer in timers)
    assert not endpoint.parent.exists()
    qt._pump_network()
    h.close()


@pytest.mark.parametrize(
    "packet",
    [b"\x00\x01x", b"\x00\x06\x00\x00\x00\x03ab", b"\x00\x06\x00\x00\x00\x02\xd8\x00"],
)
def test_batch_eight_ipc_rejects_malformed_qt_frames(packet, official_qt):
    qt, _ = official_qt
    h = batch_eight("0ad3432ccdca7ac0", qt)
    try:
        h.controls["requestNewFortune"]()
        h.controls["socket"]._extra["received"] = packet[:1]
        h.controls["socket"].emit("readyRead")
        assert h.snapshot()["pending"] and not h.snapshot()["error"]
        h.controls["socket"]._extra["received"] = packet[1:]
        h.controls["socket"].emit("readyRead")
        assert not h.snapshot()["pending"] and h.snapshot()["error"]
        assert h.controls["getFortuneButton"].enabled
    finally:
        h.close()


def test_batch_eight_ipc_timeout_is_owned_and_retry_is_cancellable(official_qt):
    qt, _ = official_qt
    h = batch_eight("0ad3432ccdca7ac0", qt)
    try:
        h.controls["requestNewFortune"]()
        h.controls["requestTimer"].emit("timeout")
        assert "timed out" in h.snapshot()["error"] and not h.snapshot()["pending"]
    finally:
        h.close()


def test_batch_eight_xml_close_before_deferred_start_and_stale_callback(official_qt):
    qt, _ = official_qt
    h = batch_eight("1e5d0f7289e1b36e", qt)
    timer = h.controls["initializeTimer"]
    callback = next(slot for obj, _, slot in h.connections if obj is timer)
    h.close()
    callback()
    assert not timer._active and not qt._schema_requests


def test_batch_eight_actual_licences_include_docstring_and_denviso_notices():
    rows = {r["source_id"]: r for r in records() if r["source_id"] in BATCH_EIGHT_IDS}
    for id in (
        "9941e3c752b3a3b7",
        "1321540b04f33117",
        "5941e31267112c98",
        "773db5c24ae98ffb",
        "5125860585e98b3a",
    ):
        licence = rows[id]["license"]
        assert licence["upstream_expression"] == "GPL-2.0-or-later"
        assert licence["selected"] == "GPL-3.0-only"
        assert "David Boddie" in licence["original_notices"][0]
        assert "either version 2" in licence["original_notices"][0]
    licence = rows["7ba49e67588b1329"]["license"]
    assert licence["selected"] == "HPND AND GPL-3.0-only"
    assert "Denviso GmbH" in licence["attribution"]
    assert "DENVISO DISCLAIMS ALL WARRANTIES" in licence["original_notices"][0]
    assert rows["de4979a99c6d0bed"]["license"]["selected"] == "GPL-3.0-only"


def test_batch_eight_eight_designer_widgets_keep_explicit_plugin_blockers():
    widgets = [
        r
        for r in records()
        if r["source_id"] in BATCH_EIGHT_IMPLEMENTED
        and "/designer/plugins/widgets/" in r["source"]["path"]
    ]
    assert len(widgets) == 8
    assert all(
        r["designer_plugin"]["implementation"] == "blocked"
        and "QtDesigner" in r["designer_plugin"]["reason"]
        for r in widgets
    )


BATCH_NINE_IDS = {
    "93131a29a3b71ea3",
    "e1c73422208670cb",
    "9fed8c2f3765272b",
    "c862c1b57a0a0412",
    "f9107c0d26ffc4aa",
    "6bd9cbb60a6ac008",
    "032d404c69db6baa",
    "4bc27e706ac146f5",
    "cb1871959e42607b",
    "04e8e49f95de6cf5",
    "24b0b2aa8998d701",
    "7bddaa324636868a",
    "fa5e7696ac61b89f",
    "9d1a670d70c19b6a",
    "3299c18eadf92b5d",
    "f581c1e4f121df88",
    "2529316479664459",
    "6386ec6f1ca4ffd4",
    "92fc3cf4b5dd009c",
    "631cc1bc310c00b9",
    "3525151ac8d550f5",
    "a207ef153f0b81b7",
    "0d72445fb116793d",
    "307534c4e8e2211c",
    "eea833917398267a",
    "ecc2e23449331df1",
    "ccad55f9e06bfa93",
    "0b7e380ab45addbd",
    "b1c25455dbcb6bac",
    "8284e0348b6f7020",
    "b4d27c5a05969f77",
    "f5ecef06968ffad8",
    "bd4a25944ae5b2d7",
    "9e402cdc525108dd",
    "3ed66f4363a81cf2",
    "b2127700642ffb25",
    "a3c7c0e56d0452cf",
    "5b93264cdefad0d7",
    "fd7c0bbed85eb2d4",
    "b92988bc55b506ee",
    "ea0deb959e907448",
    "da960851c5ad3baa",
    "5646535663e933c0",
    "a4f928dfc9be8596",
    "e6abb656a88ccad4",
    "1e800054206a98ec",
    "0dfe1b3b36d41c8d",
    "8460861d4a65f625",
    "1f671605e1034b71",
    "72838df47d1eddc0",
    "a7eae99cebfb1806",
    "2253cce5a4c3a077",
    "23d091dcf5a72224",
    "c9510fb6daa7d1bd",
    "7fece60acaf2b392",
    "856b2b33c69b4e19",
    "11ec97a8c43a5283",
    "768c423bdd1fa074",
    "edeef5f840c20e15",
    "08ba2f1b1fe02894",
    "a0ac1b252a14609e",
    "f13380d705146bff",
    "52871219c50cdd21",
    "7cc9bd76e925db18",
    "b76dc05cb743e9fc",
    "43f4640a040ded3e",
    "26b75bfff47f567d",
    "5354655012c2060e",
    "6cb023a08571bf96",
    "1ffcdfb872b0e689",
    "8fc6773f10b89095",
    "5c181bebc7c9773c",
    "e2f27c6394aa70c8",
    "5d8303b0b2237124",
    "19398065f86e2762",
    "80aa961de86e1704",
    "2588c05ccd043d91",
    "8cb9580232bd8081",
    "207f7ce534696c20",
    "96777c686c66d526",
    "d82b14fd5e1eb010",
    "ee1562b25c092ee8",
    "60a3d030c4744735",
    "f5d13b3c5b699ab3",
    "620da7edd0cd23fc",
    "c6effccd6f31f416",
    "f2767c945bece214",
    "21a081a01365c096",
    "22be270b0ff2abf7",
    "01be5e33878e4940",
    "9007853b5b845ed9",
    "1862a5f7d89bd9b6",
    "b3c5b8f7bcf09a1d",
    "e9392311a500d3dd",
    "1e79bddb6d52574d",
    "88fa78cafb505cfa",
    "83bc55d45ae367d0",
}
BATCH_NINE_IMPLEMENTED = {
    "4bc27e706ac146f5",
    "cb1871959e42607b",
    "92fc3cf4b5dd009c",
    "631cc1bc310c00b9",
    "ecc2e23449331df1",
    "b1c25455dbcb6bac",
    "edeef5f840c20e15",
    "1e79bddb6d52574d",
    "88fa78cafb505cfa",
    "83bc55d45ae367d0",
}


def batch_nine_records():
    return [
        r
        for r in json.loads((ROOT / "catalog/ports.json").read_text())["ports"]
        if r["source_id"] in BATCH_NINE_IDS
    ]


def test_batch_nine_exact_remaining_entrypoints_and_supported_ports():
    rows = batch_nine_records()
    assert {r["source_id"] for r in rows} == BATCH_NINE_IDS
    assert len(rows) == 97
    assert {
        r["source_id"] for r in rows if r["implementation"] == "implemented"
    } == BATCH_NINE_IMPLEMENTED


@pytest.mark.parametrize("row", batch_nine_records(), ids=lambda r: r["source_id"])
def test_batch_nine_provenance_license_resource_hashes_and_native_boundary(row):
    sources = {
        r["id"]: r
        for r in json.loads((ROOT / "catalog/sources.json").read_text())["files"]
    }
    assert row["source"]["sha256"] == sources[row["source_id"]]["sha256"]
    assert row["native_acceptance"] == "unexecuted"
    assert row["license"]["selected"] == (
        "MIT" if row["source"]["repository"] == "pyqt/examples" else "GPL-3.0-only"
    )
    assert row["source"]["path"] in row["license"]["reviewed_files"]
    assert row["license"]["basis"] and row["adaptations"]
    path = ROOT / row["target_path"]
    code = path.read_text()
    tree = ast.parse(code, feature_version=(3, 11))
    assert "this_file: " + row["target_path"] in code
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = (
                [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            assert not any(
                n.startswith(("PyQt", "PySide")) or n.endswith("_rc") for n in names
            )
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {"exec", "exec_", "singleShot", "exit"}
            if isinstance(node.func.value, ast.Attribute):
                assert node.func.attr != "connect", (
                    "No untracked native signal connections"
                )
    for resource in row["resources"]:
        data = (ROOT / resource["target_path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == resource["source"]["sha256"]
        assert len(data) == resource["source"]["bytes"]
        assert not resource["target_path"].endswith("_rc.py")


@pytest.mark.parametrize(
    "row",
    [r for r in batch_nine_records() if r["implementation"] == "implemented"],
    ids=lambda r: r["source_id"],
)
def test_batch_nine_build_inspect_controls_disconnect_and_close(row, official_qt):
    test_official_build_inspect_controls_disconnect_and_close(row, official_qt)


@pytest.mark.parametrize(
    "row",
    [r for r in batch_nine_records() if r["implementation"] == "blocked"],
    ids=lambda r: r["source_id"],
)
def test_batch_nine_blockers_reject_before_host_access(row, monkeypatch):
    test_batch_eight_blockers_fail_before_accessing_host(row, monkeypatch)


def nine(id, qt):
    return load_record(
        next(r for r in batch_nine_records() if r["source_id"] == id)
    ).build(qt)


@pytest.mark.parametrize("id", ["4bc27e706ac146f5", "cb1871959e42607b"])
def test_batch_nine_local_ipc_uint32_unicode_frames_and_owned_cleanup(id, official_qt):
    qt, _ = official_qt
    h = nine(id, qt)
    endpoint = h.controls["hostLineEdit"].text
    h.controls["getFortuneButton"].click()
    spin_until(qt, h, lambda: h.snapshot()["received"] == 1)
    assert h.snapshot()["fortune"]
    assert not h.snapshot()["pending"]
    assert h.controls["hostLineEdit"].isReadOnly()
    h.close()
    assert not Path(endpoint).exists()


@pytest.mark.parametrize(
    "id", ["1e79bddb6d52574d", "88fa78cafb505cfa", "83bc55d45ae367d0"]
)
def test_batch_nine_chat_unicode_roundtrip_and_close_stops_owned_threads(
    id, official_qt
):
    qt, _ = official_qt
    h = nine(id, qt)
    import socket
    from urllib.parse import urlsplit

    value = urlsplit(h.snapshot()["endpoint"])
    assert value.hostname == "127.0.0.1"
    h.controls["name"].setText("Zażółć")
    h.controls["message"].setText("Hello 🐈")
    h.controls["send_message"]()
    if id == "1e79bddb6d52574d":
        h.controls["pollTimer"].emit("timeout")
    else:
        spin_until(qt, h, lambda: "Hello 🐈" in h.snapshot()["text"])
    assert h.snapshot()["text"] == "Zażółć: Hello 🐈"
    assert h.snapshot()["sent"] == 1
    assert h.snapshot()["message"] == ""
    h.close()
    with pytest.raises(OSError):
        socket.create_connection((value.hostname, value.port), timeout=0.2)


def test_batch_nine_style_original_ui_connections_and_owned_styles(official_qt):
    qt, _ = official_qt
    h = nine("631cc1bc310c00b9", qt)
    h.controls["spinBox"].setValue(17)
    assert h.controls["horizontalScrollBar"].value == 17
    assert h.controls["horizontalScrollBar_2"].value == 17
    for button, style in [
        ("blueStyle", "blue"),
        ("khakiStyle", "khaki"),
        ("transparentStyle", "transparent"),
        ("noStyle", "nostyle"),
    ]:
        h.controls[button].click()
        assert h.snapshot()["style"] == style
    assert h.snapshot()["stylesheet"] == ""
    h.close()


def test_batch_nine_suggestions_async_xml_unicode_and_pending_close(official_qt):
    qt, _ = official_qt
    h = nine("edeef5f840c20e15", qt)
    h.widget.setText("Zażółć")
    h.controls["search"]()
    assert h.snapshot()["pending"]
    qt._pump_network()
    assert h.snapshot()["suggestions"] == [
        "Zażółć",
        "Zażółć PythonQt",
        "Zażółć FontLab",
    ]
    assert h.snapshot()["row_count"] == 3
    assert not h.snapshot()["pending"]
    h.widget.setText("")
    h.controls["search"]()
    assert h.snapshot()["row_count"] == 0
    h.widget.setText("next")
    h.controls["search"]()
    h.close()
    qt._pump_network()


def test_batch_nine_native_windows_input_painting_timers_and_store_cleanup(official_qt):
    qt, _ = official_qt
    h = nine("b1c25455dbcb6bac", qt)
    assert h.snapshot()["window_count"] == 3
    assert h.snapshot()["windows"][0]["title"] == "Window A"
    window = h.controls["window0"]
    window.show()
    for key, text in [(0, "A"), (0, "B"), (qt.QtCore.Qt.Key_Backspace, "")]:
        window.keyPressEvent(
            SimpleNamespace(key=lambda key=key: key, text=lambda text=text: text)
        )
    assert h.snapshot()["windows"][0]["text"] == "A"
    event = SimpleNamespace(pos=lambda: qt.QtCore.QPoint(20, 20))
    window.mousePressEvent(event)
    window.mouseMoveEvent(event)
    window.mouseReleaseEvent(event)
    window.render()
    stores = [h.controls["window" + str(i)]._backing for i in range(3)]
    assert stores[0]._extra["paint_calls"][-3:] == ["beginPaint", "endPaint", "flush"]
    assert all(not p.isActive() for p in qt._painters)
    timers = [h.controls["renderTimer" + str(i)] for i in range(3)]
    h.close()
    assert all(s.deleted for s in stores)
    assert all(not t.isActive() for t in timers)


@pytest.mark.parametrize(
    "row",
    [r for r in batch_nine_records() if r["implementation"] == "implemented"],
    ids=lambda r: r["source_id"],
)
def test_batch_nine_partial_build_failure_rolls_back_owned_ui_and_workers(
    row, official_qt, monkeypatch
):
    from fontlab_python_examples.official import Demo

    qt, owners = official_qt

    def fail(*args, **kwargs):
        raise RuntimeError("Injected final-build failure")

    monkeypatch.setattr(Demo, "finish", fail)
    with pytest.raises(RuntimeError, match="Injected final-build failure"):
        load_record(row).build(qt)
    assert owners and all(owner.closed for owner in owners)


def test_batch_nine_missing_capabilities_match_captured_and_current_native_stubs():
    from tests.official_doubles import CONTRACT

    evidence = json.loads((ROOT / "tests/official_contract.json").read_text())
    for row in batch_nine_records():
        if row["implementation"] != "blocked":
            continue
        needs = row["missing_capabilities"]
        for name in needs.get("modules", []):
            assert name.split(" ")[0] in evidence["absent_host_modules"]
        for name in needs.get("classes", []):
            if "." in name:
                module, cls = name.split(".")
                assert cls not in CONTRACT.get(module, {})
        for name, members in needs.get("members", {}).items():
            module, cls = name.split(".")
            for member in members:
                assert member not in CONTRACT[module][cls]
    stub_root = ROOT.parent / "fontlab-echopy/src/fontlab_echopy/PythonQt"
    if stub_root.exists():
        for module, sha in evidence["stub_sha256"].items():
            assert (
                hashlib.sha256((stub_root / (module + ".pyi")).read_bytes()).hexdigest()
                == sha
            )
        for module in evidence["absent_host_modules"]:
            assert not (stub_root / (module + ".pyi")).exists()


def test_batch_nine_ipc_preserves_uint32_qstring_unicode_payload(
    official_qt, monkeypatch
):
    import random

    monkeypatch.setattr(random, "choice", lambda values: "Zażółć 🐈")
    qt, _ = official_qt
    h = nine("4bc27e706ac146f5", qt)
    h.controls["getFortuneButton"].click()
    spin_until(qt, h, lambda: h.snapshot()["received"] == 1)
    assert h.snapshot()["fortune"] == "Zażółć 🐈"
    h.close()


def test_batch_nine_suggestions_timeout_cancels_reply_before_native_delete(official_qt):
    qt, _ = official_qt
    h = nine("edeef5f840c20e15", qt)
    h.widget.setText("waiting")
    h.controls["search"]()
    h.controls["requestTimer"].emit("timeout")
    assert not h.snapshot()["pending"]
    assert "timed out" in h.snapshot()["error"]
    qt._pump_network()
    assert h.snapshot()["suggestions"] == []
    h.close()


@pytest.mark.parametrize(
    "id, scenario",
    [
        (
            "92fc3cf4b5dd009c",
            test_batch_seven_lightmaps_owned_tiles_pan_city_night_zoom_and_drag,
        ),
        ("ecc2e23449331df1", test_batch_seven_loopback_transfer_and_close_while_active),
    ],
)
def test_batch_nine_reused_network_ports_preserve_real_interactions(
    id, scenario, official_qt, monkeypatch
):
    import sys

    monkeypatch.setattr(sys.modules[__name__], "built", lambda name, qt: nine(id, qt))
    scenario(official_qt)


def test_native_application_primary_screen_is_a_null_property(official_qt):
    qt, _ = official_qt
    assert repr(qt.QtGui.QApplication.primaryScreen) == "QScreen (QScreen at: 0x0)"
    assert qt.QtGui.QApplication.instance().primaryScreen is None
    with pytest.raises(TypeError):
        qt.QtGui.QApplication.primaryScreen()
    with pytest.raises(TypeError):
        qt.QtGui.QApplication.instance().primaryScreen()
    assert qt.QtGui.QApplication.screens() == []


@pytest.mark.parametrize("secondary_name", ["Primary", "Secondary"])
def test_batch_nine_windows_select_first_static_screen_by_name_and_geometry(
    official_qt, monkeypatch, secondary_name
):
    qt, _ = official_qt
    primary = qt.QtGui.QScreen()
    alias = qt.QtGui.QScreen()
    secondary = qt.QtGui.QScreen()
    for screen, name, x in [
        (primary, "Primary", 0),
        (alias, "Primary", 0),
        (secondary, secondary_name, 1920),
    ]:
        screen._data["name"] = name
        screen.geometry = qt.QtCore.QRect(x, 0, 1920, 1080)
        screen._data["availableGeometry"] = qt.QtCore.QRect(x, 0, 1920, 1040)
    qt._screens = [primary, alias, secondary]

    def unsafe_comparison(*args):
        pytest.fail("Compare screen names and geometry, never native wrappers")

    monkeypatch.setattr(qt.QtGui.QScreen, "__eq__", unsafe_comparison)
    h = nine("b1c25455dbcb6bac", qt)
    try:
        state = h.snapshot()
        assert state["window_count"] == 4, (
            "One extra window per non-primary screen; wrapper aliases must not duplicate it"
        )
        assert state["windows"][-1]["title"] == secondary_name
        assert h.controls["window3"]._data["screen"] is secondary
    finally:
        h.close()


def test_all_ports_avoid_primary_screen_property_calls_and_screen_at():
    for path in (ROOT / "ports").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                assert node.attr != "primaryScreen", path
            if isinstance(node, ast.Constant):
                assert node.value != "primaryScreen", path
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"primaryScreen", "screenAt"}, path


def test_screenshot_with_no_static_screens_keeps_empty_capture(official_qt):
    qt, _ = official_qt
    assert qt.QtGui.QApplication.screens() == []
    h = built("screenshot", qt)
    try:
        h.controls["newScreenshotButton"].click()
        h.controls["captureTimer"].emit("timeout")
        assert not h.snapshot()["has_capture"]
        assert h.controls["newScreenshotButton"].isEnabled()
    finally:
        h.close()
