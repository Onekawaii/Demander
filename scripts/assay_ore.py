#!/usr/bin/env python3
"""Read an external Gold Rush ORE_REGISTER.json without touching repositories.

The full source register may include private repo names. Never auto-publish it.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

PRIMARY = "Onekawaii/Demander"
EXTRACTION_QUEUE = {
    "Onekawaii/The-Aviary": "Evidence ledger: prove replay, migration and tamper behavior",
    "Onekawaii/apevm": "Trusted runner: prove lifecycle; NOT a security sandbox",
    "Onekawaii/ministry-swarm-os": "One intake surface only: certify G0-G3",
    "Onekawaii/Grandma": "Routing adapter: prove outage and no false execution",
    "Onekawaii/Deterministic-Jungle-Canopy": "Canonical hashing: prove cross-environment agreement",
    "Onekawaii/ApeGPT-": "IDE adapter: reproduce rollback and host-execution warnings",
    "Onekawaii/ApeRuntime": "Wait for emulator and physical Android acceptance",
}
REQUIRED_ASSET_GATES = (
    "owner_approval", "license_cleared", "provenance_verified",
    "clean_reproduction", "independent_negative_test", "interface_contract",
    "security_boundary_review",
)


def assay(register: Path) -> dict:
    raw = register.read_bytes()
    source = json.loads(raw)
    rows = source.get("repositories")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Invalid register: nonempty repositories array required")
    names = [row.get("repository") for row in rows if isinstance(row, dict)]
    if len(names) != len(rows) or len(names) != len(set(names)) or names.count(PRIMARY) != 1:
        raise ValueError("Register must contain unique repository names, including Demander once")
    results = []
    for row in sorted(rows, key=lambda item: item["repository"].casefold()):
        name = row["repository"]
        candidate = name in EXTRACTION_QUEUE
        gates = row.get("asset_gates", {})
        if not isinstance(gates, dict):
            gates = {}
        unresolved = [key for key in REQUIRED_ASSET_GATES if gates.get(key) is not True]
        results.append({
            "repository": name,
            "portfolio_role": "PRIMARY_EXPERIMENT" if name == PRIMARY else "PRESERVE_UNMODIFIED",
            "audit_tier": row.get("audit_tier"),
            "candidate_component": EXTRACTION_QUEUE.get(name),
            "candidate_state": "REVIEW_ELIGIBLE" if candidate and not unresolved else
                ("EVIDENCE_REQUIRED" if candidate else "NO_EXTRACTION_PLANNED"),
            "unmet_admission_gates": unresolved if candidate else [],
            "transfer_admitted": False,  # Requires a separate manual decision.
            "source_technical_status": row.get("technical_status", "UNKNOWN"),
            "source_licensing_review": row.get("licensing_review", "UNKNOWN"),
        })
    return {
        "schema_version": "gold-rush-assay/1",
        "register_sha256": hashlib.sha256(raw).hexdigest(),
        "register_snapshot_date": source.get("snapshot_date"),
        "repo_count": len(results),
        "primary_count": 1,
        "preserved_unchanged_count": len(results) - 1,
        "candidate_count": sum(1 for row in results if row["candidate_component"]),
        "assets_admitted": 0,
        "no_repo_mutations": True,
        "policy": "Other repos preserved. No source imports, merges, deletions or licenses presumed.",
        "repos": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evidence-gated non-mutating portfolio assay")
    parser.add_argument("register", type=Path, help="Local ORE_REGISTER.json; never auto-published")
    parser.add_argument("--out", type=Path, help="Optional local JSON report")
    args = parser.parse_args(argv)
    try:
        result = assay(args.register)
        content = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.out:
            path = args.out.resolve()
            if path.exists():
                raise ValueError(f"Refusing to overwrite existing report: {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        else:
            print(content, end="")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ASSAY ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
