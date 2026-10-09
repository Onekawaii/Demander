# DEMANDER UNIVERSAL — v0.3.0-alpha

**Your AI built it. Demander makes it prove it.**

First executable slice of the independently authored DPC-1 Proof Circuit. This is **alpha**, not a full verification sandbox or universal runtime debugger. HTE is not incorporated or required.

## Run without installing dependencies

```bash
python -m demander inspect .
python -m demander verify . --contract examples/demander.contract.json
python -m demander verify . --contract examples/demander.contract.json --execute
python -m demander report .demander/latest/receipt.json
python -m unittest discover -s tests -v
```

On Windows use the same commands from a PowerShell prompt after `cd` into the extracted project directory. The tool requires Python 3.11+ and has **no external runtime dependencies**.

`verify` without `--execute` never executes a project test and leaves executable criteria UNVERIFIED. `--execute` **runs code supplied by the target project as your user account**, so use it only on projects you trust or within a separate security sandbox. No sandbox or network restriction is enforced in this alpha. Contract-provided arbitrary shell commands are forbidden; only predefined verification probes are supported.

## Current capabilities

- Independent CLAIM/MAP/PROBE/RULE/RECORD checks with exact content fingerprints (SEAL); mutation detection (CROSS-CHECK)
- Stable deterministic verdict precedence: REJECTED > BLOCKED > PARTIAL > QUALIFIED
- TypeScript: local/global `tsc --noEmit` and explicit npm tests, no npx network bootstrap
- Rust: `cargo check --offline` / `cargo test --offline` when installed
- Python: source compilation and unittest execution
- File existence with SHA-256 (P1 only; not runtime proof)
- Read-only `inspect` auto-discovers TypeScript/Rust/Python/Godot project markers
- JSON receipt, Markdown summary and hash for every verification run
- Tests cover false claims, missing toolchains, source mutation, policy violations, fake device verification and error precedence

## Not yet supported

Actual runtime/gameplay instrumentation, Android device test, Godot run adapter, OS sandbox, network containment, GUI, MCP service, signed attestations, CI integration, comprehensive dependency hashing, safe execution of untrusted repositories, full DPC-1 automation. P3/P4 remain UNVERIFIED. The source hash ignores generated cache/build directories; this must be strengthened before release qualification.

Exit codes: `0` QUALIFIED (only the declared contract), `2` PARTIAL, `3` BLOCKED, `4` REJECTED, `5` tool/contract error.

Do **not** treat an automated contract PASS as a guarantee of correct end-user behavior. Tests are claims bounded by their observable verification criteria.
