# Insurance Wiki — Schema & Operation Instructions

This document defines the rules for all wiki operations. Claude Code reads this before any ingest, absorb, query, or cleanup operation.

---

## 1. Frontmatter Specification

Every wiki page **must** include YAML frontmatter. Required fields vary by page type.

### 1.1 Product Page (`wiki/products/{product}.md`)

```yaml
---
title: "Personal Automobile (PPA)"
type: product
product: auto-ppa
states_active: [AK, AL]        # states with filings in this wiki
last_updated: YYYY-MM-DD
---
```

### 1.2 State Meta Page (`wiki/states/{STATE}.md`)

```yaml
---
title: "Alaska — State Regulatory Metadata"
type: state-meta
state: AK
products_active: [auto-ppa, homeowners-hobp]
doi_name: "Alaska Division of Insurance"
statutory_refs: []             # list of key statutes referenced across products
last_updated: YYYY-MM-DD
---
```

### 1.3 Product-State Page (`wiki/product-states/{product}-{STATE}/{page}.md`)

```yaml
---
title: "Auto PPA — Alaska — Rating Rules"
type: product-state
product: auto-ppa
state: AK
page: rating-rules             # rating-rules | forms | endorsements | state-specifics
source_docs: []                # list of entry IDs that fed this page
version_current: "1.5"
version_history: ["1.0", "1.4", "1.5"]
effective_date: YYYY-MM-DD
last_updated: YYYY-MM-DD
---
```

### 1.4 Form Page (`wiki/forms/{FORM-ID}.md`)

```yaml
---
title: "PPA 0001 07 16 — Personal Automobile Policy"
type: form
form_id: PPA-0001-07-16
product: auto-ppa
scope: multistate              # multistate | state-specific
state: null                    # set if scope is state-specific
edition_date: "07 16"          # MM YY from form number
source_docs: []
last_updated: YYYY-MM-DD
---
```

### 1.5 Coverage Concept Page (`wiki/coverages/{coverage}.md`)

```yaml
---
title: "Uninsured Motorist Coverage"
type: coverage
coverage_id: uninsured-motorist
products: [auto-ppa]
states_with_variations: [AK, AL]
last_updated: YYYY-MM-DD
---
```

### 1.6 Concept / Terminology Page (`wiki/concepts/{concept}.md`)

```yaml
---
title: "Named Insured"
type: concept
concept_id: named-insured
products: [auto-ppa, homeowners-hobp, motor-truck-cargo]
last_updated: YYYY-MM-DD
---
```

### 1.7 Comparison Page (`wiki/comparisons/{id}.md`)

```yaml
---
title: "Auto PPA — Alaska vs Alabama"
type: comparison
comparison_type: state-vs-state    # state-vs-state | version-diff
product: auto-ppa
states: [AK, AL]                   # for state-vs-state
# OR:
state: AK                          # for version-diff
versions: ["1.4", "1.5"]           # for version-diff
source_docs: []
generated_date: YYYY-MM-DD
last_updated: YYYY-MM-DD
---
```

### 1.8 Wiki Entry (`wiki-entries/{id}.md`)

```yaml
---
entry_id: "2026-04-14_auto-ppa_AK_manual_v1.5"
source_file: "Vault Documents/Auto/AK/Manuals/PAU AK MAN-1.5 - Final.docx"
product: auto-ppa
state: AK
doc_type: manual               # manual | form | endorsement | filing-summary | doi-correspondence
version: "1.5"
supersedes: "1.4"              # set if this replaces a prior version
effective_date: YYYY-MM-DD
serff_tracking: ""
naic: ""
approval_status: ""            # approved | pending | withdrawn
approved_date: YYYY-MM-DD
ingested_date: YYYY-MM-DD
absorbed: false                # set to true after /wiki absorb completes
absorbed_date: null
wiki_pages_updated: []         # populated by /wiki absorb
---
```

---

## 2. Page Templates

### 2.1 Product Page Template

```markdown
---
[frontmatter]
---

# {Product Full Name}

Brief one-paragraph description of what this product is and who it covers.

## Coverage Parts

List the major coverage parts (e.g., Part A – Liability, Part B – Medical Payments).
For each: one sentence on what it covers.

## Active States

| State | Current Version | Effective Date | Status |
|---|---|---|---|
| AK | 1.5 | 2021-01-01 | Active |

## Key Forms

- [[PPA-0001-07-16]] — base policy form (multistate)
- [[PPA-0154-01-20]] — Alaska amendatory endorsement

## Related Pages

- [[coverages/uninsured-motorist]]
- [[coverages/physical-damage]]
```

### 2.2 State Meta Page Template

```markdown
---
[frontmatter]
---

# {STATE} — Regulatory Metadata

## Department of Insurance

Name, website if known.

## Active Products

| Product | Current Version | SERFF Tracking | Effective Date |
|---|---|---|---|
| auto-ppa | 1.5 | SRFF-... | 2021-01-01 |

## Key Statutes Referenced

List statutes that appear across product filings for this state.
Format: `{Statute ID} — {brief description}` (SOURCE: {entry-id})

## Filing History

Append-only table of filings processed into this wiki.

| Date Ingested | Product | Version | Doc Type | Entry ID |
|---|---|---|---|---|
```

### 2.3 Product-State Rating Rules Template

```markdown
---
[frontmatter]
---

# {Product} — {STATE} — Rating Rules

## Eligibility

Rules for who/what qualifies for coverage.
Cite each rule: (SOURCE: {entry-id} §{section})

## Coverage Options

### {Coverage Part Name}
- Available limits: ...
- Mandatory/optional: ...
- Stacking rules (if applicable): ...

## Mandatory Endorsements

List all endorsements required for this state.
Format: `{Form ID} — {description}` (SOURCE: {entry-id} §{section})

## Optional Endorsements

## Underwriting Rules

Key eligibility and risk classification rules.

## Surcharges & Discounts

Rules for rating modifications (NOT rate tables — structure only).

## State-Specific Requirements

What this state requires that differs from the multistate base.
Each item cites its statutory basis if known.

## Version History

| Version | Effective Date | Key Changes |
|---|---|---|
| 1.5 | 2021-01-01 | See [[comparisons/auto-ppa_AK_v1.4-vs-v1.5]] |
```

### 2.4 Version Diff Page Template

```markdown
---
[frontmatter]
---

# {Product} — {STATE} — v{old} vs v{new}

Effective date of new version: {date}
Source: [[wiki-entries/{new-entry-id}]]

## Summary of Changes

One-paragraph overview of what changed and why (if stated in the filing).

## Coverage Changes

### {Coverage Part}
- **Added:** ...
- **Removed:** ...
- **Modified:** ... (was: "X", now: "Y") (SOURCE: {entry-id} §{section})

## Endorsement Changes

## Eligibility / Underwriting Changes

## Rating Rule Changes

## Unchanged

Note any major areas explicitly confirmed unchanged.
```

---

## 3. Ingest Rules

`/wiki ingest [file-path]` reads a source document and produces a `wiki-entries/{id}.md` file.
**No wiki pages are modified during ingest.**

### 3.1 What to extract by document type

**Manual (.docx) — extract:**
- Eligibility rules
- Coverage options and available limits (not rate numbers)
- Mandatory and optional endorsements
- Underwriting rules
- Surcharge/discount structure and criteria (not amounts)
- State-specific requirements and statutory references
- Version number and effective date
- What this version supersedes

**Form (.docx) — extract:**
- All defined terms (from Definitions section)
- Coverage parts and what each covers
- Exclusions (complete list)
- Conditions (duties after loss, appraisal, etc.)
- Coverage triggers and limits language
- Form number, edition date

**Amendatory Endorsement (.docx) — extract:**
- Which base form it modifies
- Exact provisions added, deleted, or replaced
- Statutory basis for each change
- State and effective date

**Filing Summary (.pdf) — extract:**
- SERFF tracking number
- NAIC number
- Company name
- Program name
- Form numbers included
- Filing type
- Requested effective date
- Approval status and date
- Brief summary of what was filed

**DOI Correspondence (.pdf) — extract:**
- Date of correspondence
- Direction (inbound/outbound)
- Subject matter
- Any required changes or conditions on approval
- Final disposition

**Do NOT extract from any document:**
- Raw rate tables, base rates, relativity factors, or premium amounts
- Individual loss cost factors
- Specific dollar amounts from rate schedules

### 3.2 Entry ID format

`{YYYY-MM-DD}_{product}_{STATE}_{doc-type}_{version}`

Examples:
- `2026-04-14_auto-ppa_AK_manual_v1.5`
- `2026-04-14_auto-ppa_AK_form_PPA-0001`
- `2026-04-14_homeowners-hobp_FL_filing-summary`

### 3.3 After ingest

Append to `wiki/_log.md`:
```
[{date}] INGEST | {entry-id} | source: {source-file}
```

---

## 4. Absorb Rules

`/wiki absorb [entry-id]` reads a wiki entry and integrates it into wiki articles.
This is the intelligence step — synthesize, don't transcribe.

### 4.1 Process

1. Read the entry file
2. Check `_absorb_log.json` — if already absorbed, confirm with user before re-absorbing
3. Scan `_index.md` to identify existing pages this entry should update
4. For each relevant page:
   - If page exists: rewrite to incorporate new information, preserving and extending existing content
   - If page doesn't exist: create from the appropriate template
5. When `supersedes` is set in the entry frontmatter: create a comparison page if the prior version's page exists
6. Update `_index.md` with any new pages
7. Update `_backlinks.json` for any new wikilinks created
8. Update `_absorb_log.json`: mark entry as absorbed, list all pages touched
9. Append to `_log.md`

### 4.2 Pages typically touched per document type

| Doc type | Pages typically created/updated |
|---|---|
| Manual | product-states/{product}-{STATE}/rating-rules.md, product-states/{product}-{STATE}/endorsements.md, states/{STATE}.md, products/{product}.md |
| Form | forms/{FORM-ID}.md, product-states/{product}-{STATE}/forms.md |
| Endorsement | forms/{FORM-ID}.md, product-states/{product}-{STATE}/endorsements.md |
| Filing summary | states/{STATE}.md (filing history table) |

### 4.3 Anti-cramming rule

If a page exceeds ~100 lines of body content after absorption:
- Split off the bloated section into a focused sub-page
- Replace it with a summary + link to the sub-page
- Example: `product-states/auto-ppa-AK/rating-rules.md` splits into `rating-rules/uninsured-motorist.md`, `rating-rules/transportation-network.md`

### 4.4 Anti-thinning rule

Every page must have substance. If absorption would result in a page with fewer than 15 lines of body content, either:
- Merge it into a parent page with a section heading, or
- Continue building it — mark it as a stub in frontmatter with `stub: true`

### 4.5 Checkpoint

After every 15 entries absorbed in a session:
- Audit newly created pages for narrative coherence vs. raw-data dumps
- Rebuild `_index.md` entries for all touched pages
- Check that all new pages have required frontmatter
- Verify wikilinks resolve (no broken `[[links]]`)

### 4.6 After absorb

Append to `_log.md`:
```
[{date}] ABSORB | {entry-id} | pages updated: {count} | new pages: {list}
```

---

## 5. Query Rules

`/wiki query "<question>"` answers questions using compiled wiki knowledge.
**Read-only. Does not modify wiki pages unless explicitly instructed.**

### 5.1 Process

1. Scan `_index.md` for relevant article titles/descriptions
2. Check `_backlinks.json` for high-connectivity topics related to the question
3. Read 3–8 targeted wiki pages (not raw source docs)
4. Follow wikilinks 2–3 levels deep if needed
5. Synthesize answer with source citations in format: `(SOURCE: {entry-id} §{section})`
6. If the answer reveals a gap (important topic with no wiki page), note it

### 5.2 Citation format

Every factual claim in a query answer must be cited:
- Wiki page citation: `([[wiki/product-states/auto-ppa-AK/rating-rules]])`
- Source doc citation: `(SOURCE: 2026-04-14_auto-ppa_AK_manual_v1.5 §3.4)`

---

## 6. Cleanup Rules

`/wiki cleanup` audits the wiki for health issues.

### 6.1 Checks to run

- **Contradictions**: same rule stated differently on two pages for the same state/product
- **Orphan pages**: pages not linked from `_index.md` or any other page
- **Stale effective dates**: effective dates in the past with no newer version ingested
- **Missing frontmatter fields**: required YAML fields absent
- **Broken wikilinks**: `[[links]]` that point to non-existent pages
- **Concrete noun test**: scan all pages for entities mentioned 3+ times without their own page (people, forms, statutes, concepts) — flag as candidates for new pages
- **Stub pages**: pages marked `stub: true` that have been stubs for more than one ingest cycle

### 6.2 Output

Produce a `wiki/_cleanup_report_{date}.md` listing all issues found, categorized by severity:
- **Critical**: contradictions, broken links
- **Warning**: orphans, stale dates, missing frontmatter
- **Info**: stub pages, concrete noun candidates

Append to `_log.md`:
```
[{date}] CLEANUP | issues found: {count} | critical: {n} | warnings: {n}
```

---

## 7. Writing Standards

### Voice and tone

Write like an insurance compliance reference manual: flat, factual, precise.

**Avoid:**
- Editorial voice: "notably", "importantly", "interestingly"
- Peacock words: "comprehensive", "robust", "innovative"
- Progressive narrative: "would go on to", "eventually"
- Em dashes for decoration

**Use:**
- Active, declarative sentences
- Present tense for current rules, past tense for historical facts
- Exact form numbers, section references, and statutory citations

### Structure

Organize thematically, not chronologically. Section headers describe the topic, not the date.

- Wrong: `## March 2021 Update`
- Right: `## Transportation Network Coverage`

### Length targets

| Page type | Target length |
|---|---|
| Product overview | 40–60 lines |
| State meta | 20–40 lines |
| Product-state rating rules | 60–100 lines |
| Product-state forms | 40–80 lines |
| Form page | 40–80 lines |
| Coverage concept | 40–80 lines |
| Concept/terminology | 20–40 lines |
| Version diff | 30–60 lines |
| State comparison | 40–80 lines |

### Source citations

Every factual rule or provision stated in the wiki must end with a source citation:
```
Coverage must be offered at limits matching the liability limits. (SOURCE: 2026-04-14_auto-ppa_AK_manual_v1.5 §3.4)
```

---

## 8. Index and Log Formats

### `_index.md` entry format

```markdown
## Product-State Pages

- [[product-states/auto-ppa-AK/rating-rules]] — Auto PPA Alaska rating rules, eligibility, endorsements (v1.5, eff. 2021-01-01)
- [[product-states/auto-ppa-AK/forms]] — Auto PPA Alaska policy forms and endorsements
```

### `_log.md` entry format

```
[YYYY-MM-DD] {OPERATION} | {details}
```

Operations: `INIT`, `INGEST`, `ABSORB`, `QUERY`, `CLEANUP`

Never edit past log entries. Append only.
