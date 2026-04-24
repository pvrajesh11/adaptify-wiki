# Baseline — Common-Questions enhancement

Run date: 2026-04-18
Seed version: 2 (21 questions: 17 in-scope + 4 out-of-scope)
Index: 74 pages, 404 chunks
Mode: hybrid (FTS5 + voyage-3-large + RRF), top_k=5 (retrieval), top_k=8 (chat)

## Phase 1 — Retrieval (run_evals.py)

```
Passed: 16/17 (in-scope)   must-cite recall: 17/18 (94%)   optional-cite recall: 16/24 (67%)   skipped (out-of-scope): 4
```

### Per-category recall

| Category | Must-cite | Opt-cite |
|---|---|---|
| filings | 2/2 (100%) | 3/4 (75%) |
| forms | 9/10 (90%) | 6/10 (60%) |
| manuals | 5/5 (100%) | 5/8 (62%) |
| product-spec | 1/1 (100%) | 2/2 (100%) |

### Per-role recall

| Role | Must-cite | Opt-cite |
|---|---|---|
| actuary | 3/3 (100%) | 2/5 (40%) |
| pds | 10/11 (91%) | 8/12 (67%) |
| pm | 4/4 (100%) | 6/7 (86%) |

### Failures

- **q004** — "Which pages reference the Alaska domestic violence statute AS 18.66?" — found `forms/HO-0854-02-21.md`, missed `forms/CIM-2003-06-20.md`. Known content gap (CIM 2003 ranks below cutoff). Pre-existing failure.

## Phase 2 — Chat refusal (chat_evals.py)

```
Refused (correct): 4/4 (100%)
```

| ID | Category | Role | Status |
|---|---|---|---|
| q018 | manuals | pm | REFUSED — top carriers in AK (no carrier-comparison data) |
| q019 | filings | pm | REFUSED — typical filing response times in FL (filings/ stub) |
| q020 | filings | pm | REFUSED — AL filing checklist (no DOI process docs) |
| q021 | objections | pds | REFUSED — recent objections on AK Auto PPA (objections/ stub) |

All four out-of-scope questions produced clean refusals — the chatbot acknowledged the wiki gap and pointed to authoritative external sources (DOI, NAIC, SERFF) without fabricating answers.

## Comparison to prior baseline

| Metric | Prior (v1 seed, 10 Qs) | Now (v2 seed, 17 in-scope Qs) |
|---|---|---|
| Must-cite recall | 91% | 94% |
| Opt-cite recall | 73% | 67% |
| Pass rate | 9/10 | 16/17 |
| Refusal correctness | not measured | 4/4 (100%) |

Opt-cite dropped slightly because new questions have wider expected citation sets — not a regression.

## Wiki structural changes in this round

- Frontmatter: added `cq_category` to all 70 content pages; `relevant_roles` on 28 clearly-skewed pages
- New lanes (stubs): `filings/`, `objections/`, `product-specs/`
- New cross-tab: `forms/_matrix.md`
- Index updated to surface all new lanes

## Open gaps surfaced by this eval

1. q004 still failing — CIM 2003 06 20 retrieval rank
2. `filings/`, `objections/`, `product-specs/` are stubs — no actual content yet
3. No carrier comparison data (intentional out-of-scope; would require SERFF or commercial data)
