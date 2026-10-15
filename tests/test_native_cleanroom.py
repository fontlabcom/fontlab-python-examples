# SPDX-License-Identifier: Apache-2.0
# this_file: tests/test_native_cleanroom.py
"""Pure controller/receipt checks: these never connect to FontLab."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import native_cleanroom as driver

REPLACED = {
    "1151b1cb878f192a",
    "a601a41dc5a3c23a",
    "a33bb8c2dce4e115",
    "631cc1bc310c00b9",
}


def test_selection_when_all_or_ids_then_only_integrated_clean_room_records():
    manifest = json.loads((ROOT / "catalog/ports.json").read_text())
    rows = driver.select_records(manifest, [])
    assert len(rows) == 191, "187 clean-room records and 4 with replaced resources"
    assert {r["source_id"] for r in rows if not r.get("clean_room_receipt")} == REPLACED
    historical = next(
        r["source_id"]
        for r in manifest["ports"]
        if not driver.driven(r) and r["implementation"] == "implemented"
    )
    with pytest.raises(ValueError):
        driver.select_records(manifest, [historical])
    assert driver.select_records(
        manifest, [rows[1]["source_id"], rows[0]["source_id"]]
    ) == [rows[1], rows[0]]
    for ids in [["missing"], [rows[0]["source_id"]] * 2]:
        with pytest.raises(ValueError):
            driver.select_records(manifest, ids)


def test_batches_when_positive_then_no_empty_or_missing_records():
    assert list(driver.batches(list(range(5)), 2)) == [[0, 1], [2, 3], [4]]
    assert list(driver.batches([], 1)) == []
    with pytest.raises(ValueError):
        list(driver.batches([1], 0))


def test_purge_when_live_handle_then_refuses_without_discarding_modules():
    from types import SimpleNamespace

    held = SimpleNamespace(_handles={"active": object()})
    modules = {
        "fontlab_python_examples.launcher": held,
        "fontlab_cleanroom_a_primitives": object(),
        "other": object(),
    }
    before = dict(modules)
    with pytest.raises(RuntimeError, match="retained"):
        driver.purge_examples(modules)
    assert modules == before
    held._handles.clear()
    assert driver.purge_examples(modules) == 2
    assert list(modules) == ["other"]


def test_path_context_when_error_then_exact_path_restored(tmp_path):
    original = list(sys.path)
    with pytest.raises(RuntimeError), driver.checkout_path(tmp_path):
        assert sys.path[0] == str(tmp_path.resolve())
        raise RuntimeError("injected")
    assert sys.path == original


@pytest.mark.parametrize(
    "fail_phase", [None, "prepare", "launch", "inspect", "close", "verify"]
)
def test_run_port_when_phase_fails_then_cleanup_is_attempted_and_never_launch_retried(
    fail_phase,
):
    calls = []

    def call(action, **variables):
        calls.append(action)
        return {
            "ok": action != fail_phase,
            "host_seconds": 0.01,
            "path_restored": True,
            "data": {"clean": True},
            "error": {"type": "Injected", "message": action}
            if action == fail_phase
            else None,
        }

    row = {"source_id": "one", "implementation": "implemented"}
    receipt = driver.run_port(call, row, pause=lambda seconds: None)
    assert calls.count("launch") <= 1
    if fail_phase != "prepare":
        assert "close" in calls and "verify" in calls
    assert receipt["status"] == ("passed" if fail_phase is None else "failed")
    assert driver.summarize([receipt], ["one"])["passed"] == int(fail_phase is None)


def test_run_port_when_transport_outcome_unknown_then_reports_unclean_and_does_not_retry():
    calls = []

    def call(action, **variables):
        calls.append(action)
        if action == "launch":
            raise TimeoutError("unknown execution outcome")
        return {
            "ok": True,
            "host_seconds": 0.01,
            "path_restored": True,
            "data": {"clean": True},
        }

    receipt = driver.run_port(
        call,
        {"source_id": "one", "implementation": "implemented"},
        pause=lambda _: None,
    )
    assert receipt["status"] == "unknown" and not receipt["continue_safe"]
    assert calls == ["prepare", "launch"], (
        "Do not issue mutations over an uncertain timed-out session"
    )


def test_summary_when_run_stops_then_unexecuted_ids_explicit():
    summary = driver.summarize([{"port_id": "a", "status": "passed"}], ["a", "b"])
    assert (
        summary["not_run"] == ["b"]
        and summary["requested"] == 2
        and summary["passed"] == 1
    )


def test_compact_when_huge_snapshot_then_bounded_and_json_serializable():
    result = driver.compact({"visible": True, "rows": ["x" * 10000] * 1000})
    assert result["visible"] is True
    assert len(json.dumps(result)) < 10000


def test_host_when_wrong_import_or_prepare_error_then_path_restored(
    tmp_path, monkeypatch
):
    original = list(sys.path)
    result = driver.host_step("prepare", "one", "token", str(tmp_path))
    assert not result["ok"] and result["path_restored"]
    assert sys.path == original


def test_host_wrapper_when_generated_then_small_and_restores_path_in_finally():
    compile(driver.HOST_CODE, "<host wrapper>", "exec")
    assert len(driver.HOST_CODE.encode()) < 32768
    assert "finally:" in driver.HOST_CODE


def test_main_when_fake_transport_then_batches_short_calls_and_writes_receipts(
    tmp_path, monkeypatch
):
    from types import SimpleNamespace

    manifest = json.loads((ROOT / "catalog/ports.json").read_text())
    ids = [r["source_id"] for r in driver.select_records(manifest, [])[:2]]
    calls = []
    connections = []

    class Client:
        def __init__(self, command=None, timeout=None):
            connections.append(timeout)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def run(self, code, **variables):
            assert len(code.encode()) < 32768
            assert variables["checkout"] == str(ROOT)
            calls.append(variables["action"])
            return SimpleNamespace(
                value={
                    "ok": True,
                    "host_seconds": 0.001,
                    "path_restored": True,
                    "data": {"clean": True},
                }
            )

    monkeypatch.setitem(sys.modules, "fontlab_remopy", SimpleNamespace(FontLab=Client))
    output = tmp_path / "native.jsonl"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "native_cleanroom",
            "--ids",
            ",".join(ids),
            "--batch-size",
            "1",
            "--output",
            str(output),
        ],
    )
    assert driver.main() == 0
    records = [json.loads(line) for line in output.read_text().splitlines()]
    assert [r["port_id"] for r in records] == ids
    assert all(r["status"] == "passed" and r["files"] for r in records)
    assert connections == [4, 4]
    assert calls == ["prepare", "launch", "inspect", "close", "verify", "finish"] * 2
    summary = json.loads(output.with_suffix(".summary.json").read_text())
    assert summary["passed"] == 2 and summary["not_run"] == []


def test_main_when_connection_fails_then_unknown_receipt_and_unrun_summary(
    tmp_path, monkeypatch
):
    from types import SimpleNamespace

    class Unreachable:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            raise ConnectionError("Host unavailable")

        def __exit__(self, *args):
            pass

    monkeypatch.setitem(
        sys.modules, "fontlab_remopy", SimpleNamespace(FontLab=Unreachable)
    )
    output = tmp_path / "failed.jsonl"
    monkeypatch.setattr(sys, "argv", ["native_cleanroom", "--output", str(output)])
    assert driver.main() == 1
    receipt = json.loads(output.read_text())
    assert receipt["status"] == "unknown" and not receipt["continue_safe"]
    summary = json.loads(output.with_suffix(".summary.json").read_text())
    assert summary["recorded"] == 1 and len(summary["not_run"]) == 190


def test_owned_destruction_when_deferred_then_verify_waits_for_every_object(tmp_path):
    import threading
    from tempfile import TemporaryDirectory
    from types import SimpleNamespace

    class Node:
        def __init__(self, kind, children=()):
            self.kind = kind
            self.nodes = list(children)
            self.callbacks = []
            self.active = kind == "QTimer"
            self.visible = True

        def inherits(self, kind):
            return kind in [self.kind, "QObject"]

        def children(self):
            return self.nodes

        def connect(self, signature, callback):
            self.callbacks.append(callback)

        def isActive(self):
            return self.active

        def destroy(self):
            for node in self.nodes:
                node.destroy()
            for callback in self.callbacks:
                callback(self)

    timer = Node("QTimer")
    window = Node("QWidget", [timer])
    app = object()
    temporary = TemporaryDirectory(dir=tmp_path)
    owner = SimpleNamespace(closed=False, widget=window)
    handle = SimpleNamespace(
        widget=window,
        owner=owner,
        controls={"timer": timer},
        alerts=[],
        connections=[],
        callbacks=[],
        cleanup=[],
        release=[],
        after_close=[temporary.cleanup],
    )
    registry = {"one": handle}

    def close(pid):
        timer.active = False
        window.visible = False
        owner.closed = True
        owner.widget = None
        handle.widget = None
        for callback in handle.after_close:
            callback()
        handle.after_close.clear()
        handle.controls.clear()
        registry.clear()
        return {"closed": True, "launched": False}

    application = SimpleNamespace(
        topLevelWidgets=lambda: [window] if window.visible else [],
        topLevelWindows=list,
        instance=lambda: app,
    )
    session = {
        "pid": "one",
        "row": {"implementation": "implemented"},
        "handle": handle,
        "launcher": SimpleNamespace(close=close, _handles=registry),
        "qt": SimpleNamespace(QtGui=SimpleNamespace(QApplication=application)),
        "app": app,
        "windows": {},
        "threads": {t.ident for t in threading.enumerate()},
        "watched": {},
        "destroyed": set(),
        "callbacks": [],
        "runtime": {},
        "temporary": set(),
    }
    driver._watch(session)
    assert len(session["watched"]) == 2 and len(session["runtime"]) == 1
    assert temporary.name in session["temporary"]
    driver._close(session)
    assert not driver._verify(session)["clean"], (
        "deleteLater ownership is not destruction proof"
    )
    window.destroy()
    result = driver._verify(session)
    assert result["clean"] and result["expected_destroyed"] == result["destroyed"] == 2
    assert result["host_alive"] and result["registry_empty"]


def test_repeated_prepare_when_token_retained_then_does_not_discard_cleanup_state(
    monkeypatch,
):
    retained = {"same": {"owned": "must retain"}}
    monkeypatch.setattr(driver, "_sessions", retained)
    result = driver.host_step("prepare", "one", "same", str(ROOT))
    assert not result["ok"] and retained == {"same": {"owned": "must retain"}}


def test_owned_descriptors_when_transport_sockets_and_pipes_appear_then_ignored():
    before = {"3": "file", "4": "socket"}
    after = {"3": "file", "4": "socket", "9": "socket", "10": "fifo"}
    assert driver.owned_descriptors(before, after) == []
    assert driver.owned_descriptors(before, after | {"11": "file", "12": "dir"}) == [
        "11",
        "12",
    ]


class _Handle:
    def __init__(self):
        self.closed = 0


class _Launcher:
    def __init__(self, pid):
        self._handles = {pid: _Handle()}

    def close(self, pid):
        self._handles[pid].closed += 1
        del self._handles[pid]


class _Witnessed:
    def __init__(self):
        self.disconnected = []

    def disconnect(self, signature, slot):
        self.disconnected.append(signature)


def _stale_session(pid="one"):
    survivor, gone = _Witnessed(), _Witnessed()
    return (
        {
            "pid": pid,
            "launcher": _Launcher(pid),
            "witnesses": {"a": (survivor, print), "b": (gone, print)},
            "destroyed": {"b"},
        },
        survivor,
        gone,
    )


def test_reset_when_session_left_unclean_then_owned_cleanup_and_session_cleared(
    monkeypatch,
):
    session, survivor, gone = _stale_session()
    launcher = session["launcher"]
    monkeypatch.setattr(driver, "_sessions", {"tok": session})
    monkeypatch.setattr(driver, "purge_examples", lambda modules: 0)
    result = driver.host_step("reset", "one", "tok", str(ROOT))
    assert result["ok"], result
    assert result["data"] == {
        "sessions_reset": 1,
        "examples_closed": 1,
        "witnesses_disconnected": 1,
    }
    assert launcher._handles == {} and driver._sessions == {}
    assert survivor.disconnected == ["destroyed(QObject*)"] and gone.disconnected == []


def test_reset_when_wildcard_then_every_stale_session_cleared(monkeypatch):
    sessions = {"t1": _stale_session("one")[0], "t2": _stale_session("two")[0]}
    monkeypatch.setattr(driver, "_sessions", sessions)
    monkeypatch.setattr(driver, "purge_examples", lambda modules: 0)
    result = driver.host_step("reset", "*", "*", str(ROOT))
    assert result["ok"] and result["data"]["sessions_reset"] == 2
    assert driver._sessions == {}


def test_run_port_when_verify_stays_unclean_then_reset_and_run_may_continue():
    calls = []

    def call(action, **variables):
        calls.append(action)
        clean = action != "verify"
        return {
            "ok": True,
            "host_seconds": 0.01,
            "path_restored": True,
            "data": {"clean": clean, "sessions_reset": 1},
        }

    receipt = driver.run_port(
        call, {"source_id": "one", "implementation": "blocked"}, pause=lambda _: None
    )
    assert receipt["status"] == "failed" and "reset" in calls
    assert receipt["continue_safe"], "a clean reset lets the run go on"
    assert receipt["reset"]["sessions_reset"] == 1


def test_dependencies_when_port_delegates_then_closure_includes_helpers_and_package():
    manifest = json.loads((ROOT / "catalog/ports.json").read_text())
    row = next(r for r in manifest["ports"] if r["source_id"] == "029ea0dabe87ae57")
    files = driver.dependencies(ROOT, row)
    assert files == sorted(set(files))
    assert row["target_path"] in files
    assert (
        "ports/itemviews/pyqt-official/basicsortfiltermodel-9dab02b61cebbdb7.py"
        in files
    )
    assert "ports/layouts/pyqt-official/basiclayouts-2f94fe07de765888.py" in files
    assert "fontlab_python_examples/launcher.py" in files
    assert all((ROOT / name).is_file() for name in files)


def test_dependencies_when_synthetic_tree_then_recursive_and_missing_names_ignored(
    tmp_path,
):
    (tmp_path / "ports/x").mkdir(parents=True)
    (tmp_path / "fontlab_python_examples").mkdir()
    (tmp_path / "fontlab_python_examples/launcher.py").write_text("")
    (tmp_path / "ports/x/a.py").write_text(
        'S.port("x/b.py")\npath = root / "made-at-runtime.txt"\n'
    )
    (tmp_path / "ports/x/b.py").write_text('helper = "x/c.py"\n')
    (tmp_path / "ports/x/c.py").write_text("")
    row = {"target_path": "ports/x/a.py", "replacement_files": ["ports/x/a.py"]}
    assert driver.dependencies(tmp_path, row) == [
        "fontlab_python_examples/launcher.py",
        "ports/x/a.py",
        "ports/x/b.py",
        "ports/x/c.py",
    ]


def test_dependencies_when_resources_shipped_then_closure_includes_them():
    manifest = json.loads((ROOT / "catalog/ports.json").read_text())
    row = next(r for r in manifest["ports"] if r["source_id"] == "631cc1bc310c00b9")
    closure = driver.dependencies(ROOT, row)
    for resource in row["resources"]:
        assert resource["target_path"] in closure, resource["target_path"]


def test_changed_files_when_dependency_edited_during_run_then_reported(tmp_path):
    (tmp_path / "a.py").write_text("one")
    before = driver.file_hashes(tmp_path, ["a.py"])
    assert driver.changed_files(tmp_path, before) == []
    (tmp_path / "a.py").write_text("two")
    assert driver.changed_files(tmp_path, before) == ["a.py"]


def test_run_revision_when_git_checkout_then_commit_and_dirty_flag(tmp_path):
    import subprocess

    def git(*args):
        subprocess.run(
            ["git", "-C", str(tmp_path), *args], check=True, capture_output=True
        )

    git("init", "-q")
    (tmp_path / "f.txt").write_text("x")
    git("add", "f.txt")
    git("-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-qm", "c")
    revision = driver.run_revision(tmp_path)
    assert len(revision["commit"]) == 40 and revision["dirty"] is False
    (tmp_path / "f.txt").write_text("y")
    assert driver.run_revision(tmp_path)["dirty"] is True
