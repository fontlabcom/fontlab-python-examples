# SPDX-License-Identifier: Apache-2.0
# this_file: tests/test_samples.py
"""examples/samples/: the Samples GUI scripts, their README and their docs page."""

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docs_export
import sync_samples

SAMPLES = sorted((ROOT / "examples/samples").glob("*.py"))


def test_samples_when_listed_then_present_and_parse():
    assert len(SAMPLES) >= 100, "the Samples collection is copied"
    for path in SAMPLES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        names = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        assert "main" in names, f"{path.name}: main() entry"


def test_samples_when_described_then_flm_title_and_summary():
    for path in SAMPLES:
        category, title, summary = sync_samples.describe(path)
        assert category and title and summary, path.name


def test_readme_when_checked_then_current_and_lists_every_script():
    done = subprocess.run(
        [sys.executable, str(ROOT / "tools/sync_samples.py"), "--check"],
        capture_output=True, text=True, check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    readme = (ROOT / "examples/samples/README.md").read_text(encoding="utf-8")
    for path in SAMPLES:
        assert f"]({path.name})" in readme, f"README lists {path.name}"


def test_samples_when_scanned_then_no_local_paths():
    for path in SAMPLES:
        text = path.read_text(encoding="utf-8")
        assert "/Users/" not in text and "\\Users\\" not in text, path.name


def test_samples_page_when_built_then_linked_from_index_and_counted():
    pages = docs_export.build(ROOT)
    assert "](samples.md)" in pages["index.md"]
    manifest = json.loads(pages["manifest.json"])
    assert manifest["counts"]["samples"] == len(SAMPLES)
    assert "examples/samples/README.md" in manifest["inputs"]
    text = pages["samples.md"]
    for path in SAMPLES:
        assert f"examples/samples/{path.name})" in text, f"page links {path.name} in the repository"
