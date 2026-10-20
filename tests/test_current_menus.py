# this_file: tests/test_current_menus.py
"""Check generated documentation against the actual shipped menu sources."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_catalogue_when_built_then_every_menu_has_exact_source_inclusion():
    spec = importlib.util.spec_from_file_location(
        "docs_build", ROOT / "src_docs/current_menus.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.catalogue(ROOT)
    menus = sorted((ROOT / "Scripts").glob("*/*.py"))
    pages = list((ROOT / "src_docs/md/current").glob("*/*.md"))
    pages = [p for p in pages if p.name != "index.md"]
    assert len(menus) == len(pages), "Every menu needs its own source page"
    for source in menus:
        text = "\n".join(p.read_text() for p in pages if source.stem in p.read_text())
        assert "<!--codeinclude-->" in text, (
            f"Missing live source include: {source.name}"
        )


def test_catalogue_when_menu_is_removed_then_stale_page_is_removed(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "docs_build", ROOT / "src_docs/current_menus.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    scripts = tmp_path / "Scripts/Reports"
    scripts.mkdir(parents=True)
    source = scripts / "A report.py"
    source.write_text('"""Read a font."""\n')
    module.catalogue(tmp_path)
    source.unlink()
    module.catalogue(tmp_path)
    assert not [
        p
        for p in (tmp_path / "src_docs/md/current").glob("*/*.md")
        if p.name != "index.md"
    ], "Removed menus must not remain documented"


def test_catalogue_when_filenames_collapse_to_one_slug_then_refuses(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "docs_build", ROOT / "src_docs/current_menus.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    folder = tmp_path / "Scripts/Reports"
    folder.mkdir(parents=True)
    (folder / "A B.py").write_text("pass\n")
    (folder / "A-B.py").write_text("pass\n")
    (tmp_path / "Scripts/ignored.txt").write_text("not a menu")
    (tmp_path / "Scripts/Empty").mkdir()
    with pytest.raises(ValueError, match="Duplicate documentation slug"):
        module.catalogue(tmp_path)
