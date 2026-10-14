# this_file: tests/test_metadata_encoding.py
"""Actual UTF-8 metadata under an ASCII-default text-reader boundary."""

import json
from pathlib import Path

import pytest


def test_metadata_when_default_ascii_then_unicode_names_and_unported_paths_survive(
    monkeypatch, tmp_path
):
    from fontlab_python_examples import launcher

    real_read = Path.read_text
    ports = json.loads(
        real_read(launcher.ROOT / "catalog/ports.json", encoding="utf-8")
    )
    ports["ports"][0]["name"] = "QLabel Ą–字体"
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    (catalog / "ports.json").write_text(
        json.dumps(ports, ensure_ascii=False), encoding="utf-8"
    )
    unported = "src/未移植/main.py"
    (catalog / "sources.json").write_text(
        json.dumps(
            {"files": [{"id": "unported", "path": unported}]}, ensure_ascii=False
        ),
        encoding="utf-8",
    )
    with pytest.raises(UnicodeDecodeError):
        real_read(catalog / "ports.json", encoding="ascii")

    def ascii_default(path, encoding=None, errors=None):
        return real_read(path, encoding=encoding or "ascii", errors=errors)

    monkeypatch.setattr(Path, "read_text", ascii_default)
    monkeypatch.setattr(launcher, "ROOT", tmp_path)
    record = launcher.available()[0]
    assert record["name"] == "QLabel Ą–字体", "Unicode metadata must remain unchanged"
    assert launcher.describe(record["name"])["source_id"] == record["source_id"]
    assert launcher.describe(record["source_id"])["name"] == record["name"]
    assert launcher.close(record["name"])["closed"] is True
    with pytest.raises(NotImplementedError, match="not ported"):
        launcher.describe(unported)
