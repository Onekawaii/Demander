# DEMANDER PROOF CIRCUIT — DPC-1

**Revision:** 1.0-design  
**Project:** DEMANDER UNIVERSAL  
**Status:** Proposed original workflow specification; no executable implementation is implied.  
**Date:** 2026-10-08  
**Motto:** *A claim earns a verdict only when its evidence survives inspection.*

## 1. Purpose and separation

The Demander Proof Circuit (DPC-1) is a self-contained, language-neutral method for deciding **what has actually been established about a build**. It is intended for software, games, mobile applications, firmware and other testable artifacts.

This document is written as a **new Demander-native workflow**, not a renamed or reproduced edition of HTE. HTE is a separately developed method belonging to its author, the user's brother. No license, authorship or ownership over HTE is claimed here. DPC-1 has no runtime or specification dependency on HTE. General practices such as tests, reproducibility, version control and regression analysis are common software-engineering techniques; using them does not make DPC-1 an edition of HTE.

DPC-1 is also separate from the original Demander Gauntlet. Existing Gauntlet vocabulary can be mapped as an optional interoperability layer after the original source is provided and permission/licensing are clarified; its gate numbering is not required to run DPC-1.

DPC-1 cannot guarantee defect-free software. It can make a **bounded, inspectable qualification decision** for explicitly defined requirements, target environments, and a specific source/artifact state.

## 2. The governing model: the Proof Circuit

The circuit has **seven operations**. A failed obligation returns a *repair ticket* to the builder, not a fictitious success or a mandatory endless cycle.

```text
                         [1] CLAIM
                              |
                         [2] SEAL
                              |
                         [3] MAP
                              |
                         [4] PROBE
                              |
                         [5] CROSS-CHECK
                              |
                         [6] RULE
                           /      \
                      Accepted   Deficient
                          |          |
                    [7] RECORD   Repair ticket
                          |          |
                        Stop     Builder changes
                                     |
                           Start NEW sealed run
```

These operations correspond to:

### 1 — CLAIM: define the assertion

Record precisely what is being asserted, who asserted it, intended users, target platforms, and the observable criterion for success.

A vague statement such as “game works” must be resolved into testable propositions: “Android player can move without clipping,” “save/reload retains the placed object,” and “the signed APK installs on target device.” Separate optional goals from release-blocking obligations. Scope cannot be silently reduced after an observed failure.

**Output:** `ClaimSet` with stable requirement IDs and declared proof requirements.

### 2 — SEAL: identify exactly what is being judged

Before testing, capture the project source identity: repository location, branch and commit where present, tracked and untracked changes, relevant dependency/toolchain versions, build configuration, expected artifacts, and supported target environment. Calculate a reproducible content fingerprint or explain what could not be sealed.

After testing, tie every result to that source identity. A change in relevant files opens a **new run**; an old passing log does not silently qualify new binaries. Record artifacts by cryptographic digest.

**Output:** `TargetSeal` and `RunID`.

### 3 — MAP: connect assertions to independent observations

For each criterion define:
- an observable pass condition;
- at least one executable check or an explicitly recorded human/device test;
- what evidence is captured and by whom;
- required environment and permissions;
- likely blind spots and potential contradicting outcomes;
- dependencies on other criteria and necessary regression checks.

Create a coverage matrix. A proof gap is a visible result, not an invitation to invent a substitute test. Discovering a source file does not verify its behavior. A compiler result cannot discharge an APK usability claim.

**Output:** `ProofMap` containing criterion-to-evidence edges and unfulfilled obligations.

### 4 — PROBE: collect evidence with controlled checks

Run only specifically authorized steps. Prefer commands expressed as exact argument arrays, fixed working directories, timeouts and capture policies. Discovery is read-only by default; compiling and tests may run arbitrary code and require consent and appropriate isolation. Network use is separate opt-in authorization.

Capture exit codes, actual command arguments, timestamps, tool versions, output logs and resource bounds. For interactive requirements, use an actual runtime test harness or real device evidence. If execution is unavailable, classify it as blocked or unverified, not passed.

**Output:** independent `EvidenceRecord`s, or a documented failed/blocked attempt.

### 5 — CROSS-CHECK: look for discrepancies

Challenge the verdict before issuing it. At minimum:

1. **Identity:** do test outputs belong to the sealed source and artifact?
2. **Negative path:** has a failure case been exercised for critical behavior where practical?
3. **Scope:** are required languages, packages, components, platforms and tests all represented?
4. **Regression:** did recent edits damage previously proven behavior?
5. **Provenance:** are apparent proofs merely the builder's unsupported narrative?
6. **Contradiction:** is there direct evidence conflicting with a passing result (crashes, corrupted saves, visual mismatch)?
7. **Mutation:** did verification itself modify the source beyond its authorized boundary?

The cross-check is not a claim that every possible vulnerability has been found; it is an explicit review of the important evidence gaps for this contract.

**Output:** `ChallengeFinding`s and revised criterion statuses.

### 6 — RULE: calculate a bounded verdict

The central judge, not an adapter, decides status. Criterion statuses:

- `PASS`: current independent evidence establishes the defined condition at the required depth.
- `FAIL`: evidence contradicts the defined condition.
- `UNVERIFIED`: adequate or current evidence is absent.
- `BLOCKED`: the required check could not proceed for a documented prerequisite, environment, authorization or target-device reason.
- `NOT_APPLICABLE`: explicitly exempted by the *predeclared* contract, with rationale.

Aggregate statuses are deterministic:

- `REJECTED` if any required criterion is `FAIL`.
- `BLOCKED` if none failed but a required criterion is `BLOCKED`.
- `PARTIAL` if none failed/blocked but at least one required criterion is `UNVERIFIED`.
- `QUALIFIED` only when every applicable required criterion is `PASS`.

`NOT_APPLICABLE` is never a hidden waiver. Advisory findings may coexist with `QUALIFIED` only when clearly declared non-blocking in the original scope. A critical failure always defeats a collection of unrelated green checks.

**Output:** reproducible `Verdict` with reasons, outstanding criteria and permitted next action.

### 7 — RECORD: publish the receipt or repair ticket

Write the evidence ledger, human-readable explanation, precise verdict, all known limitations and any build-artifact hashes. A `QUALIFIED` run is a **stop condition**, not permission for endless additional checks. A failed/blocked run produces one or more prioritized repair tickets containing reproduction steps, affected requirement IDs, evidence references and proposed rechecks.

A repair belongs to an **authorized builder**, not the independent judge. After changes, the next verification starts from a fresh seal. Each work session has configured limits on time, test repetitions, expenses and repair attempts. When exhausted, stop with the true status.

**Output:** `BuildReceipt` or `RepairTicket`.

## 3. The three-part proof rule

No individual claim is accepted from a single ungrounded narrative. Each required criterion has three independently inspectable parts:

| Part | Question | Example |
|---|---|---|
| **Target** | What exactly must happen? | Player cannot move through a wall |
| **Observation** | What did a check or person actually observe? | Engine test collides against wall geometry |
| **Provenance** | Which exact source/artifact/runtime produced that observation? | Commit + worktree digest + Godot version + run log |

A missing part leaves the criterion unverified. Test outcomes do not become valid just because the agent asserts them. Where evidence is imported from CI, track its origin and verifiability; do not describe the execution as local/independent if Demander did not perform or reliably attest to it.

## 4. Four independently reported completion dimensions

Never compress these into one “done” flag:

- **Construction:** required source and components exist, with their identities recorded.
- **Behavior:** required program behavior has been observed in execution at the specified test depth.
- **Delivery:** the intended artifact/package is produced, identifiable, reachable and appropriately verified.
- **Use:** required end-user journey works on the intended target, including real-device observation where specified.

An app may be constructed and compiled but still fail behavior or be undelivered. These dimensions are **orthogonal** to the aggregate test verdict and must be reported explicitly.

## 5. Proof depths (DPC terminology)

DPC-1 intentionally uses its own `P0`–`P4` depth labels rather than inheriting any HTE or legacy gate numbers.

- `P0 — INTAKE`: claim, project, required scope and limitations recorded.
- `P1 — STATIC`: structure, config, identity, source and artifact inspection performed.
- `P2 — EXECUTION`: authorized build/tests executed and their actual outcomes captured.
- `P3 — RUNTIME`: target process or game launched and specified behavior observed.
- `P4 — TARGET USE`: intended deployment/installation and critical user journey observed on required target.

Depth is criterion-specific. A library with no graphical UI may legitimately require `P2` for certain features; a mobile game typically needs `P4` for a complete physical-device usability claim. Higher depths do **not** imply that all lower-depth obligations passed unless those checks appear in the `ProofMap`.

## 6. Review independence

Demander must not be allowed to modify a passing criterion, the contract or required proof depth to excuse failure. Evidence providers (builders, adapters, imported CI, humans) are distinct from the judgment policy. The judge can request more evidence; a builder must not be able to edit the received verdict unobserved.

A model may help propose checks and explain failures, but **non-model code** must compute the final verdict from versioned policies and recorded criterion statuses. If deterministic evaluation cannot be completed, no success claim is issued.

## 7. Safety boundary

- **Inspect** without executing repository-controlled code.
- Require explicit authorization for build/test commands (they may execute arbitrary code), installations and network.
- Execute in a documented isolation boundary where available; an allowlist alone is not a sandbox.
- Use fixed project paths, no untrusted shell interpolation, bounded logs, timeout, cancellation and subprocess cleanup.
- Exclude or redact secrets in receipts and avoid network telemetry by default.
- Protect out-of-scope files and report any mutation.
- Treat generated fixture tests or test files authored by the builder as potentially incomplete; scrutinize test adequacy.
- Never auto-reset, delete branches, merge, push, publish or deploy as part of verification.
- Use separate evidence and report storage from target source whenever possible.

## 8. Polyglot execution contract

DPC's core is not language-specific. Adapters supply detection and test runners; they **cannot return a global QUALIFIED verdict**.

Examples:

| Adapter | Candidate observations | Separate proof still needed |
|---|---|---|
| TypeScript | `tsc --noEmit`, configured test runner, browser suite | Actual browser path if required |
| Rust | `cargo check`, `cargo test`, Clippy | Actual binary/device behavior if required |
| Python | tests, type/lint checks | Actual service or GUI behavior if required |
| Godot | headless import, test harness, export | Real controls/render/collision and phone usage |
| C/C++ | build and CTest/sanitizers | Platform runtime and input behavior |
| Android | Gradle build, signing/ABI inspection | Installation and device controls |
| Other | Community-provided adapter | Adapter coverage and toolchain capability declaration |

Only declare language support after its adapter is implemented, tested and has known limitations documented.

## 9. Reference contract example

```yaml
contract_version: "dpc-1"
project: "example-godot-game"
required_target: "Android device"
criteria:
  - id: INPUT-001
    claim: "Virtual stick moves player and preserves collision"
    required_depth: P4
    critical: true
    proof:
      - kind: engine_runtime
        expected: "player never penetrates test wall"
      - kind: physical_device
        expected: "touch stick responds on target phone"
  - id: SAVE-001
    claim: "Held object remains placed after restart"
    required_depth: P3
    critical: true
    proof:
      - kind: runtime_journey
        sequence: "pickup -> place -> save -> exit -> restart -> load"
  - id: EXPORT-001
    claim: "Signed APK can be installed"
    required_depth: P4
    critical: true
    proof:
      - kind: artifact_hash
      - kind: device_install
```

Example is conceptual; it is **not** an implemented CLI/parser or a finalized wire schema.

## 10. Non-negotiable acceptance scenarios for DPC-1 itself

A proper implementation must correctly handle all the following test fixtures:

1. **Green compile, broken runtime:** compilation passes; launch crashes. Verdict `REJECTED` if runtime required.
2. **Unseen phone:** signed APK exists; no device interaction evidence. `PARTIAL` or `BLOCKED` as supported by exact prerequisites.
3. **Mixed repo:** TypeScript checks pass; required Rust checks fail. Verdict `REJECTED`.
4. **Stale receipt:** source changes after earlier green run. Previous results do not qualify new state.
5. **Dirty worktree:** commit hash alone cannot stand for uncommitted implementation.
6. **Self-reported success:** builder's prose declares success with no actual logs. `UNVERIFIED`.
7. **Bad test:** a test intentionally checks file presence while claim requires runtime behavior. Required behavior remains `UNVERIFIED`.
8. **Unauthorized script:** manifest attempts to run a dangerous setup step; inspection never executes it.
9. **Out-of-scope mutation:** verify detects unrelated changed files and records incident; no silent qualification.
10. **Timeout / missing toolchain:** verification has no success result; emits `BLOCKED` with specifics.
11. **Conflicting evidence:** one passing test and an observed runtime crash for same requirement. Verdict `REJECTED`.
12. **Correct stopping:** after requirements pass and receipt is sealed, verifier exits without initiating a speculative new build.
13. **Repair loop:** after repair, identity is re-sealed and impacted criteria are rerun; old proof cannot silently carry forward.
14. **Malicious adapter:** plugin claims global `QUALIFIED`; central policy ignores adapter-level aggregate verdicts.

## 11. Interface and reporting requirements

Planned CLI commands:

```text
demander inspect <path>
demander plan <path> --contract <file>
demander verify <path> --contract <file>
demander report <run-id>
demander compare <run-a> <run-b>
```

Planned receipt fields include:

```json
{
  "protocol": "dpc-1",
  "source": {"commit": "...", "worktree_digest": "..."},
  "target": {"os": "...", "device": "..."},
  "criteria": [{"id": "INPUT-001", "required_depth": "P4", "status": "UNVERIFIED", "evidence_ids": []}],
  "verdict": "PARTIAL",
  "dimensions": {"construction": "OBSERVED", "behavior": "UNVERIFIED", "delivery": "OBSERVED", "use": "UNVERIFIED"},
  "limitations": ["No physical Android playtest provided"]
}
```

This is a pedagogical shape, not a finalized schema. Actual hashed files must have real computed digests; never publish `...` placeholders as verification receipts.

## 12. Release rule

A DPC-1 version is not production-ready merely because this document exists. It requires:

1. A deterministic, validated contract parser and policy judge.
2. Controlled execution implemented and tested with malicious fixtures.
3. Receipts bound to real source/artifact identities.
4. Independent golden-fixture expected verdict tests.
5. At least TypeScript and Rust adapter demonstrations, including intentionally failing cases.
6. A documented security model, known limitations and independent cross-platform install test.

When a requirement lacks proof, state the gap. When the project passes its contract, **stop and issue the receipt**.

*No receipt, no banana.*
