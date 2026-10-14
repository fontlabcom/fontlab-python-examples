# this_file: tests/test_official_interaction_regressions.py
"""Reported native interactions, with deliberately lossy PythonQt doubles."""

import ast
from types import SimpleNamespace

import pytest

from fontlab_python_examples.official import read
from tests.test_official_batch import ROOT, built, owned_directory
from tests.test_official_batch import official_qt as official_qt  # noqa: PLC0414


def test_every_port_avoids_sender():
    calls = []
    for path in (ROOT / "ports").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "sender"
            ):
                calls.append(f"{path.name}:{node.lineno}")
    assert not calls, f"PythonQt slots have no sender: {calls}"


def test_calculator_slots_when_sender_is_none_then_compute_precedence(official_qt):
    qt, _ = official_qt
    h = built("calculator", qt)
    try:
        assert h.widget.sender() is None
        b, c = h.widget.digitButtons, h.controls
        b[2].click()
        c["plusButton"].click()
        b[3].click()
        c["timesButton"].click()
        b[4].click()
        c["equalButton"].click()
        assert float(h.snapshot()["display_text"]) == 14
        c["setMemoryButton"].click()
        c["clearAllButton"].click()
        c["readMemoryButton"].click()
        assert h.snapshot()["memory"] == 14
        c["clearAllButton"].click()
        b[9].click()
        c["divisionButton"].click()
        b[0].click()
        c["equalButton"].click()
        assert h.snapshot()["display_text"] == "####"
        c["clearAllButton"].click()
        b[9].click()
        c["squareRootButton"].click()
        assert float(h.snapshot()["display_text"]) == 3
        assert h.widget.digitButtons[0].sizeHint().height() > 0
    finally:
        h.close()


def test_table_lookup_loses_python_subclass(official_qt):
    qt, _ = official_qt

    class Cell(qt.QtGui.QTableWidgetItem):
        def formula(self):
            return "lost"

    table = qt.QtGui.QTableWidget(1, 1)
    table.setItem(0, 0, Cell("raw"))
    item = table.item(0, 0)
    assert not isinstance(item, Cell), "Native wrappers lose Python subclass methods"
    with pytest.raises(AttributeError):
        item.formula()
    item.setText("changed")
    assert read(table.item(0, 0), "text") == "changed", "Wrappers share native data"


def test_spreadsheet_edits_when_item_is_native_wrapper_then_recalculate(official_qt):
    qt, _ = official_qt
    h = built("spreadsheet", qt)
    try:
        c = h.controls
        assert h.snapshot()["total"] == 21883
        c["table"].item(1, 2).setData(qt.QtCore.Qt.EditRole, "200")
        assert h.snapshot()["total"] == 21933
        assert h.snapshot()["formulas"][1][2] == "200"
        c["putFormula"]("F2", "= F2")
        assert c["displayCell"](1, 5) is None
        c["putFormula"]("F2", "/ C2 C1")
        assert c["displayCell"](1, 5) == "nan"
    finally:
        h.close()


def test_application_user_edits_and_save_reset_modified(official_qt, tmp_path):
    qt, _ = official_qt
    h = built("application", qt)
    try:
        editor = h.controls["textEdit"]
        document = read(editor, "document")
        assert any(
            obj is document and sig == "contentsChanged()"
            for obj, sig, _ in h.connections
        )
        editor.setPlainText("Zoë draft")
        assert not document.isModified() and not h.snapshot()["modified"], (
            "Replacement resets modified, as in Qt"
        )
        editor.insertPlainText(" edited")
        assert document.isModified() and h.snapshot()["modified"], (
            "User-style insertion marks the window"
        )
        assert h.widget.saveFile(str(owned_directory(h) / "draft.txt"))
        assert not h.snapshot()["modified"]
    finally:
        h.close()


def test_tiles_relay_uses_emitted_bool_signature_and_grid(official_qt):
    qt, _ = official_qt
    h = built("animatedtiles", qt)
    try:
        h.controls["timer"].emit("timeout")
        h.controls["tiled"]._trigger.click()
        positions = h.snapshot()["positions"]
        assert len({p[0] for p in positions}) == len({p[1] for p in positions}) == 8
        h.controls["centered"]._trigger.click()
        assert h.snapshot()["positions"] == [[0, 0]] * 64
    finally:
        h.close()


@pytest.mark.parametrize("name", ["broadcastsender", "broadcastreceiver"])
def test_udp_requires_explicit_localhost_address(name, official_qt):
    from tests.test_official_batch import spin_until

    qt, _ = official_qt
    h = built(name, qt)
    try:
        h.controls["sendSample"]()
        spin_until(qt, h, lambda: bool(h.snapshot()["received"]))
        assert h.snapshot()["received"] == ["Broadcast message 1"]
        assert h.snapshot()["host"] == "127.0.0.1"
    finally:
        h.close()


def test_counter_offset_matches_original_notifications_only(official_qt):
    qt, _ = official_qt
    h = built("counterlabel", qt)
    try:
        w = h.widget
        w.setMaximum(200)
        w.setOffset(5)
        w.setValue(123)
        state = h.snapshot()
        assert state["value"] == 123 and state["notifications"][
            "valueChanged(int)"
        ] == [128]
        assert state["notifications"]["valueChanged(str)"] == ["128"]
        w.stepUp()
        assert h.snapshot()["value"] == 124 and h.snapshot()["notifications"][
            "valueChanged(int)"
        ] == [129]
        w.setValue(201)
        assert h.snapshot()["value"] == 124, "Out-of-range values are ignored"
    finally:
        h.close()


def test_delegate_destroyed_editor_is_removed_before_inspection(official_qt):
    qt, _ = official_qt
    h = built("spinboxdelegate", qt)
    try:
        c = h.controls
        index = c["model"].index(2, 1)
        editor = c["delegate"].createEditor(h.widget, SimpleNamespace(), index)
        c["delegate"].setEditorData(editor, index)
        editor.setValue(42)
        c["delegate"].setModelData(editor, c["model"], index)
        editor.deleteLater()
        with pytest.raises(ValueError, match="destroyed"):
            _ = editor.windowTitle
        assert "editor" not in h.controls, (
            "Drop the wrapper on destroyed without reading it"
        )
        assert h.snapshot()["rows"][2][1] == 42
        assert all(obj is not editor for obj, _, _ in h.connections)
    finally:
        h.close()


def test_recent_file_actions_bind_each_action_without_sender(official_qt, tmp_path):
    qt, _ = official_qt
    h = built("recentfiles", qt)
    try:
        paths = [owned_directory(h) / "one.txt", owned_directory(h) / "two.txt"]
        for path in paths:
            path.write_text(path.stem)
            h.widget.loadFile(str(path))
        for action, expected in zip(h.widget.recentFileActs, reversed(paths)):
            action.trigger()
            assert h.controls["textEdit"].toPlainText() == expected.stem
    finally:
        h.close()


def test_scribble_save_actions_bind_each_format_without_sender(official_qt):
    qt, _ = official_qt
    h = built("scribble", qt)
    try:
        formats = []
        h.widget.saveFile = lambda format: formats.append(format)
        for action in h.widget.saveAsActs:
            action.trigger()
        assert formats == ["png", "jpg"]
    finally:
        h.close()


def test_graphics_wrappers_are_resolved_before_python_item_methods(official_qt):
    qt, _ = official_qt
    h = built("diagramscene", qt)
    try:
        scene = h.controls["scene"]
        h.widget.buttonGroupClicked(0)
        scene.mousePressEvent(
            SimpleNamespace(
                button=lambda: qt.QtCore.Qt.LeftButton,
                scenePos=lambda: qt.QtCore.QPointF(100, 100),
            )
        )
        native = qt.QtGui.QGraphicsScene.items(scene)[0]
        with pytest.raises(AttributeError):
            native.removeArrows()
        original = scene.items()[0]
        assert original is not native and hasattr(original, "removeArrows")
        original.setSelected(True)
        for method, button in [
            (h.widget.itemColorChanged, h.widget.fillColorToolButton),
            (h.widget.lineColorChanged, h.widget.lineColorToolButton),
            (h.widget.textColorChanged, h.widget.fontColorToolButton),
        ]:
            # Each QAction has its own binding; the Python slot accepts that action.
            menu = read(button, "menu")
            for action in menu.actions():
                action.trigger()
        h.widget.deleteItem()
        assert h.snapshot()["item_count"] == 0
    finally:
        h.close()


def test_elastic_nodes_keep_python_objects_and_expose_center_control(official_qt):
    qt, _ = official_qt
    h = built("elasticnodes", qt)
    try:
        native = h.widget.scene().items()[0]
        with pytest.raises(AttributeError):
            native.calculateForces()
        before = h.snapshot()["positions"]
        h.controls["centerNode"].moveBy(40, 0)
        h.controls["step"]()
        state = h.snapshot()
        assert state["node_count"] == 9 and state["edge_count"] == 12
        assert state["positions"] != before
    finally:
        h.close()


@pytest.mark.parametrize(
    "name", ["spinboxdelegate", "stardelegate", "spreadsheet", "coloreditorfactory"]
)
def test_all_retained_delegate_editors_expire_on_destroyed(name, official_qt):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        if name == "coloreditorfactory":
            editor = h.controls["delegate"].creator.createWidget(h.widget)
        elif name == "spreadsheet":
            delegate = h.controls["table"].itemDelegate()
            model = qt.QtGui.QStandardItemModel(10, 6, h.widget)
            editor = delegate.createEditor(h.widget, None, model.index(1, 0))
        else:
            delegate = h.controls["delegate"]
            model = h.controls.get("model") or qt.QtGui.QStandardItemModel(
                1, 4, h.widget
            )
            model.setData(model.index(0, 3), 5)
            index = model.index(0, 3 if name == "stardelegate" else 0)
            editor = delegate.createEditor(h.widget, None, index)
        assert h.controls["editor"] is editor
        editor.deleteLater()
        assert "editor" not in h.controls
        assert "editor" not in h.snapshot()["controls"]
    finally:
        h.close()


def test_spreadsheet_delegate_commits_formula_and_date_action_without_sender(
    official_qt,
):
    qt, _ = official_qt
    h = built("spreadsheet", qt)
    try:
        table = h.controls["table"]
        delegate = table.itemDelegate()
        model = qt.QtGui.QStandardItemModel(10, 6, h.widget)
        index = model.index(1, 2)
        editor = delegate.createEditor(h.widget, None, index)
        delegate.setEditorData(editor, index)
        assert read(editor, "text") == "150"
        editor.setText("200")
        delegate.setModelData(editor, model, index)
        assert h.snapshot()["total"] == 21933
        editor.deleteLater()
        actions = h.widget.dateFormatMenu.actions()
        actions[1].trigger()
        assert h.widget.currentDateFormat == "yyyy/M/dd"
        assert h.snapshot()["formulas"][1][1] == "2006/6/15"
    finally:
        h.close()


def test_editor_destroyed_notification_does_not_drop_a_newer_editor(official_qt):
    qt, _ = official_qt
    h = built("spinboxdelegate", qt)
    try:
        delegate, model = h.controls["delegate"], h.controls["model"]
        index = model.index(0, 0)
        first = delegate.createEditor(h.widget, None, index)
        second = delegate.createEditor(h.widget, None, index)
        first.deleteLater()
        assert h.controls["editor"] is second
        assert "editor" in h.snapshot()["controls"]
        second.deleteLater()
        assert "editor" not in h.snapshot()["controls"]
    finally:
        h.close()


@pytest.mark.parametrize("name", ["broadcastsender", "broadcastreceiver"])
def test_udp_incomplete_write_does_not_report_a_sent_message(
    name, official_qt, monkeypatch
):
    qt, _ = official_qt
    h = built(name, qt)
    try:
        invoke = qt.QtNetwork.QUdpSocket._invoke

        def incomplete(self, key, *args, **kwargs):
            return 1 if key == "writeDatagram" else invoke(self, key, *args, **kwargs)

        monkeypatch.setattr(qt.QtNetwork.QUdpSocket, "_invoke", incomplete)
        h.controls["sendSample"]()
        state = h.snapshot()
        assert state["message_no"] == 1 and not state["received"]
        assert state["error"] == "Incomplete owned UDP datagram"
    finally:
        h.close()
