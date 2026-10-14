# this_file: tests/test_insight_batch_two.py
"""Second insight batch at the hardened Qt boundary; no native acceptance."""

import hashlib
import json
from pathlib import Path

import advanced_insight_doubles
import insight_doubles
import pytest
import test_second_batch

insight_qt = insight_doubles.insight_qt
batch_qt = test_second_batch.batch_qt
advanced_qt = advanced_insight_doubles.advanced_qt
ROOT = Path(__file__).resolve().parents[1]
SLUGS = (
    "loaded-glyph-form",
    "worker-glyph-queue",
    "owned-repl",
    "plugin-tokens",
    "metrics-undo",
    "compiled-slot-exposure",
)


def test_second_insight_manifest_when_registered_then_ranks_and_controller_contract():
    records = json.loads((ROOT / "catalog/insights.json").read_text())["insights"]
    new = [r for r in records if r["rank"] >= 13]
    assert [r["rank"] for r in new] == list(range(13, 19))
    assert tuple(r["slug"] for r in new) == SLUGS
    for record in new:
        assert record["native_acceptance"] in {"unexecuted", "passed"}
        if record["native_acceptance"] == "passed":
            assert record.get("native_evidence"), "passed needs receipts"
        assert record["controls"] and record["native_checks"]
        assert (ROOT / record["target_path"]).is_file()
        for resource in record.get("resources", []):
            assert resource["license"] == "Apache-2.0"
            assert (
                hashlib.sha256(
                    (ROOT / resource["target_path"]).read_bytes()
                ).hexdigest()
                == resource["sha256"]
            )


@pytest.mark.parametrize("slug", SLUGS)
def test_second_insight_when_launched_then_controls_inspection_and_cleanup(
    slug, advanced_qt
):
    from fontlab_python_examples import close, describe, inspect, launch

    h = launch(slug)
    assert launch(slug) is h
    assert set(h.controls) == set(describe(slug)["controls"])
    json.dumps(inspect(slug))
    assert "controls" not in h.widget.__dict__
    pairs = list(h.connections)
    original = h.owner.close

    def delete():
        assert not h.connections and not h.controls and not h.callbacks
        for obj, signature, slot in pairs:
            assert slot not in (obj.clicked if signature else obj).callbacks
        original()

    h.owner.close = delete
    close(slug)
    assert close(slug)["closed"]


def test_loaded_form_when_driven_then_named_fields_update_and_temporaries_close(
    advanced_qt, monkeypatch, tmp_path
):
    from fontlab_python_examples import launch

    monkeypatch.chdir(tmp_path)
    h = launch("loaded-glyph-form")
    h.controls["glyph_name"].setText("A.alt")
    h.controls["advance"].setValue(720)
    h.controls["apply"].clicked.emit()
    assert h.snapshot()["result"] == "A.alt: advance 720"
    assert all(obj.deleted for obj in advanced_qt.temporary_objects)


@pytest.mark.parametrize("failure", ["open", "constructor", "load", "controls"])
def test_loaded_form_when_failure_then_partial_owned_root_and_temporaries_clean(
    advanced_qt, monkeypatch, failure
):
    from fontlab_python_examples import inspect, launch

    qt = advanced_qt
    roots, widget = [], qt.QtGui.QWidget

    def root():
        value = widget()
        roots.append(value)
        return value

    monkeypatch.setattr(qt.QtGui, "QWidget", root)
    if failure == "open":
        monkeypatch.setattr(qt.QtCore.QFile, "open", lambda self, mode: False)
        monkeypatch.setattr(
            qt.QtCore.QFile, "errorString", lambda self: "Cannot read", raising=False
        )
    elif failure == "constructor":

        def fail():
            raise RuntimeError("loader failed")

        monkeypatch.setattr(qt.QtUiTools, "QUiLoader", fail)
    elif failure == "load":
        monkeypatch.setattr(qt.QtUiTools.QUiLoader, "load", lambda *args: None)
    else:
        monkeypatch.setattr(
            qt.QtUiTools.QUiLoader, "load", lambda self, source, parent: widget(parent)
        )
    with pytest.raises((RuntimeError, OSError)):
        launch("loaded-glyph-form")
    assert roots[0].deleted
    assert all(obj.deleted for obj in qt.temporary_objects)
    assert not inspect("loaded-glyph-form")["launched"]


@pytest.mark.parametrize(
    "slug, module, member",
    [
        ("loaded-glyph-form", "QtUiTools", "QUiLoader"),
        ("metrics-undo", "QtGui", "QUndoStack"),
        ("metrics-undo", "QtGui", "QUndoCommand"),
        ("compiled-slot-exposure", "QtCore", "QPoint"),
        ("compiled-slot-exposure", "QtGui", "QLineEdit"),
    ],
)
def test_optional_class_when_absent_then_clear_required_host_message(
    slug, module, member, advanced_qt, monkeypatch
):
    from fontlab_python_examples import launch

    monkeypatch.delattr(getattr(advanced_qt, module), member)
    with pytest.raises(RuntimeError, match=f"requires PythonQt.{module}.{member}"):
        launch(slug)


def test_compiled_slots_when_not_wrapped_then_clear_failure_and_owned_rollback(
    advanced_qt, monkeypatch
):
    from types import SimpleNamespace

    from fontlab_python_examples import launch

    monkeypatch.setattr(
        advanced_qt.QtGui.QLineEdit,
        "metaObject",
        lambda self: SimpleNamespace(indexOfSlot=lambda signature: -1),
    )
    with pytest.raises(RuntimeError, match="Host must expose"):
        launch("compiled-slot-exposure")
