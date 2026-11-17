# this_file: tests_docs/test_source_snapshot.py
"""Public metadata retains exact source identity without rendering implementation."""
import hashlib
import importlib.util
from pathlib import Path
from urllib.parse import quote
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize("name", ["A (B).py", "Accented Ż.py", "Tick's Proof.py", "Dots.A.py"])
def test_menu_source_when_filename_contains_punctuation_then_exact_safe_include(tmp_path, monkeypatch, name):
    spec = importlib.util.spec_from_file_location("owned_menu_docs", ROOT / "src_docs/current_menus.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = tmp_path / "Scripts/Reports" / name
    source.parent.mkdir(parents=True)
    data = b'"""Owned report fixture."""\nprint("source is not executed")\n'
    source.write_bytes(data)
    from subprocess import CompletedProcess
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: CompletedProcess(args[0], 0, data))
    module.catalogue(tmp_path, revision="a" * 40)
    pages = [p for p in (tmp_path / "src_docs/md/current").glob("*/*.md") if p.name != "index.md"]
    assert len(pages) == 1
    text = pages[0].read_text()
    digest = hashlib.sha256(data).hexdigest()
    assert "Owned report fixture." in text
    assert digest in text
    assert "https://github.com/fontlabcom/fontlab-python-examples/blob/" + "a" * 40 + "/" + quote(source.relative_to(tmp_path).as_posix(), safe="/") in text
    assert "codeinclude" not in text and 'print("source is not executed")' not in text
    assert (tmp_path / ".build/menu-sources" / (digest + ".py")).read_bytes() == data
    assert source.read_bytes() == data


@pytest.mark.parametrize("revision", ["", "main", "0" * 39, "g" * 40])
def test_catalogue_when_revision_invalid_then_existing_output_survives(tmp_path, revision):
    spec = importlib.util.spec_from_file_location("owned_menu_docs", ROOT / "src_docs/current_menus.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = tmp_path / "src_docs/md/current/sentinel.md"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"owned prior output")
    with pytest.raises(ValueError, match="complete source commit"):
        module.catalogue(tmp_path, revision=revision)
    assert output.read_bytes() == b"owned prior output"


@pytest.mark.parametrize("committed", [None, b'"""Older source."""'])
def test_catalogue_when_source_is_new_or_modified_then_does_not_invent_link(tmp_path, monkeypatch, committed):
    from src_docs import current_menus
    from subprocess import CompletedProcess

    source = tmp_path / "Scripts/Drawing/Local.py"
    source.parent.mkdir(parents=True)
    data = b'"""New drawing example."""\n'
    source.write_bytes(data)
    monkeypatch.setattr(current_menus.subprocess, "run", lambda *args, **kwargs: CompletedProcess(args[0], int(committed is None), committed or b""))
    current_menus.catalogue(tmp_path, revision="a" * 40)
    text = (tmp_path / "src_docs/md/current/drawing/local.md").read_text()
    assert hashlib.sha256(data).hexdigest() in text
    assert "Scripts/Drawing/Local.py" in text
    assert "uncommitted" in text
    assert "/blob/" not in text
