You are running `/wiki absorb` on the following entry (or set of entries):

$ARGUMENTS

If $ARGUMENTS is empty or "all", absorb all entries in `wiki-entries/` where `absorbed: false`.
Otherwise treat $ARGUMENTS as a single entry ID or file path.

This is the intelligence step. You synthesize knowledge from entries into wiki articles.
Read `schema.md` fully before proceeding — especially sections 4 (Absorb Rules) and 7 (Writing Standards).

---

## Step 1: Identify entries to absorb

Read the relevant entry file(s) from `wiki-entries/`. For each entry:
- Confirm `absorbed: false` — if already absorbed, skip and notify user
- Note the entry_id, product, state, doc_type, version, supersedes fields

---

## Step 2: For each entry, determine which wiki pages to create or update

Read `wiki/_index.md` to identify existing pages for this product/state.
Read `schema.md` sections 4.1–4.5 for scope-aware routing rules.

**Scope routing (from schema.md §4.1):**

| Entry scope | Target pages |
|---|---|
| `multistate` | `wiki/multistate/{product}/` — rating-rules index + sub-pages, endorsements |
| `state-specific` | `wiki/product-states/{product}-{STATE}/` — differences from multistate only |

**For state-specific manuals:**
Before writing any rule, check `wiki/multistate/{product}/` for the same rule.
- If multistate page exists and rule is unchanged: note in deviations table as `[multistate, unchanged]`, do NOT write full rule body
- If multistate page does not exist yet: write the full rule body and flag it as scope TBD
- If rule differs from multistate: write AK version labeled `[multistate override]`
- If rule is AK-only (no multistate equivalent): write full body labeled `[AK-specific]`

**Rating rules always split into sub-pages (schema.md §4.3):**
- `rating-rules.md` — index + deviations table
- `rating-rules/coverage-options.md`
- `rating-rules/driving-record-points.md`
- `rating-rules/state-specifics.md`

**Standard pages per entry type:**

| doc_type / scope | Pages created/updated |
|---|---|
| manual / multistate | `wiki/multistate/{product}/rating-rules.md` + sub-pages, `wiki/products/{product}.md` |
| manual / state-specific | `wiki/product-states/{product}-{STATE}/rating-rules.md` + sub-pages, `wiki/states/{STATE}.md`, `wiki/products/{product}.md` |
| form | `wiki/forms/{FORM-ID}.md` |
| endorsement | `wiki/forms/{FORM-ID}.md`, `wiki/product-states/{product}-{STATE}/endorsements.md` |
| filing-summary | `wiki/states/{STATE}.md` (effective date, SERFF, filing history) |
| doi-correspondence | `wiki/states/{STATE}.md` (DOI section) |

Also check: do any coverage concepts deserve a `wiki/coverages/` page?
Do any terms defined in the entry lack a `wiki/concepts/` page?

If `supersedes` is set AND a prior version's page exists: create a version diff page at
`wiki/comparisons/{product}_{STATE}_v{old}-vs-v{new}.md`

---

## Step 3: Write or update each page

For each page:

**If the page does not exist**: create it using the appropriate template from schema.md §2.
Set frontmatter fields including `source_docs: ["{entry-id}"]`.

**If the page exists**: read it, then rewrite it to incorporate the new entry's content.
- Preserve and extend existing content — do not discard prior knowledge
- Add new information in the appropriate thematic section
- Update version fields in frontmatter if this is a newer version
- Add the entry_id to the `source_docs` list

**Writing standard** (schema.md §7):
- Wikipedia-style: flat, factual, precise
- Thematic organization — not chronological
- Every factual rule or provision ends with: `(SOURCE: {entry-id} §{section-if-known})`
- No editorial voice, no peacock words

**No broken wikilinks** (schema.md §4.4):
Before writing any `[[wikilink]]`, verify the target file exists on disk.
If it does not exist, write as plain text with note `(page not yet created)` instead of a wikilink.

**Anti-cramming** (schema.md §4.3):
Rating rules always go into sub-pages — never into a single file.
For other page types: if body exceeds ~100 lines, split into focused sub-pages.

**Anti-thinning** (schema.md §4.4):
Every page must have at least 15 lines of body content. No stubs without `stub: true` in frontmatter.

---

## Step 4: Update system files

**`wiki/_index.md`**: Add or update entries for every page created or materially changed.
Format: `- [[{relative path without .md}]] — {one-line description} ({version if applicable}, eff. {date})`

**`wiki/_backlinks.json`**: For every new `[[wikilink]]` added to any page, add a reverse mapping:
```json
{
  "target-page": ["source-page-1", "source-page-2"]
}
```
Read the current file and merge — do not overwrite existing entries.

**`wiki/_absorb_log.json`**: Mark the entry as absorbed:
```json
{
  "{entry-id}": {
    "absorbed_date": "{today YYYY-MM-DD}",
    "wiki_pages_updated": ["{page1}", "{page2}"]
  }
}
```

**Entry file**: Update frontmatter in `wiki-entries/{entry-id}.md`:
- Set `absorbed: true`
- Set `absorbed_date: {today}`
- Set `wiki_pages_updated: [list of pages]`

---

## Step 5: Checkpoint (every 15 entries)

After every 15 entries absorbed in a single session:
- Audit 3 randomly selected new pages: are they thematic articles or raw-data dumps?
- Verify all new pages have required frontmatter fields
- Check that all `[[wikilinks]]` resolve to existing pages
- Rebuild `_index.md` section for all pages touched in this session

---

## Step 6: Handle version diffs

If the entry has `supersedes` set and the prior version's page exists:

Create `wiki/comparisons/{product}_{STATE}_v{old}-vs-v{new}.md` using the comparison template (schema.md §2.4):
- Organize changes thematically (Coverage Changes, Endorsement Changes, Underwriting Changes, etc.)
- For each changed item: state what it was and what it became, cite source
- Note areas explicitly confirmed unchanged

---

## Step 7: Append to operation log

Append to `wiki/_log.md`:
```
[{today YYYY-MM-DD}] ABSORB | {entry-id} | pages updated: {count} | new pages: {comma-separated list}
```

---

## Step 8: Report to user

Summarize:
- Entry absorbed
- Pages created (list)
- Pages updated (list)
- Version diff page created (if applicable)
- Any anti-cramming splits performed
- Any gaps flagged (topics mentioned but no wiki page exists)
- Any contradictions detected with existing wiki content
