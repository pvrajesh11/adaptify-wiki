You are running `/wiki ingest` on the following source document:

$ARGUMENTS

Your job is to read the source document and produce a structured wiki entry file. No wiki pages are modified during ingest — only a `wiki-entries/` file is created.

---

## Step 1: Parse the file path

From the path `$ARGUMENTS`, determine:

- **product**: look at the folder name
  - `Auto/` → `auto-ppa`
  - `Homeowners/` or `FL/` → `homeowners-hobp`
  - `Motor Truck Cargo/` → `motor-truck-cargo`
- **state**: 2-letter folder name under the product (AK, AL, FL, etc.)
- **doc_type**: from the subfolder and filename:
  - `Forms/` folder + base policy filename (e.g. `PPA 0001`, `HO 0003`, `CIM 7002`) → `form`
  - `Forms/` folder + amendatory/endorsement filename → `endorsement`
  - `Manuals/` folder + `.docx` file → `manual`
  - `Manuals/` folder + `.xlsx` file → `rate-table` (skip — do not ingest rate tables)
  - `Supporting Documents/` + `FilingSummary` → `filing-summary`
  - `Supporting Documents/` + `DOI_Correspondence` → `doi-correspondence`
- **version**: extract from filename if present (e.g. `MAN-1.5` → `1.5`, `v7` → `7`, `V.11` → `11`). If no version in filename, use the edition date from the form number (e.g. `07 16` from `PPA 0001 07 16`).
- **form_id**: for forms and endorsements, extract the form number (e.g. `PPA 0001 07 16`, `HO 0854 02 21`)

If doc_type is `rate-table`, stop and inform the user: "Rate table files (.xlsx) are not ingested — they contain raw rating numbers excluded from the wiki per schema.md. Skipping."

---

## Step 2: Read the source document

Use the Read tool to read the full content of `$ARGUMENTS`.

---

## Step 3: Extract content per document type

Read `schema.md` section 3.1 for the full extraction rules. Summary:

**If doc_type = `manual`**, extract:
- Eligibility rules (who/what qualifies)
- Coverage options and available limits (rules only, not rate numbers)
- Mandatory endorsements required for this state
- Optional endorsements available
- Underwriting rules and risk classification criteria
- Surcharge and discount structure and criteria (not amounts or factors)
- State-specific requirements and statutory references (cite statute IDs)
- What version this supersedes (if stated)
- Effective date

**If doc_type = `form`**, extract:
- All defined terms from the Definitions section (term + definition)
- Coverage parts: name, what it covers, triggers, key limits language
- Complete exclusions list
- Conditions (duties after loss, appraisal, cancellation, etc.)
- Form number and edition date

**If doc_type = `endorsement`**, extract:
- Which base form this modifies
- Each provision: what it adds, deletes, or replaces in the base form
- Statutory basis for each change (if stated)
- State and effective date

**If doc_type = `filing-summary`**, extract:
- SERFF tracking number
- NAIC number
- Company name
- Program name and description
- Form numbers included in the filing
- Filing type (Forms / Rules / Rates)
- Requested effective date
- Approval status and approved date
- Summary of what was filed

**If doc_type = `doi-correspondence`**, extract:
- Date
- Direction: inbound (DOI to company) or outbound (company to DOI)
- Subject matter
- Any required changes or conditions imposed by DOI
- Final disposition

**Do NOT extract**: raw rate tables, base rates, relativity factors, loss cost factors, or specific dollar amounts from rate schedules.

---

## Step 4: Generate the entry ID

Format: `{YYYY-MM-DD}_{product}_{STATE}_{doc-type}_{version}`

Use today's date. Examples:
- `2026-04-14_auto-ppa_AK_manual_v1.5`
- `2026-04-14_homeowners-hobp_AK_form_PPA-0001-07-16`
- `2026-04-14_motor-truck-cargo_AL_endorsement_CIM-2001-08-15`
- `2026-04-14_auto-ppa_AK_filing-summary`

---

## Step 5: Write the wiki entry file

Write to `wiki-entries/{entry-id}.md` with this structure:

```
---
entry_id: "{entry-id}"
source_file: "{relative path from repo root}"
product: {product}
state: {STATE}
doc_type: {doc_type}
version: "{version}"
supersedes: "{prior version or null}"
form_id: "{form number or null}"
effective_date: {YYYY-MM-DD or null}
serff_tracking: "{number or empty}"
naic: "{number or empty}"
approval_status: "{approved|pending|withdrawn|empty}"
approved_date: {YYYY-MM-DD or null}
ingested_date: {today YYYY-MM-DD}
absorbed: false
absorbed_date: null
wiki_pages_updated: []
---

# {Descriptive title}

## Source Document Summary

One paragraph describing what this document is and its scope.

## Extracted Content

[All extracted content, organized under clear headings matching the extraction rules above.
Every item of substance is preserved. Write in clear prose or structured lists.
Do not summarize away detail — the absorb step needs the full content.]

## Key Differences from Prior Version

[If supersedes is set: list what appears to be new or changed vs. what a prior version would contain.
If this is a first version or no prior version is known: write "First known version."]

## Metadata Notes

[Any unusual aspects of this document, filing notes, or context worth flagging.]
```

---

## Step 6: Update the operation log

Append this line to `wiki/_log.md`:

```
[{today YYYY-MM-DD}] INGEST | {entry-id} | source: {source file basename} | doc_type: {doc_type} | state: {STATE} | product: {product}
```

---

## Step 7: Confirm to the user

Report:
- Entry ID created
- File written to wiki-entries/
- doc_type, product, state, version extracted
- Whether `supersedes` was detected (triggers a version diff in absorb)
- Any gaps or ambiguities encountered during extraction
