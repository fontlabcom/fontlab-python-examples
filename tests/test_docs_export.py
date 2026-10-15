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
    for name in docs_export.INPUTS:
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
