#!/usr/bin/env python3
"""Phase 0 eval — multi-turn conversation scenarios.

Replays each scenario in wiki/_evals/chat_scenarios.yaml through the SAME
retrieval + chat pipeline as production (tools/chat/server.py), so the baseline
reflects what users actually experience today.

Per-turn dimensions scored:
  - action_match                  classify -> {answer, clarify, refuse}, compare to expected
  - must_cite_recall              fraction of expected_must_cite present in sources (action=answer)
  - optional_cite_recall          fraction of expected_optional_cite (action=answer)
  - topic_coverage                fraction of expected_topics found in answer (action=answer)
  - entity_inheritance            for each inherits_entities facet, >=1 source reflects it
  - clarification_topic_coverage  fraction of expected_clarification_topics (action=clarify)
  - refusal_clean                 reuses chat_evals.classify (action=refuse)

A scenario passes only if every turn passes every applicable dimension.
Writes a Markdown report to wiki/_evals/baseline_chat_scenarios.md.

Usage:
    python3 -m tools.chat_scenarios
    python3 tools/chat_scenarios.py -v        # show full responses
    python3 tools/chat_scenarios.py --limit 3 # only run first N scenarios
    python3 tools/chat_scenarios.py --no-write  # skip writing the markdown report

Requires ANTHROPIC_API_KEY and VOYAGE_API_KEY in env.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from anthropic import Anthropic  # noqa: E402

from tools.chat.server import (  # noqa: E402
    MODEL,
    SYSTEM_PROMPT,
    TOP_K,
    _build_context,
    detect_history_state,
    detect_state,
)
from tools.chat_evals import REFUSAL_RE  # noqa: E402
from tools.search import search_pages  # noqa: E402

SCENARIOS_FILE = REPO / "wiki" / "_evals" / "chat_scenarios.yaml"
REPORT_FILE = REPO / "wiki" / "_evals" / "baseline_chat_scenarios.md"

# Heuristic clarification detection. Loose by design: we'd rather catch a true
# clarify and risk classifying an answer-with-question as clarify than miss
# clarifications entirely. The trailing-`?` check filters most pure answers.
CLARIFY_PATTERNS = [
    r"\bcould you (?:clarify|specify|tell me|provide|share)\b",
    r"\bcan you (?:clarify|specify|tell me|provide|share)\b",
    r"\bwhich (?:state|product|line of business|lob|coverage|carrier|form)\b",
    r"\bwhat (?:state|product|line of business|lob|coverage|carrier)\b",
    r"\bto (?:answer|help|address)(?: this| that)?,? I('| a)?(?:m | )?(?:need|require|would need)\b",
    r"\bI (?:need|would need|'?d need|will need) (?:more |additional )?(?:information|context|details|clarification)\b",
    r"\b(?:please )?(?:specify|clarify|provide)\b.*\?",
    r"\bdo you mean\b",
    r"\bare you (?:asking about|referring to)\b",
]
CLARIFY_RE = re.compile("|".join(CLARIFY_PATTERNS), re.IGNORECASE)


# ----------------- YAML parser (stdlib-only, minimal subset) -----------------

def _strip_comment(line: str) -> str:
    # Split on " #" outside quotes; conservative for our content.
    in_str = False
    q = ""
    for i, ch in enumerate(line):
        if in_str:
            if ch == q:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            q = ch
            continue
        if ch == "#" and (i == 0 or line[i - 1].isspace()):
            return line[:i].rstrip()
    return line


def _scalar(val: str):
    v = val.strip()
    if not v:
        return ""
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if v.lower() in ("null", "~"):
        return None
    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        return v


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_yaml(text: str):
    """Parse a strict subset of YAML used by chat_scenarios.yaml.

    Supports:
      - top-level scalars        (key: value)
      - top-level mappings       (key:\n  subkey: value)
      - top-level lists          (key:\n  - value)
      - lists of mappings        (key:\n  - id: x\n    field: y)
      - nested mappings          (arbitrary depth, indent-based)
      - scalar values            string (quoted/unquoted), int, float, bool, null

    Does NOT support: flow-style (inline {} or []), multiline strings, anchors,
    tags, complex keys. Sufficient for our scenarios file; rejects anything else.
    """
    raw = [_strip_comment(l) for l in text.split("\n")]
    # Keep position-aware lines, dropping blanks and pure comments.
    lines = [(i, l) for i, l in enumerate(raw) if l.strip() and not l.lstrip().startswith("#")]

    pos = [0]

    def peek():
        if pos[0] >= len(lines):
            return None
        return lines[pos[0]]

    def consume():
        item = lines[pos[0]]
        pos[0] += 1
        return item

    def parse_block(min_indent: int):
        """Parse a mapping or list whose items live at indent >= min_indent."""
        item = peek()
        if item is None:
            return None
        _, first = item
        first_indent = _indent_of(first)
        if first_indent < min_indent:
            return None
        if first.lstrip().startswith("- "):
            return parse_list(first_indent)
        return parse_mapping(first_indent)

    def parse_mapping(indent: int):
        result = {}
        while True:
            item = peek()
            if item is None:
                return result
            _, line = item
            cur_indent = _indent_of(line)
            if cur_indent < indent:
                return result
            if cur_indent > indent:
                # Should have been consumed by a child parser already.
                raise ValueError(f"Unexpected indent at line: {line!r}")
            if line.lstrip().startswith("- "):
                # End of mapping; caller (list) will handle.
                return result
            key, _, rest = line.lstrip().partition(":")
            if not key or "" == _:
                raise ValueError(f"Bad mapping line: {line!r}")
            consume()
            rest = rest.strip()
            if rest == "":
                # Value is a block (mapping or list) at deeper indent.
                child = parse_block(indent + 1)
                result[key] = child if child is not None else {}
            else:
                result[key] = _scalar(rest)

    def parse_list(indent: int):
        result = []
        while True:
            item = peek()
            if item is None:
                return result
            _, line = item
            cur_indent = _indent_of(line)
            if cur_indent < indent:
                return result
            if cur_indent > indent:
                raise ValueError(f"Unexpected indent in list at: {line!r}")
            stripped = line.lstrip()
            if not stripped.startswith("- "):
                return result
            consume()
            after_dash = stripped[2:]
            after_indent = indent + 2  # column where after-dash content begins
            if after_dash.strip() == "":
                # Block list item: child block follows on next lines.
                child = parse_block(indent + 1)
                result.append(child if child is not None else {})
                continue
            if ":" in after_dash and not after_dash.startswith('"') and not after_dash.startswith("'"):
                # First key:value of a mapping list-item. Stitch the rest at column after_indent.
                key, _, rest = after_dash.partition(":")
                key = key.strip()
                rest = rest.strip()
                first_pair = (key, rest)
                # Now collect any further mapping fields at indent == after_indent.
                # We need to parse a synthesized mapping starting with first_pair.
                # Build the dict by hand:
                obj = {}
                if rest == "":
                    # First field's value is a nested block.
                    child = parse_block(after_indent + 1)
                    obj[key] = child if child is not None else {}
                else:
                    obj[key] = _scalar(rest)
                # Continue to consume subsequent lines at after_indent that belong to this item.
                while True:
                    nxt = peek()
                    if nxt is None:
                        break
                    _, l2 = nxt
                    ci2 = _indent_of(l2)
                    if ci2 < after_indent:
                        break
                    if ci2 > after_indent:
                        raise ValueError(f"Unexpected indent inside list-item mapping: {l2!r}")
                    s2 = l2.lstrip()
                    if s2.startswith("- "):
                        # New top-level list item at this indent — but we're inside
                        # a mapping; this means our mapping is done.
                        break
                    k2, _sep, r2 = s2.partition(":")
                    if not k2 or _sep != ":":
                        break
                    consume()
                    k2 = k2.strip()
                    r2 = r2.strip()
                    if r2 == "":
                        child = parse_block(after_indent + 1)
                        obj[k2] = child if child is not None else {}
                    else:
                        obj[k2] = _scalar(r2)
                result.append(obj)
                continue
            # Plain scalar list item: "- value"
            result.append(_scalar(after_dash))

    return parse_mapping(0)


# ----------------- Retrieval (mirrors server.py) -----------------

def ask_one_turn(client: Anthropic, messages: list, top_k: int = TOP_K):
    """Call retrieval + Anthropic on the FULL message history.

    Mirrors server.py exactly, including the Phase 2 history-state fallback:
    if the latest user message has no state token, inherit from the most recent
    prior user message that did. Returns (sources, answer).
    """
    last_user = next(
        (m["content"] for m in reversed(messages) if m.get("role") == "user"),
        "",
    )
    state = detect_state(last_user) or detect_history_state(messages)
    raw = search_pages(last_user, top_k=top_k * 2, mode="hybrid")
    if state:
        # Three-tier sort matches server.py: state-match first, then state-
        # agnostic multistate, then other-state. Required for inherited state
        # to actually surface state-specific content.
        match = [h for h in raw if h.get("state") == state]
        agnostic = [h for h in raw if not h.get("state")]
        other = [h for h in raw if h.get("state") and h.get("state") != state]
        hits = (match + agnostic + other)[:top_k]
    else:
        hits = raw[:top_k]

    system = SYSTEM_PROMPT.format(context=_build_context(hits))
    msg = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    sources = [
        {
            "id": i + 1,
            "path": h["path"],
            "heading": h.get("heading") or "",
            "state": h.get("state") or "",
            "product": h.get("product") or "",
            "type": h.get("type") or "",
        }
        for i, h in enumerate(hits)
    ]
    return sources, text


# ----------------- Action classifier -----------------

def classify_action(response: str) -> str:
    """Priority order: refuse > clarify > answer.

    Refusal detection is citation-aware: the v1 baseline showed that the dominant
    classifier failure was hedging tails ("the excerpts do not provide every
    detail ...") on otherwise correct, well-cited answers. So we only call it a
    refusal when EITHER the response carries no `[N]` citation markers (the
    model didn't think it could answer) OR the refusal phrase appears in the
    first ~200 chars (the model led with "I can't answer this"). A refusal
    phrase 1500 chars in, after several `[1]`/`[2]` citations, is a tail.

    Clarify if the response asks for missing context AND ends with `?` (or
    contains a clarification phrase). Otherwise, answer.
    """
    text = response.strip()
    has_citations = bool(re.search(r"\[\d+\]", text))
    refusal_match = REFUSAL_RE.search(text)
    is_refusal = refusal_match is not None and (
        not has_citations or refusal_match.start() < 200
    )
    if is_refusal:
        return "refuse"
    has_q = "?" in text
    if has_q and CLARIFY_RE.search(text):
        return "clarify"
    return "answer"


# ----------------- Per-turn scoring -----------------

def _frac(found: int, total: int) -> float:
    return 1.0 if total == 0 else found / total


def score_turn(turn: dict, sources: list, answer: str, prior_sources: list) -> dict:
    """Return a dict with per-dimension pass/fail and supporting numbers."""
    expected = turn.get("expected_action", "answer")
    actual = classify_action(answer)
    dims = {"action_match": {"applied": True, "expected": expected, "actual": actual,
                              "pass": expected == actual}}

    src_paths = [s["path"] for s in sources]

    if expected == "answer":
        must = turn.get("expected_must_cite") or []
        opt = turn.get("expected_optional_cite") or []
        topics = turn.get("expected_topics") or []
        must_hit = [p for p in must if p in src_paths]
        opt_hit = [p for p in opt if p in src_paths]
        topic_hit = [t for t in topics if t.lower() in answer.lower()]

        dims["must_cite_recall"] = {
            "applied": True,
            "found": len(must_hit), "total": len(must),
            "missed": [p for p in must if p not in src_paths],
            "pass": len(must_hit) == len(must),
        }
        dims["optional_cite_recall"] = {
            "applied": bool(opt),
            "found": len(opt_hit), "total": len(opt),
            "pass": True,  # never gates scenario pass
        }
        dims["topic_coverage"] = {
            "applied": bool(topics),
            "found": len(topic_hit), "total": len(topics),
            "missed": [t for t in topics if t.lower() not in answer.lower()],
            "pass": len(topic_hit) == len(topics),
        }
    else:
        dims["must_cite_recall"] = {"applied": False}
        dims["optional_cite_recall"] = {"applied": False}
        dims["topic_coverage"] = {"applied": False}

    inherits = turn.get("inherits_entities") or {}
    if inherits and expected == "answer":
        per_facet = {}
        all_pass = True
        for facet, value in inherits.items():
            if facet == "state":
                hit = any(s.get("state") == value for s in sources)
            elif facet == "lob":
                hit = any(s.get("product") == value for s in sources)
            else:
                # Unknown facet — skip but don't fail.
                continue
            per_facet[f"{facet}={value}"] = hit
            if not hit:
                all_pass = False
        dims["entity_inheritance"] = {"applied": True, "facets": per_facet, "pass": all_pass}
    else:
        dims["entity_inheritance"] = {"applied": False}

    if expected == "clarify":
        topics = turn.get("expected_clarification_topics") or []
        topic_hit = [t for t in topics if t.lower() in answer.lower()]
        dims["clarification_topic_coverage"] = {
            "applied": True,
            "found": len(topic_hit), "total": len(topics),
            "missed": [t for t in topics if t.lower() not in answer.lower()],
            "pass": len(topic_hit) == len(topics),
        }
    else:
        dims["clarification_topic_coverage"] = {"applied": False}

    if expected == "refuse":
        dims["refusal_clean"] = {"applied": True, "pass": actual == "refuse"}
    else:
        dims["refusal_clean"] = {"applied": False}

    return dims


def turn_passed(dims: dict) -> bool:
    """A turn passes only if every applied gating dimension passes.

    Optional-cite is non-gating. All other applied dimensions are gating.
    """
    for name, d in dims.items():
        if not d.get("applied"):
            continue
        if name == "optional_cite_recall":
            continue
        if not d.get("pass", False):
            return False
    return True


# ----------------- Runner -----------------

def run_scenario(client: Anthropic, scenario: dict, top_k: int, verbose: bool):
    sid = scenario.get("id", "?")
    turns_in = scenario.get("turns") or []
    messages: list[dict] = []
    sources_history: list[list] = []
    turn_results = []

    for turn in turns_in:
        question = turn.get("question", "")
        messages.append({"role": "user", "content": question})
        try:
            sources, answer = ask_one_turn(client, messages, top_k=top_k)
        except Exception as e:
            turn_results.append({
                "turn": turn.get("turn"),
                "question": question,
                "error": str(e),
                "dims": {},
                "sources": [],
                "answer": "",
                "pass": False,
            })
            # Don't continue the conversation if a turn errored.
            break
        messages.append({"role": "assistant", "content": answer})
        sources_history.append(sources)
        dims = score_turn(turn, sources, answer, sources_history[:-1])
        turn_results.append({
            "turn": turn.get("turn"),
            "question": question,
            "expected_action": turn.get("expected_action"),
            "dims": dims,
            "sources": sources,
            "answer": answer,
            "pass": turn_passed(dims),
        })
        if verbose:
            print(f"\n  [{sid} t{turn.get('turn')}] {question}")
            print(f"     -> {answer[:300]}{'...' if len(answer) > 300 else ''}")

    scenario_pass = all(t["pass"] for t in turn_results) and len(turn_results) == len(turns_in)
    return {
        "id": sid,
        "cq_category": scenario.get("cq_category", "-"),
        "role": scenario.get("role", "-"),
        "description": scenario.get("description", ""),
        "turns": turn_results,
        "pass": scenario_pass,
    }


# ----------------- Reporter -----------------

def _short(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def _dim_cell(d: dict) -> str:
    if not d.get("applied"):
        return "—"
    if "found" in d:
        mark = "✓" if d.get("pass") else "✗"
        return f"{mark} {d['found']}/{d['total']}"
    return "✓" if d.get("pass") else "✗"


def print_console(results, top_k):
    print(f"Chat scenarios: {SCENARIOS_FILE}   model={MODEL}   top_k={top_k}")
    print(f"Scenarios: {len(results)}   total turns: {sum(len(r['turns']) for r in results)}")
    print()
    header = f"{'SCEN':<6} {'TRN':<3} {'CAT':<11} {'ROLE':<7} {'EXP':<8} {'ACT':<8} {'MUST':<8} {'TOPIC':<8} {'INHERIT':<8} {'CLAR':<8} {'REF':<5} {'PASS':<5}"
    print(header)
    print("-" * len(header))
    for r in results:
        for t in r["turns"]:
            d = t.get("dims", {}) or {}
            am = d.get("action_match", {})
            print(
                f"{r['id']:<6} {str(t.get('turn','?')):<3} {_short(r['cq_category'],11):<11} "
                f"{_short(r['role'],7):<7} {_short(am.get('expected','-'),8):<8} "
                f"{_short(am.get('actual','-'),8):<8} "
                f"{_dim_cell(d.get('must_cite_recall', {})):<8} "
                f"{_dim_cell(d.get('topic_coverage', {})):<8} "
                f"{_dim_cell(d.get('entity_inheritance', {})):<8} "
                f"{_dim_cell(d.get('clarification_topic_coverage', {})):<8} "
                f"{_dim_cell(d.get('refusal_clean', {})):<5} "
                f"{('PASS' if t['pass'] else 'FAIL'):<5}"
            )
            if t.get("error"):
                print(f"        ERROR: {t['error']}")
    print("-" * len(header))
    agg = aggregate(results)
    print(
        f"Scenarios passed: {agg['scen_pass']}/{agg['scen_total']}   "
        f"Action accuracy: {agg['action_pass']}/{agg['action_total']} ({agg['action_pct']:.0%})"
    )
    print(
        f"Must-cite recall: {agg['must_found']}/{agg['must_total']} ({agg['must_pct']:.0%})   "
        f"Optional-cite recall: {agg['opt_found']}/{agg['opt_total']} ({agg['opt_pct']:.0%})"
    )
    print(
        f"Topic coverage: {agg['topic_found']}/{agg['topic_total']} ({agg['topic_pct']:.0%})   "
        f"Entity inheritance: {agg['inh_pass']}/{agg['inh_total']} ({agg['inh_pct']:.0%})"
    )
    print(
        f"Clarification quality: {agg['clar_found']}/{agg['clar_total']} ({agg['clar_pct']:.0%})   "
        f"Refusal correctness: {agg['ref_pass']}/{agg['ref_total']} ({agg['ref_pct']:.0%})"
    )


def aggregate(results):
    out = {
        "scen_pass": sum(1 for r in results if r["pass"]),
        "scen_total": len(results),
        "action_pass": 0, "action_total": 0,
        "must_found": 0, "must_total": 0,
        "opt_found": 0, "opt_total": 0,
        "topic_found": 0, "topic_total": 0,
        "inh_pass": 0, "inh_total": 0,
        "clar_found": 0, "clar_total": 0,
        "ref_pass": 0, "ref_total": 0,
    }
    for r in results:
        for t in r["turns"]:
            d = t.get("dims", {}) or {}
            am = d.get("action_match")
            if am and am.get("applied"):
                out["action_total"] += 1
                if am.get("pass"):
                    out["action_pass"] += 1
            for src, dest_f, dest_t in [
                ("must_cite_recall", "must_found", "must_total"),
                ("optional_cite_recall", "opt_found", "opt_total"),
                ("topic_coverage", "topic_found", "topic_total"),
                ("clarification_topic_coverage", "clar_found", "clar_total"),
            ]:
                dim = d.get(src) or {}
                if dim.get("applied") and "found" in dim:
                    out[dest_f] += dim["found"]
                    out[dest_t] += dim["total"]
            inh = d.get("entity_inheritance") or {}
            if inh.get("applied"):
                out["inh_total"] += 1
                if inh.get("pass"):
                    out["inh_pass"] += 1
            ref = d.get("refusal_clean") or {}
            if ref.get("applied"):
                out["ref_total"] += 1
                if ref.get("pass"):
                    out["ref_pass"] += 1
    for src_f, src_t, dest_pct in [
        ("action_pass", "action_total", "action_pct"),
        ("must_found", "must_total", "must_pct"),
        ("opt_found", "opt_total", "opt_pct"),
        ("topic_found", "topic_total", "topic_pct"),
        ("inh_pass", "inh_total", "inh_pct"),
        ("clar_found", "clar_total", "clar_pct"),
        ("ref_pass", "ref_total", "ref_pct"),
    ]:
        out[dest_pct] = (out[src_f] / out[src_t]) if out[src_t] else 0.0
    return out


def write_markdown(results, top_k):
    agg = aggregate(results)
    lines = []
    lines.append("# Phase 0 Baseline — Chat Scenarios")
    lines.append("")
    lines.append(f"Run date: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"Model: {MODEL}   top_k: {top_k}")
    lines.append(f"Scenarios: {len(results)}   Total turns: {sum(len(r['turns']) for r in results)}")
    lines.append("")
    lines.append("## Headline finding")
    lines.append("")
    lines.append(
        f"Retrieval is healthy ({agg['must_pct']:.0%} must-cite recall, "
        f"{agg['topic_pct']:.0%} topic coverage), but only "
        f"{agg['action_pct']:.0%} of turns are classified with the expected action. "
        "Inspection of failing turns shows the model usually answers correctly with the right citations, "
        "then tails off with hedging language (\"the excerpts do not provide every detail …\") that trips REFUSAL_RE. "
        "The brittleness of the heuristic refusal classifier — flagged in the Phase 0 plan — dominates the failure list. "
        "True multi-turn failures (forgotten state on a follow-up, no clarification on under-specified Qs) "
        "are visible separately in `entity_inheritance` and `action_match` on s006 t1."
    )
    lines.append("")
    lines.append("## Aggregate metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Scenarios passed (strict: every turn passes every applied dimension) | {agg['scen_pass']}/{agg['scen_total']} |")
    lines.append(f"| Action-classification accuracy | {agg['action_pass']}/{agg['action_total']} ({agg['action_pct']:.0%}) |")
    lines.append(f"| Must-cite recall | {agg['must_found']}/{agg['must_total']} ({agg['must_pct']:.0%}) |")
    lines.append(f"| Optional-cite recall | {agg['opt_found']}/{agg['opt_total']} ({agg['opt_pct']:.0%}) |")
    lines.append(f"| Topic coverage (substring) | {agg['topic_found']}/{agg['topic_total']} ({agg['topic_pct']:.0%}) |")
    lines.append(f"| Entity inheritance (turns where source reflects inherited facet) | {agg['inh_pass']}/{agg['inh_total']} ({agg['inh_pct']:.0%}) |")
    lines.append(f"| Clarification topic coverage | {agg['clar_found']}/{agg['clar_total']} ({agg['clar_pct']:.0%}) |")
    lines.append(f"| Refusal correctness | {agg['ref_pass']}/{agg['ref_total']} ({agg['ref_pct']:.0%}) |")
    lines.append("")

    lines.append("## Per-scenario results")
    lines.append("")
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        lines.append(f"### {r['id']} — {status} ({r['cq_category']} / {r['role']})")
        lines.append(f"_{r['description']}_")
        lines.append("")
        lines.append("| Turn | Q | Expected | Actual | Must | Topics | Inherit | Clar | Ref | Pass |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for t in r["turns"]:
            d = t.get("dims", {}) or {}
            am = d.get("action_match", {})
            q = (t.get("question") or "").replace("|", "\\|")
            q = q if len(q) <= 60 else q[:57] + "..."
            lines.append(
                f"| {t.get('turn','?')} | {q} | "
                f"{am.get('expected','-')} | {am.get('actual','-')} | "
                f"{_dim_cell(d.get('must_cite_recall', {}))} | "
                f"{_dim_cell(d.get('topic_coverage', {}))} | "
                f"{_dim_cell(d.get('entity_inheritance', {}))} | "
                f"{_dim_cell(d.get('clarification_topic_coverage', {}))} | "
                f"{_dim_cell(d.get('refusal_clean', {}))} | "
                f"{'✓' if t['pass'] else '✗'} |"
            )
        lines.append("")

    lines.append("## Failure diagnostics")
    lines.append("")
    failures = []
    for r in results:
        for t in r["turns"]:
            if t["pass"]:
                continue
            d = t.get("dims", {}) or {}
            for name, dim in d.items():
                if not dim.get("applied") or name == "optional_cite_recall":
                    continue
                if dim.get("pass"):
                    continue
                failures.append((r["id"], t.get("turn"), name, dim, t.get("question", ""), t.get("sources", [])))
    if not failures:
        lines.append("_No failing dimensions._")
    else:
        for sid, tid, name, dim, q, srcs in failures[:30]:
            src_paths = [s["path"] for s in srcs]
            lines.append(f"- **{sid} t{tid}** [{name}] — Q: _{q}_")
            if name == "must_cite_recall":
                lines.append(f"  - missed: `{dim.get('missed')}`")
                lines.append(f"  - top-{len(src_paths)} retrieved: `{src_paths}`")
            elif name == "topic_coverage":
                lines.append(f"  - missed substrings: `{dim.get('missed')}`")
            elif name == "entity_inheritance":
                lines.append(f"  - facets: `{dim.get('facets')}`")
                lines.append(f"  - retrieved states: `{sorted({s.get('state') for s in srcs if s.get('state')})}`   products: `{sorted({s.get('product') for s in srcs if s.get('product')})}`")
            elif name == "clarification_topic_coverage":
                lines.append(f"  - missed substrings: `{dim.get('missed')}`")
            elif name == "action_match":
                lines.append(f"  - expected `{dim.get('expected')}`, got `{dim.get('actual')}`")
            elif name == "refusal_clean":
                lines.append(f"  - did not match REFUSAL_RE — likely fabricated or partial-answer")
    lines.append("")

    lines.append("## What this baseline implies for later phases")
    lines.append("")
    lines.append("- Phase 1 (agent loop) targets `must_cite_recall` and `topic_coverage`.")
    lines.append("- Phase 2 (session entity memory) targets `entity_inheritance`.")
    lines.append("- Phase 3 (slot-filling) targets `action_match` on underspecified turns and `clarification_topic_coverage`.")
    lines.append("- Phase 4 (structured store + relations) targets the metadata-style queries (s008) and structural lookups.")
    lines.append("- Phase 5 (carrier dimension) is what would lift `refusal_clean` from \"correct refusal\" to \"correct answer\" on s007.")
    lines.append("")
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {REPORT_FILE}")


# ----------------- Main -----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=TOP_K)
    ap.add_argument("--limit", type=int, default=0, help="run only the first N scenarios")
    ap.add_argument("--no-write", action="store_true", help="skip writing the markdown report")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if not SCENARIOS_FILE.exists():
        print(f"No scenarios at {SCENARIOS_FILE}", file=sys.stderr)
        return 1
    parsed = parse_yaml(SCENARIOS_FILE.read_text(encoding="utf-8"))
    scenarios = parsed.get("scenarios") or []
    if args.limit > 0:
        scenarios = scenarios[: args.limit]
    if not scenarios:
        print("No scenarios in chat_scenarios.yaml")
        return 0

    client = Anthropic()
    results = []
    for s in scenarios:
        results.append(run_scenario(client, s, top_k=args.top, verbose=args.verbose))

    print_console(results, args.top)
    if not args.no_write:
        write_markdown(results, args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
