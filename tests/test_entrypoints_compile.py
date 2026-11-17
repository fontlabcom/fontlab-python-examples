# this_file: tests/test_entrypoints_compile.py
# SPDX-License-Identifier: Apache-2.0
"""Compile every menu, example and lesson without importing host modules."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_entrypoints_compile():
    for folder in ("Scripts", "examples", "lessons"):
        paths = sorted((ROOT / folder).rglob("*.py"))
        assert paths, f"No Python sources found in {folder}"
        for path in paths:
            compile(path.read_bytes(), str(path), "exec")
