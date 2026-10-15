# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/7da7020aa7e2732b.md
# Batch b acceptance checks also cover every assigned spec in INDEX.json.
# this_file: tests/test_cleanroom_b.py
"""Independent batch contracts; these checks do not claim native rendering."""

import ast
import hashlib
import importlib.util
import json
import math
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.official_doubles import official_host
from tests.qt_doubles import fake_host

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "quick",
    "qml",
    "network",
    "mainwindows",
    "tutorials",
    "graphicsview",
    "draganddrop",
    "painting",
}
ROWS = [
    r
    for r in json.loads((ROOT / "clean-room-specs/INDEX.json").read_text())["ports"]
    if r["target_path"].split("/")[1] in CATEGORIES
]


def module(row):
    spec = importlib.util.spec_from_file_location(
        "cleanroom_b_" + row["port_id"], ROOT / row["target_path"]
    )
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.fixture
def boundary(monkeypatch):
    qt, owners = fake_host(monkeypatch)
    return official_host(qt), owners


@pytest.mark.parametrize("row", ROWS, ids=lambda r: Path(r["target_path"]).stem)
def test_receipt_source_and_launch_lifetime(row, boundary):
    source = ROOT / row["target_path"]
    text = source.read_text()
    assert text.startswith(
        "# SPDX-License-Identifier: Apache-2.0\n# Clean-room implementation from "
        + row["spec_file"]
        + "\n"
    )
    ast.parse(text, feature_version=(3, 11))
    receipt = json.loads(
        (ROOT / "clean-room/receipts" / (row["port_id"] + ".json")).read_text()
    )
    assert receipt["port_id"] == row["port_id"]
    assert receipt["target_path"] == row["target_path"]
    assert (
        receipt["spec_sha256"]
        == hashlib.sha256((ROOT / row["spec_file"]).read_bytes()).hexdigest()
    )
    assert row["target_path"] in receipt["files"]
    assert all((ROOT / name).is_file() for name in receipt["files"])
    port = module(row)
    qt, owners = boundary
    if "## Capability boundary" in (ROOT / row["spec_file"]).read_text():
        assert receipt["implementation"] == "blocked" and receipt["blocked_reason"]

        class NoHost:
            def __getattr__(self, key):
                raise AssertionError("Blocked build accessed the host: " + key)

        with pytest.raises(NotImplementedError, match="QtQml|QtQuick"):
            port.build(NoHost())
        assert not owners
        return
    assert (
        receipt["implementation"] == "implemented" and receipt["blocked_reason"] is None
    )
    for _ in range(2):
        handle = port.build(qt)
        handle.widget.show()
        assert handle.snapshot()["closed"] is False
        assert handle.controls
        handle.close()
        assert handle.snapshot()["closed"] is True
        assert not handle.connections and not handle.cleanup
    assert all(owner.closed for owner in owners)


def get_port(prefix):
    return module(
        next(r for r in ROWS if Path(r["target_path"]).name.startswith(prefix + "-"))
    )


def until(qt, callback, condition, timeout=4):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        qt._pump_network()
        callback()
        if condition():
            return
        time.sleep(0.005)
    assert condition(), (
        "Owned asynchronous operation did not finish before its deadline"
    )


@pytest.mark.parametrize("stage", range(2, 8))
def test_contacts_reject_duplicates_cancel_and_browse(stage, boundary):
    qt, _ = boundary
    handle = get_port("part" + str(stage)).build(qt)
    c = handle.controls
    try:
        for name in ("Zinnia", "Aster", "Moss"):
            c["Add"].click()
            c["name"].setText(name)
            c["address"].setPlainText("<literal>\nSecond line; \\ value")
            c["submit"]()
        assert len(c["contacts"]) == 3
        c["Add"].click()
        c["name"].setText("Aster")
        c["address"].setPlainText("Duplicate")
        c["submit"]()
        assert len(c["contacts"]) == 3
        assert c["controller"].state["mode"] == "add"
        c["cancel"]()
        assert c["name"].text == "Moss"
        if stage >= 3:
            c["navigate"](1)
            assert c["name"].text == "Zinnia"
            c["navigate"](1)
            assert c["name"].text == "Aster"
        if stage >= 4:
            c["Edit"].click()
            c["name"].setText("Renamed")
            c["cancel"]()
            assert "Renamed" not in c["contacts"]
            c["remove"](False)
            assert len(c["contacts"]) == 3
            c["remove"](True)
            assert len(c["contacts"]) == 2
    finally:
        handle.close()


def test_contact_persistence_rejects_invalid_and_escaped_paths(boundary, tmp_path):
    qt, _ = boundary
    handle = get_port("part7").build(qt)
    c = handle.controls
    try:
        c["Add"].click()
        c["name"].setText("Aster; Studio")
        c["address"].setPlainText("First; road\nBack\\lane")
        c["submit"]()
        root = c["controller"].root()
        collection = root / "contacts.json"
        c["save_file"](collection)
        c["load_file"](collection)
        assert c["contacts"] == {"Aster; Studio": "First; road\nBack\\lane"}
        for payload in ("{}", "[]", '{"x":1}', "null", "not json", '{"x":""}'):
            bad = root / "bad.json"
            bad.write_text(payload)
            with pytest.raises(ValueError):
                c["load_file"](bad)
            assert len(c["contacts"]) == 1
        with pytest.raises(ValueError):
            c["save_file"](tmp_path / "outside.json")
        symlink = root / "outside"
        symlink.symlink_to(tmp_path, target_is_directory=True)
        with pytest.raises(ValueError):
            c["save_file"](symlink / "bad.json")
        card = root / "contact.vcf"
        c["export_file"](card)
        text = card.read_bytes().decode()
        assert "VERSION:2.1\r\n" in text and "Aster\\; Studio" in text
        assert "First\\; road;Back\\\\lane" in text
    finally:
        handle.close()
    assert not root.exists(), "Owned data folder must disappear on teardown"


@pytest.mark.parametrize("name", ["application", "mdi", "sdi", "recentfiles"])
def test_document_roundtrip_cancel_and_failed_save(name, boundary, tmp_path):
    qt, _ = boundary
    handle = get_port(name).build(qt)
    c = handle.controls
    try:
        doc = c["documents"][0]
        doc["editor"].setPlainText("New text — żółć")
        assert doc["modified"]
        called = []
        c["guard"](doc, lambda: called.append(True), "cancel")
        assert not called and doc["editor"].toPlainText() == "New text — żółć"
        path = tmp_path / "owned.txt"
        assert c["save_document"](doc, path)
        assert path.read_text() == "New text — żółć" and not doc["modified"]
        doc["editor"].setPlainText("Changed")
        assert not c["save_document"](doc, tmp_path)
        assert doc["modified"] and doc["editor"].toPlainText() == "Changed"
        c["guard"](doc, lambda: called.append(True), "discard")
        assert called == [True]
        if name in ("mdi", "sdi", "recentfiles"):
            count = len(c["documents"])
            assert c["open_file"](path) is doc
            assert len(c["documents"]) == count
        if name == "recentfiles":
            for i in range(6):
                p = tmp_path / (str(i) + ".txt")
                p.write_text(str(i))
                c["open_file"](p)
            assert len(handle.snapshot()["recent"]) == 5
    finally:
        handle.close()


@pytest.mark.parametrize(
    "name", ["basicdrawing", "painterpaths", "concentriccircles", "transformations"]
)
def test_paint_callbacks_and_extreme_controls(name, boundary):
    qt, _ = boundary
    handle = get_port(name).build(qt)
    try:
        c = handle.controls
        canvas = c["canvas"]
        for shape in range(13 if name == "basicdrawing" else 4):
            c["set_option"]("shape", shape)
            canvas.paintEvent(None)
        for brush in range(8):
            c["set_option"]("brush", brush)
            c["set_option"]("width", 0)
            c["set_option"]("rotation", 360)
            canvas.paintEvent(None)
        assert all(not painter._active for painter in qt._painters)
    finally:
        handle.close()


def test_puzzle_occupancy_restart_and_exact_completion(boundary):
    qt, _ = boundary
    handle = get_port("puzzle").build(qt)
    c = handle.controls
    try:
        assert c["place"](0, 0)
        assert not c["place"](1, 0)
        c["return_tile"](0)
        assert 0 in c["order"] and 0 not in c["positions"]
        for i in range(25):
            assert c["place"](i, i)
        assert handle.snapshot()["correct"] == 25 and handle.snapshot()["completed"]
        assert c["completion"].isActive()
        c["restart"]()
        assert not c["positions"] and len(c["order"]) == 25
        assert handle.snapshot()["correct"] == 0
    finally:
        handle.close()


@pytest.mark.parametrize("name", ["collidingmice", "elasticnodes"])
def test_scene_coincident_positions_remain_finite_and_timers_stop(name, boundary):
    qt, _ = boundary
    handle = get_port(name).build(qt)
    c = handle.controls
    try:
        for node in c["nodes"]:
            node.setPos(0.0, 0.0)
        for _ in range(30):
            c["tick"]()
        assert all(
            math.isfinite(float(node.pos().x()))
            and math.isfinite(float(node.pos().y()))
            for node in c["nodes"]
        )
        timer = c["simulation"]
    finally:
        handle.close()
    assert not timer.isActive()


def test_flow_connectors_deletion_and_zero_length(boundary):
    qt, _ = boundary
    port = get_port("diagramscene")
    assert port.boundary_point(
        (0, 0), (200, 0), [(-50, -30), (50, -30), (50, 30), (-50, 30)]
    ) == (50, 0)
    handle = port.build(qt)
    c = handle.controls
    try:
        a, b = c["add_node"](0, 100, 100), c["add_node"](1, 300, 150)
        assert not c["connect_nodes"](a, a)
        assert c["connect_nodes"](a, b)
        c["nodes"][b]["item"].setPos(350.0, 120.0)
        c["update_links"]()
        assert len(c["links"]) == 1
        c["nodes"][a]["item"].setSelected(True)
        c["delete_selected"]()
        assert not c["links"] and a not in c["nodes"]
    finally:
        handle.close()


@pytest.mark.parametrize("name", ["broadcastsender", "broadcastreceiver"])
def test_udp_owned_delivery_bounded_history_and_cleanup(name, boundary):
    qt, _ = boundary
    handle = get_port(name).build(qt)
    c = handle.controls
    try:
        assert handle.snapshot()["sent"] == 0
        if name == "broadcastreceiver":
            assert "Start" not in c
        for _ in range(105):
            c["sample_send"]()
            c["poll"]()
        until(qt, c["poll"], lambda: handle.snapshot()["received"] == 105)
        assert len(handle.snapshot()["messages"]) == 100
        receiver = c["receiver"]
    finally:
        handle.close()
    assert receiver.fileno() == -1


@pytest.mark.parametrize(
    "name",
    [
        "fortuneclient",
        "blockingfortuneclient",
        "fortuneserver",
        "threadedfortuneserver",
    ],
)
def test_fortune_fragmented_unicode_owned_endpoint_and_worker_cleanup(name, boundary):
    qt, _ = boundary
    port = get_port(name)
    encoded = port.fortune_frame("Zażółć 🌿")
    fragments = bytearray()
    for byte in encoded[:-1]:
        fragments.append(byte)
        assert port.take_frame(fragments) is None
    fragments.append(encoded[-1])
    assert port.take_frame(fragments) == "Zażółć 🌿" and not fragments
    handle = port.build(qt)
    c = handle.controls
    peer = c["peer"]
    try:
        assert not c["request"]("127.0.0.2", peer.port)
        assert c["request"](peer.host, peer.port)
        until(qt, c["poll"], lambda: not handle.snapshot()["busy"])
        assert handle.snapshot()["fortune"] in port.FORTUNES
        assert not handle.snapshot()["error"]
    finally:
        handle.close()
    assert not peer.thread.is_alive() and peer.socket.fileno() == -1


def test_http_download_bytes_cancel_and_foreign_endpoint(boundary):
    qt, _ = boundary
    port = get_port("http")
    handle = port.build(qt)
    c = handle.controls
    root = c["controller"].root()
    try:
        assert not c["download"]("http://example.invalid/sample")
        assert c["download"]()
        until(qt, lambda: None, lambda: not handle.snapshot()["active"])
        assert Path(handle.snapshot()["output"]).read_bytes() == port.FIXTURE
        assert c["download"]()
        c["cancel"]()
        assert not (root / "sample.part").exists()
        qt._pump_network()
        assert not handle.snapshot()["active"]
    finally:
        handle.close()
    assert not root.exists()


def test_map_projection_cache_and_inspection_no_network(boundary):
    qt, _ = boundary
    port = get_port("lightmaps")
    assert port.mercator(0, 0, 3) == (4.0, 4.0)
    assert all(math.isfinite(v) for v in port.mercator(90, 1000, 5))
    handle = port.build(qt)
    c = handle.controls
    try:
        c["fetch"]()
        until(qt, lambda: None, lambda: handle.snapshot()["cache"] > 0)
        count = handle.snapshot()["requests"]
        handle.snapshot()
        assert handle.snapshot()["requests"] == count
        c["fetch"]()
        assert handle.snapshot()["requests"] == count
        c["pan"](300, 0)
        assert handle.snapshot()["requests"] > count
    finally:
        handle.close()


def test_full_fifty_mebibyte_loopback_and_cancel(boundary):
    qt, _ = boundary
    port = get_port("loopback")
    assert len(port.CHUNK) == 65536
    handle = port.build(qt)
    c = handle.controls
    peer = c["peer"]
    try:
        assert c["start"]()
        assert not c["start"]()
        until(
            qt,
            lambda: (c["write"](), c["poll"]()),
            lambda: not handle.snapshot()["active"],
            timeout=8,
        )
        assert handle.snapshot()["sent"] == handle.snapshot()["received"] == port.TOTAL
        assert not handle.snapshot()["error"]
        assert c["start"]()
    finally:
        handle.close()
    assert not peer.thread.is_alive()


def test_lazy_mime_only_encodes_when_retrieved(boundary):
    qt, _ = boundary
    handle = get_port("delayedencoding").build(qt)
    try:
        mime = handle.controls["mime_factory"]()
        assert mime.formats() == ["image/png"]
        assert handle.snapshot()["encodings"] == 0
        first = mime.retrieveData("image/png", 0)
        second = mime.retrieveData("image/png", 0)
        assert first.data() == second.data() and first.data()
        assert handle.snapshot()["encodings"] == 1
        mime.deleteLater()
    finally:
        handle.close()


def test_robot_animation_pad_history_embedded_reversal_and_anchor_edges(boundary):
    qt, _ = boundary
    for name in ("dragdroprobot", "padnavigator", "embeddeddialogs", "anchorlayout"):
        handle = get_port(name).build(qt)
        c = handle.controls
        try:
            if name == "dragdroprobot":
                c["tick"]()
                assert handle.snapshot()["frame"] == 1
            elif name == "padnavigator":
                c["select"](8)
                c["flip"]()
                c["title"].setText("A new workspace")
                c["flip"]()
                assert (
                    handle.snapshot()["selection"] == 8
                    and not handle.snapshot()["back"]
                )
            elif name == "embeddeddialogs":
                assert len(c["proxies"]) == 100
                c["states"][0]["target"] = 1
                for _ in range(5):
                    c["tick"]()
                assert 0 < c["states"][0]["progress"] < 1
                c["states"][0]["target"] = 0
                for _ in range(8):
                    c["tick"]()
                assert c["states"][0]["progress"] == 0
                assert all(state["progress"] == 0 for state in c["states"][1:])
            else:
                for width in (320, 650, 900):
                    c["arrange"](width)
                    rects = handle.snapshot()["rectangles"]
                    assert rects[2][0] == rects[5][2] == rects[6][2]
                    assert rects[5][1] + rects[5][3] == rects[6][1]
        finally:
            handle.close()


@pytest.mark.parametrize(
    "row",
    [r for r in ROWS if r["target_path"].split("/")[1] not in {"qml", "quick"}],
    ids=lambda r: Path(r["target_path"]).stem,
)
def test_build_failure_after_resource_creation_cleans_owned_objects(
    row, boundary, monkeypatch
):
    qt, owners = boundary
    port = module(row)
    peers = []
    if hasattr(port, "attach_peer"):
        attach = port.attach_peer

        def retain(session, serve):
            peer = attach(session, serve)
            peers.append(peer)
            return peer

        monkeypatch.setattr(port, "attach_peer", retain)

    def fail(session):
        raise RuntimeError("Injected finalization failure")

    monkeypatch.setattr(port.Session, "finish", fail)
    with pytest.raises(RuntimeError, match="Injected finalization failure"):
        port.build(qt)
    assert owners and all(owner.closed for owner in owners)
    assert all(
        not peer.thread.is_alive() and peer.socket.fileno() == -1 for peer in peers
    )


@pytest.mark.parametrize("name", ["draggableicons", "draggabletext", "fridgemagnets"])
def test_canceled_drag_preserves_tiles_and_invalid_offset_falls_back(name, boundary):
    qt, _ = boundary
    port = get_port(name)
    handle = port.build(qt)
    c = handle.controls
    try:
        original = len(c["labels"])
        label = c["labels"][0]
        label.mousePressEvent(
            SimpleNamespace(
                button=lambda: qt.QtCore.Qt.LeftButton,
                pos=lambda: qt.QtCore.QPoint(3, 5),
            )
        )
        assert len(c["labels"]) == original and not handle.snapshot()["dragging"]
        mime = qt.QtCore.QMimeData()
        mime.setData(port.MIME, qt.QtCore.QByteArray(b'{"offset":"broken"}'))
        assert c["payload"](mime)[1] == [0, 0]
        mime.deleteLater()
    finally:
        handle.close()


def test_svg_invalid_input_preserves_view_and_raster_switch(boundary):
    qt, _ = boundary
    handle = get_port("svgviewer").build(qt)
    c = handle.controls
    try:
        initial = handle.snapshot()["filename"]
        invalid = c["controller"].root() / "invalid.svg"
        invalid.write_text("<svg broken")
        with pytest.raises(ValueError):
            c["open_file"](invalid)
        assert handle.snapshot()["filename"] == initial
        for backend in ("raster", "native", "raster"):
            c["backend"](backend)
            assert handle.snapshot()["renderer"] == backend
        c["zoom"](1.15)
        assert handle.snapshot()["zoom"] == 1.15
    finally:
        handle.close()


def test_dock_owned_pdf_dialog_and_literal_letter_insertions(boundary):
    qt, _ = boundary
    handle = get_port("dockwidgets").build(qt)
    c = handle.controls
    try:
        c["insert_customer"]("Aster <literal>")
        c["insert_paragraph"]("An original paragraph.")
        c["Print"].trigger()
        printer = c["printer"]
        assert str(printer.outputFileName()).endswith("letter.pdf")
        assert handle.alerts
    finally:
        handle.close()


def test_first_address_stage_has_literal_fields_without_collection_operations(boundary):
    qt, _ = boundary
    handle = get_port("part1").build(qt)
    try:
        c = handle.controls
        c["name"].setText("<name>")
        c["address"].setPlainText("<address>\nSecond line")
        assert handle.snapshot()["name"] == "<name>"
        assert handle.snapshot()["address"] == "<address>\nSecond line"
        assert set(c) == {"controller", "name", "address"}
    finally:
        handle.close()
