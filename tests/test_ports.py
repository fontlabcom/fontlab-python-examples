# this_file: tests/test_ports.py
"""Portable provenance checks; these do not prove native Qt behavior."""

import ast
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDS = {"ce3e17a7a2a03a02", "f5ddfd0eaacbf845", "79cc15680bc2cebb", "402068f40005cd66"}


def test_manifest_when_first_batch_then_exact_catalog_sources_and_licensed_paths():
    catalog = json.loads((ROOT / "catalog/sources.json").read_text())
    files = {item["id"]: item for item in catalog["files"]}
    manifest = json.loads((ROOT / "catalog/ports.json").read_text())
    assert {item["source_id"] for item in manifest["ports"]} >= IDS
    for port in manifest["ports"]:
        original = files[port["source_id"]]
        for key in (
            "repository",
            "commit",
            "path",
            "sha256",
            "git_blob_sha",
            "bytes",
            "upstream_url",
        ):
            assert port["source"][key] == original[key], key
        expected_target = original["target_path"]
        if original["path"].startswith("src/pyqt-official/"):
            category = original["path"].split("/")[2]
            expected_target = (
                f"ports/{category}/pyqt-official/" + Path(expected_target).name
            )
        if original["repository"] == "eyllanesc/QtExamples":
            expected_target = expected_target.replace(
                "/eyllanesc-qtexamples/", "/eyllanesc/"
            )
        assert port["target_path"] == expected_target
        assert port["implementation"] in {
            "implemented",
            "blocked",
            "clean_room_pending",
        }
        if port["implementation"] == "clean_room_pending":
            assert port["archive"] and port["spec"] and "license" not in port
            assert port["native_acceptance"] == "unexecuted"
            continue
        if port["implementation"] == "blocked":
            assert port["blocked_reason"]
            assert port["native_acceptance"] == "unexecuted"
            continue
        assert port["native_acceptance"] in {"pending", "passed", "unexecuted"}
        if port["native_acceptance"] == "passed" and port["source_id"] in IDS:
            evidence = port["native_evidence"]
            report_path = Path(evidence["report"])
            assert not report_path.is_absolute() and ".." not in report_path.parts
            receipt = json.loads((ROOT / report_path).read_text(encoding="utf-8"))
            assert receipt["this_file"] == report_path.as_posix()
            assert receipt["implementation_commit"] == evidence["implementation_commit"]
            launched = receipt["native"]["launch"][port["name"]]
            assert launched["source_id"] == port["source_id"]
            assert launched["launched"] is True and launched["visible"] is True
            assert launched["closed"] is False
            closed = receipt["native"]["close"][port["name"]]
            assert closed["source_id"] == port["source_id"]
            assert closed["closed"] is True and closed["launched"] is False
            destruction = receipt["native"]["destruction"]
            assert destruction["expected"], "Passed acceptance must track owned objects"
            assert set(destruction["expected"]) == set(destruction["destroyed"])
            assert destruction["registry_empty"] is True
            assert destruction["host_application_alive"] is True
        assert port["license"]["selected"] in {
            "Apache-2.0",
            "MIT",
            "BSD-3-Clause",
            "BSD-3-Clause AND GPL-3.0-only",
            "GPL-3.0-only",
            "HPND AND GPL-3.0-only",
        }
        if port.get("clean_room_receipt"):
            assert port["license"]["basis"] == (
                f"clean-room implementation from {port['spec']}; no upstream code"
            )
            assert (ROOT / port["clean_room_receipt"]).is_file()
        else:
            assert original["path"] in port["license"]["reviewed_files"]
            assert (ROOT / port["license"]["notice_path"]).is_file()
        assert not Path(port["target_path"]).is_absolute()
        tree = ast.parse((ROOT / port["target_path"]).read_text())
        imports = [
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ]
        assert not any(name.startswith(("PyQt", "PySide")) for name in imports)
        assert (
            "this_file: " + port["target_path"]
            in (ROOT / port["target_path"]).read_text()
        )


def test_designer_when_copied_then_original_bytes_and_connection_wiring():
    manifest = json.loads((ROOT / "catalog/ports.json").read_text())
    port = next(
        item for item in manifest["ports"] if item["source_id"] == "402068f40005cd66"
    )
    resource = port["resources"][0]
    catalog = json.loads((ROOT / "catalog/sources.json").read_text())
    original = next(
        item for item in catalog["files"] if item["id"] == resource["source_id"]
    )
    data = (ROOT / resource["target_path"]).read_bytes()
    assert resource["target_path"] == original["target_path"]
    assert len(data) == original["bytes"] == resource["source"]["bytes"]
    assert (
        hashlib.sha256(data).hexdigest()
        == original["sha256"]
        == resource["source"]["sha256"]
    )
    assert (
        hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        == original["git_blob_sha"]
    )
    ui = ET.fromstring(data)
    assert {
        (node.findtext("signal"), node.findtext("slot"))
        for node in ui.findall("connections/connection")
    } == {("accepted()", "accept()"), ("rejected()", "reject()")}
    assert resource["license"]["selected"] == "MIT"
    assert "UI source" in resource["license"]["basis"]


def test_recovered_originals_when_local_receipt_available_then_manifest_hashes():
    import pytest

    receipt = (
        ROOT.parent
        / "verification/issue-101-ecosystem/evidence/examples-source-recovery.json"
    )
    if not receipt.exists():
        pytest.skip("Private recovery receipt is not distributed")
    recovery = json.loads(receipt.read_text())["repositories"]
    manifest = json.loads((ROOT / "catalog/ports.json").read_text())
    for port in manifest["ports"]:
        for record in [port, *port["resources"]]:
            source = record["source"]
            repo = next(
                item for item in recovery if item["repository"] == source["repository"]
            )
            mapping = repo["files"][source["path"]]
            data = (
                ROOT.parent / repo["source_directory"] / mapping["storage_path"]
            ).read_bytes()
            assert (
                source["sha256"]
                == mapping["sha256"]
                == hashlib.sha256(data).hexdigest()
            )
            assert source["bytes"] == mapping["bytes"] == len(data)
            assert source["git_blob_sha"] == mapping["git_blob_sha"]
