# SPDX-License-Identifier: Apache-2.0
# this_file: tests/test_replacement_assets.py
"""Replacement assets: only exact generator output is recorded or accepted."""

import shutil
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import replacement_assets as assets

BACKGROUND = f"{assets.STYLE}/files/nature_1.png"


def tree(tmp_path: Path) -> Path:
    """A copy of the catalogue and every generated asset at its shipped path."""
    for name in ("catalog/ports.json", "catalog/licenses.json"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    for name, data in assets.assets().items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_bytes(data)
    return tmp_path


def test_assets_when_generated_twice_then_identical_and_background_is_png():
    first = assets.assets()
    assert first == assets.assets()
    assert not any(name.endswith(".jpg") for name in first)
    png = first[BACKGROUND]
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    assert struct.unpack(">II", png[16:24]) == (320, 240)
    assert "nature_1.png" in first[f"{assets.STYLE}/files/transparent.qss"].decode()


@pytest.mark.parametrize(
    "payload", [b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"not an image", b""]
)
def test_stale_when_file_is_not_generator_output_then_reported(tmp_path, payload):
    root = tree(tmp_path)
    assert assets.stale(root) == []
    (root / BACKGROUND).write_bytes(payload)
    assert assets.stale(root) == [BACKGROUND]


def test_stale_when_upstream_file_still_shipped_then_reported(tmp_path):
    root = tree(tmp_path)
    leftover = root / f"{assets.STYLE}/files/nature_1.jpg"
    leftover.write_bytes(b"\xff\xd8\xff\xe0 upstream")
    assert assets.stale(root) == [f"{assets.STYLE}/files/nature_1.jpg"]


def test_record_when_a_file_is_foreign_then_refused_and_catalogue_unchanged(tmp_path):
    root = tree(tmp_path)
    icon = f"{assets.NUMBERED[0]}/icon-adeb6eaa0049d0d3.svg"
    (root / icon).write_bytes(b"<svg>third-party original</svg>")
    before = {
        n: (root / n).read_bytes()
        for n in ("catalog/ports.json", "catalog/licenses.json")
    }
    with pytest.raises(ValueError, match=icon):
        assets.record(root)
    assert before == {n: (root / n).read_bytes() for n in before}


def test_record_when_generated_then_background_points_at_shipped_png(tmp_path):
    import json

    root = tree(tmp_path)
    assets.record(root)
    ports = json.loads((root / "catalog/ports.json").read_text())["ports"]
    resource = next(
        r
        for p in ports
        for r in p["resources"]
        if r["target_path"].endswith("nature_1.jpg")
    )
    assert resource["replacement"]["target_path"] == BACKGROUND
    ledger = json.loads((root / "catalog/licenses.json").read_text())["files"]
    assert ledger[resource["target_path"]]["replacement"] == resource["replacement"]


def test_stored_when_decompressed_then_round_trips_including_empty_and_large():
    import zlib

    for data in (b"", b"x" * 10, bytes(range(256)) * 600):
        assert zlib.decompress(assets.stored(data)) == data
