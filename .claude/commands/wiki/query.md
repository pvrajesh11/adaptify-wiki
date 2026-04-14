You are running `/wiki query` to answer the following question:

$ARGUMENTS

Answer using only compiled wiki knowledge — do not read raw source documents.
Every factual claim must be cited. This operation is read-only; do not modify any wiki files.

---

## Step 1: Understand the question

Parse the question to identify:
- **Scope**: which product(s) and/or state(s) are relevant? Or is this a cross-product/cross-state question?
- **Type**: coverage rule? rating rule? eligibility? definition? state comparison? version diff? filing metadata?
- **Specificity**: is this about a specific form, endorsement, or provision?

---

## Step 2: Find relevant pages

Read `wiki/index.md` — scan all entries for pages relevant to the question's scope and type.

Then check `wiki/_backlinks.json` — look for the key concepts in the question. Pages with high connectivity (many backlinks) are likely central to the answer.

Identify 3–8 pages to read. Prioritize:
1. Product-state pages matching the question's product/state
2. Coverage concept pages for the coverage type asked about
3. Form pages if the question is about a specific form
4. Comparison pages if the question asks about differences

---

## Step 3: Read the pages and follow links

Read the identified pages. If a page contains `[[wikilinks]]` to other pages that seem relevant, follow them up to 2–3 levels deep.

---

## Step 4: Synthesize the answer

Write a clear, direct answer:

- Lead with the direct answer, not preamble
- Organize by product/state if the question spans multiple
- For comparisons (state vs state, version vs version): use a structured format with clear before/after or side-by-side presentation
- For coverage questions: state what's covered, what's excluded, and any conditions
- For rating rule questions: state the rule and its criteria

**Citation format** — every factual claim ends with one of:
- Wiki citation: `([[product-states/auto-ppa-AK/rating-rules]])`
- Source citation: `(SOURCE: {entry-id} §{section})`

If the wiki has a version diff page relevant to the question, reference it explicitly.

---

## Step 5: Flag gaps

If the question cannot be fully answered from the current wiki:
- State clearly what is and isn't known
- List the specific source documents that would need to be ingested to fill the gap
- Do not speculate or infer beyond what the wiki contains

---

## Step 6: Suggest a follow-up page (optional)

If the answer synthesized here would be valuable as a permanent wiki page (e.g., a common question that no single page currently answers), recommend creating a comparison or concept page, but do not create it automatically.
