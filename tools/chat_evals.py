#!/usr/bin/env python3
"""Phase 2 eval — chatbot refusal correctness on out-of-scope questions.

Loads wiki/_evals/seed.yaml, filters to `expected: out_of_scope`, and asks the
chatbot (same retrieval + system prompt as production) each question. Classifies
each response as REFUSED (correct) or FABRICATED (incorrect) using keyword
heuristics. No LLM-as-judge — keep it cheap and deterministic.

Usage:
    python3 tools/chat_evals.py
    python3 tools/chat_evals.py -v       # show full responses
    python3 tools/chat_evals.py --top 8

Requires ANTHROPIC_API_KEY in env.
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from anthropic import Anthropic  # noqa: E402

from tools.run_evals import parse_seed_yaml  # noqa: E402
from tools.search import search_pages  # noqa: E402
from tools.chat.server import (  # noqa: E402
    MODEL,
    SYSTEM_PROMPT,
    TOP_K,
    _build_context,
    detect_state,
)

SEED = REPO / "wiki" / "_evals" / "seed.yaml"

# Phrases that indicate the model correctly refused / acknowledged the gap.
# Patterns are intentionally loose — false positives (calling a fabrication a
# refusal) are worse than false negatives. If a fabricated answer also happens
# to start with "I don't have data on X but here's a guess", -v reveals it.
REFUSAL_PATTERNS = [
    r"\bdo(?:n['\u2019]t|es not| not)\s+\w*\s*(?:have|contain|include|cover|mention|provide|address|discuss)\b",
    r"\bno (?:information|data|details|content|coverage|mention|documentation)\b",
    r"\bnot (?:available|provided|covered|included|in (?:the )?(?:wiki|excerpts)|address(?:ed)?)\b",
    r"\b(?:wiki|excerpts?|source(?:s)?|documentation|context) (?:do not|does not|doesn['\u2019]t|don['\u2019]t|provide no|contain no)\b",
    r"\bcannot (?:answer|determine|find|provide)\b",
    r"\bunable to (?:answer|find|determine|provide)\b",
    r"\bI (?:do not|don['\u2019]t) have\b",
    r"\bno (?:relevant|matching) (?:information|excerpts|content)\b",
    r"\binsufficient (?:information|context|data)\b",
]

REFUSAL_RE = re.compile("|".join(REFUSAL_PATTERNS), re.IGNORECASE)


def classify(response: str) -> str:
    """REFUSED if any refusal phrase matches; FABRICATED otherwise."""
    return "REFUSED" if REFUSAL_RE.search(response) else "FABRICATED"


def ask(client: Anthropic, question: str, top_k: int) -> tuple[str, list]:
    """Mirror server.py's retrieval + state-boost + prompt assembly."""
    state = detect_state(question)
    raw = search_pages(question, top_k=top_k * 2, mode="hybrid")
    if state:
        on = [h for h in raw if not h.get("state") or h.get("state") == state]
        off = [h for h in raw if h.get("state") and h.get("state") != state]
        hits = (on + off)[:top_k]
    else:
        hits = raw[:top_k]

    system = SYSTEM_PROMPT.format(context=_build_context(hits))
    msg = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    return text, hits


def run(top_k: int = TOP_K, verbose: bool = False):
    if not SEED.exists():
        print(f"No seed at {SEED}", file=sys.stderr)
        return 1
    parsed = parse_seed_yaml(SEED.read_text(encoding="utf-8"))
    questions = [q for q in (parsed.get("questions") or []) if q.get("expected") == "out_of_scope"]
    if not questions:
        print("No out_of_scope questions in seed.yaml")
        return 0

    client = Anthropic()
    print(f"Chat eval: {SEED}   model={MODEL}   top_k={top_k}")
    print(f"Out-of-scope probes: {len(questions)}")
    print()
    print(f"{'ID':<6} {'CAT':<13} {'ROLE':<8} {'STATUS':<11}  QUESTION")
    print("-" * 110)

    refused = 0
    rows = []
    for q in questions:
        qid = q.get("id", "?")
        question = q.get("question", "")
        cq = q.get("cq_category", "-")
        role = q.get("role", "-")

        try:
            response, _ = ask(client, question, top_k)
        except Exception as e:
            print(f"{qid:<6} {cq:<13} {role:<8} {'ERROR':<11}  {question[:50]}")
            print(f"        {e}")
            rows.append((qid, "ERROR", question, str(e)))
            continue

        status = classify(response)
        if status == "REFUSED":
            refused += 1
        q_short = question if len(question) <= 50 else question[:47] + "..."
        print(f"{qid:<6} {cq:<13} {role:<8} {status:<11}  {q_short}")
        rows.append((qid, status, question, response))

    total = len(questions)
    print("-" * 110)
    print(f"Refused (correct): {refused}/{total} ({refused / total:.0%})")

    if verbose:
        print()
        for qid, status, question, response in rows:
            print(f"\n[{qid}] ({status}) {question}")
            print(f"  response: {response[:600]}{'...' if len(response) > 600 else ''}")

    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=TOP_K)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    sys.exit(run(top_k=args.top, verbose=args.verbose))
