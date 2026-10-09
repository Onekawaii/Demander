# Demander v0.3 — Verified scope and gaps

## Verified by execution
- Python 3.13 / Linux container: 18/18 adversarial unittests; self-contract P1/P2 qualification.
- Python 3.11.9 / Windows Desktop Commander: 18/18 unittests; same transferred runtime ZIP (SHA256 `8a38cca9e974a5b8f62960360de47d42e082b05ca9b0c796a64e708b6fb87bf4`) self-contract P1/P2 QUALIFIED; receipt SHA256 `b39e08b5636adf155d3feb87c8b8151a7c328228f37c783028112d13b000d797`.
- TypeScript on Linux: strict compiler pass for clean example; compiler failure detected for deliberately invalid TypeScript.
- Rust: intentionally BLOCKED when `cargo` absent; no Rust compilation claim.
- P2 unauthorized check: PARTIAL, no code execution.

## Still incomplete
- No Rust compiler was installed or used in the connected Windows proof, and no Rust test was executed.
- No native Windows `.exe`, Android APK, browser UI, Godot gameplay harness, MCP server, CI check-run integration or automated repair system.
- No OS sandbox or network isolation: authorized tests run as the current account. **Do not use `--execute` on untrusted repositories.**
- No user-device P4 proof, crash visual evidence, dependency signature attestation, trusted build artifact provenance, or guarantee of correctness outside declared criteria.
- Source sealing excludes build caches (`target`, `dist`, `build`, `.demander`) by design; use a dedicated artifact hash for shipped outputs. This alpha cannot establish complete supply-chain integrity.
- Target-specific Python compilation scans the project and could exceed platform argument limits on very large repositories. Add bounded selection and batching.
- Exact HTE text was not reused. DPC-1 is independent by specification and implementation; a legal similarity/license review was not performed.

## Next engineering sprint
1. Implement safe plugin adapter interface and schema validation with capability declarations.
2. Add actual TypeScript test runner detection (Vitest/Jest/node:test) and bounded subprocess execution.
3. Add real Rust toolchain CI for independent offline Rust test proof.
4. Add sandbox/containers or explicit trust levels, and network isolation where supported.
5. Add immutable receipts linked to commits/build-artifact digests and verify their signature/attestation.
6. Add Godot headless and mobile/device proof adapters without conflating test existence with runtime evidence.
