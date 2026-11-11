# this_file: tests/test_menu_consolidations.py
"""Keep implementation routes separate from immutable history and parity claims."""

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

from scriptmix_destinations import check_destination

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "examples_consolidation_layout", ROOT.parent / "fontlab-python-scriptmix/menu_layout.py"
)
LAYOUT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAYOUT)


class ConsolidationTests(unittest.TestCase):
    def test_all_sources_when_proposed_then_exactly_100_routes_to_25_labs(self):
        rows = LAYOUT.consolidation_rows(ROOT)
        current = {p.relative_to(ROOT).as_posix() for p in ROOT.glob("Scripts/*/*.py")}
        self.assertEqual(len(rows), 100)
        self.assertEqual({row["source"]["path"] for row in rows} | {
            row["destination"]["path"] for row in rows
            if row["acceptance"]["state"] == "implemented"
        }, current)
        self.assertEqual(len({row["destination"]["path"] for row in rows}), 25)
        for row in rows:
            source = ROOT / row["source"]["path"]
            self.assertEqual(row["source"]["sha256"], hashlib.sha256(LAYOUT.source_bytes(ROOT, row["source"])).hexdigest())
            self.assertIn(row["acceptance"]["state"], {"proposed", "implemented"})
            self.assertIs(row["acceptance"]["behavior_parity"], False)
            self.assertIs(row["acceptance"]["native"], False)
            self.assertEqual(row["disposition"], "absorbed")
            if row["acceptance"]["state"] == "proposed":
                self.assertIsNone(row["destination"]["sha256"])
            else:
                target = ROOT / row["destination"]["path"]
                self.assertEqual(row["destination"]["sha256"],
                                 hashlib.sha256(target.read_bytes()).hexdigest())
            self.assertTrue(row["destination"]["tab"].strip())
            self.assertEqual(row["destination"]["action"], source.stem)
            self.assertTrue(row["destination"]["path"].startswith("Scripts/Labs/"))
            for route in row["test_routes"]:
                self.assertTrue((ROOT / route.split("::", 1)[0]).is_file(), route)

    def test_sources_when_resolved_then_exact_committed_bytes(self):
        for row in LAYOUT.consolidation_rows(ROOT):
            self.assertEqual(
                LAYOUT.source_bytes(ROOT, row["source"]),
                LAYOUT.source_bytes(ROOT, row["source"], committed=True),
            )

    def test_adaptations_when_mapped_then_original_identities_and_hashes_survive(self):
        rows = {row["source"]["path"]: row for row in LAYOUT.consolidation_rows(ROOT)}
        adaptations = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
        matched = 0
        for adaptation in adaptations:
            menu = adaptation["menu"]
            if menu in rows:
                self.assertEqual(adaptation["destination_sha256"], rows[menu]["source"]["sha256"])
                self.assertRegex(adaptation["source_sha256"], r"^[0-9a-f]{64}$")
                matched += 1
        self.assertGreater(matched, 0)
        self.assertEqual(len(json.loads((ROOT / "rescue-index.json").read_text())["menus"]), 494)

    def test_scriptmix_destinations_when_reconciled_then_all_24_pins_match(self):
        records = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
        cross_repo = [row for row in records if row["menu"].startswith("fontlab-python-scriptmix/")]
        self.assertEqual(len(cross_repo), 24)
        for row in cross_repo:
            self.assertEqual(check_destination(row["menu"], row["destination_sha256"]), row["destination_sha256"])

    def test_packaged_menus_when_proposed_then_all_16_remain_accounted(self):
        rows = {row["source"]["path"]: row for row in LAYOUT.consolidation_rows(ROOT)}
        packaged = list((ROOT / "lessons/Scripts").glob("*/*.py"))
        self.assertEqual(len(packaged), 16)
        for path in packaged:
            row = rows[path.relative_to(ROOT / "lessons").as_posix()]
            self.assertIn(row["acceptance"]["state"], {"proposed", "implemented"})
            self.assertFalse(row["acceptance"]["native"])
            self.assertEqual((ROOT / row["source"]["path"]).read_bytes(),
                             LAYOUT.source_bytes(ROOT, row["source"], committed=True))


if __name__ == "__main__":
    unittest.main()
