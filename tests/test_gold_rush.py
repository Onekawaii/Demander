import json
from pathlib import Path
import tempfile
import unittest

from scripts.assay_ore import PRIMARY, REQUIRED_ASSET_GATES, assay
from scripts.proof_pilot import run


class GoldRushTests(unittest.TestCase):
    def test_preserves_other_repositories_and_admits_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ore.json"
            rows = [
                {"repository": PRIMARY, "audit_tier": "A"},
                {"repository": "Onekawaii/apevm", "audit_tier": "B"},
                {"repository": "Onekawaii/NoTransfer", "audit_tier": "C"},
            ]
            path.write_text(json.dumps({"repositories": rows}), encoding="utf-8")
            before = path.read_bytes()
            result = assay(path)
            self.assertEqual(result["repo_count"], 3)
            self.assertEqual(result["preserved_unchanged_count"], 2)
            self.assertEqual(result["assets_admitted"], 0)
            self.assertEqual(path.read_bytes(), before)
            self.assertTrue(all(not row["transfer_admitted"] for row in result["repos"]))
            runner = next(row for row in result["repos"] if row["repository"] == "Onekawaii/apevm")
            self.assertEqual(runner["candidate_state"], "EVIDENCE_REQUIRED")

    def test_explicit_gates_still_require_manual_transfer(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ore.json"
            rows = [
                {"repository": PRIMARY},
                {"repository": "Onekawaii/The-Aviary", "asset_gates": {
                    gate: True for gate in REQUIRED_ASSET_GATES
                }},
            ]
            path.write_text(json.dumps({"repositories": rows}), encoding="utf-8")
            result = assay(path)
            asset = next(row for row in result["repos"] if row["repository"] != PRIMARY)
            self.assertEqual(asset["candidate_state"], "REVIEW_ELIGIBLE")
            self.assertFalse(asset["transfer_admitted"])

    def test_duplicate_repository_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ore.json"
            path.write_text(json.dumps({"repositories": [
                {"repository": PRIMARY}, {"repository": PRIMARY}
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                assay(path)

    def test_generated_fixture_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "pilot"
            result = run(out)
            self.assertTrue(result["passed"])
            self.assertEqual([case["actual"] for case in result["cases"]],
                             ["PARTIAL", "QUALIFIED", "REJECTED"])
            self.assertTrue(result["mutation_invalidates_previous_receipt"])
            self.assertTrue((out / "pilot_summary.sha256").is_file())

    def test_artifact_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "pilot"
            out.mkdir()
            (out / "keep.txt").write_text("do not overwrite", encoding="utf-8")
            with self.assertRaises(ValueError):
                run(out)
            self.assertEqual((out / "keep.txt").read_text(), "do not overwrite")


if __name__ == "__main__":
    unittest.main()
