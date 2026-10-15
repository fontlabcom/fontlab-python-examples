#!/usr/bin/env -S uv run --python 3.11 -s
# /// script
# requires-python = ">=3.11"
# dependencies = ["fontlab-remopy"]
# [tool.uv.sources]
# fontlab-remopy = { path = "../../fontlab-remopy" }
# ///
# SPDX-License-Identifier: Apache-2.0
# this_file: tools/native_cleanroom.py
"""Launch/inspect/close acceptance through Remopy, one short host call per phase.

Run in an owned FontLab session. This driver never edits catalogue acceptance
(tools/record_native.py applies a reviewed proposal). From the workspace root:

    verification/issue-104/fl-native.sh --lane L6c -- bash -c \
      "cd fontlab-python-examples && uv run --python 3.11 tools/native_cleanroom.py --output OUT.jsonl"

fontlab-remopy resolves from the sibling ../fontlab-remopy checkout (not on PyPI).
Its destroyed-signal witnesses retain plain data only and expire with Qt objects.
No application loop, processEvents, screen/clipboard/tray action or font mutation.
"""

import argparse
import hashlib
import importlib
import json
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

HOST_BUDGET = 3.5
_sessions: dict[str, dict] = {}
PREFIXES = (
    "fontlab_python_examples",
    "fontlab_example_",
    "fontlab_cleanroom_",
    "cleanroom_",
    "fontlabapp",
)

# Import by exact filename, independently of any other checkout's tools package.
HOST_CODE = """import sys, importlib.util
from pathlib import Path
_old = list(sys.path)
try:
    sys.path[:] = [checkout, *extras] + [p for p in _old if p != checkout and p not in extras]
    _key = '_fontlab_native_cleanroom_driver'
    _file = Path(checkout) / 'tools/native_cleanroom.py'
    _module = sys.modules.get(_key)
    if _module is None or Path(_module.__file__).resolve() != _file.resolve() or getattr(_module, '_driver_sha256', None) != driver_sha256:
        if _module is not None and getattr(_module, '_sessions', None):
            raise RuntimeError('Previous native acceptance still owns a session')
        _spec = importlib.util.spec_from_file_location(_key, _file)
        _module = importlib.util.module_from_spec(_spec)
        sys.modules[_key] = _module
        _spec.loader.exec_module(_module)
        _module._driver_sha256 = driver_sha256
    result = _module.host_step(action, port_id, token, checkout, extras)
finally:
    sys.path[:] = _old
result['path_restored'] = result['path_restored'] and sys.path == _old
"""


def select_records(manifest: dict, ids: list[str]) -> list[dict]:
    """Select only receipt-integrated ports; reject typos and duplicate requests."""
    records = {
        r["source_id"]: r for r in manifest["ports"] if r.get("clean_room_receipt")
    }
    requested = ids or list(records)
    if len(requested) != len(set(requested)) or set(requested) - records.keys():
        raise ValueError("IDs must be distinct integrated clean-room port IDs")
    selected = [records[pid] for pid in requested]
    if not selected or any(
        r["implementation"] not in {"implemented", "blocked"} for r in selected
    ):
        raise ValueError("Integrate the clean-room receipts before native acceptance")
    return selected


def batches(items: list, size: int):
    """Batch client connections only; never combine ports in one FontLab call."""
    if size < 1:
        raise ValueError("Batch size must be positive")
    for start in range(0, len(items), size):
        yield items[start : start + size]


@contextmanager
def checkout_path(root: Path, extras: tuple = ()):
    """The checkout (and e.g. a fontlab-fontlabapp src) first; restored afterwards."""
    previous = list(sys.path)
    first = [str(root.resolve()), *(str(Path(e).resolve()) for e in extras)]
    try:
        sys.path[:] = first + [p for p in previous if p not in first]
        yield
    finally:
        sys.path[:] = previous


def purge_examples(modules: dict) -> int:
    """Refuse to unload code while any launcher retains a live example."""
    names = [name for name in modules if name.startswith(PREFIXES)]
    for name in names:
        if getattr(modules[name], "_handles", None):
            raise RuntimeError(
                "Existing examples are retained; close them before acceptance"
            )
    for name in names:
        del modules[name]
    importlib.invalidate_caches()
    return len(names)


def compact(value: Any, depth: int = 0) -> Any:
    """Bound Remopy's 64 KiB output without evaluating native properties."""
    if isinstance(value, str):
        return value[:300]
    if depth > 3:
        return "<truncated>"
    if isinstance(value, dict):
        return {str(k): compact(v, depth + 1) for k, v in list(value.items())[:16]}
    if isinstance(value, (list, tuple)):
        return [compact(v, depth + 1) for v in value[:12]]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return "<non-JSON value>"


def read(obj: Any, name: str) -> Any:
    value = getattr(obj, name)
    return value() if callable(value) else value


def _windows(qt: Any) -> dict:
    # str(QObject) identifies the native pointer, including when wrappers differ.
    return {
        str(w): w
        for w in list(qt.QtGui.QApplication.topLevelWidgets())
        + list(qt.QtGui.QApplication.topLevelWindows())
    }


def _fds() -> set[str]:
    import os

    try:
        names = os.listdir("/dev/fd")
    except OSError:
        return set()
    result = set()
    for name in names:
        try:
            os.fstat(int(name))
        except (ValueError, OSError):
            continue
        result.add(name)
    return result


def _prepare(token: str, pid: str, root: Path, extras: tuple = ()) -> dict:
    if _sessions:
        raise RuntimeError("An earlier acceptance session still needs cleanup")
    purged = purge_examples(sys.modules)
    launcher = importlib.import_module("fontlab_python_examples.launcher")
    package = importlib.import_module("fontlab_python_examples")
    if (
        Path(launcher.__file__).resolve()
        != root / "fontlab_python_examples/launcher.py"
        or Path(package.__file__).resolve()
        != root / "fontlab_python_examples/__init__.py"
    ):
        raise RuntimeError("Example import does not come from the requested checkout")
    if extras:
        widgets = Path(importlib.import_module("fontlabapp.widgets").__file__).resolve()
        if not any(widgets.is_relative_to(Path(e).resolve()) for e in extras):
            raise RuntimeError("fontlabapp does not come from the requested source")
    row = launcher.describe(pid)
    if not row.get("clean_room_receipt"):
        raise ValueError("Port has no integrated clean-room receipt")
    qt = importlib.import_module("PythonQt")
    app = qt.QtGui.QApplication.instance()
    if app is None:
        raise RuntimeError("FontLab's existing QApplication is required")
    _sessions[token] = {
        "pid": pid,
        "launcher": launcher,
        "row": row,
        "qt": qt,
        "app": app,
        "windows": _windows(qt),
        "threads": {t.ident for t in threading.enumerate()},
        "fds": _fds(),
        "watched": {},
        "destroyed": set(),
        "callbacks": [],
        "temporary": set(),
        "runtime": {},
        "handle": None,
    }
    return {
        "purged": purged,
        "import_verified": True,
        "module": "fontlab_python_examples/launcher.py",
    }


def _watch(session: dict) -> None:
    """Observe only owned QObjects, never arbitrary properties on controls."""
    handle = session["handle"]
    if handle is None:
        return
    queue = [handle.widget] + [a.widget for a in handle.alerts if not a.closed]
    queue += list(handle.controls.values())
    deadline = time.monotonic() + 1.5
    while queue:
        if len(session["watched"]) >= 2048 or time.monotonic() >= deadline:
            raise RuntimeError("Owned object traversal exceeded the short-call budget")
        obj = queue.pop()
        if obj is None or not callable(getattr(type(obj), "inherits", None)):
            continue
        try:  # a class wrapper kept as a control has an unbound inherits()
            obj.inherits("QObject")
        except TypeError:
            continue
        key = str(obj)
        # Explicit safe methods only; generic property enumeration can crash
        # unloaded native renderers in this PythonQt build.
        for native, method in [
            ("QTimer", "isActive"),
            ("QBasicTimer", "isActive"),
            ("QThread", "isRunning"),
            ("QTcpServer", "isListening"),
            ("QLocalServer", "isListening"),
        ]:
            if obj.inherits(native):
                session["runtime"][key] = (obj, method)
        if not obj.inherits("QObject"):
            continue
        if key in session["watched"]:
            continue
        session["watched"][key] = obj

        # Native destruction auto-disconnects this witness. It never calls a
        # deleted wrapper or retains the emitted QObject argument.
        def destroyed(*args: Any, identity: str = key) -> None:
            session["destroyed"].add(identity)

        obj.connect("destroyed(QObject*)", destroyed)
        session["callbacks"].append(destroyed)
        children = getattr(obj, "children", None)
        if callable(children):  # some owned objects shadow children (e.g. None)
            queue.extend(children())
    for callback in handle.after_close:
        owner = getattr(callback, "__self__", None)
        if isinstance(owner, TemporaryDirectory):
            session["temporary"].add(owner.name)
        elif owner is not None and not callable(getattr(type(owner), "inherits", None)):
            # Batch B's bound disposal method owns a TemporaryDirectory field.
            for resource in getattr(owner, "__dict__", {}).values():
                if isinstance(resource, TemporaryDirectory):
                    session["temporary"].add(resource.name)


def _launch(session: dict) -> dict:
    launcher, row = session["launcher"], session["row"]
    if row["implementation"] == "blocked":
        original_host, original_builder = launcher._host, launcher._builder

        def forbidden(*args: Any) -> None:
            raise AssertionError("Blocked launch accessed the host or builder")

        launcher._host = launcher._builder = forbidden
        try:
            try:
                launcher.launch(session["pid"])
            except NotImplementedError as error:
                if row["blocked_reason"] not in str(error):
                    raise AssertionError(
                        "Capability exception omitted the recorded reason"
                    ) from error
                return {"capability_failure": str(error), "host_accessed": False}
            raise AssertionError("Blocked example unexpectedly launched")
        finally:
            launcher._host, launcher._builder = original_host, original_builder
    try:
        handle = launcher.launch(session["pid"])
    finally:
        session["handle"] = launcher._handles.get(session["pid"])
        _watch(session)
    if handle.owner.closed:
        raise AssertionError("Example closed during launch")
    return {"launched": True, "owned_objects": len(session["watched"])}


def _inspect(session: dict) -> dict:
    if session["row"]["implementation"] == "blocked":
        return {"blocked": True, "clean": _verify(session)["clean"]}
    _watch(session)
    handle = session["handle"]
    widget = handle.widget
    visible = bool(widget.isVisible())
    is_widget = widget.inherits("QWidget")
    top_level = bool(widget.isWindow() if is_widget else widget.isTopLevel())
    title = str(read(widget, "windowTitle" if is_widget else "title"))
    tree = [
        str(obj.className())
        for key, obj in session["watched"].items()
        if key not in session["destroyed"]
    ][:32]
    state = session["launcher"].inspect(session["pid"])
    if (
        not visible
        or not top_level
        or handle.owner.closed
        or not (title.strip() or tree)
    ):
        raise AssertionError("Example has no visible, populated top-level window")
    return {
        "visible": visible,
        "top_level": top_level,
        "title": title,
        "object_tree": tree,
        "snapshot": compact(state),
    }


def _close(session: dict) -> dict:
    handle = session["handle"]
    if handle is not None:
        _watch(session)
    result = session["launcher"].close(session["pid"])
    if handle is not None:
        if not handle.owner.closed or handle.widget is not None:
            raise AssertionError("Owned window not released")
        if any(
            getattr(handle, field)
            for field in [
                "connections",
                "controls",
                "callbacks",
                "alerts",
                "cleanup",
                "release",
                "after_close",
            ]
        ):
            raise AssertionError("Owned cleanup left retained callbacks or resources")
    running = [
        key
        for key, (obj, method) in session["runtime"].items()
        if key not in session["destroyed"] and bool(read(obj, method))
    ]
    if running:
        raise AssertionError(
            "Owned timers, threads or listeners remain active after close"
        )
    return {
        "closed": True,
        "runtime_resources_stopped": len(session["runtime"]),
        "snapshot": compact(result),
    }


def _verify(session: dict) -> dict:
    launcher, qt = session["launcher"], session["qt"]
    survivors = set(session["watched"]) - session["destroyed"]
    new_windows = set(_windows(qt)) - set(session["windows"])
    new_threads = [
        t.name for t in threading.enumerate() if t.ident not in session["threads"]
    ]
    directories = [p for p in session["temporary"] if Path(p).exists()]
    blocked = session["row"]["implementation"] == "blocked"
    descriptors = sorted(_fds() - session["fds"]) if blocked else []
    clean = not (
        survivors
        or new_windows
        or new_threads
        or directories
        or descriptors
        or launcher._handles
    )
    alive = str(qt.QtGui.QApplication.instance()) == str(session["app"])
    clean = clean and alive
    return {
        "clean": clean,
        "expected_destroyed": len(session["watched"]),
        "destroyed": len(session["destroyed"]),
        "surviving_objects": len(survivors),
        "new_windows": len(new_windows),
        "new_threads": new_threads,
        "temporary_directories_remaining": len(directories),
        "new_file_descriptors": len(descriptors) if blocked else None,
        "registry_empty": not launcher._handles,
        "host_alive": alive,
    }


def host_step(action: str, port_id: str, token: str, checkout: str, extras: tuple = ()) -> dict:
    """Called in FontLab. Each phase restores sys.path even when it fails."""
    original = list(sys.path)
    started = time.monotonic()
    existed = token in _sessions
    result = {"ok": False, "data": None}
    try:
        with checkout_path(Path(checkout), tuple(extras)):
            if action == "prepare":
                data = _prepare(token, port_id, Path(checkout).resolve(), tuple(extras))
            else:
                session = _sessions[token]
                if session["pid"] != port_id:
                    raise ValueError("Acceptance token belongs to another port")
                if action == "launch":
                    data = _launch(session)
                elif action == "inspect":
                    data = _inspect(session)
                elif action == "close":
                    data = _close(session)
                elif action == "verify":
                    data = _verify(session)
                elif action == "finish":
                    data = _verify(session)
                    if not data["clean"]:
                        raise RuntimeError("Owned resources still survive")
                    del _sessions[token]
                    purge_examples(sys.modules)
                else:
                    raise ValueError("Unknown acceptance phase")
            result.update(ok=True, data=data)
    except Exception as error:  # noqa: BLE001 - transport a phase failure as plain data
        result["error"] = {"type": type(error).__name__, "message": str(error)[:2000]}
    result["host_seconds"] = time.monotonic() - started
    if not result["ok"] and action == "prepare" and not existed:
        _sessions.pop(token, None)
    result["path_restored"] = sys.path == original
    if result["host_seconds"] >= HOST_BUDGET:
        result.update(
            ok=False,
            error={"type": "Deadline", "message": "Host phase exceeded 3.5 seconds"},
        )
    return result


def run_port(call: Any, record: dict, pause: Any = time.sleep) -> dict:
    """No launch retries; always close known executions and stop on uncertainty."""
    pid, token = record["source_id"], uuid.uuid4().hex
    receipt = {
        "port_id": pid,
        "implementation": record["implementation"],
        "status": "failed",
        "phases": {},
        "continue_safe": False,
    }
    prepared = False
    uncertain = False

    def step(action: str) -> dict:
        result = call(action, port_id=pid, token=token)
        receipt["phases"][action] = result
        if (
            not result.get("ok")
            or not result.get("path_restored")
            or result.get("host_seconds", 5) >= HOST_BUDGET
        ):
            raise RuntimeError(f"{action}: {result.get('error', 'host phase failed')}")
        return result

    try:
        step("prepare")
        prepared = True
        step("launch")
        pause(0.1)
        step("inspect")
        receipt["status"] = "passed"
    except (TimeoutError, ConnectionError, OSError) as error:
        uncertain = True
        receipt.update(status="unknown", error=str(error))
    except Exception as error:  # noqa: BLE001 - per-port errors must become receipts
        receipt["error"] = str(error)
        # A transport exception has no returned phase envelope: outcome unknown.
        if prepared and "launch" not in receipt["phases"]:
            uncertain = True
            receipt["status"] = "unknown"
    finally:
        if prepared and not uncertain:
            closed = False
            try:
                step("close")
                closed = True
            except Exception as error:  # noqa: BLE001 - retain close failures too
                receipt.update(status="failed", cleanup_error=str(error))
            try:
                pause(0.15)
                for attempt in range(4):
                    verified = step("verify")
                    if verified["data"].get("clean"):
                        break
                    pause(0.15)
                else:
                    raise RuntimeError("Owned resources survived deferred destruction")
                if closed:
                    step("finish")
                    receipt["continue_safe"] = True
            except Exception as error:  # noqa: BLE001 - never hide cleanup failure
                receipt.update(status="failed", cleanup_error=str(error))
    return receipt


def summarize(results: list[dict], ids: list[str]) -> dict:
    completed = {r["port_id"] for r in results}
    return {
        "requested": len(ids),
        "recorded": len(results),
        **{
            state: sum(r["status"] == state for r in results)
            for state in ["passed", "failed", "unknown"]
        },
        "not_run": [pid for pid in ids if pid not in completed],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ids",
        nargs="+",
        default=[],
        help="Port IDs, separated by spaces or commas; default all 187",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Ports per client connection; each phase stays a separate host call",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("verification/native-cleanroom.jsonl")
    )
    parser.add_argument("--command", help="Explicit FontLab MCP bridge executable")
    parser.add_argument(
        "--fontlabapp-src",
        type=Path,
        help="fontlab-fontlabapp src to import in FontLab when it is not installed "
        "(default: a sibling ../fontlab-fontlabapp/src checkout, if present)",
    )
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    root = Path(__file__).resolve().parents[1]
    fontlabapp_src = args.fontlabapp_src or root.parent / "fontlab-fontlabapp" / "src"
    extras = [str(fontlabapp_src.resolve())] if (fontlabapp_src / "fontlabapp").is_dir() else []
    ids = [pid for value in args.ids for pid in value.split(",") if pid]
    try:
        records = select_records(
            json.loads((root / "catalog/ports.json").read_text()), ids
        )
    except ValueError as error:
        parser.error(str(error))
    from fontlab_remopy import FontLab

    results = []
    transport_error = None
    driver_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary_path = args.output.with_suffix(".summary.json")
    if summary_path.exists():
        parser.error("Summary already exists; choose a new --output")
    with args.output.open("x", encoding="utf-8") as output:
        try:
            for group in batches(records, args.batch_size):
                with FontLab(command=args.command, timeout=4) as fl:
                    for record in group:

                        def call(action: str, **variables: Any) -> dict:
                            started = time.monotonic()
                            result = fl.run(
                                HOST_CODE,
                                checkout=str(root),
                                extras=extras,
                                driver_sha256=driver_sha256,
                                action=action,
                                **variables,
                            ).value
                            result["client_seconds"] = time.monotonic() - started
                            return result

                        receipt = run_port(call, record)
                        receipt["files"] = {
                            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                            for name in record["replacement_files"]
                        }
                        results.append(receipt)
                        output.write(json.dumps(receipt, ensure_ascii=False) + "\n")
                        output.flush()
                        if not receipt["continue_safe"]:
                            return 1
        except Exception as error:  # noqa: BLE001 - connection failure needs a receipt too
            transport_error = type(error).__name__ + ": " + str(error)
            completed = {r["port_id"] for r in results}
            pending = next(
                (r for r in records if r["source_id"] not in completed), None
            )
            if pending is not None:
                receipt = {
                    "port_id": pending["source_id"],
                    "implementation": pending["implementation"],
                    "status": "unknown",
                    "phases": {},
                    "continue_safe": False,
                    "error": type(error).__name__ + ": " + str(error),
                }
                results.append(receipt)
                output.write(json.dumps(receipt) + "\n")
                output.flush()
            return 1
        finally:
            summary = summarize(results, [r["source_id"] for r in records])
            if transport_error:
                summary["driver_error"] = transport_error
            summary["driver_sha256"] = hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest()
            summary_path.write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )
            print(json.dumps(summary))
    return int(any(r["status"] != "passed" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
