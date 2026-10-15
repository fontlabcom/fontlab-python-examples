# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/INDEX.json (batch c)
# this_file: tests/test_cleanroom_c.py
"""Independent replacement contracts; doubles do not establish native acceptance."""

import ast
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from official_doubles import official_host
from qt_doubles import fake_host

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = set(
    "animation dbus opengl remoteobjects webkit tools richtext multimediawidgets sql threads ipc pyuic multimedia activeqt qtdemo xmlpatterns".split()
)
PORTS = [
    p
    for p in json.loads((ROOT / "clean-room-specs/INDEX.json").read_text())["ports"]
    if p["target_path"].split("/")[1] in CATEGORIES
]


def load(port):
    spec = importlib.util.spec_from_file_location(
        "cleanroom_c_" + port["port_id"], ROOT / port["target_path"]
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def host(monkeypatch):
    qt, owners = fake_host(monkeypatch)
    official_host(qt)
    return qt, owners


@pytest.mark.parametrize("port", PORTS, ids=lambda p: Path(p["target_path"]).stem)
def test_receipt_and_import(port):
    receipt = json.loads(
        (ROOT / "clean-room/receipts" / (port["port_id"] + ".json")).read_text()
    )
    assert receipt["port_id"] == port["port_id"]
    assert receipt["target_path"] == port["target_path"]
    assert (
        receipt["spec_sha256"]
        == hashlib.sha256((ROOT / port["spec_file"]).read_bytes()).hexdigest()
    )
    assert port["target_path"] in receipt["files"]
    for name in receipt["files"]:
        assert (ROOT / name).is_file()
        if name.endswith(".py"):
            source = (ROOT / name).read_text()
            assert source.startswith(
                "# SPDX-License-Identifier: Apache-2.0\n# Clean-room implementation from "
                + port["spec_file"]
            )
            compile(source, name, "exec")
            tree = ast.parse(source)
            assert not any(
                isinstance(n, ast.ImportFrom)
                and n.module == "fontlab_python_examples.official"
                for n in ast.walk(tree)
            )
    assert callable(load(port).build)


@pytest.mark.parametrize("port", PORTS, ids=lambda p: Path(p["target_path"]).stem)
def test_launch_boundary_and_owned_close(port, host):
    qt, owners = host
    module = load(port)
    blocked = "## Capability boundary" in (ROOT / port["spec_file"]).read_text()
    if blocked:

        class Untouchable:
            def __getattr__(self, name):
                raise AssertionError("blocked port accessed host: " + name)

        with pytest.raises(NotImplementedError, match="unavailable|lacks"):
            module.build(Untouchable())
        assert not owners
        return
    for _ in range(2):
        handle = module.build(qt)
        assert not handle.owner.closed
        json.dumps(handle.snapshot())
        handle.close()
        handle.close()
        assert handle.owner.closed
        assert not handle.connections
    assert all(owner.closed for owner in owners)


def port_module(port_id):
    return load(next(p for p in PORTS if p["port_id"] == port_id))


@pytest.fixture
def launch_port(host):
    handles = []

    def launch(port_id):
        handle = port_module(port_id).build(host[0])
        handles.append(handle)
        return handle

    yield launch
    for handle in reversed(handles):
        handle.close()


SUPPORTED = [
    p
    for p in PORTS
    if "## Capability boundary" not in (ROOT / p["spec_file"]).read_text()
]


@pytest.mark.parametrize("port", SUPPORTED, ids=lambda p: Path(p["target_path"]).stem)
def test_partial_construction_failure_releases_owner(port, host, monkeypatch):
    qt, owners = host

    def fail(*args):
        raise RuntimeError("injected title failure")

    monkeypatch.setattr(qt.QtGui.QWidget, "setWindowTitle", fail)
    with pytest.raises(RuntimeError, match="injected title failure"):
        load(port).build(qt)
    assert owners and all(owner.closed for owner in owners), (
        "Partial construction leaked its owner"
    )


@pytest.mark.parametrize("port", SUPPORTED, ids=lambda p: Path(p["target_path"]).stem)
def test_native_window_close_uses_owned_cleanup(port, launch_port):
    from types import SimpleNamespace

    handle = launch_port(port["port_id"])
    accepted = []
    handle.widget.closeEvent(
        SimpleNamespace(accept=lambda: accepted.append(True), ignore=lambda: None)
    )
    assert handle.owner.closed, "Native close must release the same owned lifetime"
    assert not handle.connections


@pytest.mark.parametrize(
    "port_id,works",
    [
        ("5a8e48d2a1396cea", True),
        ("b7db02f540cc7559", False),
        ("b9660f4ee653ca01", True),
    ],
)
def test_form_variants_add_clear_and_close(port_id, works, launch_port):
    handle = launch_port(port_id)
    for _ in range(2):
        handle.controls["Add"].emit("clicked")
    assert handle.snapshot()["count"] == (8 if works else 0)
    handle.controls["Clear"].emit("clicked")
    assert handle.snapshot()["count"] == 0
    handle.controls["OK"].emit("clicked")
    assert handle.owner.closed


@pytest.mark.parametrize("port_id", ["27709a02d37b9ba9", "b95b687bbc541207"])
def test_real_transfer_completes_restarts_and_stops_under_backpressure(port_id):
    import queue
    import time

    module = port_module(port_id)
    for consume in (True, False, True):
        transfer = module.Transfer()
        transfer.start()
        received = ""
        try:
            if consume:
                deadline = time.monotonic() + 5
                while len(received) < 100000 and time.monotonic() < deadline:
                    try:
                        received += transfer.messages.get(timeout=0.05)
                    except queue.Empty:
                        pass
                assert received == "ACGT" * 25000, "Stream lost or reordered symbols"
            else:
                time.sleep(0.03)
                assert transfer.messages.qsize() <= 8, (
                    "GUI delivery must remain bounded"
                )
        finally:
            transfer.stop()
        assert not any(t.is_alive() for t in transfer.threads)


@pytest.mark.parametrize("port_id", ["0ad3432ccdca7ac0", "a14d08fe23965bec"])
def test_fortune_unicode_fragment_framing_and_invalid_lengths(port_id):
    module = port_module(port_id)
    for text in ("A quiet current.", "Zażółć Ω 😀"):
        framed = module.packet(text)
        for length in range(len(framed)):
            assert module.decode(framed[:length]) is None
        assert module.decode(framed) == text
        with pytest.raises(ValueError):
            module.decode(framed + b"!")
    for bad in (b"\x00\x01X", b"\xff\xff", b"\x00\x06\x00\x00\x00\x03AB"):
        with pytest.raises(ValueError):
            module.decode(bad)


@pytest.mark.parametrize("port_id", ["0ad3432ccdca7ac0", "a14d08fe23965bec"])
def test_local_peer_roundtrip_foreign_endpoint_refusal_and_cleanup(
    port_id, launch_port, host
):
    import time

    handle = launch_port(port_id)
    endpoint = Path(handle.controls["endpoint"])
    handle.controls["request"]()
    deadline = time.monotonic() + 2
    while not handle.snapshot()["message"] and time.monotonic() < deadline:
        host[0]._pump_network()
        handle.controls["receive"]()
        time.sleep(0.01)
    assert handle.snapshot()["message"] in port_module(port_id).FORTUNES
    handle.controls["server_name"].setText("unowned-peer")
    handle.controls["request"]()
    assert "Only this example" in str(handle.controls["status"].text)
    handle.close()
    assert not endpoint.exists() and not endpoint.parent.exists()


def test_encoding_preview_cancel_and_strict_output_copy(launch_port, tmp_path):
    handle = launch_port("19571722ed96aa9c")
    editor = handle.controls["editor"]
    editor.setPlainText("Prior document")
    sample = tmp_path / "sample.txt"
    sample.write_bytes("Café".encode("latin1"))
    handle.controls["preview_file"](str(sample))
    assert editor.toPlainText() == "Prior document", (
        "Preview must not replace before acceptance"
    )
    preview = handle.controls["preview_codec"]
    preview.setCurrentIndex(1)
    assert "Café" == handle.controls["preview_text"].toPlainText()
    destination = Path(handle.controls["directory"]) / "copy.txt"
    editor.setPlainText("Café")
    handle.controls["save_file"](str(destination), "iso-8859-1")
    assert destination.read_bytes().decode("iso-8859-1") == "Café"
    handle.controls["save_file"](str(tmp_path / "outside.txt"), "utf-8")
    assert not (tmp_path / "outside.txt").exists()
    editor.setPlainText("Ω")
    handle.controls["save_file"](str(destination), "ascii")
    assert destination.read_bytes().decode("iso-8859-1") == "Café"
    handle.close()
    assert not destination.parent.exists()


def test_syntax_multiline_comments_and_quoted_comment_markers():
    module = port_module("428c50abcef7adfe")
    spans, inside = module.spans("int count; /* begin")
    assert inside and spans[-1][2] == "comment"
    spans, inside = module.spans("still here */ return count;", inside)
    assert not inside and spans[0][2] == "comment"
    assert any(kind == "keyword" for _, _, kind in spans)
    spans, inside = module.spans('"/* ordinary text */" // end')
    assert [kind for _, _, kind in spans] == ["string", "comment"] and not inside


@pytest.mark.parametrize(
    "bad",
    [
        "<!DOCTYPE x><x/>",
        '<!DOCTYPE x [<!ENTITY a SYSTEM "file:///etc/passwd">]><x>&a;</x>',
        '<x xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="x https://invalid/x"/>',
        '<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema"><s:include schemaLocation="file:///secret"/></s:schema>',
    ],
)
def test_xml_external_references_rejected_without_native_validation(
    bad, host, launch_port
):
    handle = launch_port("1e5d0f7289e1b36e")
    qt = host[0]
    previous = len(qt._schema_requests)
    handle.controls["instance"].setPlainText(bad)
    handle.controls["validate"]()
    assert handle.snapshot()["valid"] is False
    assert len(qt._schema_requests) == previous, (
        "Rejected references reached the native XML engine"
    )


def test_xml_native_diagnostics_and_edit_clear(host, launch_port):
    qt = host[0]
    handle = launch_port("1e5d0f7289e1b36e")
    qt._validation_result = (False, "Quantity is invalid", 2, 5)
    handle.controls["validate"]()
    state = handle.snapshot()
    assert state["valid"] is False and state["line"] == 2 and state["column"] == 5
    handle.controls["instance"].setPlainText("<order/>")
    assert handle.snapshot()["valid"] is None and handle.snapshot()["line"] == 0


def test_translated_windows_toggle_and_child_close(launch_port):
    from types import SimpleNamespace

    handle = launch_port("eca1cd9ef1528607")
    handle.controls["Show All"].emit("clicked")
    assert all(handle.snapshot()["languages"].values())
    windows = handle.controls["windows"]
    assert windows["Français"].windowTitle != windows["Polski"].windowTitle
    windows["Français"].closeEvent(SimpleNamespace(ignore=lambda: None))
    assert not handle.controls["checks"]["Français"].checked
    handle.controls["Hide All"].emit("clicked")
    assert not any(handle.snapshot()["languages"].values())


@pytest.mark.parametrize("text,result", [("false", False), (" TRUE ", True)])
def test_settings_booleans_do_not_use_string_truthiness(text, result, host):
    module = port_module("9e41e71c41b116a8")
    assert module.parse_scalar(text, "bool", host[0].QtCore) is result
    with pytest.raises(ValueError):
        module.parse_scalar("probably", "bool", host[0].QtCore)


def test_settings_edits_refresh_and_leave_import_source_unchanged(
    launch_port, tmp_path
):
    handle = launch_port("9e41e71c41b116a8")
    source = tmp_path / "source.ini"
    original = b"[display]\nenabled=false\nsize=20\n"
    source.write_bytes(original)
    handle.controls["import_file"](str(source))
    handle.controls["settings"].setValue("display/enabled", False)
    handle.controls["refresh"]()
    assert handle.controls["settings"].value("display/enabled") is False
    assert source.read_bytes() == original


def test_calendar_leap_month_and_font_limits(launch_port):
    handle = launch_port("c56cf1699b07b350")
    handle.controls["year"].setValue(2024)
    handle.controls["month"].setCurrentIndex(1)
    handle.controls["size"].setValue(64)
    state = handle.snapshot()
    assert max(day for week in state["weeks"] for day in week) == 29
    assert state["font_size"] == 64


def test_order_rejects_bad_quantities_and_escapes_customer_markup():
    module = port_module("c997677a2bdb4f34")
    for bad in ("-1", "1.5", "no", "10001"):
        with pytest.raises(ValueError):
            module.quantities([bad])
    text = module.letter("<Mira>", "A&B", [1, 2, 0], False)
    assert "&lt;Mira&gt;" in text and "A&amp;B" in text and "17.00" in text


def test_rich_editor_protects_demonstration_and_outputs(launch_port, tmp_path):
    handle = launch_port("b34b2f696a977e74")
    root = Path(handle.controls["directory"])
    demo = root / "demonstration.html"
    original = demo.read_bytes()
    handle.controls["editor"].setPlainText("Changed")
    assert not handle.controls["save_file"](str(demo))
    assert not handle.controls["save_file"](str(tmp_path / "outside.txt"))
    assert demo.read_bytes() == original
    assert handle.controls["save_file"](str(root / "new.txt"))
    assert (root / "new.txt").read_text() == "Changed"
    handle.close()
    assert not root.exists()


def test_fractal_scanline_is_bounded_and_navigation_generation_changes(launch_port):
    module = port_module("0788354954c8e613")
    pixels = module.scanline(32, 20, 10, (-0.5, 0), 0.02, 24)
    assert len(pixels) == 32 and all(0 <= p < 512 for p in pixels)
    handle = launch_port("0788354954c8e613")
    generation = handle.snapshot()["generation"]
    handle.controls["request"]()
    assert handle.snapshot()["generation"] == generation + 1


def test_tile_layouts_have_64_independent_numeric_destinations():
    module = port_module("1cf57c0f2ac8880a")
    layouts = [
        module.positions(name)
        for name in ("Grid", "Ellipse", "Figure eight", "Scatter", "Center")
    ]
    assert all(len(rows) == 64 for rows in layouts)
    assert len({tuple(rows) for rows in layouts}) == 5


def test_gl_and_raster_share_phase_and_end_painters(host, launch_port):
    handle = launch_port("c82d1af7d1a7b0cf")
    handle.controls["advance"]()
    handle.controls["raster"].paintEvent(None)
    handle.controls["opengl"].paintGL()
    assert handle.snapshot()["phase"] == 1
    assert all(not painter._active for painter in host[0]._painters)


def test_animation_states_redirect_and_stop_native_machines(launch_port):
    tiles = launch_port("1cf57c0f2ac8880a")
    for name in ("Scatter", "Ellipse", "Grid", "Center"):
        tiles.controls[name].emit("clicked", False)
        assert tiles.snapshot()["layout"] == name
    scenes = launch_port("29f6a7d0a3bb6813")
    for expected in (1, 2, 0, 1):
        scenes.controls["cycle"].emit("clicked", False)
        assert scenes.snapshot()["state"] == expected
    chooser = launch_port("de30d23621025fe6")
    for index in (2, 0, 3):
        chooser.controls["choices"][index].emit("clicked", False)
        assert chooser.snapshot()["index"] == index
    blocks = launch_port("b7283d74afb78218")
    visited = set()
    for _ in range(7):
        visited.add(blocks.snapshot()["state"])
        blocks.controls["timer"].emit("timeout")
    assert len(visited) == 7
    for handle in (tiles, scenes, chooser, blocks):
        machine = handle.controls["machine"]
        handle.close()
        assert not machine.isRunning()


def test_stickman_four_authored_poses_and_coincident_joints(launch_port):
    handle = launch_port("243ae486f9528e8c")
    for name in ("jump", "dance", "rest", "dead"):
        handle.controls["choose"](name)
        assert handle.snapshot()["activity"] == name
    handle.controls["joints"][1].setPos(handle.controls["joints"][0].pos)
    handle.controls["stabilize"]()
    assert handle.snapshot()["bones"] == 15


def test_easing_controls_have_47_curves_and_parameter_changes(launch_port):
    handle = launch_port("bd6c8feb783ba845")
    assert handle.snapshot()["curves"] == 47
    handle.controls["curves"].setCurrentRow(10)
    handle.controls["period"].setValue(0.8)
    handle.controls["path"].setCurrentIndex(1)
    handle.controls["timer"].emit("timeout")
    assert isinstance(handle.snapshot()["progress"], float)


def test_rich_editor_cancel_discard_and_save_before_action(launch_port):
    handle = launch_port("b34b2f696a977e74")
    module = port_module("b34b2f696a977e74")
    editor = handle.controls["editor"]
    document = module.value(editor, "document")
    document.setModified(True)
    actions = []
    handle.controls["guard"](lambda: actions.append("continued"))
    assert not actions
    handle.alerts[-1].widget.emit("finished", 0)
    assert not actions, "Cancel must leave the document untouched"
    handle.controls["guard"](lambda: actions.append("continued"))
    # Obtain the actual captured enum from the host class, not a guessed value.
    box = handle.alerts[-1].widget
    box.emit("finished", type(box).Discard)
    assert actions == ["continued"]


def test_order_dialog_invalid_input_stays_then_creates_tab(launch_port):
    handle = launch_port("c997677a2bdb4f34")
    handle.controls["name"].setText("Mira")
    table = handle.controls["quantities"]
    table.item(0, 2).setText("invalid")
    handle.controls["create"]()
    assert handle.snapshot()["letters"] == 0
    assert handle.controls["feedback"].text
    table.item(0, 2).setText("2")
    handle.controls["create"]()
    assert handle.snapshot()["letters"] == 1


def test_timer_callbacks_after_owned_close_are_inert(launch_port):
    for port_id in (
        "0788354954c8e613",
        "c82d1af7d1a7b0cf",
        "bd6c8feb783ba845",
        "27709a02d37b9ba9",
    ):
        handle = launch_port(port_id)
        ticker = handle.controls["timer"]
        callbacks = [
            callback for obj, signature, callback in handle.connections if obj is ticker
        ]
        handle.close()
        assert not ticker._active
        for callback in callbacks:
            callback()
        assert handle.snapshot() == {"launched": True, "closed": True}


@pytest.mark.parametrize("port", PORTS, ids=lambda p: Path(p["target_path"]).stem)
def test_launcher_contract_with_receipt_overlay_only_in_memory(port, host, monkeypatch):
    from fontlab_python_examples import launcher

    records = launcher.available()
    receipt = json.loads(
        (ROOT / "clean-room/receipts" / (port["port_id"] + ".json")).read_text()
    )
    merged = [
        dict(
            record,
            implementation=receipt["implementation"],
            blocked_reason=receipt["blocked_reason"],
        )
        if record["source_id"] == port["port_id"]
        else record
        for record in records
    ]
    monkeypatch.setattr(launcher, "available", lambda: merged)
    if receipt["implementation"] == "blocked":
        with pytest.raises(NotImplementedError):
            launcher.launch(port["port_id"])
        assert not host[1], "Launcher accessed native ownership for a blocked record"
        return
    try:
        handle = launcher.launch(port["port_id"])
        assert launcher.launch(port["port_id"]) is handle
        assert launcher.inspect(port["port_id"])["visible"] is True
    finally:
        launcher.close(port["port_id"])
    assert launcher.inspect(port["port_id"])["launched"] is False
    assert all(owner.closed for owner in host[1])


def test_completion_suffix_and_dynamic_activation_disconnect(host, launch_port):
    module = port_module("10ef4dacb4db4080")
    assert module.completion_suffix("anchorage", "ANC") == "horage"
    assert module.completion_suffix("anchor", "anchor") == ""
    assert module.completion_suffix("anchor", "curve") is None
    handle = launch_port("10ef4dacb4db4080")
    previous = handle.controls["completer"]
    replacement = host[0].QtGui.QCompleter(handle.widget)
    handle.controls["replace_completer"](replacement)
    assert not previous._signals["activated(QString)"].callbacks
    assert previous.deleted
    assert handle.controls["completer"] is replacement


def test_regexp_captures_clear_and_escaped_pattern_roundtrips(launch_port):
    handle = launch_port("626fd0acec74fd91")
    handle.controls["pattern"].setEditText(r"(st\w+)")
    assert handle.snapshot()["captures"] == ["stones", "stones"]
    handle.controls["pattern"].setEditText("absent")
    assert handle.snapshot()["position"] == -1 and not handle.snapshot()["captures"]
    pattern = r'"quote"\\path'
    handle.controls["pattern"].setEditText(pattern)
    assert json.loads(handle.snapshot()["escaped"]) == pattern


def test_settings_value_delegate_restricts_columns_and_commits_types(launch_port):
    from types import SimpleNamespace

    handle = launch_port("9e41e71c41b116a8")
    delegate = handle.controls["delegate"]
    committed = []
    model = SimpleNamespace(setData=lambda index, text, role: committed.append(text))
    for kind, text in (
        ("bool", "false"),
        ("int", "42"),
        ("float", "2.5"),
        ("str", "river"),
    ):
        index = SimpleNamespace(
            column=lambda: 2,
            row=lambda: 0,
            sibling=lambda r, c: SimpleNamespace(data=lambda role: kind),
            data=lambda role: text,
        )
        editor = delegate.createEditor(handle.widget, None, index)
        delegate.setEditorData(editor, index)
        delegate.setModelData(editor, model, index)
        assert committed[-1] == text
    assert (
        delegate.createEditor(handle.widget, None, SimpleNamespace(column=lambda: 0))
        is None
    )
