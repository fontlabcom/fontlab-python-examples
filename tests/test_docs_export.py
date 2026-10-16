# SPDX-License-Identifier: Apache-2.0
# this_file: tests/test_docs_export.py
"""docs-export/ is complete, exact, deterministic and current."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docs_export

PORTS = json.loads((ROOT / "catalog/ports.json").read_text())["ports"]


def test_build_when_run_twice_then_identical_bytes():
    assert docs_export.build(ROOT) == docs_export.build(ROOT)


def test_committed_export_when_checked_then_current():
    done = subprocess.run(
        [sys.executable, str(ROOT / "tools/docs_export.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr


def test_manifest_when_read_then_lists_every_page_with_hash_and_counts():
    pages = docs_export.build(ROOT)
    manifest = json.loads(pages["manifest.json"])
    assert manifest["format"] == "fontlab-python-examples.docs-export.v1"
    listed = {page["path"]: page["sha256"] for page in manifest["pages"]}
    assert set(listed) == set(pages) - {"manifest.json"}
    for path, digest in listed.items():
        assert hashlib.sha256(pages[path].encode()).hexdigest() == digest, path
    implemented = sum(p["implementation"] == "implemented" for p in PORTS)
    assert manifest["counts"]["records"] == len(PORTS) == 299
    assert manifest["counts"]["implemented"] == implemented
    assert manifest["counts"]["recipes"] == 9 and manifest["counts"]["insights"] == 18
    for name in docs_export.inputs(ROOT):
        assert (
            manifest["inputs"][name]
            == hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        )


def test_category_pages_when_built_then_every_record_once_with_exact_status():
    pages = docs_export.build(ROOT)
    text = "".join(v for k, v in pages.items() if k.startswith("categories/"))
    for port in PORTS:
        assert text.count(f"- Port: [`{port['target_path']}`]") == 1, port["source_id"]
        block = text.split(f"- Port: [`{port['target_path']}`]", 1)[1].split(
            "\n### ", 1
        )[0]
        assert f"- Implementation: **{port['implementation']}**" in block
        assert f"- Licence: {port['license']['selected']}" in block
        if port["implementation"] == "implemented":
            assert f'examples.launch("{port["source_id"]}")' in block
            assert block.count("- Native acceptance: passed") == 1
        else:
            assert "- Blocked: " in block and "examples.launch" not in block


def test_links_when_relative_then_target_an_exported_page():
    pages = docs_export.build(ROOT)
    for path, text in pages.items():
        if not path.endswith(".md"):
            continue
        for target in re.findall(r"\]\(([^)#\s]+)", text):
            if re.match(r"[a-z]+:", target):
                continue
            resolved = (Path(path).parent / target).as_posix()
            parts = []
            for part in resolved.split("/"):
                parts.pop() if part == ".." else parts.append(part)
            assert "/".join(parts) in pages, (path, target)


def test_anchors_when_titles_repeat_then_suffixed_like_markdown_toc():
    assert docs_export.anchors(["A/b", "a/B", "A b!"]) == ["ab", "ab_1", "a-b"]


def test_source_base_url_when_given_then_repository_links_use_it():
    pages = docs_export.build(ROOT, "https://example.test/repo/")
    assert "https://example.test/repo/ports/" in pages["categories/widgets.md"]
    assert (
        json.loads(pages["manifest.json"])["source_base_url"]
        == "https://example.test/repo/"
    )


def test_manifest_inputs_when_listed_then_include_every_recipe_readme(tmp_path):
    readmes = sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "examples/recipes").rglob("README.md")
    )
    inputs = json.loads(docs_export.build(ROOT)["manifest.json"])["inputs"]
    assert set(readmes) <= set(inputs) and len(readmes) == 10
    import shutil

    for name in ("catalog/ports.json", "catalog/sources.json", "catalog/insights.json"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    shutil.copytree(ROOT / "examples/recipes", tmp_path / "examples/recipes")
    for name in ("README.md", "native_manifest.json"):
        (tmp_path / "examples/getgo").mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / "examples/getgo" / name, tmp_path / "examples/getgo" / name)
    shutil.copytree(ROOT / "examples/samples", tmp_path / "examples/samples")
    before = json.loads(docs_export.build(tmp_path)["manifest.json"])["inputs"]
    readme = tmp_path / "examples/recipes/layer_backup/README.md"
    readme.write_text(readme.read_text() + "\nEdited.\n")
    after = json.loads(docs_export.build(tmp_path)["manifest.json"])["inputs"]
    changed = {k for k in before if before[k] != after[k]}
    assert changed == {"examples/recipes/layer_backup/README.md"}


def test_links_when_github_fontlabcom_then_only_public_repositories():
    public = {
        "fontlab-python-docs",
        "fontlab-python-examples",
        "typerig-lib",
        "extend-fontlab",
    }
    for path, text in docs_export.build(ROOT).items():
        for repo in re.findall(r"github\.com/fontlabcom/([\w.-]+)", text):
            assert repo in public, (path, repo)


def test_getgo_page_when_built_then_links_public_fonts_and_counts_examples():
    pages = docs_export.build(ROOT)
    text = pages["getgo.md"]
    assert text.startswith("# Real GetGo fonts")
    assert text.count("https://code.fontlab.com/getgo-fonts/") >= 13, "each example links its GetGo page"
    assert "](getgo.md)" in pages["index.md"]
    manifest = json.loads(pages["manifest.json"])
    native = json.loads((ROOT / "examples/getgo/native_manifest.json").read_text())
    assert manifest["counts"]["getgo_examples"] == len(native["examples"]) == 13
    assert "examples/getgo/README.md" in manifest["inputs"]
    assert "(../../testdata" not in text, "relative repository links must be absolute"


def test_check_when_finder_metadata_is_present_then_export_stays_current_and_is_kept(tmp_path):
    out = tmp_path / "docs-export"
    base = [sys.executable, str(ROOT / "tools/docs_export.py"), "--output", str(out)]
    assert subprocess.run(base, capture_output=True, text=True).returncode == 0
    for junk in (".DS_Store", "._index.md", "categories/.DS_Store"):
        (out / junk).write_bytes(b"finder")
    done = subprocess.run([*base, "--check"], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert subprocess.run(base, capture_output=True, text=True).returncode == 0
    assert (out / ".DS_Store").is_file(), "generation must not delete or depend on Finder files"
