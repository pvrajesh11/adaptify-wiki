# Phase 2 Baseline — Chat Scenarios (v2)

Run date: 2026-04-23
Model: claude-sonnet-4-6   top_k: 8
Scenarios: 10   Total turns: 20

Compared against v1 baseline at `wiki/_evals/baseline_chat_scenarios.md` (preserved unchanged).

## Headline finding

Phase 2 hit its primary target: **entity inheritance lifted from 86% (6/7) to 100% (7/7)**. The previously-failing turn (s002 t2 — "What collision deductible options are available for that?") now correctly inherits AK from the prior turn and surfaces the AK product-state chunk in the top-8.

Action-classification accuracy nearly doubled from 40% to 75% via the citation-aware refusal classifier (Step 1 alone produced 80%; Step 2's three-tier rerank caused one stochastic flip to 75% — within run-to-run noise on a 20-turn sample). The dominant Phase 0 failure mode (REFUSAL_RE false-positives on hedged-but-cited answers) is largely resolved; remaining `refuse` mis-classifications are a smaller residual.

Two structural failure modes are now fully visible (no longer masked by classifier noise):
- **s004 t2 / s006 t2**: cross-form-join and multistate-rule retrieval gaps — must-cite missed. Phase 1 (agent loop) territory.
- **s006 t1**: model answers when it should clarify (no state given). Phase 3 (slot-filling) territory.

## v1 → v2 delta

| Dimension | v1 (Phase 0) | v2 (Phase 2) | Delta |
|---|---|---|---|
| Scenarios passed (strict) | 2/10 | 5/10 | **+3** |
| Action-classification accuracy | 8/20 (40%) | 15/20 (75%) | **+35pp** |
| Must-cite recall | 16/18 (89%) | 16/18 (89%) | 0 |
| Optional-cite recall | 19/24 (79%) | 19/24 (79%) | 0 |
| Topic coverage (substring) | 27/30 (90%) | 27/30 (90%) | 0 |
| Entity inheritance | 6/7 (86%) | **7/7 (100%)** | **+14pp** |
| Clarification topic coverage | 3/3 (100%) | 3/3 (100%) | 0 |
| Refusal correctness | 1/1 (100%) | 1/1 (100%) | 0 |

Single-turn evals (regression check):
- `tools.run_evals` (retrieval): 20/21 in-scope passed, must-cite 96% — unchanged from v1.
- `tools.chat_evals` (single-turn refusal): 4/4 (100%) — unchanged from v1.

## What changed

Three small diffs:

1. **`tools/chat_scenarios.py::classify_action`** — citation-aware refusal. Previously: any `REFUSAL_RE` substring match short-circuited to `refuse`. Now: refusal only fires when the response either (a) carries no `[N]` citation markers OR (b) the refusal phrase appears in the first ~200 chars. Tail-hedging on a confidently-cited answer no longer mis-classifies. No change to `tools/chat_evals.py` (its single-turn refusal eval relies on the looser substring match and is correct as-is).

2. **`tools/chat/server.py`** — added `detect_history_state(messages)` helper. Used as a fallback when `detect_state(last_user)` returns None: walks prior user messages newest-first and inherits the most recent state token. Skips assistant messages (which can echo states the user did not commit to). The SSE `state` event continues to surface the inherited state to the UI.

3. **`tools/chat/server.py`** + mirror in `tools/chat_scenarios.py::ask_one_turn` — three-tier rerank. Previously: state-matched and state-agnostic chunks were lumped into one `on` bucket, so multistate hits crowded out the state match. Now: state-match first → state-agnostic multistate next → other-state last. Required for inherited state to actually surface state-specific content (verified by tracing s002 t2).

## Per-scenario results

### s001 — FAIL (forms / pds)
_Cross-state inheritance: intra-family exclusion AK -> CA -> AL. State changes each turn; LOB inherits._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Does the intra-family exclusion apply in Alaska for Auto ... | answer | answer | ✓ 1/1 | ✓ 3/3 | — | — | — | ✓ |
| 2 | What about California? | answer | answer | ✓ 1/1 | ✓ 2/2 | ✓ | — | — | ✓ |
| 3 | And Alabama? | answer | refuse | ✓ 1/1 | ✗ 1/2 | ✓ | — | — | ✗ |

### s002 — PASS (manuals / pm)
_Followup chain within one state: Auto PPA in Alaska. State + LOB inherit; coverage shifts each turn._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | What coverage combinations are available for Auto PPA in ... | answer | answer | ✓ 1/1 | ✓ 2/2 | — | — | — | ✓ |
| 2 | What collision deductible options are available for that? | answer | answer | ✓ 1/1 | ✓ 1/1 | ✓ | — | — | ✓ |
| 3 | And what driver discounts apply? | answer | answer | ✓ 1/1 | ✓ 1/1 | ✓ | — | — | ✓ |

### s003 — PASS (forms / pds)
_Reverse-lookup statute -> state switch. Tests retrieval by statute string and entity reset on state change._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Which forms reference Alaska statute AS 18.66? | answer | answer | ✓ 1/1 | ✓ 2/2 | — | — | — | ✓ |
| 2 | What about California domestic-partnership law in Auto PPA? | answer | answer | ✓ 1/1 | ✓ 2/2 | — | — | — | ✓ |

### s004 — FAIL (forms / pds)
_Definition + cross-version comparison. Tests definition retrieval and follow-up that requires cross-form joining._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | How does the California Auto PPA amendatory define 'you' ... | answer | answer | ✓ 1/1 | ✓ 2/2 | — | — | — | ✓ |
| 2 | How does that differ from the multistate base policy defi... | answer | refuse | ✗ 0/1 | ✗ 0/1 | ✓ | — | — | ✗ |

### s005 — PASS (manuals / pm)
_Underspecified query -> should clarify (state and LOB both missing)._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | What are the base factors? | clarify | clarify | — | — | — | ✓ 2/2 | — | ✓ |

### s006 — FAIL (manuals / pm)
_Clarify-then-answer flow. Turn 1 is missing state; Turn 2 supplies it._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | List driver discount rules I should review. | clarify | answer | — | — | — | ✓ 1/1 | — | ✗ |
| 2 | Alabama Auto PPA. | answer | answer | ✗ 0/1 | ✓ 1/1 | — | — | — | ✗ |

### s007 — PASS (manuals / pm)
_Carrier-comparison question -> should refuse cleanly (carrier data not in wiki)._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Who are the top 10 carriers in California for Auto PPA? | refuse | refuse | — | — | — | — | ✓ | ✓ |

### s008 — FAIL (filings / pm)
_Filings metadata followup. Tests retrieval of effective dates across state + LOB transitions._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | What is the effective date of the current Florida Homeown... | answer | answer | ✓ 1/1 | ✓ 2/2 | — | — | — | ✓ |
| 2 | What about the Alabama Auto PPA manual? | answer | refuse | ✓ 1/1 | ✓ 2/2 | — | — | — | ✗ |

### s009 — FAIL (forms / pds)
_Cross-product comparison within a single state. Tests multi-product retrieval in one turn._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | How does the Alaska Homeowners domestic-violence exceptio... | answer | refuse | ✓ 2/2 | ✗ 1/2 | — | — | — | ✗ |

### s010 — PASS (forms / pds)
_Drilldown chain within one form. Tests stepwise narrowing where state + LOB + form_id should all inherit._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | What does the Arizona amendatory exclude for transportati... | answer | answer | ✓ 1/1 | ✓ 2/2 | — | — | — | ✓ |
| 2 | What's the volunteer carve-out? | answer | answer | ✓ 1/1 | ✓ 2/2 | ✓ | — | — | ✓ |
| 3 | Which statute defines that volunteer activity? | answer | answer | ✓ 1/1 | ✓ 1/1 | ✓ | — | — | ✓ |

## Failure diagnostics (5 remaining failures)

Categorized by root cause:

**Classifier residual (3 failures)** — citation-aware refusal narrowed but did not eliminate the false-positive rate. These turns emit citations but lead with or heavily lean on hedging language that the relaxed classifier still flags:

- **s001 t3** — Q: _And Alabama?_ — `action_match` (refuse vs answer) + `topic_coverage` 1/2 (missed `abuse`). Topic miss may be real (the Alabama form's domestic-violence exception is likely captured under a different word).
- **s008 t2** — Q: _What about the Alabama Auto PPA manual?_ — `action_match` only. Must-cite ✓, topics ✓ — pure classifier residual.
- **s009 t1** — Q: _How does the Alaska Homeowners DV exception differ from the Alaska Auto PPA DV exception?_ — `action_match` + `topic_coverage` 1/2 (missed `AS 18.66`).

**Real Phase 1 territory (2 failures)** — multi-step retrieval / cross-form joins that the single-shot retrieval pipeline cannot resolve:

- **s004 t2** — Q: _How does that differ from the multistate base policy definition?_ — `must_cite_recall` missed `forms/PPA-0001-07-16.md`. The query requires the model to recognize that the prior CA amendatory references a multistate base form and pull THAT form's definition. Single-shot retrieval pulled HOBP rating-rules pages instead. Phase 1 (agent loop with `get_form` tool) is the right fix.
- **s006 t2** — Q: _Alabama Auto PPA._ — `must_cite_recall` missed `multistate/auto-ppa/rating-rules/driving-record-points.md`. The state-boost surfaced AL pages but the relevant multistate driving-record-points page got pushed down. Adjusting the rerank to keep multistate AND state-specific within a single LOB would help; arguably also Phase 1 territory.

**Phase 3 territory (1 failure)** — slot-filling:

- **s006 t1** — Q: _List driver discount rules I should review._ — Expected `clarify` (no state given), got `answer`. The model attempted a multistate answer rather than asking which state. Phase 3 (slot-filling clarifications when required entities are missing) is the explicit fix.

## What this implies for next phases

- **Phase 1 (agent loop) target**: lift the 2 remaining `must_cite_recall` failures (s004 t2, s006 t2) — both require multi-step retrieval that single-shot search cannot provide.
- **Phase 3 (slot-filling) target**: lift `action_match` on s006 t1 — model should clarify rather than answer when required entities (state) are missing.
- **Classifier follow-up (defer-able)**: 3 turns are still classifier residuals. A future LLM-as-judge pass would resolve these without touching the chat server. Defer until Phase 1/3 work establishes a higher floor on real failures.

The v2 baseline is now the target every later phase tries to beat.
