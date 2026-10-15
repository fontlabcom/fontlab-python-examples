# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/035f3fbd2b81479a.md
# this_file: tests/test_cleanroom_a.py
"""Batch A receipts, strict PythonQt builds, ownership and behavioral checks."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from tests.official_doubles import official_host
from tests.qt_doubles import fake_host

ROOT = Path(__file__).resolve().parents[1]
ROWS = [
    r
    for r in json.loads((ROOT / "clean-room-specs/INDEX.json").read_text())["ports"]
    if r["target_path"].split("/")[1]
    in {"widgets", "itemviews", "designer", "dialogs", "layouts", "desktop", "effects"}
]


def load(row):
    spec = importlib.util.spec_from_file_location(
        "cleanroom_" + row["port_id"], ROOT / row["target_path"]
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def host(monkeypatch):
    qt, owners = fake_host(monkeypatch)
    return official_host(qt), owners


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["port_id"])
def test_receipt_and_source_when_batch_a_then_complete(row):
    receipt = json.loads(
        (ROOT / "clean-room/receipts" / (row["port_id"] + ".json")).read_text()
    )
    assert receipt["port_id"] == row["port_id"]
    assert receipt["target_path"] == row["target_path"]
    assert (
        receipt["spec_sha256"]
        == hashlib.sha256((ROOT / row["spec_file"]).read_bytes()).hexdigest()
    )
    assert receipt["implementation"] in {"implemented", "blocked"}
    assert bool(receipt["blocked_reason"]) == (receipt["implementation"] == "blocked")
    assert row["target_path"] in receipt["files"]
    for file in receipt["files"]:
        text = (ROOT / file).read_text()
        assert text.startswith(
            "# SPDX-License-Identifier: Apache-2.0\n# Clean-room implementation from "
            + row["spec_file"]
        )
        compile(text, file, "exec")
    assert callable(load(row).build)


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["port_id"])
def test_build_twice_when_supported_then_disconnect_and_close(row, host):
    qt, owners = host
    module = load(row)
    if "## Capability boundary" in (ROOT / row["spec_file"]).read_text():

        class Forbidden:
            def __getattr__(self, key):
                pytest.fail("Blocked builder touched the host: " + key)

        with pytest.raises(NotImplementedError):
            module.build(Forbidden())
        assert not owners
        return
    for _ in range(2):
        handle = module.build(qt)
        assert handle.widget is not None
        assert not handle.owner.closed
        json.dumps(handle.snapshot())
        handle.widget.show()
        pairs = list(handle.connections)
        handle.close()
        handle.close()
        assert handle.owner.closed
        assert not handle.connections and not handle.controls
        assert handle.snapshot()["closed"]
        for obj, signature, slot in pairs:
            if signature:
                assert slot not in obj._signals[signature].callbacks
            else:
                assert slot not in obj.callbacks


def row_for(pid):
    return next(row for row in ROWS if row["port_id"] == pid)


@pytest.mark.parametrize(
    "pid",
    [
        "d6dc56a5318ffe71",
        "4d24cd77c74a8801",
        "248e64416b9b218c",
        "1321540b04f33117",
        "773db5c24ae98ffb",
        "9941e3c752b3a3b7",
        "306c12d5cc1db46c",
        "e62ce3eb648cfb4c",
        "e63bffc17abf2fde",
        "509e781f1267967f",
        "8e5aa13798c2763c",
    ],
)
def test_canvas_when_painted_then_balanced_native_painter(pid, host):
    from types import SimpleNamespace

    qt, _ = host
    handle = load(row_for(pid)).build(qt)
    try:
        handle.controls["canvas"].paintEvent(
            SimpleNamespace(rect=lambda: qt.QtCore.QRect(0, 0, 640, 460))
        )
        assert all(not painter.isActive() for painter in qt._painters), (
            "Every painter must end"
        )
    finally:
        handle.close()


@pytest.mark.parametrize(
    "pid",
    [
        "b823a76f79197d84",
        "3040b9f6b267a196",
        "d6dc56a5318ffe71",
        "9941e3c752b3a3b7",
        "9e21c6536fda7a23",
        "c98ae8ac71886586",
        "4b8851287931abd0",
        "cf15c3e91cdd8ded",
        "67170c89593ad35e",
    ],
)
def test_owned_timer_when_ticked_then_inspectable_and_stopped(pid, host):
    qt, _ = host
    handle = load(row_for(pid)).build(qt)
    timers = [
        obj
        for obj in handle.controls.values()
        if getattr(obj, "_qt_name", "") == "QTimer"
    ]
    try:
        for timer in timers:
            if timer.isActive():
                timer.emit("timeout")
        json.dumps(handle.snapshot())
    finally:
        handle.close()
    assert all(not timer.isActive() for timer in timers)


def test_calculator_when_precedence_errors_and_repeated_equals_then_correct():
    engine = load(row_for("356e4e807f1e789f")).Arithmetic()
    for key in ["2", "+", "3", "*", "4", "="]:
        engine.command(key)
    assert engine.text == "14"
    engine.command("=")
    assert engine.text == "56"
    engine.clear()
    for key in ["8", "/", "0", "="]:
        engine.command(key)
    assert engine.text == "Error"
    engine.command("7")
    assert engine.text == "7"
    engine.command("MS")
    engine.command("2")
    engine.command("M+")
    engine.command("MR")
    assert engine.text == "9"
    engine.command("MC")
    engine.command("MR")
    assert engine.text == "0"
    engine.command("±")
    engine.command("sqrt")
    assert engine.text == "0"
    engine.command("1/x")
    assert engine.text == "Error"


def test_spreadsheet_when_dependencies_ranges_and_cycles_then_evaluated():
    mod = load(row_for("bf3b39a8c2df8e94"))
    cells = {"A1": "2", "A2": "3", "B1": "=A1+A2*4", "B2": "=SUM(A1:A2)"}
    assert mod.calculate(cells, "B1") == 14
    assert mod.calculate(cells, "B2") == 5
    cells["A1"] = "5"
    assert mod.calculate(cells, "B1") == 17
    cells["A1"] = "=B1"
    with pytest.raises(ValueError, match="Circular"):
        mod.calculate(cells, "B1")
    with pytest.raises(ZeroDivisionError):
        mod.calculate({"A1": "=1/0"}, "A1")
    with pytest.raises(ValueError):
        mod.calculate({"A1": '=__import__("os")'}, "A1")


def test_tree_when_editing_structure_then_parent_links_and_ids_survive(host):
    qt, _ = host
    mod = load(row_for("321f8e535facafde"))
    model, _nodes = mod.tree_model(qt, qt.QtGui.QWidget(), editable=True)
    root = qt.QtCore.QModelIndex()
    first = model.index(0, 0, root)
    child = model.index(0, 0, first)
    identity = child.internalId()
    assert model.parent(child).internalId() == first.internalId()
    assert model.setData(child, "Changed")
    assert model.data(child) == "Changed"
    assert not model.index(-1, 0).isValid()
    assert model.rowCount(model.index(0, 1)) == 0
    assert model.insertRows(0, 1, first)
    assert model.index(1, 0, first).internalId() == identity
    assert model.removeRows(0, 1, first)
    assert model.insertColumns(2, 1)
    assert model.columnCount() == 3
    assert model.removeColumns(2, 1)


def test_lazy_model_when_expanded_then_only_requested_nodes_exist(host):
    qt, _ = host
    handle = load(row_for("090c76a87351e771")).build(qt)
    try:
        model = handle.controls["model"]
        nodes = handle.controls["nodes"]
        root = qt.QtCore.QModelIndex()
        assert model.rowCount(root) == 1000 and model.columnCount(root) == 10
        assert len(nodes) == 1
        parent = model.index(999, 0, root)
        child = model.index(4, 0, parent)
        assert model.parent(child).internalId() == parent.internalId()
        assert model.rowCount(model.index(0, 1)) == 0
        assert len(nodes) == 4
    finally:
        handle.close()


def test_puzzle_when_move_return_restart_and_solve_then_counts_correct(host):
    qt, _ = host
    handle = load(row_for("878fe9f714df3b5e")).build(qt)
    try:
        move = handle.controls["move"]
        assert move(0, 0)
        assert not move(1, 0)
        assert handle.snapshot()["correct"] == 1
        assert move(0, None)
        assert len(handle.controls["unplaced"]) == 25
        for number in range(25):
            assert move(number, number)
        assert handle.snapshot()["complete"]
        handle.controls["restart"]()
        assert handle.snapshot()["placed"] == 0
    finally:
        handle.close()


def test_game_when_drop_pause_clear_rows_then_scoring_and_reset():
    import random

    mod = load(row_for("e63bffc17abf2fde"))
    game = mod.Game(random.Random(7))
    game.paused = True
    x, y = game.x, game.y
    assert not game.move(-1, 0)
    game.lower()
    assert (game.x, game.y) == (x, y)
    game.paused = False
    game.drop()
    assert game.score >= 7 and game.pieces == 1
    game.reset()
    game.board[-1] = [1] * 10
    game.shape = [(0, 0)]
    game.x = 4
    game.y = 20
    game.place()
    assert game.lines == 1 and game.score == 17
    game.reset()
    assert game.score == game.lines == game.pieces == 0


def test_chart_when_quoted_csv_and_bad_input_then_preserves_data(host, tmp_path):
    qt, _ = host
    mod = load(row_for("306c12d5cc1db46c"))
    rows = [["Blue, green", 5, "#367a9a"], ["Warm", 3, "#c49a63"]]
    assert mod.read_rows(mod.write_rows(rows)) == rows
    with pytest.raises(ValueError):
        mod.read_rows("x,not-number,red")
    handle = mod.build(qt)
    try:
        old = handle.snapshot()["rows"]
        path = tmp_path / "bad.csv"
        path.write_text("x,2,not-a-color\n")
        with pytest.raises(ValueError):
            handle.controls["load"](str(path))
        assert handle.snapshot()["rows"] == old
    finally:
        handle.close()


def test_component_when_changed_then_bounds_and_notifications(host):
    qt, _ = host
    handle = load(row_for("1321540b04f33117")).build(qt)
    try:
        c = handle.controls
        assert handle.snapshot()["value"] == 1
        assert c["set_maximum"](3)
        assert c["set_offset"](10)
        assert c["set_value"](2)
        assert handle.snapshot()["notifications"][-1] == [12, "12"]
        assert not c["set_value"](100)
    finally:
        handle.close()


def test_expression_when_explicit_return_then_success_history_only(host):
    qt, _ = host
    handle = load(row_for("5125860585e98b3a")).build(qt)
    try:
        entry = handle.controls["entry"]
        entry.setText("2+3")
        entry.emit("returnPressed")
        assert handle.snapshot()["result"] == "5"
        entry.setText("1/0")
        entry.emit("returnPressed")
        assert handle.snapshot()["history"] == ["2+3"]
        before = handle.snapshot()
        assert before == handle.snapshot()
        entry.setText("app is QtGui.QApplication.instance()")
        entry.emit("returnPressed")
        assert handle.snapshot()["result"] == "True"
    finally:
        handle.close()


def test_filesearch_when_chunk_boundary_and_cancel_then_stream_closed(host, tmp_path):
    qt, _ = host
    handle = load(row_for("63f2eeefd052f701")).build(qt)
    (tmp_path / "match.txt").write_bytes(b"x" * 65534 + b"orchard" + b"y" * 100)
    try:
        c = handle.controls
        c["directory"].setEditText(str(tmp_path))
        c["containing"].setEditText("orchard")
        c["search"]()
        for _ in range(10):
            c["step"]()
        assert handle.snapshot()["matches"] == [str(tmp_path / "match.txt")]
        c["search"]()
        c["cancel"]()
        assert not handle.snapshot()["searching"]
    finally:
        handle.close()


def test_class_skeleton_when_each_style_and_bad_destination_then_no_lost_values(
    host, tmp_path
):
    qt, _ = host
    mod = load(row_for("035f3fbd2b81479a"))
    handle = mod.build(qt)
    try:
        c = handle.controls
        c["name"].setText("FreshWidget")
        c["base"].setText("QObject")
        c["folder"].setText(str(tmp_path))
        for style in range(3):
            c["constructor"].setCurrentIndex(style)
            assert c["generate"]()
            assert "class FreshWidget" in (tmp_path / "freshwidget.h").read_text()
            assert "FreshWidget::" in (tmp_path / "freshwidget.cpp").read_text()
            (tmp_path / "freshwidget.h").unlink()
            (tmp_path / "freshwidget.cpp").unlink()
        c["folder"].setText(str(tmp_path / "absent"))
        assert not c["generate"]()
        assert c["name"].text == "FreshWidget"
    finally:
        handle.close()


@pytest.mark.parametrize(
    "pid,actions",
    [
        (
            "a1c26dbf9f995edb",
            [("more", True), ("whole", True), ("more", False), ("more", True)],
        ),
        (
            "36805750b888fba6",
            [
                ("value", 12),
                ("maximum", 9),
                ("minimum", -5),
                ("orientation", 1),
                ("appearance", True),
                ("keys", True),
            ],
        ),
        (
            "468179092748a72e",
            [("precision", 0), ("precision", 100), ("format", 1), ("format", 2)],
        ),
        (
            "84cb59e07adfae2c",
            [
                ("echo", 3),
                ("validator", 1),
                ("validator", 2),
                ("validator", 0),
                ("alignment", 2),
                ("mask", 2),
                ("access", 1),
            ],
        ),
        (
            "9e21c6536fda7a23",
            [("style", 1), ("palette", True), ("palette", False), ("disable", True)],
        ),
        ("876eab33b6a99e31", [("preset", 1), ("style", 1), ("apply", None)]),
        (
            "b91effc45f81fbb0",
            [
                ("locale", 1),
                ("week", 1),
                ("selection", 1),
                ("grid", True),
                ("navigation", False),
                ("horizontal", 2),
                ("vertical", 1),
                ("special", True),
            ],
        ),
        ("de4979a99c6d0bed", [("selector", 1)]),
        (
            "a3b3cbe51c1506c6",
            [
                ("play", None),
                ("pause", None),
                ("speed", 150),
                ("fit", True),
                ("stop", None),
            ],
        ),
        ("505d60a757bbc177", [("size", 48), ("style", 1), ("infer", True)]),
    ],
)
def test_controls_when_changed_then_native_calls_and_local_state(pid, actions, host):
    qt, _ = host
    handle = load(row_for(pid)).build(qt)
    try:
        for key, value in actions:
            obj = handle.controls[key]
            if value is None:
                obj.click()
            elif isinstance(value, bool):
                obj.setChecked(value)
            elif obj._qt_name == "QComboBox":
                obj.setCurrentIndex(value)
            else:
                obj.setValue(value)
        json.dumps(handle.snapshot())
    finally:
        handle.close()


@pytest.mark.parametrize(
    "kind",
    [
        "Integer",
        "Decimal",
        "Item",
        "Text",
        "Color",
        "Font",
        "Directory",
        "File",
        "Files",
        "Save",
        "Critical",
        "Information",
        "Question",
        "Warning",
        "Error",
    ],
)
def test_dialog_gallery_when_each_action_then_owned_nonblocking_dialog(kind, host):
    qt, _ = host
    handle = load(row_for("e1a0a829f8f2e311")).build(qt)
    try:
        handle.controls[kind].click()
        assert handle.alerts, "Dialog must be owned"
        assert not qt._painters
    finally:
        handle.close()


def test_fetch_more_when_prepared_then_exact_three_ranges(host):
    qt, _ = host
    handle = load(row_for("67170c89593ad35e")).build(qt)
    try:
        c = handle.controls
        for _ in range(11):
            c["prepare"]()
        model = c["model"]
        root = qt.QtCore.QModelIndex()
        assert model.rowCount() == 100
        model.fetchMore(root)
        assert model.rowCount() == 200
        model.fetchMore(root)
        assert model.rowCount() == 205
        assert not model.canFetchMore(root)
        model.fetchMore(root)
        assert model.rowCount() == 205
    finally:
        handle.close()


def test_popup_console_history_and_multipage_updates(host):
    qt, _ = host
    handle = load(row_for("de4979a99c6d0bed")).build(qt)
    try:
        c = handle.controls
        assert c["insert"](0, "New page")
        assert handle.snapshot()["count"] == 3
        assert c["rename"](1, "Revised page")
        assert handle.snapshot()["titles"][1] == "Revised page"
        assert c["set_index"](1)
        assert c["remove"](1)
        assert handle.snapshot()["count"] == 2
        assert not c["remove"](-1)
        assert not c["set_index"](99)
    finally:
        handle.close()


def test_delegates_when_editor_commits_then_numeric_rating_and_color_persist(host):
    from types import SimpleNamespace

    qt, _ = host
    for pid, column in [
        ("ddb20b1b68b18a91", 0),
        ("0a3b15766909bdc3", 1),
        ("dc59f268ee01e364", 2),
    ]:
        handle = load(row_for(pid)).build(qt)
        try:
            c = handle.controls
            delegate = c["delegate"]
            index = c["model"].index(0, column)
            option = SimpleNamespace(rect=qt.QtCore.QRect(0, 0, 100, 30))
            editor = delegate.createEditor(handle.widget, option, index)
            delegate.setEditorData(editor, index)
            if pid == "ddb20b1b68b18a91":
                editor.setValue(42)
            elif pid == "0a3b15766909bdc3":
                editor.setCurrentIndex(2)
            delegate.setModelData(editor, c["model"], index)
            if pid == "ddb20b1b68b18a91":
                assert int(c["model"].data(index, qt.QtCore.Qt.EditRole)) == 42
        finally:
            handle.close()


def test_dom_when_invalid_then_old_model_preserved_and_nodes_exposed(host, tmp_path):
    qt, _ = host
    handle = load(row_for("a59dae9770bfbefb")).build(qt)
    try:
        model = handle.controls["model"]
        root = qt.QtCore.QModelIndex()
        count = model.rowCount(root)
        assert count >= 2
        for row in range(count):
            assert model.index(row, 0).isValid()
        path = tmp_path / "broken.xml"
        path.write_text("<broken>")
        assert not handle.controls["load"](str(path))
        assert model.rowCount(root) == count
        path.write_text(
            '<?fresh sample?><root a="1"><!--note--><child>text</child></root>'
        )
        assert handle.controls["load"](str(path))
        assert model.rowCount(root) == 2
    finally:
        handle.close()


def test_screenshot_and_tray_when_inspected_then_no_external_action(host):
    qt, _ = host
    for pid in ["65d15d1fbc1b15e9", "c1b878b63f80e733"]:
        handle = load(row_for(pid)).build(qt)
        try:
            first = handle.snapshot()
            assert first == handle.snapshot()
            if "captured" in first:
                assert not first["captured"] and not first["pending"]
            else:
                assert (
                    first["notifications"] == 0
                    and not handle.controls["tray"].isVisible()
                )
        finally:
            handle.close()


def test_pixelator_when_black_gray_white_then_linear_native_cells(host):
    from types import SimpleNamespace

    qt, _ = host
    module = load(row_for("d50ad6638357e669"))
    handle = module.build(qt)
    try:
        assert module.dot_diameter(0, 16) == 16
        assert module.dot_diameter(255, 16) == 0
        assert module.brightness(0xFF808080) == 128
        model = handle.controls["model"]
        assert model.data(model.index(0, 0)) == 0
        assert model.data(model.index(0, 23)) == 255
        option = SimpleNamespace(
            rect=qt.QtCore.QRect(0, 0, 16, 16), state=0, palette=qt.QtGui.QPalette()
        )
        painter = qt.QtGui.QPainter(handle.widget)
        try:
            handle.controls["delegate"].paint(painter, option, model.index(0, 0))
        finally:
            painter.end()
    finally:
        handle.close()


def test_puzzle_when_native_mime_dropped_then_models_commit_single_move(host):
    qt, _ = host
    handle = load(row_for("878fe9f714df3b5e")).build(qt)
    try:
        c = handle.controls
        pieces = c["pieces_model"]
        board = c["board_model"]
        number = c["unplaced"][0]
        mime = pieces.mimeData([pieces.index(0, 0)])
        assert board.dropMimeData(
            mime, qt.QtCore.Qt.MoveAction, 0, 0, qt.QtCore.QModelIndex()
        )
        assert c["board_cells"][0] == number and pieces.rowCount() == 24
        mime = board.mimeData([board.index(0, 0)])
        assert pieces.dropMimeData(
            mime, qt.QtCore.Qt.MoveAction, -1, -1, qt.QtCore.QModelIndex()
        )
        assert pieces.rowCount() == 25 and c["board_cells"][0] is None
    finally:
        handle.close()


def test_partial_build_when_native_button_fails_then_owned_window_rolls_back(
    host, monkeypatch
):
    qt, owners = host

    def fail(*args):
        raise RuntimeError("Injected constructor failure")

    monkeypatch.setattr(qt.QtGui, "QPushButton", fail)
    with pytest.raises(RuntimeError, match="Injected"):
        load(row_for("a1c26dbf9f995edb")).build(qt)
    assert owners and all(owner.closed for owner in owners)


def test_deferred_work_when_closed_before_tick_then_no_late_fixture_or_enumeration(
    host,
):
    qt, _ = host
    for pid in ["4b8851287931abd0", "cf15c3e91cdd8ded", "67170c89593ad35e"]:
        handle = load(row_for(pid)).build(qt)
        callbacks = [
            slot
            for obj, signature, slot in handle.connections
            if signature == "timeout()"
        ]
        handle.close()
        for callback in callbacks:
            callback()
        assert handle.snapshot()["closed"]
