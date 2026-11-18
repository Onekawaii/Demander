# Demander / ProofForge — Commercial Experiment 001

**Status:** experimental branch; no production, customer, or paid validation claimed.
**Product owner:** Demander. **Other 38 repositories:** preserve as-is.
**Candidate buyer:** indie software agencies and developers receiving AI-generated Python patches.
**Job:** distinguish "code was generated" from "declared checks actually ran and passed."

## One narrow product promise

Provide a scoped report containing source fingerprint, declared tests,
actual exit statuses, negative-control failures and explicit UNVERIFIED areas.
This is not a correctness guarantee, sandbox, AI model evaluation system,
Android verifier, or automated production approval.

## Independently inspectable demonstration

From a clean Windows checkout with Python 3.11+ and no third-party runtime libraries:

~~~powershell
cd .\Demander
python -m unittest discover -s tests -v
python -m scripts.proof_pilot --out "$env:TEMP\demander-pilot-001"
~~~

Output path must be new or empty. The command runs only deliberately generated,
trusted Python fixtures. Their unittest code DOES run with current OS-user
permissions. Inspect the source before running it. No third-party repositories
are accessed.

| Test | Expected verdict | Why |
|---|---|---|
| Generated good, read-only | PARTIAL | File exists; test execution unverified |
| Generated good, authorized unittest | QUALIFIED | Declared P1/P2 checks met for this fixture only |
| Generated broken, authorized unittest | REJECTED | Test demands 2+2=4 but target returns 0 |
| Mutated source after good receipt | Old receipt invalidated | Source hash differs |

Results include pilot_summary.json, its SHA-256 file, and three receipt.json files.
These are generated-fixture demonstration artifacts, NOT external customer proof.

## Actual customer pilot — NOT yet performed

Choose one customer-authorized trusted Python repository. Default to read-only
inspect / verify without --execute. Running arbitrary project tests as a normal
OS user is unsafe without independent isolation. Do not enable execution
against foreign untrusted code.

Acceptance:
1. Customer provides consent, objective, exact commit and declared test criteria.
2. Reviewer independently checks criteria; builder assertions alone do not count.
3. A read-only run shows actual scope and UNVERIFIED outcomes.
4. An isolated, explicitly authorized run proves a good and deliberately broken case.
5. A third party reproduces evidence from a clean checkout.
6. Buyer reports value, failure detection and willingness to pay.

Do not claim paid validation from GitHub stars, self-tests or hypothetical pricing.

## Unmeasured customer metrics

| Metric | Current state |
|---|---|
| External developer interviews | UNKNOWN |
| Customer-authorized repositories | UNKNOWN |
| Independently reproduced pilot passes | UNKNOWN |
| False accepts / false rejects | UNKNOWN |
| Time to first receipt | UNKNOWN |
| Signed pilots / revenue | UNKNOWN |

Advance only after green CI plus reproducible, independent real-user validation.
A successful generated-fixture demonstration is insufficient for merge or release.
