# this_file: tests/test_catalog.py
"""Acceptance checks for the complete portable catalog committed in this repo."""

import json
from collections import Counter
from pathlib import Path

import pytest

CATALOG = Path(__file__).resolve().parents[1] / "catalog" / "sources.json"


@pytest.fixture
def catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_complete_pinned_sources_and_file_denominators(catalog):
    expected = {
        "pyqt/examples": ("83eed0514582c8deb60d9e9e6bff31ceffe4eaeb", 805, 308),
        "eyllanesc/QtExamples": ("a01fd7d10d45801b10876f94c07aaefb11bc2e12", 764, 157),
    }
    assert len(catalog["files"]) == 1569, (
        "Both complete source trees must remain in scope"
    )
    for repository, (commit, count, python_count) in expected.items():
        files = [f for f in catalog["files"] if f["repository"] == repository]
        assert len(files) == count
        assert sum("python" in f for f in files) == python_count
        assert {f["commit"] for f in files} == {commit}
    assert len({f["id"] for f in catalog["files"]}) == 1569
    assert len({f["target_path"].casefold() for f in catalog["files"]}) == 1569


def test_resources_helpers_and_license_gaps_are_visible(catalog):
    counts = Counter(f["kind"] for f in catalog["files"])
    assert all(
        counts[k] > 0
        for k in [
            "python",
            "qml",
            "ui",
            "qrc",
            "license",
            "dependency",
            "asset-or-configuration",
        ]
    )
    assert catalog["counts"]["auxiliary_python_files"] > 0
    assert catalog["counts"]["static_ambiguous_candidates"] == 17
    assert catalog["counts"]["ambiguous_candidates"] == 0
    assert (
        sum(f["license"]["declared_terms"] == ["unknown"] for f in catalog["files"]) > 0
    )
    assert all(f["license"]["review_state"] == "pending" for f in catalog["files"])
    assert all(
        len(f["sha256"]) == 64 and len(f["git_blob_sha"]) == 40
        for f in catalog["files"]
    )


def test_required_capabilities_and_case_collision_are_mapped(catalog):
    needs = {n for e in catalog["examples"] for n in e["capability_needs"]}
    assert {
        "qml",
        "webengine",
        "multimedia",
        "gstreamer",
        "matplotlib",
        "database",
        "network",
        "platform",
        "video-overlay",
    } <= needs
    files = {
        f["path"]: f
        for f in catalog["files"]
        if f["repository"] == "eyllanesc/QtExamples"
    }
    first, second = (
        files["others/matplotlib/Subplot.py"],
        files["others/matplotlib/subplot.py"],
    )
    assert first["sha256"] != second["sha256"]
    assert first["target_path"].casefold() != second["target_path"].casefold()
    assert first["example_ids"] and second["example_ids"]


def test_all_native_and_port_states_remain_pending(catalog):
    for record in catalog["files"] + catalog["examples"]:
        assert record["port_state"] == "pending", "Inventory must not manufacture ports"
        assert record["runtime_state"] == "unexecuted", (
            "Static analysis does not prove host support"
        )
    assert (
        catalog["counts"]["examples_ported"]
        == catalog["counts"]["examples_native_executed"]
        == 0
    )
    text = CATALOG.read_text(encoding="utf-8")
    assert (
        "/Users/" not in text and "/Volumes/" not in text and "storage_path" not in text
    )
