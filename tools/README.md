# Retrieval tools

Keyword + semantic search over the wiki. Stdlib Python only (no numpy, no PyYAML); Voyage API for embeddings.

## Setup (one-time)

```bash
# 1. Voyage API key (embeddings). Get one at voyageai.com → Account → API Keys.
export VOYAGE_API_KEY="pa-..."
# (Persist in ~/.zshenv or ~/.bashrc.)

# 2. Build the chunk store, FTS5 index, and embeddings.
python3 tools/chunk_wiki.py        # wiki/*.md → tools/.cache/chunks.jsonl
python3 tools/build_index.py       # chunks.jsonl → FTS5 SQLite
python3 tools/build_embeddings.py  # adds 1024-dim voyage-3-large vectors
```

The build takes ~25 min on the Voyage free tier (3 RPM throttling). One-time;
re-run only after wiki content changes.

## Searching

### From the command line

```bash
# Default: hybrid (BM25 + semantic RRF) if embeddings present.
python3 tools/search.py "intra-family exclusion alaska"

# Restrict to one product/state/type.
python3 tools/search.py "HO 0801" --product homeowners-hobp --state AL
python3 tools/search.py "abuse exception" --type form

# Mode override.
python3 tools/search.py "named insured" --mode semantic
python3 tools/search.py "AS 18.66"       --mode keyword

# Return raw chunks instead of deduplicated pages.
python3 tools/search.py "Part D" --chunks --top 10
```

Flags: `--mode {auto,keyword,semantic,hybrid}` · `--top N` · `--product`
`--state` `--scope` `--type` · `--chunks` (chunks not pages).

### From Python

```python
from tools.search import search_pages, search_chunks

hits = search_pages("domestic violence exception", top_k=5, mode="hybrid")
for h in hits:
    print(h["score"], h["path"], h["heading"])
```

### From Obsidian

Obsidian has no built-in hook for an external Python script. Two options:

**A. Shell command palette.** Install the [Shell commands](https://github.com/Taitava/obsidian-shellcommands)
community plugin, then add a command:

```
cd /Users/raj/claude/adaptify-wiki && python3 tools/search.py "{{selection}}" --top 5
```

Select query text in any note, run the command, and the hits print to the
plugin's output modal. You can click the path in the output to open the page.

**B. Terminal pane.** Install [Terminal](https://github.com/polyipseity/obsidian-terminal),
open a pane inside the vault, and run `python3 tools/search.py "..."` directly.
Faster for iterative querying than the shell-commands modal.

Obsidian's own search (Ctrl/Cmd+Shift+F) stays useful for exact-string matches
across the vault — it's complementary, not replaced.

### From the GitHub Pages site

The published Jekyll site has no server — it can't run Python. Options:

- **Jekyll's built-in search** (already enabled in `_config.yml` via the
  `just-the-docs` theme) does client-side keyword search over page titles and
  bodies. Use it for quick lookups; it won't do semantic matching.
- **GitHub UI search** — `https://github.com/<user>/adaptify-wiki/search?q=AS+18.66`
  searches the repo directly. Good for exact-string hunts.
- **For semantic search** clone the repo and run the CLI locally; the Jekyll
  site is not the place for LLM-powered retrieval.

## How it works

- **Chunking** (`chunk_wiki.py`): split each `.md` on H2 headings, drop chunks
  <40 non-whitespace chars. Frontmatter (title, summary, tags, citations,
  scope, product, state) is attached to every chunk.
- **Keyword** (`search.py` → `search_chunks_keyword`): SQLite FTS5 with
  `porter unicode61` tokenizer, ranked by BM25. FTS body column indexes
  `search_text` (title + summary + heading + tags + citations + body).
- **Semantic** (`search.py` → `search_chunks_semantic`): Voyage
  `voyage-3-large` 1024-dim embeddings, packed as float32 BLOBs in SQLite.
  Cosine similarity in pure Python. Query embeddings are cached
  (`tools/.cache/query_embeddings.json`, sha256-keyed).
- **Hybrid** (`search.py` → `search_chunks_hybrid`): weighted Reciprocal Rank
  Fusion (k=20) of both lists, with semantic weighted 3× over keyword. Tuned
  against `wiki/_evals/seed.yaml`.

## Evals

```bash
python3 tools/run_evals.py              # top_k=5, auto mode
python3 tools/run_evals.py --mode keyword
python3 tools/run_evals.py --top 10 -v  # verbose: show misses
```

Baseline on the current corpus (10 questions, must-cite recall@5):

| Mode     | Recall |
|----------|--------|
| keyword  | 73%    |
| semantic | 91%    |
| hybrid   | 91%    |

Hybrid matches semantic today; it wins when the query has an exact token that
semantic alone under-weights.
