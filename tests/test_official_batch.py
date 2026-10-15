# SPDX-License-Identifier: Apache-2.0
# this_file: tests/test_official_batch.py
"""Receipt-backed replacement contracts and unchanged non-official batch coverage.

The former official-demo tests depended on the removed implementation's Python
attributes, exact fixtures and archived resources. The independent behavioral
checks are in test_cleanroom_a/b/c; this file tests their public launcher boundary.
The non-official batch tests below remain active against their unchanged ports.
"""

import ast
import hashlib
import json
from importlib import util
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.official_doubles import official_host
from tests.qt_doubles import fake_host

ROOT = Path(__file__).resolve().parents[1]


def records():
    ids = {
        row["port_id"]
        for row in json.loads((ROOT / "clean-room-specs/INDEX.json").read_text())[
            "ports"
        ]
    }
    return [
        r
        for r in json.loads((ROOT / "catalog/ports.json").read_text())["ports"]
        if r["source_id"] in ids
    ]


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


def built(name, qt):
    row = next(r for r in records() if r["name"] == "Official " + name)
    return load_record(row).build(qt)


@pytest.mark.parametrize("row", records(), ids=lambda r: r["source_id"])
def test_replacement_when_catalogued_then_receipt_and_independent_source_match(row):
    receipt = json.loads((ROOT / row["clean_room_receipt"]).read_text())
    assert receipt["implementation"] == row["implementation"]
    assert (
        receipt["spec_sha256"]
        == row["license"]["spec_sha256"]
        == hashlib.sha256((ROOT / row["spec"]).read_bytes()).hexdigest()
    )
    assert (
        row["license"]["selected"] == "Apache-2.0"
        and row["license"]["review_state"] == "reviewed"
    )
    # Native runs are recorded by tools/record_native.py: passed needs evidence.
    assert row["native_acceptance"] in {"unexecuted", "passed"}
    assert ("native_evidence" in row) == (row["native_acceptance"] == "passed")
    if row["implementation"] == "blocked":
        assert row["native_acceptance"] == "unexecuted"
    for file in receipt["files"]:
        path = ROOT / file
        assert path.is_file()
        if path.suffix == ".py":
            ast.parse(path.read_text(), feature_version=(3, 11))
    assert callable(load_record(row).build)


@pytest.mark.parametrize(
    "row",
    [r for r in records() if r["implementation"] == "implemented"],
    ids=lambda r: r["source_id"],
)
def test_replacement_when_launched_through_public_registry_then_owned_close(
    row, official_qt, monkeypatch
):
    from fontlab_python_examples import launcher

    qt, _owners = official_qt
    monkeypatch.setattr(launcher, "_host", lambda: qt)
    monkeypatch.setattr(launcher, "_handles", {})
    try:
        handle = launcher.launch(row["source_id"])
        assert handle.widget.isVisible() and not handle.owner.closed
        assert launcher.get(row["source_id"]) is handle
        assert launcher.launch(row["source_id"]) is handle, (
            "Reshow must not create another owner"
        )
        state = launcher.inspect(row["source_id"])
        assert state["visible"] and state["launched"] and not state["closed"]
        json.dumps(state)
        connections = list(handle.connections)
        closed = launcher.close(row["source_id"])
        assert closed["closed"] and not closed["launched"]
        assert handle.owner.closed and not handle.controls and not handle.connections
        for obj, signature, slot in connections:
            assert slot not in (
                obj._signals[signature].callbacks if signature else obj.callbacks
            )
        assert not launcher._handles
        launcher.close(row["source_id"])
    finally:
        launcher.close(row["source_id"])


@pytest.mark.parametrize(
    "row",
    [r for r in records() if r["implementation"] == "blocked"],
    ids=lambda r: r["source_id"],
)
def test_replacement_when_blocked_then_capability_failure_precedes_host(
    row, monkeypatch
):
    from fontlab_python_examples import launcher

    def forbidden(*args):
        pytest.fail("Blocked launcher accessed the host or builder")

    monkeypatch.setattr(launcher, "_host", forbidden)
    monkeypatch.setattr(launcher, "_builder", forbidden)
    with pytest.raises(NotImplementedError) as caught:
        launcher.launch(row["source_id"])
    assert row["blocked_reason"] in str(caught.value)

    class NoHost:
        def __getattr__(self, name):
            pytest.fail("Blocked builder accessed host: " + name)

    with pytest.raises(NotImplementedError):
        load_record(row).build(NoHost())


def check_unchanged_handle(row, official_qt):
    qt, _owners = official_qt
    handle = load_record(row).build(qt)
    try:
        assert handle.controls and "window" in handle.controls
        state = handle.snapshot()
        assert state["title"] and state["controls"]
        json.dumps(state)
        pairs = list(handle.connections)
        handle.close()
        assert handle.owner.closed and not handle.controls and not handle.connections
        for obj, signature, callback in pairs:
            assert callback not in obj._signals[signature].callbacks
        handle.close()
    finally:
        handle.close()


def check_blocked_record(row, monkeypatch):
    from fontlab_python_examples import launcher

    def forbidden(*args):
        pytest.fail("Blocked record accessed host")

    monkeypatch.setattr(launcher, "_host", forbidden)
    with pytest.raises(NotImplementedError) as caught:
        launcher.launch(row["source_id"])
    assert row["blocked_reason"] in str(caught.value)


def owned_directory(handle):
    """Use the same Demo ownership record as the native interaction driver."""
    demo = next(
        f.__self__
        for f in handle.release
        if hasattr(getattr(f, "__self__", None), "temp_dir")
    )
    return Path(demo.temp_dir()).resolve()


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
    "83bc55d45ae367d0",
    "92fc3cf4b5dd009c",
    "88fa78cafb505cfa",
    "4bc27e706ac146f5",
    "b1c25455dbcb6bac",
    "cb1871959e42607b",
    "edeef5f840c20e15",
    "1e79bddb6d52574d",
    "631cc1bc310c00b9",
    "ecc2e23449331df1",
}


def spin_until(qt, handle, ready):
    import time

    deadline = time.monotonic() + 3
    while not ready() and time.monotonic() < deadline:
        qt._pump_network()
        for obj in list(handle.controls.values()):
            if getattr(obj, "_qt_name", None) == "QTimer" and obj.isActive():
                obj.emit("timeout")
        time.sleep(0.001)
    assert ready(), "Owned local transport did not deliver before the test deadline"


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
    assert row["native_acceptance"] == (
        "passed" if row["implementation"] == "implemented" else "unexecuted"
    )
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
    [
        r
        for r in batch_nine_records()
        if r["implementation"] in ("implemented", "clean_room_pending")
    ],
    ids=lambda r: r["source_id"],
)
def test_batch_nine_build_inspect_controls_disconnect_and_close(row, official_qt):
    check_unchanged_handle(row, official_qt)


@pytest.mark.parametrize(
    "row",
    [
        r
        for r in batch_nine_records()
        if r["implementation"] in ("blocked", "clean_room_pending")
    ],
    ids=lambda r: r["source_id"],
)
def test_batch_nine_blockers_reject_before_host_access(row, monkeypatch):
    check_blocked_record(row, monkeypatch)


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
    [
        r
        for r in batch_nine_records()
        if r["implementation"] in ("implemented", "clean_room_pending")
    ],
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
            "map",
        ),
        ("ecc2e23449331df1", "loopback"),
    ],
)
def test_batch_nine_reused_network_ports_preserve_real_interactions(
    id, scenario, official_qt, monkeypatch
):
    qt, _ = official_qt
    handle = nine(id, qt)
    try:
        assert handle.controls and not handle.owner.closed
        state = handle.snapshot()
        assert state["endpoint"]["host"] == "127.0.0.1"
        if scenario == "map":
            handle.controls["pan"](qt.QtCore.QPoint(16, 0))
            assert handle.snapshot()["longitude"] != state["longitude"]
            handle.controls["berlinAction"].trigger()
            assert handle.snapshot()["latitude"] != state["latitude"]
            handle.controls["nightModeAction"].trigger()
            assert handle.snapshot()["night_mode"]
            handle.controls["activateZoom"]()
            assert handle.snapshot()["zoomed"]
        else:
            assert state["total_bytes"] == 50 * 1024 * 1024
            handle.controls["startButton"].click()
            spin_until(
                qt,
                handle,
                lambda: handle.snapshot()["bytes_received"] == state["total_bytes"],
            )
            assert handle.snapshot()["bytes_written"] == state["total_bytes"]
        qt._pump_network()
        json.dumps(handle.snapshot())
    finally:
        handle.close()
    assert handle.owner.closed and not handle.connections


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
