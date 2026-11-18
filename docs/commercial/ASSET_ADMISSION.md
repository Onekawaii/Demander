# Gold Rush asset admission and preservation policy

The November 17 ORE_REGISTER.json is a prospecting document, NOT a dependency
manifest, license grant or acceptance certificate. It records technical
status as not independently retested and says licensing review is required.
Keep the full register locally, outside this public repo: it may name
private projects.

## Preservation covenant

Only Onekawaii/Demander may be changed by this experiment. All other 38
repositories remain unchanged. Do not modify, merge, rename, delete,
force-push, archive or copy source from them. A GitHub URL does not establish
permission to import source.

Use the local mining register read-only:

~~~powershell
cd .\Demander
python -m scripts.assay_ore "C:\path\to\ORE_REGISTER.json" --out "$env:TEMP\gold-rush-assay.json"
~~~

The assay report is local and never automatically published. It refuses
to overwrite an existing report. Even a fully reviewed candidate remains
transfer_admitted = false until a separate explicit decision.

## Extraction queue — proposed only

| Order | Source | Candidate | Proof required |
|---|---|---|---|
| 1 | The Aviary | SQLite receipt ledger | Replay/migration/tamper tests |
| 2 | APEVM | Trusted runner | Execution lifecycle, documented lack of sandbox |
| 3 | Ministry | One Intake/Run Ledger surface | One certified G0-G3 vertical slice |
| 4 | Grandma | Offline routing adapter | Outage and no false execution tests |
| 5 | Jungle Canopy | Canonical hash utilities | Cross-version and cross-platform fixtures |
| 6 | ApeGPT | Local IDE adapter | Rollback and host-access boundary |
| 7 | ApeRuntime | Android testing client | Emulator and physical device evidence |

Each candidate must satisfy all seven gates:
owner approval; license clearance; exact source SHA/provenance;
clean reproduction; independent negative test; stable interface contract;
and security boundary review.

**Current admission: ZERO.**

Prefer thin adapters and explicit contracts, not blind source copies.
Shared implementation between the builder and verifier can share a bug;
require independent acceptance tests.

The remaining source projects retain their own identities and priorities.
Do not treat creative/IP projects as disposable because they lack VC metrics.
