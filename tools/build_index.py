#!/usr/bin/env python3
"""Build an SQLite FTS5 keyword index from tools/.cache/chunks.jsonl.

Two tables:
  chunks      — metadata (path, title, heading, product, state, scope, tags, body, ...)
  chunks_fts  — FTS5 virtual table over search_text (porter stemmer + unicode61)

Stdlib only. Run: python3 tools/build_index.py
"""

import json
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHUNKS = REPO / "tools" / ".cache" / "chunks.jsonl"
DB = REPO / "tools" / ".cache" / "index.sqlite"


SCHEMA = """
DROP TABLE IF EXISTS chunks;
DROP TABLE IF EXISTS chunks_fts;

CREATE TABLE chunks (
    chunk_id    TEXT PRIMARY KEY,
    path        TEXT NOT NULL,
    title       TEXT,
    heading     TEXT,
    summary     TEXT,
    type        TEXT,
    product     TEXT,
    state       TEXT,
    scope       TEXT,
    form_id     TEXT,
    tags_json   TEXT,
    citations_json TEXT,
    body        TEXT,
    search_text TEXT
);

CREATE INDEX idx_chunks_path    ON chunks(path);
CREATE INDEX idx_chunks_product ON chunks(product);
CREATE INDEX idx_chunks_state   ON chunks(state);
CREATE INDEX idx_chunks_scope   ON chunks(scope);

CREATE VIRTUAL TABLE chunks_fts USING fts5(
    chunk_id UNINDEXED,
    path UNINDEXED,
    title,
    heading,
    summary,
    body,
    tokenize = 'porter unicode61'
);
"""


def main():
    if not CHUNKS.exists():
        print(f"Missing {CHUNKS}. Run tools/chunk_wiki.py first.", file=sys.stderr)
        return 1

    DB.parent.mkdir(parents=True, exist_ok=True)

    # Preserve existing embeddings across rebuilds: snapshot chunk_id → vector
    # before we wipe and re-insert. Skip snapshot if DB missing or column absent.
    existing_embeds: dict[str, tuple] = {}
    if DB.exists():
        _c = sqlite3.connect(DB)
        try:
            cols = {r[1] for r in _c.execute("PRAGMA table_info(chunks)")}
            if "embedding" in cols:
                for cid, emb, model in _c.execute(
                    "SELECT chunk_id, embedding, embedding_model FROM chunks "
                    "WHERE embedding IS NOT NULL"
                ):
                    existing_embeds[cid] = (emb, model)
        finally:
            _c.close()
        DB.unlink()

    con = sqlite3.connect(DB)
    try:
        # Verify FTS5 is compiled in.
        try:
            con.execute("CREATE VIRTUAL TABLE _probe USING fts5(x);")
            con.execute("DROP TABLE _probe;")
        except sqlite3.OperationalError as e:
            print(f"FTS5 unavailable in this sqlite3 build: {e}", file=sys.stderr)
            return 2

        con.executescript(SCHEMA)

        inserted = 0
        with CHUNKS.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                c = json.loads(line)
                con.execute(
                    """INSERT INTO chunks
                    (chunk_id, path, title, heading, summary, type, product, state, scope,
                     form_id, tags_json, citations_json, body, search_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        c["chunk_id"],
                        c["path"],
                        c.get("title"),
                        c.get("heading"),
                        c.get("summary"),
                        c.get("type"),
                        c.get("product"),
                        c.get("state"),
                        c.get("scope"),
                        c.get("form_id"),
                        json.dumps(c.get("tags") or []),
                        json.dumps(c.get("citations") or []),
                        c.get("body"),
                        c.get("search_text"),
                    ),
                )
                # FTS body field = search_text so citations/tags are indexed too.
                con.execute(
                    """INSERT INTO chunks_fts
                    (chunk_id, path, title, heading, summary, body)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        c["chunk_id"],
                        c["path"],
                        c.get("title") or "",
                        c.get("heading") or "",
                        c.get("summary") or "",
                        c.get("search_text") or c.get("body") or "",
                    ),
                )
                inserted += 1
        con.commit()

        # Restore embeddings for chunk_ids that still exist.
        if existing_embeds:
            con.execute("ALTER TABLE chunks ADD COLUMN embedding BLOB")
            con.execute("ALTER TABLE chunks ADD COLUMN embedding_model TEXT")
            restored = 0
            for cid, (emb, model) in existing_embeds.items():
                cur = con.execute(
                    "UPDATE chunks SET embedding = ?, embedding_model = ? "
                    "WHERE chunk_id = ?",
                    (emb, model, cid),
                )
                restored += cur.rowcount
            con.commit()
            print(f"Restored {restored}/{len(existing_embeds)} embeddings")

        print(f"Built {DB}")
        print(f"Indexed {inserted} chunks")
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
