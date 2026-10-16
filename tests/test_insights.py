# this_file: tests/test_insights.py
"""Original insight examples tested at the existing Qt boundary, never native proof."""

import json
from pathlib import Path

import insight_doubles
import pytest
import test_second_batch

# Expose existing fixtures without redefining the boundary.
insight_qt = insight_doubles.insight_qt
batch_qt = test_second_batch.batch_qt

from workspace_paths import reference_file

ROOT = Path(__file__).resolve().parents[1]


def records():
    return json.loads((ROOT / "catalog/insights.json").read_text(encoding="utf-8"))[
        "insights"
    ]


@pytest.mark.parametrize(
    "slug",
    [
        "signal-lifetime",
        "glyph-list",
        "metrics-table",
        "timer-batch",
        "contour-canvas",
        "owned-key-filter",
        "metric-controls",
        "glyph-properties",
        "sandbox-settings",
        "callback-errors",
        "owned-dock",
        "contour-scene",
    ],
)
def test_insight_when_launched_then_inspects_and_disconnects_before_deletion(
    slug, insight_qt
):
    from fontlab_python_examples import close, inspect, launch

    handle = launch(slug)
    assert launch(slug) is handle, "Named relaunch must preserve owned identity"
    json.dumps(inspect(slug))
    assert inspect(slug)["closed"] is False
    pairs = list(handle.connections)
    events = []
    for obj, signature, slot in pairs:
        signal = obj.clicked if signature else obj
        assert slot in signal.callbacks, (
            "Every connection must retain its exact callable"
        )
        original = signal.disconnect

        def disconnect(callback, original=original):
            events.append("disconnect")
            original(callback)

        signal.disconnect = disconnect
    original_close = handle.owner.close

    def delete():
        assert not handle.connections and not handle.callbacks
        assert handle.model is None and handle.inspect_ui is dict
        for obj, signature, slot in pairs:
            assert slot not in (obj.clicked if signature else obj).callbacks
        events.append("delete")
        original_close()

    handle.owner.close = delete
    close(slug)
    assert events == ["disconnect"] * len(pairs) + ["delete"]
    assert close(slug)["closed"] is True


def test_manifest_when_validated_then_unique_original_targets_and_real_citations():
    data = json.loads((ROOT / "catalog/insights.json").read_text())
    assert data["schema_version"] == "fontlab.examples-insights.v1"
    items = records()
    assert len(items) == len({r["slug"] for r in items}) == 18
    assert [r["rank"] for r in items] == list(range(1, 19))
    sources = json.loads(
        (ROOT / "catalog/pythonqt-reference-manifest.json").read_text()
    )["sources"]
    by_name = {s["name"]: s for s in sources}
    for item in items:
        assert item["native_acceptance"] in {"unexecuted", "pending", "passed"}
        if item["native_acceptance"] != "unexecuted":
            assert item.get("native_evidence"), "native states need workspace receipts"
        assert item["license"] == "Apache-2.0"
        assert item["target_path"] == f"ports/insights/{item['slug']}.py"
        source = (ROOT / item["target_path"]).read_text()
        assert source.startswith(f"# this_file: {item['target_path']}")
        assert item["title"] and item["idiom"] and item["native_checks"]
        assert 1 <= len(item["inspiration"]) <= 3
        for cite in item["inspiration"]:
            path, line = cite["citation"].rsplit(":", 1)
            assert path.startswith("_reference/")
            assert 1 <= int(line) <= len(reference_file(path).read_text().splitlines())
            name = path.split("/")[1]
            assert cite["license"]["evidence_paths"] == by_name[name]["license_files"]
            assert cite["license"]["status"] == "unresolved"
            assert cite["citation"] in source, "Header must cite actual inspiration"


def test_partial_build_when_child_creation_fails_then_owned_window_is_closed(
    insight_qt, monkeypatch
):
    from fontlab_python_examples import inspect, launch

    windows = []
    widget = insight_qt.QtGui.QWidget

    def window():
        value = widget()
        windows.append(value)
        return value

    def fail(*args):
        raise RuntimeError("child creation failed")

    monkeypatch.setattr(insight_qt.QtGui, "QWidget", window)
    monkeypatch.setattr(insight_qt.QtGui, "QLabel", fail)
    with pytest.raises(RuntimeError, match="child creation failed"):
        launch("signal-lifetime")
    assert windows[0].deleted, "Partial builds must close the root owner"
    assert inspect("signal-lifetime")["launched"] is False


@pytest.mark.parametrize("slug", ["timer-batch", "owned-key-filter"])
def test_native_owner_when_already_destroyed_then_cleanup_avoids_dead_calls(
    slug, insight_qt, monkeypatch
):
    from fontlab_python_examples import close, launch

    handle = launch(slug)
    controls = handle.controls

    def dead(*args):
        raise AssertionError("Native wrappers must not be called after destruction")

    if slug == "timer-batch":
        controls["timer"].stop()  # Native parent destruction also removes its timer.
        monkeypatch.setattr(controls["timer"], "stop", dead)
    else:
        monkeypatch.setattr(controls["editor"], "removeEventFilter", dead)
    handle.owner.close()
    assert close(slug)["closed"] is True
