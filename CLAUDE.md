# adaptify-wiki — Claude Instructions

## What this repo is

An LLM-maintained insurance product knowledge wiki covering all 50 states and multiple product lines.
Built on the Karpathy + Farzaa wiki pattern: raw sources are ingested into structured markdown pages that compile knowledge once and keep it current.

## Source documents (read-only, NOT in this repo)

```
~/claude/adaptify/Vault Documents/
  Auto/         → Personal Automobile (PPA) filings by state
  Homeowners/   → Homeowners (HOBP) filings by state
  FL/           → Florida Homeowners filings
  Motor Truck Cargo/ → MTC filings by state
```

Each state folder has three subfolders:
- `Forms/` — policy forms and amendatory endorsements (.docx)
- `Manuals/` — underwriting/rating manuals (.docx) and rate tables (.xlsx)
- `Supporting Documents/` — DOI correspondence and filing summaries (.pdf)

**Never modify files in Vault Documents. They are the immutable source of truth.**

## Repo structure

```
wiki-entries/     # Step 1: One .md per source document (ingest output)
wiki/
  _index.md       # Master article catalog — update on every wiki change
  _log.md         # Append-only operation log — never edit past entries
  _backlinks.json # Reverse link map — rebuilt by /wiki cleanup
  _absorb_log.json # Tracks which source docs fed which wiki pages
  products/       # Product line overview pages
  states/         # State regulatory metadata pages
  product-states/ # Intersection pages (most content lives here)
  coverages/      # Cross-cutting coverage concept pages
  forms/          # Individual form reference pages
  concepts/       # Insurance terminology pages
  comparisons/    # State vs state, version vs version diff pages
```

## Core rules

1. **Every wiki page must have YAML frontmatter** — see schema.md for required fields per page type
2. **Every factual claim must cite its source** — format: `(SOURCE: {doc-id} §{section})`
3. **Never modify source documents** in Vault Documents
4. **`_log.md` is append-only** — never edit or delete past log entries
5. **`_index.md` must be updated** every time a wiki page is created or materially changed
6. **Writing standard**: Wikipedia-style — flat, factual, precise. No editorial voice.
7. **Anti-cramming**: when a page exceeds ~100 lines of content, split into focused sub-pages
8. **Anti-thinning**: every page must have substance. Stubs with fewer than 15 lines are failures.

## Operations

See `schema.md` for full instructions on each operation:

- `/wiki ingest [file-path]` — convert source doc to a structured wiki-entry
- `/wiki absorb [entry-id]` — integrate entry into wiki articles
- `/wiki query "<question>"` — answer questions using the wiki
- `/wiki cleanup` — health check: contradictions, orphans, stale dates, missing pages

## Product line codes

| Code | Full name |
|---|---|
| `auto-ppa` | Personal Automobile (PPA) |
| `homeowners-hobp` | Homeowners (HOBP) |
| `motor-truck-cargo` | Motor Truck Cargo (MTC) |

## State codes

Standard two-letter USPS abbreviations (AK, AL, FL, ...).
