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

Standard pages per entry type (from schema.md §4.2):

| doc_type | Pages to create/update |
|---|---|
| manual | `wiki/product-states/{product}-{STATE}/rating-rules.md`, `wiki/product-states/{product}-{STATE}/endorsements.md`, `wiki/states/{STATE}.md`, `wiki/products/{product}.md` |
| form | `wiki/forms/{FORM-ID}.md`, `wiki/product-states/{product}-{STATE}/forms.md` |
| endorsement | `wiki/forms/{FORM-ID}.md`, `wiki/product-states/{product}-{STATE}/endorsements.md` |
| filing-summary | `wiki/states/{STATE}.md` (filing history table only) |
| doi-correspondence | `wiki/states/{STATE}.md` (DOI correspondence section) |

Also check: do any coverage concepts mentioned deserve a `wiki/coverages/` page?
Do any terms defined in the entry lack a `wiki/concepts/` page?

If `supersedes` is set in the entry AND a prior version's page exists: create a version diff page at
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

**Anti-cramming** (schema.md §4.3):
If any page would exceed ~100 lines of body content after this absorption:
- Split the bloated section into a focused sub-page
- Replace with a summary + wikilink to the sub-page

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
