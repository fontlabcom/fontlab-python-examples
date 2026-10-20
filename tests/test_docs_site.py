# this_file: tests/test_docs_site.py
"""Retained catalogue export has exact page hashes and an explicit status."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_export_when_retained_catalogue_is_present_then_all_hashes_match():
    spec = importlib.util.spec_from_file_location("examples_docs", ROOT / "src_docs/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.export(ROOT)
    output = ROOT / ".build/export"
    manifest = json.loads((output / "manifest.json").read_text())
    original = json.loads((ROOT / "src_docs/retained-export/manifest.json").read_text())
    assert manifest["counts"] == original["counts"], "Keep the full retained catalogue denominator"
    assert len(manifest["pages"]) == len(original["pages"]), "Keep every retained export page"
    for row in manifest["pages"]:
        data = (output / row["path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["sha256"], row["path"]
        assert b"retained catalogue" in data, "Archived launch instructions need a visible status"


@pytest.mark.parametrize("bad_path,bad_hash,match", [
    ("../outside.md", False, "Unsafe retained export path"),
    ("index.md", True, "differs from its manifest"),
])
def test_export_when_generated_manifest_is_invalid_then_refuses(tmp_path, monkeypatch, bad_path, bad_hash, match):
    spec = importlib.util.spec_from_file_location("examples_docs", ROOT / "src_docs/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = tmp_path / ".build/retained-export"
    output.mkdir(parents=True)
    data = b"# Retained example\n"
    (output / "index.md").write_bytes(data)
    row = {"path": bad_path, "sha256": "bad" if bad_hash else hashlib.sha256(data).hexdigest()}
    (output / "manifest.json").write_text(json.dumps({"pages": [row]}))
    monkeypatch.setenv("FONTLAB_RETAINED_EXPORT", str(output))
    data = json.loads((output / "manifest.json").read_text())
    data["format"] = "fontlab-python-examples.docs-export.v1"
    (output / "manifest.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match=match):
        module.export(tmp_path)


@pytest.mark.parametrize("arguments,command", [([], "build"), (["--serve", "--offline"], "serve"), (["--export-only"], None)])
def test_main_when_mode_is_selected_then_exports_before_rendering(monkeypatch, arguments, command):
    spec = importlib.util.spec_from_file_location("examples_docs", ROOT / "src_docs/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    called = []
    monkeypatch.setattr(module, "export", lambda root: called.append(root))
    monkeypatch.setattr(module, "catalogue", lambda root: called.append("current menus"))
    monkeypatch.setattr(module.subprocess, "run", lambda args, **kwargs: called.append(args))
    monkeypatch.setattr(sys, "argv", ["build.py", *arguments])
    module.main()
    expected = [ROOT, "current menus"]
    if command:
        expected.append(["properdocs", command, "--strict", "-f", "src_docs/mkdocs.yml"])
    assert called == expected, "Export must complete before any render or local preview"
