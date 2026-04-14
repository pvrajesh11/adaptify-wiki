# Insurance Wiki — Schema & Operation Instructions

This document defines the rules for all wiki operations. Claude Code reads this before any ingest, absorb, query, or cleanup operation.

---

## 0. Core Design Principles

### Multistate Base + State Diff Model

Insurance manuals come in two layers:
- **Multistate base** (`MULTI` in filename) — rules that apply across all states by default
- **State manual** (state code in filename, e.g. `AK MAN`) — rules that override or extend the multistate base for a specific state

**Wiki structure mirrors this:**
```
wiki/multistate/{product}/     ← compiled from MULTI manuals
wiki/product-states/{product}-{STATE}/  ← only what DIFFERS from multistate base
```

A state page documents: (a) explicit overrides stated in the state manual, (b) rules the state manual says "do not apply", and (c) state-specific additions not in the multistate base. If a rule is identical to the multistate base, it is NOT repeated on the state page — instead link to `[[multistate/{product}/...]]`.

**Ingest order matters:** Always ingest the MULTI manual before the state manual. The absorb step for state manuals requires the multistate pages to exist.

### No Broken Wikilinks

Before writing any `[[wikilink]]` in any page, verify the target page exists on disk. If the target does not yet exist, write the reference as plain text with a note `(page not yet created)` rather than as a wikilink. This keeps the wiki navigable at all times.

### Rating Rules Sub-Pages

The `product-states/{product}-{STATE}/rating-rules.md` file is an **index page** that links to sub-pages. Content is split as follows:

```
rating-rules.md                  ← index: list of sub-pages + brief summary of each
rating-rules/coverage-options.md ← all coverage parts, UM/UIM rules, FPB, tort options
rating-rules/driving-record-points.md ← point assignment structure, exceptions
rating-rules/state-specifics.md  ← state-specific carve-outs, special vehicles, TNP
```

Apply the same sub-page pattern to multistate pages when they exceed ~100 lines.

---

## 1. Frontmatter Specification

Every wiki page **must** include YAML frontmatter. Required fields vary by page type.

### 1.1 Product Page (`wiki/products/{product}.md`)

```yaml
---
title: "Personal Automobile (PPA)"
type: product
product: auto-ppa
states_active: [AK, AL]
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
statutory_refs: []
last_updated: YYYY-MM-DD
---
```

### 1.3 Multistate Base Page (`wiki/multistate/{product}/{page}.md`)

```yaml
---
title: "Auto PPA — Multistate — Coverage Options"
type: multistate
product: auto-ppa
page: coverage-options           # rating-rules | coverage-options | driving-record-points | endorsements
source_docs: []                  # MULTI manual entry IDs
version_current: "01 21"
last_updated: YYYY-MM-DD
---
```

### 1.4 Product-State Index Page (`wiki/product-states/{product}-{STATE}/rating-rules.md`)

```yaml
---
title: "Auto PPA — Alaska — Rating Rules"
type: product-state
product: auto-ppa
state: AK
page: rating-rules
multistate_base: "multistate/auto-ppa"   # which multistate base this extends
source_docs: []
version_current: "1.5"
version_history: ["1.5"]
effective_date: YYYY-MM-DD               # from filing summary, not manual
last_updated: YYYY-MM-DD
---
```

### 1.5 Rating Rules Sub-Page (`wiki/product-states/{product}-{STATE}/rating-rules/{sub}.md`)

```yaml
---
title: "Auto PPA — Alaska — Driving Record Points"
type: product-state-sub
product: auto-ppa
state: AK
parent: rating-rules
sub: driving-record-points       # coverage-options | driving-record-points | state-specifics
source_docs: []
scope_notes: ""                  # e.g. "AK-specific" or "Multistate rule, applies in AK unchanged"
last_updated: YYYY-MM-DD
---
```

### 1.6 Product-State Endorsements Page (`wiki/product-states/{product}-{STATE}/endorsements.md`)

```yaml
---
title: "Auto PPA — Alaska — Endorsements"
type: product-state
product: auto-ppa
state: AK
page: endorsements
source_docs: []
version_current: "1.5"
last_updated: YYYY-MM-DD
---
```

### 1.7 Form Page (`wiki/forms/{FORM-ID}.md`)

```yaml
---
title: "PPA 0001 07 16 — Personal Automobile Policy"
type: form
form_id: PPA-0001-07-16
product: auto-ppa
scope: multistate
state: null
edition_date: "07 16"
source_docs: []
last_updated: YYYY-MM-DD
---
```

### 1.8 Coverage Concept Page (`wiki/coverages/{coverage}.md`)

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

### 1.9 Concept / Terminology Page (`wiki/concepts/{concept}.md`)

```yaml
---
title: "Named Insured"
type: concept
concept_id: named-insured
products: [auto-ppa, homeowners-hobp, motor-truck-cargo]
last_updated: YYYY-MM-DD
---
```

### 1.10 Comparison Page (`wiki/comparisons/{id}.md`)

```yaml
---
title: "Auto PPA — Alaska vs Alabama"
type: comparison
comparison_type: state-vs-state    # state-vs-state | version-diff
product: auto-ppa
states: [AK, AL]
# OR for version-diff:
state: AK
versions: ["1.4", "1.5"]
source_docs: []
generated_date: YYYY-MM-DD
last_updated: YYYY-MM-DD
---
```

### 1.11 Wiki Entry (`wiki-entries/{id}.md`)

```yaml
---
entry_id: "2026-04-14_auto-ppa_AK_manual_v1.5"
source_file: "Vault Documents/Auto/AK/Manuals/PAU AK MAN-1.5 - Final.docx"
product: auto-ppa
state: AK                          # "MULTI" for multistate manuals
doc_type: manual
scope: state-specific              # multistate | state-specific
version: "1.5"
supersedes: "1.4"
effective_date: YYYY-MM-DD
serff_tracking: ""
naic: ""
approval_status: ""
approved_date: YYYY-MM-DD
ingested_date: YYYY-MM-DD
absorbed: false
absorbed_date: null
wiki_pages_updated: []
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

One paragraph description of what this product covers and who it's for.

## Coverage Parts

| Coverage | Description |
|---|---|
| Liability | ... |
| Medical Payments | ... |
| ...  | ... |

## Active States

| State | Version | Effective Date | Status |
|---|---|---|---|
| AK | 1.5 | 2021-01-01 | Active |

## Multistate Base

See multistate/auto-ppa/ (link only if page exists) for rules that apply by default across all states.

## State Pages

- [[product-states/auto-ppa-AK/rating-rules]] — Alaska
```

### 2.2 Multistate Base Page Template

```markdown
---
[frontmatter]
---

# {Product} — Multistate — {Page Topic}

Source: {MULTI manual entry ID}

> These rules apply in all states unless explicitly overridden in a state manual.
> State-specific overrides are documented in the relevant product-state page.

## {Section}

{Content}

Each rule labeled: `[multistate]` where ambiguity is possible.
```

### 2.3 Product-State Rating Rules Index Template

```markdown
---
[frontmatter]
---

# {Product} — {STATE} — Rating Rules

Multistate base: [[multistate/{product}/rating-rules]] (if exists)
State manual: {manual filename and version}
Effective date: {from filing summary}
See also: [[product-states/{product}-{STATE}/endorsements]] | [[states/{STATE}]]

## Sub-Pages

- [[rating-rules/coverage-options]] — coverage availability, UM/UIM, FPB, tort options
- [[rating-rules/driving-record-points]] — point structure, exceptions
- [[rating-rules/state-specifics]] — state-specific rules, TNP, special vehicles

## State Deviations from Multistate Base

Summary table of where AK differs from the multistate base:

| Topic | Multistate Rule | AK Override |
|---|---|---|
| Intra-Family Exclusion | Applies | Does not apply |
| Financial Responsibility Filing | Applies | Does not apply |
| UM/UIM | Optional offering | Mandatory offering (written rejection required) |

## Version History

| Version | Effective Date | Key Changes |
|---|---|---|
| 1.5 | TBD | First ingested version |
```

### 2.4 Rating Rules Sub-Page: Coverage Options

```markdown
---
[frontmatter]
---

# {Product} — {STATE} — Coverage Options

Parent: [[product-states/{product}-{STATE}/rating-rules]]

## Policy Form

## Uninsured Motorist Coverage
[AK-specific or multistate label on each rule]

## Underinsured Motorist Coverage

## First Party Benefits

## Tort Options
```

### 2.5 Rating Rules Sub-Page: Driving Record Points

```markdown
---
[frontmatter]
---

# {Product} — {STATE} — Driving Record Points

Parent: [[product-states/{product}-{STATE}/rating-rules]]

> Scope: [multistate base | AK-specific override — note which applies]

## Experience Period

## Point Assignment Triggers

## Point Structure Table

## Additional Points

## Exceptions (Points NOT Assigned For)
```

### 2.6 Rating Rules Sub-Page: State Specifics

```markdown
---
[frontmatter]
---

# {Product} — {STATE} — State-Specific Rules

Parent: [[product-states/{product}-{STATE}/rating-rules]]

Rules in this page are AK-specific and have no multistate equivalent,
OR are multistate rules that do not apply in AK.

## Rules That Do Not Apply

## State-Specific Additions

## Special Vehicle Classes

## Transportation Network Coverage
```

### 2.7 Endorsements Page Template

(unchanged — table format is working well)

### 2.8 State Meta Page Template

(unchanged)

### 2.9 Version Diff Page Template

```markdown
---
[frontmatter]
---

# {Product} — {STATE} — v{old} vs v{new}

Effective date of new version: {date}
Source: {new-entry-id}

## Summary of Changes

## Coverage Changes

## Endorsement Changes

## Underwriting / Rating Rule Changes

## Rules Added or Removed

## Unchanged Areas
```

---

## 3. Ingest Rules

`/wiki ingest [file-path]` reads a source document and produces a `wiki-entries/` file.
**No wiki pages are modified during ingest — only a `wiki-entries/` file is created.**

### 3.1 Determine Scope from Filename

| Filename pattern | `scope` | `state` |
|---|---|---|
| Contains `MULTI` | `multistate` | `MULTI` |
| Contains state code (e.g. `AK`, `AL`) | `state-specific` | `{STATE}` |

### 3.2 What to Extract by Document Type

**Manual (.docx) — extract:**
- Eligibility rules
- Coverage options and available limits (rules only, not rate numbers)
- Mandatory and optional endorsements with form numbers
- Underwriting rules and risk classification criteria
- Surcharge/discount structure and criteria (not amounts or factors)
- State-specific requirements and statutory references
- What this version supersedes (if stated)
- Effective date (if stated — usually not; use filing summary)
- For each rule: note whether it is labeled "multistate" or "state-specific" in the source

**Form (.docx) — extract:**
- All defined terms (term + definition)
- Coverage parts: name, what it covers, triggers, key limits language
- Exclusions (complete list)
- Conditions (duties after loss, appraisal, cancellation, etc.)
- Form number and edition date

**Amendatory Endorsement (.docx) — extract:**
- Which base form it modifies
- Each provision added, deleted, or replaced
- Statutory basis for each change
- State and effective date

**Filing Summary (.pdf) — extract:**
- SERFF tracking number
- NAIC number
- Company name
- Program name
- Form numbers included
- Filing type
- Requested effective date ← **this is the authoritative effective date**
- Approval status and date

**Rate Table (.xlsx) — SKIP:**
Rate table files are not ingested. Inform user: "Rate table files (.xlsx) are excluded per schema. Skipping."

**DOI Correspondence (.pdf) — extract:**
- Date, direction, subject, required changes, disposition

### 3.3 Ingest Order (Required)

For each state/product combination, ingest in this order:
1. Filing summary PDF first (establishes effective date and SERFF metadata)
2. MULTI manual (establishes multistate base)
3. State manual (establishes state-specific overrides)
4. Base form(s)
5. Amendatory endorsement(s)
6. DOI correspondence last

### 3.4 Entry ID Format

- State-specific: `{YYYY-MM-DD}_{product}_{STATE}_{doc-type}_{version}`
- Multistate: `{YYYY-MM-DD}_{product}_MULTI_{doc-type}_{version}`

### 3.5 After Ingest

Append to `wiki/_log.md`:
```
[{date}] INGEST | {entry-id} | source: {basename} | scope: {multistate|state-specific}
```

---

## 4. Absorb Rules

`/wiki absorb [entry-id or "all"]` integrates entries into wiki articles.

### 4.1 Scope-Aware Routing

| Entry scope | Target pages |
|---|---|
| `multistate` | `wiki/multistate/{product}/` pages |
| `state-specific` | `wiki/product-states/{product}-{STATE}/` pages (differences only) |

**For state-specific manuals:** Before writing any rule to a state page, check if the same rule exists in `wiki/multistate/{product}/`. If it does and is unchanged in AK, do NOT repeat it on the state page. Instead note it in the "State Deviations" summary table as "same as multistate". Only write rules that differ, are absent from multistate, or are explicitly noted as not applying.

### 4.2 Pages Touched per Document Type

| doc_type / scope | Pages created/updated |
|---|---|
| manual / multistate | `wiki/multistate/{product}/rating-rules.md` and sub-pages, `wiki/products/{product}.md` |
| manual / state-specific | `wiki/product-states/{product}-{STATE}/rating-rules.md` (index) and sub-pages, `wiki/states/{STATE}.md`, `wiki/products/{product}.md` |
| form | `wiki/forms/{FORM-ID}.md` |
| endorsement | `wiki/forms/{FORM-ID}.md`, `wiki/product-states/{product}-{STATE}/endorsements.md` |
| filing-summary | `wiki/states/{STATE}.md` (effective date, SERFF, filing history) |
| doi-correspondence | `wiki/states/{STATE}.md` (DOI section) |

### 4.3 Rating Rules Sub-Page Split (Always Apply)

When absorbing a manual (multistate or state-specific), always split rating rules into sub-pages:
- `rating-rules.md` — index page + state deviations table
- `rating-rules/coverage-options.md` — coverage parts, UM/UIM, FPB, tort options
- `rating-rules/driving-record-points.md` — point structure, exceptions
- `rating-rules/state-specifics.md` — rules not applying, state additions, TNP, special vehicles

Never write all rating rule content into a single `rating-rules.md` file.

### 4.4 No Broken Wikilinks Rule

Before writing any `[[wikilink]]`:
1. Check if the target file exists on disk
2. If yes: write as `[[path/to/page]]`
3. If no: write as plain text with note `(page not yet created)` — do NOT create a wikilink

### 4.5 Scope Labels on Rules

Each extracted rule in a state page must be labeled with its scope:
- `[AK-specific]` — only exists in the AK manual, no multistate equivalent
- `[multistate, unchanged]` — same as multistate base; note only in deviations table, don't repeat body
- `[multistate override]` — differs from multistate base; write the AK version and note what changed

### 4.6 Anti-Cramming and Anti-Thinning

Anti-cramming: No single page body exceeds ~100 lines. Split per §4.3 pattern.
Anti-thinning: Every page must have at least 15 lines of body content. Merge stubs into parent pages.

### 4.7 After Absorb

Update: `_index.md`, `_backlinks.json`, `_absorb_log.json`, entry frontmatter, `_log.md`.

---

## 5. Query Rules

`/wiki query "<question>"` — read-only.

1. Scan `_index.md` for relevant pages
2. Check `_backlinks.json` for high-connectivity topics
3. Read 3–8 targeted pages; follow wikilinks 2–3 levels deep
4. For state-specific questions: read both the state page AND the multistate base page, since state pages only document differences
5. Synthesize with citations: `(SOURCE: {entry-id} §{section})`
6. Flag gaps: topics not yet in wiki

---

## 6. Cleanup Rules

`/wiki cleanup` audits the wiki.

Checks: contradictions, broken wikilinks, orphan pages, stale effective dates,
missing frontmatter, unabsorbed entries, concrete noun test, stub pages, anti-cramming candidates.

**Additional check for multistate model:**
- State pages that repeat rules verbatim from the multistate base (should be removed — link instead)
- State pages that don't have a corresponding multistate base page (ingest order violation)

Produces: `wiki/_cleanup_report_{date}.md`

---

## 7. Writing Standards

Wikipedia-style: flat, factual, precise. No editorial voice.

Every rule ends with source citation: `(SOURCE: {entry-id} §{section})`

Scope labels on every rule in state pages: `[AK-specific]`, `[multistate, unchanged]`, `[multistate override]`.

Thematic organization — not chronological.

### Length Targets

| Page type | Target |
|---|---|
| Product overview | 40–60 lines |
| Multistate base sub-page | 40–80 lines |
| State meta | 20–40 lines |
| Rating rules index | 20–40 lines |
| Rating rules sub-page | 40–80 lines |
| Endorsements | 40–80 lines |
| Form page | 40–80 lines |
| Coverage concept | 40–80 lines |
| Version diff | 30–60 lines |
| State comparison | 40–80 lines |

---

## 8. System File Formats

### `_index.md` Entry Format
```
- [[path/to/page]] — one-line description (version, eff. date if applicable)
```
Only list pages that actually exist on disk.

### `_log.md` Entry Format
```
[YYYY-MM-DD] {OPERATION} | {details}
```
Operations: `INIT`, `INGEST`, `ABSORB`, `QUERY`, `CLEANUP`
Append only — never edit past entries.
