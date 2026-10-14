# this_file: fontlab_python_examples/launcher.py
"""Retain only owned examples across isolated Remopy Python executions."""

import json
from importlib import import_module, util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_handles: dict[str, Any] = {}


def available() -> list[dict]:
    """Return recorded names/provenance, including explicit blocked states."""
    records = json.loads((ROOT / "catalog/ports.json").read_text(encoding="utf-8"))[
        "ports"
    ]
    insight_path = ROOT / "catalog/insights.json"
    if insight_path.exists():
        for insight in json.loads(insight_path.read_text(encoding="utf-8"))["insights"]:
            records.append(
                {
                    **insight,
                    "name": insight["slug"],
                    "source_id": "insight:" + insight["slug"],
                    "source": {
                        "path": insight["target_path"],
                        "repository": "fontlab-python-examples",
                    },
                    "implementation": "implemented",
                }
            )
    return records


def describe(name: str) -> dict:
    """Resolve a human name or source ID; distinguish known unported sources."""
    for record in available():
        if name in (record["name"], record["source_id"], record["source"]["path"]):
            return record
    catalog = json.loads((ROOT / "catalog/sources.json").read_text(encoding="utf-8"))
    if any(name in (entry["id"], entry["path"]) for entry in catalog["files"]):
        raise NotImplementedError(f"Example {name!r} is known but not ported yet")
    raise ValueError(f"Unknown example {name!r}; use available() for implemented names")


def _host() -> Any:
    try:
        qt = import_module("PythonQt")
        import_module("fontlab")
    except ModuleNotFoundError as error:
        if error.name not in {"PythonQt", "fontlab"}:
            raise
        raise RuntimeError(
            "Launch examples inside FontLab with its PythonQt"
        ) from error
    if qt.QtGui.QApplication.instance() is None:
        raise RuntimeError("Launch requires FontLab's existing QApplication")
    try:
        import_module("fontlabapp.widgets")
    except ModuleNotFoundError as error:
        if error.name not in {"fontlabapp", "fontlabapp.widgets"}:
            raise
        raise RuntimeError(
            "Launch requires fontlab-fontlabapp installed inside FontLab"
        ) from error
    return qt


def _builder(record: dict) -> Any:
    module_name = "fontlab_example_" + record["source_id"]
    spec = util.spec_from_file_location(module_name, ROOT / record["target_path"])
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build


def launch(name: str) -> Any:
    """Build or reshow one owned example; return its direct native handle."""
    record = describe(name)
    if record["implementation"] == "blocked":
        raise NotImplementedError(
            f"Example {name!r} is not ported: {record['blocked_reason']}"
        )
    qt = _host()
    handle = _handles.get(record["source_id"])
    if handle is not None and not handle.owner.closed:
        handle.widget.show()
        return handle
    handle = _builder(record)(qt)
    try:
        if handle.widget.inherits("QWidget"):
            handle.widget.setAttribute(qt.QtCore.Qt.WA_QuitOnClose, False)
        handle.widget.show()
    except BaseException:
        handle.close()
        raise
    _handles[record["source_id"]] = handle
    return handle


def get(name: str) -> Any:
    """Return the retained handle for direct widget/button interaction in host."""
    source_id = describe(name)["source_id"]
    if source_id not in _handles:
        raise RuntimeError(f"Example {name!r} is not launched; call launch() first")
    return _handles[source_id]


def inspect(name: str) -> dict:
    """Return JSON-friendly state without touching a destroyed native wrapper."""
    record = describe(name)
    handle = _handles.get(record["source_id"])
    state = {"name": record["name"], "source_id": record["source_id"]}
    state.update(handle.snapshot() if handle else {"launched": False, "closed": True})
    return state


def close(name: str) -> dict:
    """Idempotently remove only this example's retained native ownership."""
    record = describe(name)
    handle = _handles.get(record["source_id"])
    if handle is not None:
        handle.close()
        del _handles[record["source_id"]]
    return inspect(name)
