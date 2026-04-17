#!/usr/bin/env python3
"""Chunk every wiki/*.md into heading-scoped chunks for retrieval.

- Split on `## ` (H2). Content before the first H2 becomes an "intro" chunk.
- H3/H4 stay inside their parent H2 chunk.
- Each chunk inherits the page's frontmatter (title, type, product, state,
  scope, tags, citations, summary).

Output: tools/.cache/chunks.jsonl  (one chunk per line)

Stdlib only. Run: python3 tools/chunk_wiki.py
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WIKI = REPO / "wiki"
OUT = REPO / "tools" / ".cache" / "chunks.jsonl"

SKIP_FILES = {"_log.md", "_schema_audit.md", "_absorb_log.json", "_backlinks.json"}
SKIP_DIRS = {"_evals", "ins"}


# Minimal YAML frontmatter parser — same subset as validate_frontmatter.py.
def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    block = text[4:end]
    body = text[end + 4 :].lstrip("\n")
    result = {}
    current_key = None
    for raw in block.split("\n"):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(("  - ", "- ")):
            val = line.split("- ", 1)[1].strip().strip('"').strip("'")
            if current_key is not None:
                if not isinstance(result.get(current_key), list):
                    result[current_key] = []
                result[current_key].append(val)
            continue
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        current_key = key
        if val == "":
            result[key] = None
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            result[key] = [] if not inner else [
                x.strip().strip('"').strip("'") for x in inner.split(",")
            ]
        elif val in ("true", "false"):
            result[key] = val == "true"
        elif val == "null":
            result[key] = None
        else:
            result[key] = val.strip('"').strip("'")
    return result, body


def chunks_for_page(rel_path: str, text: str):
    fm, body = parse_frontmatter(text)
    page_title = fm.get("title") or Path(rel_path).stem
    page_summary = fm.get("summary") or ""

    # Strip the first H1 line if present (same as page title, no info).
    body_lines = body.split("\n")
    if body_lines and body_lines[0].startswith("# "):
        body_lines = body_lines[1:]

    # Split on H2.
    chunks_raw = []
    current_heading = "Overview"
    current_buf: list[str] = []
    for line in body_lines:
        if re.match(r"^##\s+", line):
            if current_buf and "".join(current_buf).strip():
                chunks_raw.append((current_heading, "\n".join(current_buf).strip()))
            current_heading = line.lstrip("# ").strip()
            current_buf = []
        else:
            current_buf.append(line)
    if current_buf and "".join(current_buf).strip():
        chunks_raw.append((current_heading, "\n".join(current_buf).strip()))

    # Drop empty and very short chunks (< 40 chars of non-whitespace).
    chunks_raw = [
        (h, b) for (h, b) in chunks_raw if len(re.sub(r"\s+", "", b)) >= 40
    ]

    common = {
        "path": rel_path,
        "title": page_title,
        "summary": page_summary,
        "type": fm.get("type"),
        "product": fm.get("product"),
        "state": fm.get("state"),
        "scope": fm.get("scope"),
        "tags": fm.get("tags") or [],
        "citations": fm.get("citations") or [],
        "form_id": fm.get("form_id"),
    }

    out = []
    for idx, (heading, body_text) in enumerate(chunks_raw):
        # search_text = lexical bundle: title + summary + heading + body.
        search_text = "\n".join(
            x
            for x in (
                page_title,
                page_summary,
                heading,
                " ".join(str(x) for x in (common["tags"] or [])),
                " ".join(str(x) for x in (common["citations"] or [])),
                body_text,
            )
            if x
        )
        chunk = dict(common)
        chunk.update(
            {
                "chunk_id": f"{rel_path}#{idx:02d}",
                "chunk_idx": idx,
                "heading": heading,
                "body": body_text,
                "search_text": search_text,
            }
        )
        out.append(chunk)
    return out


def walk():
    for md in sorted(WIKI.rglob("*.md")):
        if md.name in SKIP_FILES:
            continue
        rel = md.relative_to(WIKI)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        yield str(rel), md.read_text(encoding="utf-8")


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    count_pages = 0
    count_chunks = 0
    with OUT.open("w", encoding="utf-8") as f:
        for rel, text in walk():
            chunks = chunks_for_page(rel, text)
            for c in chunks:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
            count_pages += 1
            count_chunks += len(chunks)
    print(f"Wrote {OUT}")
    print(f"Pages: {count_pages}  Chunks: {count_chunks}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
