You are running `/wiki cleanup` to audit the health of the insurance wiki.

$ARGUMENTS

If $ARGUMENTS specifies a scope (e.g., a product or state), limit the audit to that scope.
Otherwise audit the entire wiki.

Read `schema.md` section 6 (Cleanup Rules) before proceeding.
This operation is read-only except for writing the cleanup report file.

---

## Step 1: Inventory all wiki pages

Read `wiki/index.md` to get the full list of pages.
Then verify each listed page actually exists on disk.

---

## Step 2: Run all health checks

For each wiki page found, check:

### A. Contradictions (Critical)
Compare pages that cover the same product/state/topic. Flag if:
- The same rule is stated differently on two pages
- A coverage limit or rule conflicts between a product-state page and a coverage concept page
- An endorsement is listed as mandatory on one page but optional on another

### B. Broken wikilinks (Critical)
Scan all pages for `[[wikilinks]]`. For each link, verify the target page exists.
List all broken links with: source page → broken link target.

### C. Missing frontmatter fields (Warning)
Check each page's YAML frontmatter against the required fields in schema.md §1 for its page type.
List any missing required fields.

### D. Orphan pages (Warning)
Pages not referenced in `_index.md` AND not linked from any other page.
Cross-reference `wiki/_backlinks.json` — pages with no backlinks are orphan candidates.

### E. Stale effective dates (Warning)
Pages where `effective_date` in frontmatter is in the past AND `version_current` has not been updated
since the last ingest. Flag as potentially stale.

### F. Absorbed entries with no wiki pages (Warning)
Read `wiki/_absorb_log.json`. Check if any entry shows `wiki_pages_updated: []` — absorbed but produced no pages.

### G. Unabsorbed entries (Info)
Read all files in `wiki-entries/` where `absorbed: false`. List them — these are waiting for `/wiki absorb`.

### H. Concrete noun test (Info)
Scan all wiki pages for entities mentioned 3 or more times that do not have their own wiki page:
- Form numbers (e.g., `PPA 0154`) mentioned frequently but no `wiki/forms/PPA-0154.md`
- Coverage types mentioned frequently but no `wiki/coverages/` page
- Insurance concepts (terms, conditions) mentioned frequently but no `wiki/concepts/` page
- State statutes referenced frequently but not documented in the state's meta page

Rank candidates by mention frequency.

### I. Stub pages (Info)
Pages with `stub: true` in frontmatter. List them — they need more content.

### J. Anti-cramming check (Info)
Pages with body content exceeding ~100 lines. Flag for potential splitting.

---

## Step 3: Write the cleanup report

Write `wiki/_cleanup_report_{YYYY-MM-DD}.md`:

```markdown
---
type: cleanup-report
generated: {YYYY-MM-DD}
scope: {full | product | state}
total_pages_audited: {n}
critical_issues: {n}
warning_issues: {n}
info_items: {n}
---

# Wiki Cleanup Report — {YYYY-MM-DD}

## Critical Issues

### Contradictions
{list each contradiction: page A vs page B, the conflicting statements}

### Broken Wikilinks
{list each: source page → broken link}

## Warnings

### Missing Frontmatter Fields
{list each: page → missing fields}

### Orphan Pages
{list each page with no inbound links}

### Stale Effective Dates
{list each page with potentially stale content}

### Absorbed Entries with No Pages
{list entry IDs}

## Info

### Unabsorbed Entries
{list entry IDs waiting for /wiki absorb}

### Concrete Noun Candidates (missing pages)
{ranked list: entity name | mentioned N times | suggested page path}

### Stub Pages
{list each stub page}

### Anti-Cramming Candidates
{list pages over ~100 lines}

## Summary & Recommended Actions

{Prioritized list of what to fix first, with suggested commands}
```

---

## Step 4: Update the operation log

Append to `wiki/_log.md`:
```
[{today YYYY-MM-DD}] CLEANUP | pages audited: {n} | critical: {n} | warnings: {n} | info: {n} | report: wiki/_cleanup_report_{date}.md
```

---

## Step 5: Report to user

Give a brief summary of findings and direct them to the cleanup report file for details.
Highlight any critical issues that need immediate attention.
