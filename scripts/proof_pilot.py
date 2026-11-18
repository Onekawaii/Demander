#!/usr/bin/env python3
"""Bounded Demander commercial-pilot demonstration using GENERATED, trusted fixtures.

This is a test of Demander's observable P1/P2 claims, not a customer pilot,
secure sandbox, real-device run, or test of arbitrary untrusted code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from demander.cli import verify
from demander.core import seal


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(directory: Path, *, broken: bool) -> Path:
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "tests").mkdir()
    (directory / "app.py").write_text(
        "def add(a, b):\n    return a - b\n" if broken
        else "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    (directory / "tests" / "test_app.py").write_text(
        "import unittest\nfrom app import add\n\n"
        "class TestAdd(unittest.TestCase):\n"
        "    def test_two_plus_two(self):\n"
        "        self.assertEqual(add(2, 2), 4)\n",
        encoding="utf-8",
    )
    contract = {
        "schema_version": "dpc-1/1",
        "contract_id": "proof-pilot-generated-fixture-v1",
        "criteria": [
            {
                "id": "source-present", "probe": "file_exists",
                "artifact": "app.py", "path": ".", "criticality": "required",
                "depth": "P1", "observation": "Source is present and hashed",
            },
            {
                "id": "trusted-test-exec", "probe": "python_unittest",
                "path": ".", "criticality": "required", "depth": "P2",
                "observation": "One known test runs against generated code",
            },
        ],
    }
    path = directory / "contract.json"
    path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run(out: Path) -> dict:
    out = out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"Refusing to overwrite nonempty output directory: {out}")
    out.mkdir(parents=True, exist_ok=True)

    good = out / "good_fixture"
    bad = out / "bad_fixture"
    good_contract = _fixture(good, broken=False)
    bad_contract = _fixture(bad, broken=True)
    cases = [
        ("read_only", good, good_contract, False, "PARTIAL"),
        ("known_good", good, good_contract, True, "QUALIFIED"),
        ("known_broken", bad, bad_contract, True, "REJECTED"),
    ]
    observations = []
    for name, root, contract, execute, expected in cases:
        path = out / "receipts" / name
        result = verify(root, str(contract), execute, str(path), 30)
        receipt = path / "receipt.json"
        criteria = json.loads(receipt.read_text(encoding="utf-8"))["criteria"]
        actual = result["verdict"]
        observations.append({
            "case": name, "expected": expected, "actual": actual,
            "matches_expectation": actual == expected,
            "execution_authorized": execute,
            "statuses": {item["id"]: item["status"] for item in criteria},
            "receipt_sha256": _sha256(receipt),
            "report_sha256": _sha256(path / "report.md"),
        })

    # A previous positive receipt must not be reused after the target changes.
    positive_receipt = json.loads(
        (out / "receipts" / "known_good" / "receipt.json").read_text(encoding="utf-8")
    )
    old_seal = positive_receipt["source_after"]["sha256"]
    with (good / "app.py").open("a", encoding="utf-8") as stream:
        stream.write("# deliberate post-verification mutation\n")
    mutated_seal = seal(good)["sha256"]
    mutation_detected = old_seal != mutated_seal

    passed = all(case["matches_expectation"] for case in observations) and mutation_detected
    summary = {
        "schema_version": "demander-proof-pilot/1",
        "kind": "GENERATED_FIXTURE_DEMONSTRATION",
        "passed": passed,
        "cases": observations,
        "mutation_invalidates_previous_receipt": mutation_detected,
        "positive_receipt_source_sha256": old_seal,
        "mutated_source_sha256": mutated_seal,
        "limits": [
            "No external customer repository was tested",
            "Authorized tests run as the current OS user; no sandbox or network isolation",
            "P3/P4, Android, GUI, security assurance, and production readiness are UNVERIFIED",
            "SHA-256 detects changed bytes but does not authenticate receipt authorship",
        ],
    }
    report = out / "pilot_summary.json"
    report.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (out / "pilot_summary.sha256").write_text(
        f"{_sha256(report)}  pilot_summary.json\n", encoding="ascii"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prove bounded P1/P2 behavior on generated fixtures only")
    parser.add_argument("--out", required=True, type=Path, help="Fresh empty output directory")
    args = parser.parse_args(argv)
    try:
        result = run(args.out)
    except (ValueError, OSError) as exc:
        print(f"PILOT ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
