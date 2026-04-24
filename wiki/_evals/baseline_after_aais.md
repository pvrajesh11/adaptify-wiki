# Baseline — After AAIS AZ + CA Ingest

Run date: 2026-04-18
Seed version: 3 (25 questions: 21 in-scope + 4 out-of-scope)
Index: 80 pages, 429 chunks
Mode: hybrid (FTS5 + voyage-3-large + RRF), top_k=5 (retrieval), top_k=8 (chat)

## Phase 1 — Retrieval (run_evals.py)

```
Passed: 20/21 (in-scope)   must-cite recall: 22/23 (96%)   optional-cite recall: 21/31 (68%)   skipped (out-of-scope): 4
```

### Per-category recall

| Category | Must-cite | Opt-cite |
|---|---|---|
| filings | 4/4 (100%) | 4/5 (80%) |
| forms | 12/13 (92%) | 12/16 (75%) |
| manuals | 5/5 (100%) | 4/8 (50%) |
| product-spec | 1/1 (100%) | 1/2 (50%) |

### Per-role recall

| Role | Must-cite | Opt-cite |
|---|---|---|
| actuary | 3/3 (100%) | 2/5 (40%) |
| pds | 13/14 (93%) | 13/18 (72%) |
| pm | 6/6 (100%) | 6/8 (75%) |

### New AAIS questions (q022–q025) — all PASS

| ID | Question | Must | Opt |
|---|---|---|---|
| q022 | What does the Arizona amendatory exclude for transportation network drivers? | 1/1 | 2/2 |
| q023 | Which Arizona statute does the AZ Auto PPA reference for shared-expense carpools? | 2/2 | 1/1 |
| q024 | How does the California Auto PPA amendatory define 'you' and 'your'? | 1/1 | 2/2 |
| q025 | Which states recognize domestic partnership in the Auto PPA 'you' or 'family member' definition? | 1/1 | 2/2 |

### Failures

- **q004** — "Which pages reference the Alaska domestic violence statute AS 18.66?" — found `forms/HO-0854-02-21.md`, missed `forms/CIM-2003-06-20.md`. Pre-existing failure, unchanged.

## Phase 2 — Chat refusal (chat_evals.py)

```
Refused (correct): 4/4 (100%)
```

| ID | Category | Role | Status |
|---|---|---|---|
| q018 | manuals | pm | REFUSED — top carriers in AK |
| q019 | filings | pm | REFUSED — typical filing response times in FL |
| q020 | filings | pm | REFUSED — AL filing checklist |
| q021 | objections | pds | REFUSED — recent objections on AK Auto PPA |

## Comparison to prior baseline

| Metric | Prior (v2 seed, 17 in-scope) | Now (v3 seed, 21 in-scope) |
|---|---|---|
| Must-cite recall | 17/18 (94%) | 22/23 (96%) |
| Opt-cite recall | 16/24 (67%) | 21/31 (68%) |
| Pass rate | 16/17 | 20/21 |
| Refusal correctness | 4/4 (100%) | 4/4 (100%) |
| Index size | 74 pages, 404 chunks | 80 pages, 429 chunks |

Recall improved on both must-cite and opt-cite. The 4 new AAIS questions added 5 must-cite citations and 7 opt-cite citations, all hit. q004 remains the only retrieval failure.

## Wiki changes in this round

- Ingested 2 AAIS amendatory endorsements (AZ, CA) under naming convention (b) — accurate AAIS form IDs `PA-XXXX-XX-XX`.
- New pages (6): `forms/PA-0102-07-18.md`, `forms/PA-0104-01-25.md`, `states/AZ.md`, `states/CA.md`, `product-states/auto-ppa-AZ/endorsements.md`, `product-states/auto-ppa-CA/endorsements.md`.
- Updated pages (4): `products/auto-ppa.md` (active states AK/AL/AZ/CA, key forms), `forms/_matrix.md` (2 new rows + coverage patterns), `wiki/index.md` (new states + product-states + forms + counts), `wiki/_log.md`, `wiki/_absorb_log.json`.
- Backfilled `bureau: aais` and `aais_form_id` on 3 existing PPA forms (PPA-0001-07-16, PPA-0101-03-18, PPA-0154-01-20).
- Added 4 new in-scope eval questions (q022–q025).

## Open gaps surfaced by this eval

1. q004 still failing — CIM 2003 06 20 retrieval rank for AS 18.66 reverse lookup (carried over).
2. `filings/`, `objections/`, `product-specs/` are stubs — no actual content yet (carried over).
3. No carrier comparison data (intentional out-of-scope).
4. AZ and CA Auto PPA — only the AAIS amendatory endorsement is ingested per state; no rating manual or underwriting rules.
