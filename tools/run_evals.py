#!/usr/bin/env python3
"""Run the eval seed set against the current index and report recall@k.

Loads wiki/_evals/seed.yaml (simple YAML subset parser — stdlib only).
For each question, calls tools.search.search_pages() and checks whether
every `must_cite` path appears in the top-k pages.

Output: prints a per-question table and overall recall metrics.

Usage:
    python3 tools/run_evals.py            # default top_k=5
    python3 tools/run_evals.py --top 10
"""

import argparse
import re
import sys
from pathlib import Path

# Make `tools.search` importable whether or not tools/ is a package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.search import search_pages  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SEED = REPO / "wiki" / "_evals" / "seed.yaml"


def parse_seed_yaml(text: str):
    """Tiny YAML parser for the specific shape of seed.yaml.

    Grammar supported:
        key: value
        key: "quoted value"
        key: [a, b]
        key:
          - item
          - item
        - id: q001         (list-of-dicts under `questions:`)
          key: value
          ...

    Not a general YAML parser — just enough for this file.
    """
    # Strip comment-only lines and full trailing comments on value lines.
    def strip_comment(line: str) -> str:
        # Only strip `#` that's outside quotes. For this file's content, a
        # conservative approach suffices: split on " #" (space-hash).
        idx = line.find(" #")
        if idx >= 0:
            return line[:idx].rstrip()
        return line

    lines = [strip_comment(l) for l in text.split("\n")]

    # Top-level keys
    top = {}
    questions = []
    i = 0
    in_questions = False
    current_q = None
    current_list_key = None  # for multi-line lists inside a question

    def flush_q():
        nonlocal current_q
        if current_q is not None:
            questions.append(current_q)
            current_q = None

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue

        # Start of a question item.
        m_item = re.match(r"^(\s*)- (\w+)\s*:\s*(.*)$", line)
        # Continuation of a question's fields.
        m_kv = re.match(r"^(\s+)(\w+)\s*:\s*(.*)$", line)
        # Top-level key.
        m_top = re.match(r"^(\w+)\s*:\s*(.*)$", line)
        # List item under a key.
        m_listitem = re.match(r"^(\s+)- (.*)$", line)

        if not in_questions and m_top and m_top.group(1) == "questions":
            in_questions = True
            i += 1
            continue

        if in_questions:
            # New question item marker: "  - id: ..."
            if m_item and m_item.group(2) == "id":
                flush_q()
                current_q = {"id": _clean(m_item.group(3))}
                current_list_key = None
                i += 1
                continue

            # A key within the current question, or a list continuation.
            if current_q is not None:
                if m_listitem and current_list_key is not None:
                    current_q[current_list_key].append(_clean(m_listitem.group(2)))
                    i += 1
                    continue

                if m_kv:
                    key = m_kv.group(2)
                    val = m_kv.group(3).strip()
                    if val == "":
                        current_q[key] = []
                        current_list_key = key
                    elif val.startswith("[") and val.endswith("]"):
                        inner = val[1:-1].strip()
                        current_q[key] = (
                            []
                            if not inner
                            else [_clean(x.strip()) for x in inner.split(",")]
                        )
                        current_list_key = None
                    else:
                        current_q[key] = _clean(val)
                        current_list_key = None
                    i += 1
                    continue

        elif m_top:
            key = m_top.group(1)
            val = m_top.group(2).strip()
            if val:
                top[key] = _clean(val)
            i += 1
            continue

        i += 1

    flush_q()
    top["questions"] = questions
    return top


def _clean(val: str) -> str:
    v = val.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1]
    return v


def run(top_k: int = 5, verbose: bool = False, mode: str = "auto"):
    if not SEED.exists():
        print(f"No seed at {SEED}", file=sys.stderr)
        return 1
    parsed = parse_seed_yaml(SEED.read_text(encoding="utf-8"))
    questions = parsed.get("questions") or []

    total_must = 0
    total_must_found = 0
    total_opt = 0
    total_opt_found = 0
    rows = []
    # Bucketed counters for cq_category and role
    bucket_must = {}  # key -> [found, total]
    bucket_opt = {}

    def bump(d, key, found, total):
        if not key:
            key = "-"
        slot = d.setdefault(key, [0, 0])
        slot[0] += found
        slot[1] += total

    for q in questions:
        qid = q.get("id", "?")
        question = q.get("question", "")
        intent = q.get("intent", "-")
        cq = q.get("cq_category", "-")
        role = q.get("role", "-")
        expected = q.get("expected", "in_scope")
        must = q.get("must_cite") or []
        opt = q.get("optional_cite") or []

        # Out-of-scope questions are not retrieval-evaluated here.
        # chat_evals.py handles refusal correctness.
        if expected == "out_of_scope":
            rows.append(
                {
                    "id": qid,
                    "intent": intent,
                    "cq": cq,
                    "role": role,
                    "status": "SKIP",
                    "must_recall": "-",
                    "opt_recall": "-",
                    "missed": [],
                    "hits": [],
                    "question": question,
                }
            )
            continue

        hits = search_pages(question, top_k=top_k, mode=mode)
        hit_paths = [h["path"] for h in hits]

        must_hit = [p for p in must if p in hit_paths]
        opt_hit = [p for p in opt if p in hit_paths]

        total_must += len(must)
        total_must_found += len(must_hit)
        total_opt += len(opt)
        total_opt_found += len(opt_hit)

        bump(bucket_must, f"cat:{cq}", len(must_hit), len(must))
        bump(bucket_must, f"role:{role}", len(must_hit), len(must))
        bump(bucket_opt, f"cat:{cq}", len(opt_hit), len(opt))
        bump(bucket_opt, f"role:{role}", len(opt_hit), len(opt))

        status = "PASS" if len(must_hit) == len(must) else "FAIL"
        rows.append(
            {
                "id": qid,
                "intent": intent,
                "cq": cq,
                "role": role,
                "status": status,
                "must_recall": f"{len(must_hit)}/{len(must)}",
                "opt_recall": f"{len(opt_hit)}/{len(opt)}" if opt else "-",
                "missed": [p for p in must if p not in hit_paths],
                "hits": hit_paths,
                "question": question,
            }
        )

    # Report
    print(f"Eval: {SEED}   top_k={top_k}   mode={mode}")
    print()
    print(f"{'ID':<6} {'STATUS':<6} {'CAT':<13} {'ROLE':<8} {'MUST':<6} {'OPT':<6}  QUESTION")
    print("-" * 110)
    for r in rows:
        q = r["question"]
        if len(q) > 45:
            q = q[:42] + "..."
        print(
            f"{r['id']:<6} {r['status']:<6} {r['cq']:<13} {r['role']:<8} "
            f"{r['must_recall']:<6} {r['opt_recall']:<6}  {q}"
        )

    total_in = sum(1 for r in rows if r["status"] != "SKIP")
    passed = sum(1 for r in rows if r["status"] == "PASS")
    skipped = sum(1 for r in rows if r["status"] == "SKIP")
    must_recall = (total_must_found / total_must) if total_must else 0.0
    opt_recall = (total_opt_found / total_opt) if total_opt else 0.0

    print("-" * 110)
    print(
        f"Passed: {passed}/{total_in} (in-scope)   "
        f"must-cite recall: {total_must_found}/{total_must} ({must_recall:.0%})   "
        f"optional-cite recall: {total_opt_found}/{total_opt} ({opt_recall:.0%})   "
        f"skipped (out-of-scope): {skipped}"
    )

    # Per-bucket breakdown
    print()
    print("Per-category recall (must-cite / opt-cite):")
    for key in sorted(k for k in bucket_must if k.startswith("cat:")):
        m = bucket_must[key]
        o = bucket_opt.get(key, [0, 0])
        m_pct = (m[0] / m[1]) if m[1] else 0.0
        o_pct = (o[0] / o[1]) if o[1] else 0.0
        print(
            f"  {key[4:]:<14} must {m[0]}/{m[1]} ({m_pct:.0%})   "
            f"opt {o[0]}/{o[1]} ({o_pct:.0%})"
        )
    print()
    print("Per-role recall (must-cite / opt-cite):")
    for key in sorted(k for k in bucket_must if k.startswith("role:")):
        m = bucket_must[key]
        o = bucket_opt.get(key, [0, 0])
        m_pct = (m[0] / m[1]) if m[1] else 0.0
        o_pct = (o[0] / o[1]) if o[1] else 0.0
        print(
            f"  {key[5:]:<14} must {m[0]}/{m[1]} ({m_pct:.0%})   "
            f"opt {o[0]}/{o[1]} ({o_pct:.0%})"
        )

    if verbose:
        print()
        for r in rows:
            if r["status"] == "FAIL":
                print(f"\n[{r['id']}] {r['question']}")
                print(f"  missed must_cite: {r['missed']}")
                print(f"  top-{top_k} hits:")
                for p in r["hits"]:
                    print(f"    - {p}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--mode", choices=["auto", "keyword", "semantic", "hybrid"], default="auto")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    sys.exit(run(top_k=args.top, verbose=args.verbose, mode=args.mode))
