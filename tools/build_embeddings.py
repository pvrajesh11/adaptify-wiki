#!/usr/bin/env python3
"""Embed every chunk via Voyage API and store vectors as SQLite BLOBs.

Reads chunk text from tools/.cache/index.sqlite (built by build_index.py).
Adds an `embedding` BLOB column to the chunks table if missing, then writes
a 1024-dim float32 vector per chunk.

Env: VOYAGE_API_KEY must be set.
Model: voyage-3-large (1024 dims).
Stdlib only (urllib for HTTP, struct for packing, sqlite3 for storage).

Usage: python3 tools/build_embeddings.py
Cost: ~$0.01 for the full wiki at current voyage-3-large pricing.
"""

import json
import os
import sqlite3
import struct
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "tools" / ".cache" / "index.sqlite"

VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"
MODEL = "voyage-3-large"
INPUT_TYPE_DOC = "document"

# Voyage free-tier limits (no payment method): 3 RPM, 10K TPM.
# We target ~2.5 RPM and ~8K TPM to leave headroom. Override with THROTTLE=0
# and BATCH_SIZE env vars once a payment method is added.
BATCH_SIZE = int(os.environ.get("VOYAGE_BATCH_SIZE", "6"))
MIN_SECONDS_BETWEEN_REQUESTS = float(os.environ.get("VOYAGE_MIN_INTERVAL", "24"))


def pack_vec(vec):
    return struct.pack(f"<{len(vec)}f", *vec)


def unpack_vec(blob):
    n = len(blob) // 4
    return struct.unpack(f"<{n}f", blob)


def voyage_embed(texts, input_type=INPUT_TYPE_DOC, model=MODEL, max_retries=6):
    """POST to Voyage with exponential backoff on 429/5xx."""
    key = os.environ.get("VOYAGE_API_KEY")
    if not key:
        raise RuntimeError("VOYAGE_API_KEY not set")
    payload = json.dumps(
        {"input": texts, "model": model, "input_type": input_type}
    ).encode("utf-8")

    backoff = 30.0
    for attempt in range(1, max_retries + 1):
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
            items = sorted(data["data"], key=lambda x: x["index"])
            return [it["embedding"] for it in items], data.get("usage", {})
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                sleep_for = backoff
                print(f"  HTTP {e.code} (attempt {attempt}/{max_retries}); sleeping {sleep_for:.0f}s")
                time.sleep(sleep_for)
                backoff = min(backoff * 1.5, 90.0)
                continue
            msg = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Voyage HTTP {e.code}: {msg}") from e
        except urllib.error.URLError as e:
            if attempt < max_retries:
                print(f"  URL error {e}; retrying in {backoff:.0f}s")
                time.sleep(backoff)
                backoff = min(backoff * 1.5, 90.0)
                continue
            raise


def ensure_schema(con):
    cols = {row[1] for row in con.execute("PRAGMA table_info(chunks)")}
    if "embedding" not in cols:
        con.execute("ALTER TABLE chunks ADD COLUMN embedding BLOB")
    if "embedding_model" not in cols:
        con.execute("ALTER TABLE chunks ADD COLUMN embedding_model TEXT")
    con.commit()


def main():
    if not DB.exists():
        print(f"Missing {DB}. Run chunk_wiki.py and build_index.py first.", file=sys.stderr)
        return 1
    if not os.environ.get("VOYAGE_API_KEY"):
        print("VOYAGE_API_KEY not set in environment.", file=sys.stderr)
        return 2

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        ensure_schema(con)

        rows = con.execute(
            """SELECT chunk_id, search_text
               FROM chunks
               WHERE embedding IS NULL
                  OR embedding_model IS NOT ?""",
            (MODEL,),
        ).fetchall()
        total = len(rows)
        if total == 0:
            print(f"All chunks already embedded with {MODEL}. Nothing to do.")
            return 0

        n_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        eta_sec = n_batches * MIN_SECONDS_BETWEEN_REQUESTS
        print(
            f"Embedding {total} chunks with {MODEL} "
            f"(batch={BATCH_SIZE}, min_interval={MIN_SECONDS_BETWEEN_REQUESTS}s)"
        )
        print(f"{n_batches} batches; ETA ~{eta_sec / 60:.1f} min")
        total_tokens = 0
        last_req_at = 0.0
        start = time.time()
        for i in range(0, total, BATCH_SIZE):
            # Rate limit: sleep so we never exceed the configured interval.
            if last_req_at:
                elapsed_since = time.time() - last_req_at
                if elapsed_since < MIN_SECONDS_BETWEEN_REQUESTS:
                    time.sleep(MIN_SECONDS_BETWEEN_REQUESTS - elapsed_since)
            batch = rows[i : i + BATCH_SIZE]
            texts = [r["search_text"] or r["chunk_id"] for r in batch]
            vecs, usage = voyage_embed(texts)
            last_req_at = time.time()
            total_tokens += usage.get("total_tokens", 0)
            for r, v in zip(batch, vecs):
                con.execute(
                    "UPDATE chunks SET embedding = ?, embedding_model = ? WHERE chunk_id = ?",
                    (pack_vec(v), MODEL, r["chunk_id"]),
                )
            con.commit()
            done = min(i + BATCH_SIZE, total)
            elapsed = time.time() - start
            remaining = (n_batches - ((done + BATCH_SIZE - 1) // BATCH_SIZE)) * MIN_SECONDS_BETWEEN_REQUESTS
            print(
                f"  {done}/{total} chunks  {total_tokens} tokens  "
                f"elapsed {elapsed:.0f}s  remaining ~{max(0, remaining):.0f}s"
            )
        elapsed = time.time() - start
        print(f"Done in {elapsed:.1f}s. {total_tokens} total tokens.")
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
