# this_file: tests/test_issue122_E11.py
# SPDX-License-Identifier: Apache-2.0
"""Audit the ten retired thread/SQL identities without executing archive code.

Keep exact source paths, bytes and upstream attribution traceable. Read AST and
catalogue data only. These checks establish retirement evidence, not current
native Qt capabilities. No runtime tool, font writer or App helper is added.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
INDEX = json.loads((ROOT / "rescue-index.json").read_text(encoding="utf-8"))["menus"]
CATALOGUE = json.loads(
    (ARCHIVE / "rescued/part3/pyqt-official-ports/catalog/ports.json").read_text(
        encoding="utf-8"
    )
)["ports"]
# Freeze all identities, including the two byte-identical SQL refusals.
IDENTITIES: tuple[tuple[str, str, str], ...] = (
    ('Scripts/Archived UI L-Z/Threads - Official mandelbrot - 0788354954c8e613.py',
     'rescued/part2/ports/threads/pyqt-official/mandelbrot-0788354954c8e613.py',
     'b58d3caa4e80202c5067b4e7b86eabc46b7dd92ae61a3da7f6be28bc28f43414'),
    ('Scripts/Archived UI L-Z/Threads - Official semaphores - b95b687bbc541207.py',
     'rescued/part2/ports/threads/pyqt-official/semaphores-b95b687bbc541207.py',
     '1a82b277e5e459b1ab17380c23be1364399449be1db325f9cd0f0d7aa4161144'),
    ('Scripts/Archived UI L-Z/Threads - Official waitconditions - 27709a02d37b9ba9.py',
     'rescued/part2/ports/threads/pyqt-official/waitconditions-27709a02d37b9ba9.py',
     'a00f70fd1a22242b65a933fe20c0a7c2452403d545ad6db7ed9284c46a48fe6b'),
    ('Scripts/Archived Official/cachedtable-0b0d8d2fae153e5e - f0c5ee22.py',
     'rescued/part3/pyqt-official-ports/ports/sql/pyqt-official/cachedtable-0b0d8d2fae153e5e.py',
     '983329e5248839393d3debd5ee96f588508c0293132094c7f99cb48bd84ddd66'),
    ('Scripts/Archived Official/querymodel-2c4c366f259d7d80 - 54b2fc0d.py',
     'rescued/part3/pyqt-official-ports/ports/sql/pyqt-official/querymodel-2c4c366f259d7d80.py',
     'ddc6283b5a5f6379fb10a24c3ba7508540c34584394c749176116fcd7ed5f8ac'),
    ('Scripts/Archived Official/relationaltablemodel-9030a87a532b8d8f - bb5bbd01.py',
     'rescued/part3/pyqt-official-ports/ports/sql/pyqt-official/relationaltablemodel-9030a87a532b8d8f.py',
     'fa0b65f1ae6d9709f7cb7f9347e5746b087804d5b0c7f041e2b58530b1f5d007'),
    ('Scripts/Archived Official/tablemodel-0677ebfd7fa2cc60 - b4800039.py',
     'rescued/part3/pyqt-official-ports/ports/sql/pyqt-official/tablemodel-0677ebfd7fa2cc60.py',
     '983329e5248839393d3debd5ee96f588508c0293132094c7f99cb48bd84ddd66'),
    ('Scripts/Archived Official/mandelbrot-0788354954c8e613 - 7418b84c.py',
     'rescued/part3/pyqt-official-ports/ports/threads/pyqt-official/mandelbrot-0788354954c8e613.py',
     '4d345d8c12bbc8f7325321f7a37d475707d3eb99cf06dfd9c5163ed8ade01517'),
    ('Scripts/Archived Official/semaphores-b95b687bbc541207 - 88cd6a00.py',
     'rescued/part3/pyqt-official-ports/ports/threads/pyqt-official/semaphores-b95b687bbc541207.py',
     'ea9b20dbcd502f442df0f5405411be7e40357d471868b3e322ab75937ee1bfb2'),
    ('Scripts/Archived Official/waitconditions-27709a02d37b9ba9 - 3b5f74e3.py',
     'rescued/part3/pyqt-official-ports/ports/threads/pyqt-official/waitconditions-27709a02d37b9ba9.py',
     'faf31de1e729815bfdba3890f6e201c4c65c0f17336899e61393b0ebb91c331c'),
 )
THREADS = tuple(row for row in IDENTITIES if "/threads/" in row[1])
SQL = tuple(row for row in IDENTITIES if "/sql/" in row[1])
FAMILIES = {Path(row[1]).stem.split("-")[0] for row in IDENTITIES}


def test_inventory_when_selected_then_all_ten_identities_and_seven_families() -> None:
    """Fail on missing variants, accidental scope growth or merged SQL identities."""
    actual = {
        (row["menu"], row["target"], row["target_sha256"])
        for row in INDEX
        if any(f"/{group}/" in row["target"] for group in ("threads", "sql"))
    }
    assert actual == set(IDENTITIES), "Keep the full E11 source denominator"
    assert len(IDENTITIES) == 10 and len(THREADS) == 6 and len(SQL) == 4
    assert FAMILIES == {
        "mandelbrot", "semaphores", "waitconditions", "cachedtable",
        "querymodel", "relationaltablemodel", "tablemodel",
    }, "Do not fold byte-identical SQL sources into one identity"


@pytest.mark.parametrize("menu,source,digest", IDENTITIES)
def test_identity_when_retired_then_exact_bytes_and_no_archived_dispatcher(
    menu: str, source: str, digest: str
) -> None:
    """Read preserved bytes only; do not import a demo or start workers."""
    payload = (ARCHIVE / source).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == digest, source
    assert not (ROOT / menu).exists(), "Never restore the archived menu dispatcher"
    ast.parse(payload, filename=source, feature_version=(3, 11))


@pytest.mark.parametrize("menu,source,digest", SQL)
def test_sql_when_inspected_then_explicit_qtsql_capability_refusal(
    menu: str, source: str, digest: str
) -> None:
    """Confirm the actual static refusal and its precise catalogue explanation."""
    tree = ast.parse((ARCHIVE / source).read_text(encoding="utf-8"))
    build = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    assert build.name == "build", source
    refusal = build.body[-1]
    assert isinstance(refusal, ast.Raise) and isinstance(refusal.exc, ast.Call)
    assert isinstance(refusal.exc.func, ast.Name)
    assert refusal.exc.func.id == "NotImplementedError", source
    messages = [
        node.value for node in ast.walk(build)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    record = next(row for row in CATALOGUE if source.endswith(row["target_path"]))
    assert record["implementation"] == "blocked", source
    assert record["blocked_reason"] in messages, source
    assert "PythonQt does not export QtSql" in record["blocked_reason"]
    required = {
        "cachedtable": "QSqlTableModel", "tablemodel": "QSqlTableModel",
        "querymodel": "QSqlQueryModel",
        "relationaltablemodel": "QSqlRelationalTableModel",
    }
    family = Path(source).stem.split("-")[0]
    assert required[family] in record["blocked_reason"], source


@pytest.mark.parametrize("menu,source,digest", THREADS)
def test_threads_when_inspected_then_synthetic_workers_without_font_inputs(
    menu: str, source: str, digest: str
) -> None:
    """Bind retirement reasons to scalar demo workloads, without running them."""
    tree = ast.parse((ARCHIVE / source).read_text(encoding="utf-8"))
    imports = {
        node.module if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "threading" in imports or any(
        isinstance(node, ast.Name) and node.id == "WorkerDelivery"
        for node in ast.walk(tree)
    ), "This retirement covers worker demos"
    assert not imports.intersection({"fontlab", "FL", "fontgate", "fly"}), source
    constants: list[Any] = [
        node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)
    ]
    if "mandelbrot-" in source:
        functions = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
        assert functions.intersection({"scanline", "render_rows"}), source
    else:
        assert "ACGT" in constants, "Transfer data is synthetic DNA text"
        assert 100000 in constants and 8192 in constants, source


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_provenance_when_read_then_exact_upstream_identity_and_bsd_notice(
    family: str,
) -> None:
    """Retain author and licence facts; no upstream code is redistributed."""
    record = next(
        row for row in CATALOGUE
        if Path(row["target_path"]).stem.split("-")[0] == family
    )
    assert record["source"]["repository"] == "pyqt/examples"
    assert record["source"]["commit"] == "83eed0514582c8deb60d9e9e6bff31ceffe4eaeb"
    assert record["license"]["selected"] == "BSD-3-Clause AND GPL-3.0-only"
    notice = "\n".join(record["license"]["original_notices"])
    assert "$QT_BEGIN_LICENSE:BSD$" in notice
    assert "Riverbank Computing Limited" in notice and "Nokia Corporation" in notice
    assert record["resources"] == [], "No companion resources need a disposition"
