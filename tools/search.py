#!/usr/bin/env python3
"""Search over the indexed wiki: keyword (FTS5), semantic (Voyage), or hybrid (RRF).

Library:
    from tools.search import search_pages, search_chunks
    # default mode = "hybrid" if embeddings present, else "keyword"

CLI:
    python3 tools/search.py "intra-family exclusion alaska"
    python3 tools/search.py "HO 0801" --product homeowners-hobp --mode keyword
    python3 tools/search.py "abuse exception across states" --mode semantic

Hybrid fusion: Reciprocal Rank Fusion (RRF) with k=60. Keyword uses BM25,
semantic uses cosine similarity over Voyage voyage-3-large embeddings.
"""

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import struct
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "tools" / ".cache" / "index.sqlite"
QCACHE = REPO / "tools" / ".cache" / "query_embeddings.json"

VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"
VOYAGE_MODEL = "voyage-3-large"

# Match FTS5 unicode61 default tokenization: split on non-word chars.
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)

_STOP = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "does", "for",
    "from", "how", "in", "is", "it", "of", "on", "or", "that", "the",
    "to", "what", "when", "where", "which", "who", "why", "with",
    "this", "under", "across",
}


def _sanitize(query: str) -> str:
    tokens = _TOKEN_RE.findall(query)
    keep = [t for t in tokens if len(t) >= 2 and t.lower() not in _STOP]
    if not keep:
        return '""'
    return " OR ".join(f'"{t}"' for t in keep)


# ----- Keyword search (FTS5 / BM25) -----

def search_chunks_keyword(query: str, top_k: int = 40, filters=None):
    filters = filters or {}
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        sql = """
            SELECT f.chunk_id, f.path, f.title, f.heading, f.summary,
                   c.product, c.state, c.scope, c.type, c.form_id, c.body,
                   bm25(chunks_fts) AS score
            FROM chunks_fts f
            JOIN chunks c ON c.chunk_id = f.chunk_id
            WHERE chunks_fts MATCH ?
        """
        args = [_sanitize(query)]
        for col in ("product", "state", "scope", "type"):
            if filters.get(col):
                sql += f" AND c.{col} = ?"
                args.append(filters[col])
        sql += " ORDER BY score ASC LIMIT ?"
        args.append(top_k)
        return [dict(r) for r in con.execute(sql, args).fetchall()]
    finally:
        con.close()


# ----- Semantic search (Voyage + cosine) -----

def _load_qcache():
    if QCACHE.exists():
        try:
            return json.loads(QCACHE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_qcache(cache):
    QCACHE.parent.mkdir(parents=True, exist_ok=True)
    QCACHE.write_text(json.dumps(cache), encoding="utf-8")


def _voyage_query_embed(query: str, model=VOYAGE_MODEL):
    cache_key = hashlib.sha256(f"{model}|{query}".encode("utf-8")).hexdigest()
    cache = _load_qcache()
    if cache_key in cache:
        return cache[cache_key]
    key = os.environ.get("VOYAGE_API_KEY")
    if not key:
        raise RuntimeError("VOYAGE_API_KEY not set")
    payload = json.dumps(
        {"input": [query], "model": model, "input_type": "query"}
    ).encode("utf-8")
    req = urllib.request.Request(
        VOYAGE_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Voyage HTTP {e.code}: {msg}") from e
    vec = data["data"][0]["embedding"]
    cache[cache_key] = vec
    _save_qcache(cache)
    return vec


def _unpack(blob):
    n = len(blob) // 4
    return struct.unpack(f"<{n}f", blob)


def _cosine(a, b):
    # Both 1024-dim. Pure Python; fast enough at this scale.
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def search_chunks_semantic(query: str, top_k: int = 40, filters=None):
    filters = filters or {}
    qvec = _voyage_query_embed(query)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        sql = """
            SELECT chunk_id, path, title, heading, summary,
                   product, state, scope, type, form_id, body, embedding
            FROM chunks WHERE embedding IS NOT NULL
        """
        args = []
        for col in ("product", "state", "scope", "type"):
            if filters.get(col):
                sql += f" AND {col} = ?"
                args.append(filters[col])
        rows = con.execute(sql, args).fetchall()
    finally:
        con.close()

    scored = []
    for r in rows:
        d = dict(r)
        vec = _unpack(d.pop("embedding"))
        d["score"] = _cosine(qvec, vec)  # higher is better
        scored.append(d)
    scored.sort(key=lambda x: -x["score"])
    return scored[:top_k]


# ----- Hybrid (RRF fusion) -----

def _rrf_fuse(ranked_lists, weights=None, k=20):
    """Weighted Reciprocal Rank Fusion.

    k=20 (vs. the canonical k=60) gives top-ranked items more dominance —
    useful when one ranker is noticeably stronger and we don't want a weak
    ranker's #1 pick to outweigh a strong ranker's #1 pick.

    weights: parallel list of floats. Default 1.0 per list.
    """
    weights = weights or [1.0] * len(ranked_lists)
    scores = {}
    rows_by_id = {}
    for ranked, w in zip(ranked_lists, weights):
        for rank, row in enumerate(ranked, start=1):
            cid = row["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + w * 1.0 / (k + rank)
            rows_by_id.setdefault(cid, row)
    return [
        dict(rows_by_id[cid], score=s)
        for cid, s in sorted(scores.items(), key=lambda x: -x[1])
    ]


def search_chunks_hybrid(query: str, top_k: int = 40, filters=None):
    # Semantic is the stronger signal on this corpus (insurance rules +
    # comparison / definition queries). Give it 2x weight over keyword.
    kw = search_chunks_keyword(query, top_k=top_k, filters=filters)
    sm = search_chunks_semantic(query, top_k=top_k, filters=filters)
    return _rrf_fuse([kw, sm], weights=[1.0, 3.0], k=20)[:top_k]


# ----- Dispatch + page-level dedup -----

def _has_embeddings():
    if not DB.exists():
        return False
    con = sqlite3.connect(DB)
    try:
        row = con.execute(
            "SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL"
        ).fetchone()
        return (row[0] or 0) > 0
    finally:
        con.close()


def search_chunks(query: str, top_k: int = 20, filters=None, mode: str = "auto"):
    if not DB.exists():
        raise RuntimeError(f"No index at {DB}. Run build_index.py.")
    if mode == "auto":
        mode = "hybrid" if _has_embeddings() else "keyword"
    if mode == "keyword":
        return search_chunks_keyword(query, top_k=top_k, filters=filters)
    if mode == "semantic":
        return search_chunks_semantic(query, top_k=top_k, filters=filters)
    if mode == "hybrid":
        return search_chunks_hybrid(query, top_k=top_k, filters=filters)
    raise ValueError(f"Unknown mode: {mode}")


def search_pages(query: str, top_k: int = 10, filters=None, mode: str = "auto"):
    hits = search_chunks(query, top_k=top_k * 4, filters=filters, mode=mode)
    # Best-scoring chunk per path. Hybrid returns RRF scores (higher = better);
    # keyword returns BM25 (lower = better); semantic returns cosine (higher).
    # Determine sort direction from the mode.
    if mode == "auto":
        mode = "hybrid" if _has_embeddings() else "keyword"
    higher_better = mode in ("semantic", "hybrid")
    best = {}
    for h in hits:
        p = h["path"]
        if p not in best:
            best[p] = h
        else:
            if higher_better and h["score"] > best[p]["score"]:
                best[p] = h
            elif (not higher_better) and h["score"] < best[p]["score"]:
                best[p] = h
    ordered = sorted(best.values(), key=lambda x: -x["score"] if higher_better else x["score"])
    return ordered[:top_k]


def _fmt(hit):
    return (
        f"  {hit['score']:+.4f}  {hit['path']}  "
        f"[{hit.get('type') or '?'}/{hit.get('product') or '-'}/{hit.get('state') or '-'}]\n"
        f"           → {hit.get('heading') or ''}"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="+")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--mode", choices=["auto", "keyword", "semantic", "hybrid"], default="auto")
    ap.add_argument("--chunks", action="store_true")
    ap.add_argument("--product")
    ap.add_argument("--state")
    ap.add_argument("--scope")
    ap.add_argument("--type")
    args = ap.parse_args()

    query = " ".join(args.query)
    filters = {k: getattr(args, k) for k in ("product", "state", "scope", "type") if getattr(args, k)}
    fn = search_chunks if args.chunks else search_pages
    hits = fn(query, top_k=args.top, filters=filters, mode=args.mode)
    print(f"Query: {query}")
    print(f"Mode: {args.mode}{'  (→ ' + ('hybrid' if _has_embeddings() else 'keyword') + ')' if args.mode == 'auto' else ''}")
    if filters:
        print(f"Filters: {filters}")
    print(f"Hits: {len(hits)}")
    for h in hits:
        print(_fmt(h))
    return 0


if __name__ == "__main__":
    sys.exit(main())
