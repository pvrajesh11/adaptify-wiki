# Phase 0 Baseline — Chat Scenarios

Run date: 2026-04-23
Model: claude-sonnet-4-6   top_k: 8
Scenarios: 10   Total turns: 20

## Headline finding

Retrieval is healthy (89% must-cite recall, 90% topic coverage), but only 40% of turns are classified with the expected action. Inspection of failing turns shows the model usually answers correctly with the right citations, then tails off with hedging language ("the excerpts do not provide every detail …") that trips REFUSAL_RE. The brittleness of the heuristic refusal classifier — flagged in the Phase 0 plan — dominates the failure list. True multi-turn failures (forgotten state on a follow-up, no clarification on under-specified Qs) are visible separately in `entity_inheritance` and `action_match` on s006 t1.

## Aggregate metrics

| Metric | Value |
|---|---|
| Scenarios passed (strict: every turn passes every applied dimension) | 2/10 |
| Action-classification accuracy | 8/20 (40%) |
| Must-cite recall | 16/18 (89%) |
| Optional-cite recall | 19/24 (79%) |
| Topic coverage (substring) | 27/30 (90%) |
| Entity inheritance (turns where source reflects inherited facet) | 6/7 (86%) |
| Clarification topic coverage | 3/3 (100%) |
| Refusal correctness | 1/1 (100%) |

## Per-scenario results

### s001 — FAIL (forms / pds)
_Cross-state inheritance: intra-family exclusion AK -> CA -> AL. State changes each turn; LOB inherits._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Does the intra-family exclusion apply in Alaska for Auto ... | answer | answer | ✓ 1/1 | ✓ 3/3 | — | — | — | ✓ |
| 2 | What about California? | answer | refuse | ✓ 1/1 | ✓ 2/2 | ✓ | — | — | ✗ |
| 3 | And Alabama? | answer | refuse | ✓ 1/1 | ✗ 1/2 | ✓ | — | — | ✗ |

### s002 — FAIL (manuals / pm)
_Followup chain within one state: Auto PPA in Alaska. State + LOB inherit; coverage shifts each turn._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | What coverage combinations are available for Auto PPA in ... | answer | answer | ✓ 1/1 | ✓ 2/2 | — | — | — | ✓ |
| 2 | What collision deductible options are available for that? | answer | refuse | ✓ 1/1 | ✓ 1/1 | ✗ | — | — | ✗ |
| 3 | And what driver discounts apply? | answer | refuse | ✓ 1/1 | ✓ 1/1 | ✓ | — | — | ✗ |

### s003 — FAIL (forms / pds)
_Reverse-lookup statute -> state switch. Tests retrieval by statute string and entity reset on state change._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Which forms reference Alaska statute AS 18.66? | answer | answer | ✓ 1/1 | ✓ 2/2 | — | — | — | ✓ |
| 2 | What about California domestic-partnership law in Auto PPA? | answer | refuse | ✓ 1/1 | ✓ 2/2 | — | — | — | ✗ |

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

### s010 — FAIL (forms / pds)
_Drilldown chain within one form. Tests stepwise narrowing where state + LOB + form_id should all inherit._

| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | What does the Arizona amendatory exclude for transportati... | answer | refuse | ✓ 1/1 | ✓ 2/2 | — | — | — | ✗ |
| 2 | What's the volunteer carve-out? | answer | refuse | ✓ 1/1 | ✓ 2/2 | ✓ | — | — | ✗ |
| 3 | Which statute defines that volunteer activity? | answer | refuse | ✓ 1/1 | ✓ 1/1 | ✓ | — | — | ✗ |

## Failure diagnostics

- **s001 t2** [action_match] — Q: _What about California?_
  - expected `answer`, got `refuse`
- **s001 t3** [action_match] — Q: _And Alabama?_
  - expected `answer`, got `refuse`
- **s001 t3** [topic_coverage] — Q: _And Alabama?_
  - missed substrings: `['abuse']`
- **s002 t2** [action_match] — Q: _What collision deductible options are available for that?_
  - expected `answer`, got `refuse`
- **s002 t2** [entity_inheritance] — Q: _What collision deductible options are available for that?_
  - facets: `{'state=AK': False, 'lob=auto-ppa': True}`
  - retrieved states: `[]`   products: `['auto-ppa', 'homeowners-hobp', 'motor-truck-cargo']`
- **s002 t3** [action_match] — Q: _And what driver discounts apply?_
  - expected `answer`, got `refuse`
- **s003 t2** [action_match] — Q: _What about California domestic-partnership law in Auto PPA?_
  - expected `answer`, got `refuse`
- **s004 t2** [action_match] — Q: _How does that differ from the multistate base policy definition?_
  - expected `answer`, got `refuse`
- **s004 t2** [must_cite_recall] — Q: _How does that differ from the multistate base policy definition?_
  - missed: `['forms/PPA-0001-07-16.md']`
  - top-8 retrieved: `['multistate/homeowners-hobp/rating-rules/rating-factors.md', 'product-states/homeowners-hobp-AK/rating-rules/coverage-options.md', 'multistate/homeowners-hobp/rating-rules/flood-coverage.md', 'product-states/homeowners-hobp-AK/rating-rules.md', 'product-states/homeowners-hobp-FL/rating-rules/coverage-options.md', 'multistate/auto-ppa/README.md', 'multistate/homeowners-hobp/rating-rules/coverage-options.md', 'multistate/homeowners-hobp/rating-rules.md']`
- **s004 t2** [topic_coverage] — Q: _How does that differ from the multistate base policy definition?_
  - missed substrings: `['spouse']`
- **s006 t1** [action_match] — Q: _List driver discount rules I should review._
  - expected `clarify`, got `answer`
- **s006 t2** [must_cite_recall] — Q: _Alabama Auto PPA._
  - missed: `['multistate/auto-ppa/rating-rules/driving-record-points.md']`
  - top-8 retrieved: `['product-states/auto-ppa-AL/endorsements.md', 'product-states/auto-ppa-AL/rating-rules.md', 'forms/PPA-0101-03-18.md', 'products/auto-ppa.md', 'product-states/auto-ppa-AL/rating-rules/state-specifics.md', 'states/AL.md', 'product-states/auto-ppa-AL/rating-rules/coverage-options.md', 'product-states/auto-ppa-AL/rating-rules/driving-record-points.md']`
- **s008 t2** [action_match] — Q: _What about the Alabama Auto PPA manual?_
  - expected `answer`, got `refuse`
- **s009 t1** [action_match] — Q: _How does the Alaska Homeowners domestic-violence exception differ from the Alaska Auto PPA domestic-violence exception?_
  - expected `answer`, got `refuse`
- **s009 t1** [topic_coverage] — Q: _How does the Alaska Homeowners domestic-violence exception differ from the Alaska Auto PPA domestic-violence exception?_
  - missed substrings: `['AS 18.66']`
- **s010 t1** [action_match] — Q: _What does the Arizona amendatory exclude for transportation network drivers?_
  - expected `answer`, got `refuse`
- **s010 t2** [action_match] — Q: _What's the volunteer carve-out?_
  - expected `answer`, got `refuse`
- **s010 t3** [action_match] — Q: _Which statute defines that volunteer activity?_
  - expected `answer`, got `refuse`

## What this baseline implies for later phases

- Phase 1 (agent loop) targets `must_cite_recall` and `topic_coverage`.
- Phase 2 (session entity memory) targets `entity_inheritance`.
- Phase 3 (slot-filling) targets `action_match` on underspecified turns and `clarification_topic_coverage`.
- Phase 4 (structured store + relations) targets the metadata-style queries (s008) and structural lookups.
- Phase 5 (carrier dimension) is what would lift `refusal_clean` from "correct refusal" to "correct answer" on s007.
