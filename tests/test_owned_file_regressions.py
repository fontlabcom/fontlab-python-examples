# this_file: tests/test_owned_file_regressions.py
"""Native file-boundary regressions using the exported PythonQt doubles."""

import ast
import pickle
import plistlib
from pathlib import Path

import pytest

from fontlab_python_examples.official import Demo, read
from tests.port_state import require_current
from tests.test_official_batch import built
from tests.test_official_batch import official_qt as official_qt  # noqa: PLC0414


def owner(h):
    return next(
        f.__self__ for f in h.release if isinstance(getattr(f, "__self__", None), Demo)
    )


def test_recentfiles_tuple_settings_reorder_deduplicate_and_limit(official_qt):
    qt, _ = official_qt
    h = built("recentfiles", qt)
    try:
        paths = [str(Path(owner(h).temp_dir()) / f"{i}.txt") for i in range(7)]
        h.widget._settings.setValue("recentFileList", tuple(paths[:5]))
        h.widget.setCurrentFile(paths[2])
        assert list(h.widget._settings.value("recentFileList")) == [
            paths[2],
            paths[0],
            paths[1],
            paths[3],
            paths[4],
        ]
        h.widget.setCurrentFile(paths[6])
        assert list(h.widget._settings.value("recentFileList")) == [
            paths[6],
            paths[2],
            paths[0],
            paths[1],
            paths[3],
        ]
        assert h.widget.recentFileActs[0].data() == paths[6]
    finally:
        h.close()


@pytest.mark.parametrize("name", ["application", "sdi", "recentfiles", "mdi"])
def test_editor_save_refuses_outside_paths_visibly(name, official_qt, tmp_path):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        target = tmp_path / "private.txt"
        target.write_text("Keep this file", encoding="utf-8")
        window = h.widget
        if name == "mdi":
            window.newFile()
            window = window.activeMdiChild()
        assert window.saveFile(str(target)) is False
        assert target.read_text() == "Keep this file"
        assert "temporary directory" in h.snapshot()["error"]
        assert h.controls["active_dialog"].isVisible()
    finally:
        h.close()


@pytest.mark.parametrize(
    "name,action",
    [
        ("textedit", "actionSaveAs"),
        ("dockwidgets", "saveAct"),
        ("separations", "saveAction"),
    ],
)
def test_save_dialog_refuses_outside_path_before_write(
    name, action, official_qt, tmp_path
):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        target = tmp_path / "outside.html"
        h.controls[action].setEnabled(True)
        h.controls[action].trigger()
        box = h.controls["active_dialog"]
        box._extra["selectedFiles"] = [str(target)]
        box.accept()
        assert not target.exists()
        assert "temporary directory" in h.snapshot()["error"]
        assert h.controls["active_dialog"].isVisible()
        if name == "textedit":
            assert h.snapshot()["file"] == ""
    finally:
        h.close()


def test_textedit_load_allows_read_but_save_and_pdf_refuse_outside_paths(
    official_qt, tmp_path
):
    qt, _ = official_qt
    h = built("textedit", qt)
    demo = owner(h)
    try:
        target = tmp_path / "outside.odt"
        target.write_text("Original", encoding="utf-8")
        assert h.widget.load(str(target)) is True
        assert h.controls["textEdit"].toPlainText() == "Original"
        h.widget.fileName = str(target)
        assert h.widget.fileSave() is False
        assert target.read_text() == "Original"
        with pytest.raises(ValueError, match="temporary directory"):
            demo.pdf_printer(str(tmp_path / "outside.pdf"))
    finally:
        h.close()


@pytest.mark.parametrize(
    "button",
    [
        "directoryButton",
        "openFileNameButton",
        "openFileNamesButton",
        "saveFileNameButton",
    ],
)
def test_standarddialogs_native_checkbox_cannot_enable_native_panel(
    button, official_qt
):
    qt, _ = official_qt
    h = built("standarddialogs", qt)
    try:
        h.widget.native.setChecked(True)
        h.controls[button].click()
        box = h.controls["active_dialog"]
        assert box._data["option"] == (qt.QtGui.QFileDialog.DontUseNativeDialog, True)
        assert box.isVisible()
        assert box.findChild(qt.private.QObject, "fileNameEdit") is not None
        assert read(box, "windowModality") == qt.QtCore.Qt.NonModal
    finally:
        h.close()


def test_owned_temp_cleanup_runs_after_close_and_is_idempotent(
    official_qt, tmp_path, isolated_tempfiles
):
    qt, _ = official_qt
    h = built("recentfiles", qt)
    demo = owner(h)
    root = Path(demo.temp_dir())
    assert root.parent == isolated_tempfiles, "Never write late.ini to system temp"
    foreign = tmp_path / "fontlab-official-foreign"
    foreign.mkdir()
    (foreign / "keep").write_text("keep")
    original_close = h.owner.close

    def closing_write():
        root.mkdir(exist_ok=True)
        (root / "late.ini").write_text("closed")
        original_close()

    try:
        h.owner.close = closing_write
        h.close()
        assert not root.exists(), (
            "Remove owned files after native close callbacks finish"
        )
        h.owner.close = original_close
        h.close()
        assert not root.exists(), "Repeated close must not recreate late.ini"
        assert (foreign / "keep").read_text() == "keep"
    finally:
        h.owner.close = original_close
        h.close()
        (foreign / "keep").unlink()
        foreign.rmdir()


def test_owned_path_rejects_symlink_and_sibling_prefix(official_qt, tmp_path):
    qt, _ = official_qt
    h = built("recentfiles", qt)
    demo = owner(h)
    try:
        root = Path(demo.temp_dir())
        (root / "escape").symlink_to(tmp_path, target_is_directory=True)
        for path in [
            root / "escape" / "outside.txt",
            Path(str(root) + "-other") / "outside.txt",
            root,
        ]:
            with pytest.raises(ValueError, match="temporary directory"):
                demo.owned_path(str(path))
    finally:
        h.close()


@pytest.mark.parametrize(
    "name,control", [("codecs", "save"), ("stylesheet", "saveButton")]
)
def test_remaining_text_writers_refuse_outside_dialog_selection(
    name, control, official_qt, tmp_path
):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        if name == "codecs":
            h.widget.save("utf-8")
        else:
            h.controls[control].click()
        h.controls["active_dialog"]._extra["selectedFiles"] = [
            str(tmp_path / "outside.txt")
        ]
        h.controls["active_dialog"].accept()
        assert not (tmp_path / "outside.txt").exists()
        assert "temporary directory" in h.snapshot()["error"]
        assert h.controls["active_dialog"].isVisible()
    finally:
        h.close()


def test_scribble_save_refuses_outside_paths(official_qt, tmp_path):
    qt, _ = official_qt
    h = built("scribble", qt)
    try:
        assert (
            h.widget.scribbleArea.saveImage(str(tmp_path / "outside.png"), "PNG")
            is False
        )
        assert not (tmp_path / "outside.png").exists()
        assert "temporary directory" in h.snapshot()["error"]
        assert h.controls["active_dialog"].isVisible()
    finally:
        h.close()


@pytest.mark.parametrize("location", ["asset", "user", "owned"])
def test_codecs_open_reads_without_mutating_source(location, official_qt, tmp_path):
    qt, _ = official_qt
    h = built("codecs", qt)
    try:
        demo = owner(h)
        asset = demo.assets / "encodedfiles" / "utf-8.txt"
        source = asset
        if location != "asset":
            directory = tmp_path if location == "user" else Path(demo.temp_dir())
            source = directory / "source.txt"
            source.write_bytes(asset.read_bytes())
        original = source.read_bytes()
        h.controls["openAct"].trigger()
        box = h.controls["active_dialog"]
        assert box.findChild(qt.private.QObject, "fileNameEdit") is not None
        box._extra["selectedFiles"] = [str(source)]
        box.accept()
        assert h.widget.previewForm.isVisible(), "Readable source opens codec preview"
        h.widget.previewForm.accept()
        assert h.snapshot()["text"] == original.decode("utf-8")
        assert not h.snapshot()["error"] and source.read_bytes() == original
    finally:
        h.close()


@pytest.mark.parametrize("name", ["application", "sdi", "recentfiles", "mdi"])
def test_editor_read_allows_user_file_and_save_stays_owned(name, official_qt, tmp_path):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        source = tmp_path / "source.txt"
        source.write_text("Read Ą–字体", encoding="utf-8")
        window = h.widget
        if name == "mdi":
            window.newFile()
            window = window.activeMdiChild()
        assert window.loadFile(str(source)) is not False
        editor = window if name == "mdi" else window.textEdit
        assert editor.toPlainText() == "Read Ą–字体"
        assert not h.snapshot()["error"]
        assert window.saveFile(str(source)) is False
        assert source.read_text(encoding="utf-8") == "Read Ą–字体"
    finally:
        h.close()


@pytest.mark.parametrize(
    "name,method",
    [
        ("scribble", "openImage"),
        ("imageviewer", "loadImage"),
        ("separations", "openImageFile"),
    ],
)
def test_image_reads_allow_bundled_asset_and_user_file(
    name, method, official_qt, tmp_path
):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        asset = next((Path(__file__).resolve().parents[1] / "ports").rglob("*.png"))
        user = tmp_path / "image.png"
        user.write_bytes(asset.read_bytes())
        obj = h.widget.scribbleArea if name == "scribble" else h.widget
        for source in (asset, user):
            assert getattr(obj, method)(str(source)) is not False
            assert not h.snapshot()["error"], "Image reads must not use owned_path"
            assert source.read_bytes() == user.read_bytes()
    finally:
        h.close()


@pytest.mark.parametrize("part", [6, 7])
def test_addressbook_read_allows_user_file_and_write_refused(
    part, official_qt, tmp_path
):
    qt, _ = official_qt
    h = built(f"addressbook part{part}", qt)
    try:
        source = tmp_path / "contacts.abk"
        data = pickle.dumps({"Zoë": "Łódź"})
        source.write_bytes(data)
        h.controls["loadContacts"](str(source))
        assert h.snapshot()["contacts"] == {"Zoë": "Łódź"}
        h.controls["saveContacts"](str(source))
        assert source.read_bytes() == data and h.snapshot()["error"]
    finally:
        h.close()


@pytest.mark.parametrize("kind", ["ini", "plist"])
def test_settings_import_reads_user_file_and_edits_owned_copy(
    kind, official_qt, tmp_path
):
    qt, _ = official_qt
    h = built("settingseditor", qt)
    try:
        source = tmp_path / f"source.{kind}"
        data = (
            b"[General]\nname=original\n"
            if kind == "ini"
            else plistlib.dumps({"name": "original"})
        )
        source.write_bytes(data)
        action = "openIniFileAct" if kind == "ini" else "openPropertyListAct"
        h.controls[action].trigger()
        box = h.controls["active_dialog"]
        box._extra["selectedFiles"] = [str(source)]
        box.accept()
        settings = h.widget.settingsTree.settings
        target = Path(settings._args[0])
        assert target.is_relative_to(Path(owner(h).temp_dir()))
        settings.setValue("name", "changed")
        settings.sync()
        assert source.read_bytes() == data, "Settings edits never reach imported source"
        assert not h.snapshot()["error"]
    finally:
        h.close()


def test_open_dialog_owned_hint_does_not_restrict_reads(official_qt, tmp_path):
    qt, _ = official_qt
    h = built("codecs", qt)
    try:
        source = tmp_path / "read.txt"
        source.write_text("Readable")
        selected = []
        box = owner(h).choose(h.widget, selected.append, owned=True)
        box._extra["selectedFiles"] = [str(source)]
        box.accept()
        assert selected == [str(source)], "Only save selections enforce owned_path"
    finally:
        h.close()


@pytest.mark.parametrize("escape", ["directory", "header", "implementation"])
def test_classwizard_validates_both_outputs_before_any_write(
    escape, official_qt, tmp_path, monkeypatch
):
    qt, _ = official_qt
    h = built("classwizard", qt)
    try:
        root = Path(owner(h).temp_dir())
        values = {
            "className": "Sample",
            "baseClass": "",
            "macroName": "SAMPLE_H",
            "baseInclude": "",
            "outputDir": str(root),
            "header": "sample.h",
            "implementation": "sample.cpp",
        }
        if escape == "directory":
            values["outputDir"] = str(tmp_path)
        else:
            values[escape] = str(tmp_path / "outside.cpp")
        monkeypatch.setattr(type(h.widget), "field", lambda self, name: values[name])
        h.widget.accept()
        assert not list(root.iterdir()) and not list(tmp_path.iterdir())
        assert "temporary directory" in h.snapshot()["error"]
        assert h.controls["active_dialog"].isVisible()
    finally:
        h.close()


def test_textedit_checks_appended_extension_and_preserves_document_on_refusal(
    official_qt, tmp_path
):
    qt, _ = official_qt
    h = built("textedit", qt)
    try:
        root = Path(owner(h).temp_dir())
        target = tmp_path / "outside.odt"
        target.write_text("Original")
        (root / "doc.odt").symlink_to(target)
        document = read(h.controls["textEdit"], "document")
        document.setModified(True)
        h.widget.fileSaveAs()
        box = h.controls["active_dialog"]
        box._extra["selectedFiles"] = [str(root / "doc")]
        box.accept()
        assert target.read_text() == "Original" and document.isModified()
        assert h.snapshot()["file"] == ""
        assert h.controls["active_dialog"].isVisible()
    finally:
        h.close()


def test_print_dialog_rechecks_user_output_before_render(official_qt, tmp_path):
    qt, _ = official_qt
    h = built("dockwidgets", qt)
    try:
        rendered = []
        demo = owner(h)
        box = demo.print_dialog(h.widget, rendered.append)
        box.printer().setOutputFileName(str(tmp_path / "outside.pdf"))
        box.accept()
        assert not rendered and not (tmp_path / "outside.pdf").exists()
        assert "temporary directory" in h.snapshot()["error"]
        assert h.controls["active_dialog"].isVisible()
    finally:
        h.close()


def test_close_refuses_retargeted_temporary_directory(official_qt, tmp_path):
    qt, _ = official_qt
    h = built("recentfiles", qt)
    demo = owner(h)
    root = demo.temporary.name
    original = demo.temporary
    borrowed = type(original)(dir=tmp_path, prefix="fontlab-official-")
    try:
        demo.temporary = borrowed
        with pytest.raises(RuntimeError, match="ownership changed"):
            h.close()
        assert Path(borrowed.name).exists(), "Never delete a borrowed directory"
    finally:
        demo.temporary = original
        h.close()
        borrowed.cleanup()
    assert not Path(root).exists()


def test_close_refuses_foreign_directory_replacing_owned_name(official_qt, tmp_path):
    qt, _ = official_qt
    h = built("recentfiles", qt)
    root = Path(owner(h).temp_dir())
    original = tmp_path / "original"
    root.rename(original)
    root.mkdir()
    (root / "foreign").write_text("keep")
    try:
        with pytest.raises(RuntimeError, match="ownership changed"):
            h.close()
        assert (root / "foreign").read_text() == "keep"
    finally:
        (root / "foreign").unlink()
        root.rmdir()
        original.rename(root)
        h.close()
    assert not root.exists()


def test_all_ports_convert_settings_list_defaults_before_use():
    from tests.test_official_batch import records

    require_current(next(r for r in records() if r["name"] == "Official recentfiles"))
    root = Path(__file__).resolve().parents[1]
    checked = 0
    for path in (root / "ports").rglob("*.py"):
        tree = ast.parse(path.read_text())
        parents = {
            child: node
            for node in ast.walk(tree)
            for child in ast.iter_child_nodes(node)
        }
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "value"
                and len(node.args) == 2
                and isinstance(node.args[1], ast.List)
            ):
                continue
            checked += 1
            parent = parents[node]
            assert (
                isinstance(parent, ast.Call)
                and isinstance(parent.func, ast.Name)
                and parent.func.id == "list"
            ), f"Normalize PythonQt tuple/list settings at {path.name}:{node.lineno}"
    assert checked == 3, "Audit all three recentFileList reads"


def test_all_port_open_and_load_methods_avoid_write_ownership_checks():
    root = Path(__file__).resolve().parents[1]
    paths = list((root / "ports").rglob("*.py"))
    paths.append(root / "fontlab_python_examples" / "editor.py")
    for path in paths:
        for function in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(
                function, ast.FunctionDef
            ) or not function.name.startswith(("open", "load")):
                continue
            assert not any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "owned_path"
                for node in ast.walk(function)
            ), f"Read method must not enforce write ownership: {path}:{function.lineno}"
