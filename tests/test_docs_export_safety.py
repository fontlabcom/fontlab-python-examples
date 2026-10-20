# this_file: tests/test_docs_export_safety.py
"""Only owned manifest/page fixtures execute; never a rescued generator."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module():
    spec = importlib.util.spec_from_file_location(
        "owned_examples_docs", ROOT / "src_docs/build.py"
    )
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def fixture(tmp_path, monkeypatch):
    source = tmp_path / "checkpoint"
    source.mkdir()
    data = b"# Retained title\n\nOriginal paragraph.\n"
    (source / "index.md").write_bytes(data)
    row = {
        "path": "index.md",
        "title": "Retained title",
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    (source / "manifest.json").write_text(
        json.dumps(
            {
                "format": "fontlab-python-examples.docs-export.v1",
                "counts": {"records": 299},
                "pages": [row],
            }
        )
    )
    monkeypatch.setenv("FONTLAB_RETAINED_EXPORT", str(source))
    return source, row


def test_export_when_verified_then_never_execute_rescued_source_and_preserve_input(
    tmp_path, monkeypatch
):
    mod = module()
    source, _row = fixture(tmp_path, monkeypatch)
    before = {p.name: p.read_bytes() for p in source.iterdir()}
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *a, **k: pytest.fail("Must not execute a rescued exporter"),
    )
    mod.export(tmp_path)
    assert before == {p.name: p.read_bytes() for p in source.iterdir()}
    target = tmp_path / ".build/export"
    manifest = json.loads((target / "manifest.json").read_text())
    assert manifest["counts"] == {"records": 299}
    assert (
        manifest["pages"][0]["sha256"]
        == hashlib.sha256((target / "index.md").read_bytes()).hexdigest()
    )
    assert (target / "index.md").read_text().count("!!! note") == 1
    monkeypatch.setenv("FONTLAB_RETAINED_EXPORT", str(target))
    mod.export(tmp_path)
    assert (target / "index.md").read_text().count("!!! note") == 1


@pytest.mark.parametrize(
    "fault", ["traversal", "hash", "duplicate", "symlink", "format"]
)
def test_export_when_bad_input_then_keep_accepted_output(tmp_path, monkeypatch, fault):
    mod = module()
    source, row = fixture(tmp_path, monkeypatch)
    manifest = json.loads((source / "manifest.json").read_text())
    if fault == "traversal":
        manifest["pages"][0]["path"] = "../outside.md"
    elif fault == "hash":
        manifest["pages"][0]["sha256"] = "bad"
    elif fault == "duplicate":
        manifest["pages"].append(dict(row))
    elif fault == "format":
        manifest["format"] = "other"
    else:
        (tmp_path / "outside.md").write_bytes((source / "index.md").read_bytes())
        (source / "index.md").unlink()
        (source / "index.md").symlink_to(tmp_path / "outside.md")
    (source / "manifest.json").write_text(json.dumps(manifest))
    output = tmp_path / ".build/export"
    output.mkdir(parents=True)
    (output / "accepted.md").write_text("keep")
    with pytest.raises(ValueError):
        mod.export(tmp_path)
    assert (output / "accepted.md").read_text() == "keep"
