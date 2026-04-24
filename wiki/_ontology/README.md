---
title: "Insurance Product Ontology"
summary: "Spec for what an insurance product is in this wiki: entities, canonical IDs, where each is stored today, where each will live as the structured store comes online, and the relations between them."
type: ontology
cq_category: reference
last_updated: 2026-04-23
status: phase-0.5-baseline
---

# Insurance Product Ontology

> **Maintenance rule:** if you add an entity in code or a new lane in the wiki, update this doc in the same PR. Spec drift kills the spec.

## 1. Overview

This document is the canonical list of entities the wiki and the structured store (Phase 4) need to model in order to answer the Common Questions taxonomy. It is **descriptive of today** and **prescriptive of tomorrow** — every entity entry says where it lives now and where it should live once the structured store lands.

What this is:
- The schema spec for Phase 4 DuckDB tables.
- The frontmatter-extension target list (e.g. add `carrier`, add `rule_id`).
- The ingest checklist — every new doc must map its content to one or more entities below.
- The eval-coverage map — every entity should be touched by at least one eval scenario.

What this is **not**:
- Not a database schema (table-level DDL belongs in Phase 4 docs).
- Not a controlled vocabulary spec (existing taxonomies like `cq_category` and `type` are summarized in the appendix, not redesigned here).
- Not a UI / product spec.
- Not auto-generated from frontmatter — it is hand-maintained and slightly ahead of code.

## 2. Two-store principle

The wiki is two complementary stores. Every entity below says which store(s) it lives in.

| Store | Role | Strengths | Limits |
|---|---|---|---|
| **Prose wiki** (`wiki/**/*.md` + YAML frontmatter) | Narrative, clause text, comparisons, human-readable summaries | Citable, browsable, LLM-RAG friendly, edit-anywhere | Bad at counting, joining, filtering by exact value |
| **Structured store** (Phase 4 DuckDB) | Facets, rules, factors, joins, derived tables | Exact lookup, aggregation, NL→SQL | No prose; loses context when isolated |

Today only the prose wiki exists. The Phase 4 store is a planned addition; this doc is its schema spec.

## 3. Entity catalog

Each entry follows the same shape: canonical ID, where stored today, where it should be stored, relations it participates in, current status, and (if missing/partial) what's missing and which CQ question first surfaces the gap.

Status legend: ✅ first-class (modeled, retrievable, indexed) · ⚠️ partial (exists in some form but not addressable / queryable / canonical) · ❌ missing (no representation today).

---

### 3.1 Product (LOB)
- **Canonical ID**: kebab-case slug. e.g. `auto-ppa`, `homeowners-hobp`, `motor-truck-cargo`.
- **Storage today**: `wiki/products/<lob>.md` page; `product:` frontmatter facet on every page that belongs to the LOB.
- **Storage target (Phase 4)**: `products(product_id, name, base_form_id, active_states[])` table; frontmatter unchanged.
- **Relations**: `Form --APPLIES_TO_PRODUCT--> Product`; `Product --HAS_BASE_FORM--> Form`; `Product --ACTIVE_IN--> State`.
- **Status**: ✅ first-class.
- **Example**: `wiki/products/auto-ppa.md`.

### 3.2 State
- **Canonical ID**: USPS 2-letter code (`AK`, `AL`, `AZ`, `CA`, `FL`).
- **Storage today**: `wiki/states/<XX>.md` page; `state:` frontmatter facet on state-specific pages.
- **Storage target (Phase 4)**: `states(state_code, name, doi_url, …)` table; frontmatter unchanged.
- **Relations**: `Form --APPLIES_TO_STATE--> State`; `Filing --FILED_IN--> State`; `Statute --ENACTED_BY--> State`.
- **Status**: ✅ first-class.
- **Example**: `wiki/states/AK.md`.

### 3.3 Bureau
- **Canonical ID**: lowercase short code (`aais`, `iso`, `naic`, `companion`).
- **Storage today**: `bureau:` frontmatter facet on form pages. No dedicated page or table.
- **Storage target (Phase 4)**: `bureaus(bureau_id, full_name)` lookup table; frontmatter unchanged.
- **Relations**: `Form --ISSUED_BY_BUREAU--> Bureau`.
- **Status**: ✅ first-class for AAIS forms ingested 2026-04-18; no other bureaus represented yet.
- **Example**: `bureau: aais` on `wiki/forms/PA-0102-07-18.md`.

### 3.4 Form (endorsement / base / amendatory)
- **Canonical ID**: `<filing_org>-<series>-<edition>` rendered with hyphens, e.g. `PA-0102-07-18`, `PPA-0001-07-16`, `HO-0854-02-21`. Bureau-specific id (`aais_form_id: "PA 0102 07 18"`) preserved as separate facet.
- **Storage today**: `wiki/forms/<id>.md` page with prose for each amendment, plus `form_id:`, `aais_form_id:`, `amends:`, `states_filed:`, `bureau:`, `citations:` frontmatter. Catalog view at `wiki/forms/_matrix.md`.
- **Storage target (Phase 4)**: `forms(form_id, bureau, edition, base_or_amendatory, base_form_id, …)` table + `form_states(form_id, state_code, mandatory)`. Prose page persists for clause-level retrieval.
- **Relations**: `Form --AMENDS--> Form`, `Form --REPLACES--> Form`, `Form --APPLIES_TO_STATE--> State`, `Form --APPLIES_TO_PRODUCT--> Product`, `Form --CITES_STATUTE--> Statute`, `Form --ISSUED_BY_BUREAU--> Bureau`.
- **Status**: ✅ first-class.
- **Example**: `wiki/forms/PA-0102-07-18.md`.

### 3.5 Product-State Binding
- **Canonical ID**: `<product>-<state>` (e.g. `auto-ppa-AK`).
- **Storage today**: `wiki/product-states/<product>-<XX>/` directory; pages combine `product:` + `state:` frontmatter.
- **Storage target (Phase 4)**: `product_states(product_id, state_code, status, current_filing_id, last_updated)` join table.
- **Relations**: `ProductState --HAS_MANUAL--> Manual`, `ProductState --REQUIRES_ENDORSEMENT--> Form`, `ProductState --GOVERNED_BY_FILING--> Filing`.
- **Status**: ✅ first-class.
- **Example**: `wiki/product-states/auto-ppa-AK/`.

### 3.6 Manual (rating manual)
- **Canonical ID** (target): `<product>-<state>-<version>`, e.g. `auto-ppa-AK-v1.5`. Today there is no `manual_id` field.
- **Storage today**: prose pages under `wiki/product-states/<product>-<XX>/rating-rules/` (`coverage-options.md`, `driving-record-points.md`, `state-specifics.md`, etc.); manual version captured only in page text and `_log.md`.
- **Storage target (Phase 4)**: `manuals(manual_id, product_id, state_code, version, effective_date, supersedes_id)` table; prose pages persist as the rule body.
- **Relations**: `Manual --INCLUDES_RULE--> Rule`, `Manual --SUPERSEDES--> Manual`, `Manual --GOVERNED_BY_FILING--> Filing`.
- **Status**: ⚠️ partial.
- **Gaps**: no `manual_id`; cannot ask "what's the current AK Auto PPA manual version?" structurally; manual versions are only discoverable through prose.
- **First appears in CQ**: filings/version-history questions ("Which manual version is in effect in AL today?").
- **Example**: `wiki/product-states/auto-ppa-AK/rating-rules.md` references "AK manual v1.5 effective 2026-01-01" in prose only.

### 3.7 Coverage
- **Canonical ID**: kebab-case slug, e.g. `uninsured-motorist`, `transportation-network`, `collision`, `comprehensive`. Per LOB; coverages are not globally unique.
- **Storage today**: `wiki/coverages/` lane has 2 pages today (`uninsured-motorist.md`, `transportation-network.md`); most coverages are mentioned only inline in form/manual prose.
- **Storage target (Phase 4)**: `coverages(coverage_id, product_id, name, summary)` table; prose pages persist for narrative.
- **Relations**: `Form --COVERS--> Coverage`, `Coverage --HAS_LIMIT--> Limit`, `Coverage --HAS_DEDUCTIBLE--> Deductible`, `Manual --PRICES--> Coverage`.
- **Status**: ⚠️ partial.
- **Gaps**: most coverages are not addressable; the `COVERS` relation has no frontmatter source today.
- **First appears in CQ**: "What collision deductible options are available in AK?" (Phase 0 scenario s002 t2).

### 3.8 Clause (Exclusion / Definition / Condition)
- **Canonical ID** (target): `<form_id>#<section>`, e.g. `PA-0102-07-18#partA-1f` for the Part A.1.f TNC exclusion. Today there is no `clause_id`.
- **Storage today**: paragraph-level inside form pages, addressed only by `###` heading.
- **Storage target (Phase 4)**: `clauses(clause_id, form_id, section, kind, summary, body_anchor)` table where `kind ∈ {exclusion, definition, condition, payment, suit-limitation, …}`; prose body stays in the form page.
- **Relations**: `Form --HAS_CLAUSE--> Clause`, `Clause --SUPERSEDES_CLAUSE--> Clause` (for amendatories that replace base-form clauses), `Clause --CITES_STATUTE--> Statute`, `Clause --APPLIES_TO_COVERAGE--> Coverage`.
- **Status**: ⚠️ partial.
- **Gaps**: no canonical clause IDs; cross-form comparison ("how does the CA intra-family exclusion differ from AZ?") relies on retrieval finding the right paragraph.
- **First appears in CQ**: forms/clause-comparison questions; Phase 0 scenarios s001 (intra-family) and s004 (definition diff).

### 3.9 Statute
- **Canonical ID** (target): a normalized string per state, e.g. `AS 18.66` (Alaska), `ARS § 43-1201` (Arizona), `Cal Fam C § 297` (California domestic partnership). Today the value lives only in `citations:` frontmatter as free-text.
- **Storage today**: free-text strings inside `citations: [...]` frontmatter on form pages. No `wiki/statutes/` lane.
- **Storage target (Phase 4)**: `wiki/statutes/<id>.md` lane (one page per statute, summary + reverse index of citing forms) + `statutes(statute_id, state_code, title, url, summary)` table.
- **Relations**: `Form --CITES_STATUTE--> Statute`, `Clause --CITES_STATUTE--> Statute`, `Statute --ENACTED_BY--> State`.
- **Status**: ⚠️ partial.
- **Gaps**: no canonical IDs; reverse lookup ("which forms cite AS 18.66?") works only by FTS hit on the citation string. q004 (current eval seed) fails partly for this reason.
- **First appears in CQ**: q004 reverse-lookup; Phase 0 scenario s003.

### 3.10 Limit / Deductible
- **Canonical ID** (target): composite — `(coverage_id, state_code, kind, value, edition)`.
- **Storage today**: unstructured prose inside manual pages and form bodies.
- **Storage target (Phase 4)**: `limits(coverage_id, state_code, value, kind, source_filing_id, effective_date)` rows.
- **Relations**: `Coverage --HAS_LIMIT--> Limit`, `Limit --DEFINED_IN--> Filing`, `Limit --REQUIRED_BY--> Statute` (for statutory minimums).
- **Status**: ❌ missing.
- **Gaps**: cannot ask "what's the minimum BI limit in AZ?" or "list collision deductibles available in AK Auto PPA" structurally.
- **First appears in CQ**: rating-manual questions; Phase 0 scenario s002 t2.

### 3.11 Rating Rule
- **Canonical ID** (target): `<manual_id>#<rule_number>` (e.g. `auto-ppa-AK-v1.5#10.2` for the AK intra-family override).
- **Storage today**: prose under `product-states/<lob>-<state>/rating-rules/`. Rule numbers appear in headings (e.g. "Rule 6.3 — Driver Discounts") but are not structured fields.
- **Storage target (Phase 4)**: `rules(rule_id, manual_id, rule_number, kind, summary, body_anchor)` where `kind ∈ {coverage, eligibility, factor, discount, surcharge, exclusion-override, …}`.
- **Relations**: `Manual --INCLUDES_RULE--> Rule`, `Rule --OVERRIDES_RULE--> Rule` (state vs multistate), `Rule --HAS_FACTOR--> Factor`.
- **Status**: ❌ missing.
- **Gaps**: cannot dedupe rules across states; cannot ask "what's different about Rule 10.2 in AK vs the multistate base?" via SQL.
- **First appears in CQ**: q002 (state-override of intra-family), Phase 0 scenarios s001, s002.

### 3.12 Rating Factor
- **Canonical ID** (target): `(rule_id, factor_class, key)`, e.g. `(auto-ppa-AK#6.3, driver-age, "16-20")`.
- **Storage today**: prose tables in some manuals; not extracted as data.
- **Storage target (Phase 4)**: `factors(rule_id, factor_class, key, value, effective_date)` rows. Excel-exportable.
- **Relations**: `Rule --HAS_FACTOR--> Factor`.
- **Status**: ❌ missing.
- **Gaps**: the entire Common-Questions actuary use-case ("factor selections table for AK Auto PPA") is unanswerable structurally today.
- **First appears in CQ**: every actuary question that asks for tables.

### 3.13 Discount / Surcharge
- **Canonical ID** (target): `(coverage_id, state_code, name, kind)` where `kind ∈ {discount, surcharge}`.
- **Storage today**: mentioned inline in `multistate/auto-ppa/rating-rules/driving-record-points.md` and similar; not structured.
- **Storage target (Phase 4)**: `discounts(discount_id, name, product_id, state_code, kind, applies_to_coverage, factor_value, eligibility_text, source_rule_id)` table.
- **Relations**: `Discount --APPLIES_TO_COVERAGE--> Coverage`, `Discount --DEFINED_BY_RULE--> Rule`.
- **Status**: ❌ missing.
- **Gaps**: cannot ask "list driver discounts available in AL Auto PPA" with structured rows; today depends on RAG hitting the right prose page.
- **First appears in CQ**: q012, Phase 0 scenario s006.

### 3.14 Filing
- **Canonical ID** (target): SERFF tracking number when available, else `<state>-<product>-<filing_date>`.
- **Storage today**: `wiki/filings/` exists as a stub directory only; no real filing pages yet.
- **Storage target (Phase 4)**: `filings(filing_id, serff_tracking, state_code, product_id, filing_type, filed_date, effective_date, status, summary)` table + per-filing wiki page for narrative.
- **Relations**: `Filing --INTRODUCES_FORM--> Form`, `Filing --INTRODUCES_MANUAL--> Manual`, `Filing --FILED_BY_CARRIER--> Carrier`, `Filing --SUPERSEDES_FILING--> Filing`, `Objection --OBJECTS_TO--> Filing`.
- **Status**: ❌ missing.
- **Gaps**: filing-metadata questions (effective dates, response times, SERFF status) cannot be answered.
- **First appears in CQ**: q010, q019, Phase 0 scenario s008.

### 3.15 Objection
- **Canonical ID** (target): `<filing_id>#<objection_number>`.
- **Storage today**: `wiki/objections/` exists as a stub directory only.
- **Storage target (Phase 4)**: `objections(objection_id, filing_id, raised_date, status, summary, doi_response_text)` table + per-objection wiki page.
- **Relations**: `Objection --OBJECTS_TO--> Filing`, `Objection --CITES_STATUTE--> Statute`.
- **Status**: ❌ missing.
- **Gaps**: objections-category CQ questions are entirely unsupported.
- **First appears in CQ**: q021 (refusal probe today), Phase 0 baseline.

### 3.16 Carrier
- **Canonical ID** (target): NAIC company code; secondary alias on group code.
- **Storage today**: not modeled anywhere. Today the wiki only contains AAIS bureau forms — there is no per-carrier filing data.
- **Storage target (Phase 5)**: `wiki/carriers/<naic>.md` lane + `carriers(naic, name, group_naic, group_name, …)` table.
- **Relations**: `Filing --FILED_BY_CARRIER--> Carrier`, `Carrier --MEMBER_OF--> CarrierGroup`, `Carrier --WRITES_IN--> State`.
- **Status**: ❌ missing.
- **Gaps**: every comparison question ("top 10 carriers in CO") and every filing-attribution question is unanswerable; today's correct response is a clean refusal (Phase 0 scenario s007 passes today by refusing).
- **First appears in CQ**: q018 (refusal probe), Phase 0 scenario s007.

### 3.17 Territory
- **Canonical ID** (target): `<state>-<territory_code>` from each state's manual.
- **Storage today**: not modeled.
- **Storage target (Phase 4)**: `territories(territory_id, state_code, name, definition_text, factor_default)` table; per-state territory map page where worth maintaining.
- **Relations**: `Territory --DEFINED_IN_STATE--> State`, `Rule --APPLIES_TO_TERRITORY--> Territory`.
- **Status**: ❌ missing (speculative — no CQ question asks for territory yet).
- **First appears in CQ**: not yet. Mark `(speculative)` and reconsider when first territory-rating question appears.

### 3.18 Vehicle Class / Symbol
- **Canonical ID** (target): bureau-specific symbol, e.g. ISO symbol number.
- **Storage today**: not modeled.
- **Storage target (Phase 4)**: `vehicle_symbols(symbol_id, bureau, year_range, make, model, value_band, …)` table.
- **Relations**: `Rule --APPLIES_TO_SYMBOL--> Symbol`, `Symbol --ISSUED_BY_BUREAU--> Bureau`.
- **Status**: ❌ missing (speculative — no CQ question asks for symbols yet).
- **First appears in CQ**: not yet. Mark `(speculative)`.

### 3.19 Driver Classification
- **Canonical ID** (target): `(state_code, age_band, marital, gender, use_class, points_band)` composite.
- **Storage today**: mentioned in driving-record-points pages; no structured rows.
- **Storage target (Phase 4)**: `driver_classes(class_id, …)` if a CQ question demands it; otherwise leave as prose.
- **Status**: ❌ missing.
- **First appears in CQ**: actuary factor-table questions. Defer to Phase 4 only if Phase 0 evals show this is required.

### 3.20 Loss Cost
- **Canonical ID** (target): `(coverage_id, state_code, territory_id, class_id, edition)`.
- **Storage today**: not modeled. (Loss costs are usually .xlsx in Vault Documents; not yet ingested.)
- **Storage target (Phase 4)**: `loss_costs(...)` table fed from rate-table .xlsx ingestion.
- **Status**: ❌ missing (speculative — depends on Vault Documents .xlsx ingestion path).
- **First appears in CQ**: pricing-comparison questions. Mark `(speculative)`.

### 3.21 Eligibility Rule
- **Canonical ID** (target): `<manual_id>#<eligibility_section>`.
- **Storage today**: mentioned in prose under `multistate/<lob>/rating-rules/underwriting-rules.md` and similar; no structured representation.
- **Storage target (Phase 4)**: rolled into the `rules` table with `kind = "eligibility"`. No separate table.
- **Relations**: `Rule --DISQUALIFIES--> RiskAttribute` (where RiskAttribute is a free-text or enum tag).
- **Status**: ❌ missing.
- **First appears in CQ**: "What risks are ineligible for HOBP in FL?" (filings/manuals questions).

---

## 4. Relations table (mirrors Phase 4 `relations` schema)

The Phase 4 structured store will materialize a single `relations(subject_id, predicate, object_id, source_filing_id, effective_date)` table. Every predicate below is a row-type that table must support. Predicates marked _gap_ have no frontmatter source today; they document what Phase 4 needs to begin recording.

| Predicate | Subject → Object | Source today |
|---|---|---|
| `AMENDS` | Form → Form | `amends:` frontmatter |
| `REPLACES` | Form → Form | `replaces:` frontmatter (HO 0801 supersedes HO 0814 in AL) |
| `SUPERSEDES_FILING` | Filing → Filing | gap — no `filings/` data yet |
| `CITES_STATUTE` | Form / Clause → Statute | `citations:` frontmatter (free-text strings) |
| `APPLIES_TO_STATE` | Form → State | `state:` / `states_filed:` frontmatter |
| `APPLIES_TO_PRODUCT` | Form → Product | `product:` frontmatter |
| `ISSUED_BY_BUREAU` | Form → Bureau | `bureau:` frontmatter |
| `MANDATORY_IN_STATE` | Form → State | prose only — gap |
| `COVERS` | Form / Clause → Coverage | implicit; no field today — gap |
| `INCLUDES_RULE` | Manual → Rule | gap |
| `OVERRIDES_RULE` | Rule (state) → Rule (multistate) | gap |
| `HAS_FACTOR` | Rule → Factor | gap |
| `HAS_LIMIT` | Coverage → Limit | gap |
| `INTRODUCES_FORM` | Filing → Form | gap |
| `INTRODUCES_MANUAL` | Filing → Manual | gap |
| `FILED_BY_CARRIER` | Filing → Carrier | gap (Phase 5) |
| `OBJECTS_TO` | Objection → Filing | gap |
| `ENACTED_BY` | Statute → State | gap (implicit in statute id) |

## 5. Status summary

At-a-glance: where each entity is, where it is going.

| # | Entity | Status | Where it lives now | Where it will live (Phase 4+) |
|---|---|---|---|---|
| 1 | Product (LOB) | ✅ | `products/` page + frontmatter | frontmatter (unchanged) + `products` table |
| 2 | State | ✅ | `states/` page + frontmatter | frontmatter (unchanged) + `states` table |
| 3 | Bureau | ✅ | `bureau:` frontmatter | `bureaus` lookup table |
| 4 | Form | ✅ | `forms/` page + frontmatter | frontmatter + `forms` + `form_states` tables |
| 5 | Product-State Binding | ✅ | `product-states/` directory | `product_states` table |
| 6 | Manual | ⚠️ | prose under `product-states/.../rating-rules/` | `manuals` table + prose |
| 7 | Coverage | ⚠️ | sparse `coverages/` pages + inline mentions | `coverages` table + prose |
| 8 | Clause | ⚠️ | `###` headings inside form pages | `clauses` table + prose body |
| 9 | Statute | ⚠️ | citation strings in frontmatter | `wiki/statutes/<id>.md` + `statutes` table |
| 10 | Limit / Deductible | ❌ | unstructured prose | `limits` table |
| 11 | Rating Rule | ❌ | unstructured prose | `rules` table |
| 12 | Rating Factor | ❌ | unstructured prose tables | `factors` table |
| 13 | Discount / Surcharge | ❌ | inline manual prose | `discounts` table |
| 14 | Filing | ❌ | `filings/` stub directory | `filings` table + per-filing page |
| 15 | Objection | ❌ | `objections/` stub directory | `objections` table + per-objection page |
| 16 | Carrier | ❌ | — | `wiki/carriers/<naic>.md` + `carriers` table (Phase 5) |
| 17 | Territory | ❌ (speculative) | — | `territories` table when first needed |
| 18 | Vehicle Class / Symbol | ❌ (speculative) | — | `vehicle_symbols` table when first needed |
| 19 | Driver Classification | ❌ | inline prose | rolled into `factors` or its own table |
| 20 | Loss Cost | ❌ (speculative) | — | `loss_costs` table when .xlsx ingest exists |
| 21 | Eligibility Rule | ❌ | inline prose | merged into `rules` table with `kind = "eligibility"` |

## 6. Gap-driven roadmap pointer

Each gap entity points to the phase that fills it. No new phases introduced here — pointers only.

| Gap | Filled by |
|---|---|
| Manual ID + version table | Phase 4 (structured store + relations) |
| Coverage as first-class | Phase 4 |
| Clause-level addressability | Phase 4 |
| Statute as first-class (`wiki/statutes/`) | Phase 4 |
| Limit / Deductible / Rating Rule / Rating Factor / Discount tables | Phase 4 |
| Filing + Objection lanes filled with real data | Phase 4 (lanes) + future ingest work |
| Carrier as first-class facet | Phase 5 |
| Territory / Vehicle Symbol / Loss Cost | Re-evaluate after Phase 4; only build when CQ demands it |

## 7. Verification

How to check this doc against reality:

1. **Coverage check**: every existing top-level wiki lane (`forms/`, `products/`, `states/`, `coverages/`, `product-states/`, `multistate/`, `filings/`, `objections/`, `product-specs/`, `comparisons/`, `concepts/`) maps to ≥1 entity here. ✅ confirmed at write time.
2. **CQ-question coverage**: 5 spot-check CQ questions (one per category) — every entity each presupposes is named. ✅ confirmed.
3. **Phase 4 readiness**: every relation predicate already used in frontmatter (`amends`, `citations`, `bureau`, `state`, `product`, `replaces`) appears in §4. ✅ confirmed.
4. **Phase 0 alignment**: at least one entity referenced by a Phase 0 chat scenario appears with status flagged. ✅ — Statute (s003), Clause (s001/s004), Carrier (s007), Manual (s002 t2/s006), Coverage (s002 t2), Discount (s006), Filing (s008).
5. **Single-pass scan**: a new reader can answer "what entities exist, what's modeled, what's not, where is each one stored" by reading §3 + §5 once.

## 8. Appendix — existing taxonomies (not redesigned here)

These are controlled vocabularies already in use across the wiki. Listed here for completeness; not part of the entity catalog.

| Vocabulary | Values | Where used |
|---|---|---|
| `cq_category` | `manuals`, `forms`, `filings`, `objections`, `product-spec`, `reference` | seed.yaml, frontmatter, evals |
| `role` | `pm`, `pds`, `actuary` | seed.yaml, `relevant_roles:` frontmatter |
| `type` (page kind) | `coverage`, `form`, `index`, `multistate`, `multistate-index`, `product`, `product-state`, `product-state-sub`, `state-meta`, `ontology` | frontmatter `type:` field; enforced by `tools/validate_frontmatter.py` |
| `bureau` | `aais` (others not yet represented) | form frontmatter |
| `scope` | `multistate`, `state-specific`, `base` | form frontmatter |

## 9. Maintenance notes

- This doc is the source of truth for entity naming. Code that references entity IDs (Phase 4 schema, Phase 1 agent tool names) should match the canonical IDs in §3.
- When a new ingest introduces an entity not in this list, add the entity entry in the same PR. Adding code without updating §3 is a process bug.
- When an entity moves from ⚠️ to ✅, update §3 and §5 in the same PR that lands the structured representation.
- When the Phase 4 schema lands, this doc gets a new appendix linking each entity to its DDL.
