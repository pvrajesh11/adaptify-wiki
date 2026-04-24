"""RAG chatbot over the Adaptify wiki.

Reuses tools.search.search_pages for retrieval, streams Claude's answer over
SSE. Run: `uvicorn tools.chat.server:app --reload --port 8000`.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

from anthropic import Anthropic
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.search import search_pages  # noqa: E402

CHAT_HTML = Path(__file__).parent / "chat.html"
MODEL = "claude-sonnet-4-6"
TOP_K = 8
MAX_TOKENS = 2000

# Full 50 states + DC. Detected in the user's last message to boost state-matching
# chunks in retrieval (without excluding multistate / concept / index pages).
STATE_NAMES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "district of columbia": "DC", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
    "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
    "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
    "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
    "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI",
    "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
    "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}
STATE_CODES = set(STATE_NAMES.values())


def detect_state(text: str) -> Optional[str]:
    """Return a two-letter state code if present, else None.

    Matches full names case-insensitively, and 2-letter codes only in uppercase
    to avoid false matches (e.g., "in" → Indiana).
    """
    lower = text.lower()
    # Longest names first so "new york" beats "new" being part of another word.
    for name, code in sorted(STATE_NAMES.items(), key=lambda x: -len(x[0])):
        if re.search(r"\b" + re.escape(name) + r"\b", lower):
            return code
    for code in STATE_CODES:
        if re.search(r"\b" + code + r"\b", text):
            return code
    return None


def detect_history_state(messages: list) -> Optional[str]:
    """Walk PRIOR user messages newest-first; return the first state token found.

    Used as a fallback when detect_state(last_user) returns None — the user
    asked a follow-up like "what about the deductibles?" without naming the
    state. Without this, retrieval drops the prior state's chunks.

    Skips the latest user message (caller already tried that via detect_state).
    Skips assistant messages — assistant text often echoes states the user did
    not commit to, which would inject phantom inheritance.
    """
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    if len(user_msgs) <= 1:
        return None
    for content in reversed(user_msgs[:-1]):
        s = detect_state(content)
        if s:
            return s
    return None

SYSTEM_PROMPT = """You are a specialist assistant for the Adaptify insurance wiki, which documents Personal Auto (PPA), Homeowners (HOBP), and Motor Truck Cargo filings across Alaska, Alabama, and Florida.

Answer using ONLY the excerpts below. Each excerpt has a numeric id, a file path, and the content. When you state a fact, cite the excerpt inline like [1] or [3]. If the excerpts don't answer the question, say so — don't guess or use outside knowledge.

Be precise about state-specific vs. multistate rules. Name the relevant form IDs (e.g., HO 0854 02 21, PPA 0154 01 20, CIM 2003 06 20) when they apply. Keep answers tight and factual.

<excerpts>
{context}
</excerpts>"""


app = FastAPI()
client = Anthropic()


class ChatRequest(BaseModel):
    messages: list[dict]


@app.get("/")
def home():
    return HTMLResponse(CHAT_HTML.read_text(encoding="utf-8"))


def _build_context(hits):
    parts = []
    for i, h in enumerate(hits, start=1):
        parts.append(
            f'<excerpt id="{i}" path="{h["path"]}" heading="{h.get("heading") or ""}">\n'
            f'{h.get("body") or ""}\n'
            f'</excerpt>'
        )
    return "\n\n".join(parts)


@app.post("/chat")
def chat(req: ChatRequest):
    last_user = next(
        (m["content"] for m in reversed(req.messages) if m.get("role") == "user"),
        "",
    )
    if not last_user:
        return {"error": "no user message"}

    # Session-memory fallback: if the latest user message has no state token,
    # inherit the most recent prior user-message state. The SSE `state` event
    # below surfaces the inherited value to the UI so the user can see what
    # state we're answering for.
    state = detect_state(last_user) or detect_history_state(req.messages)
    # Retrieve a wider pool so the state-boost re-rank has room to reorder
    # without dropping the multistate baseline. Three-tier sort: state-matched
    # chunks first (so an inherited state actually surfaces state-specific
    # content), state-agnostic multistate next (still relevant), other-state
    # last. The previous two-tier sort lumped state-matched with multistate,
    # which let multistate hits crowd out the state match — defeating the
    # purpose of inheriting the state.
    raw = search_pages(last_user, top_k=TOP_K * 2, mode="hybrid")
    if state:
        match = [h for h in raw if h.get("state") == state]
        agnostic = [h for h in raw if not h.get("state")]
        other = [h for h in raw if h.get("state") and h.get("state") != state]
        hits = (match + agnostic + other)[:TOP_K]
    else:
        hits = raw[:TOP_K]

    system = SYSTEM_PROMPT.format(context=_build_context(hits))
    sources = [
        {"id": i + 1, "path": h["path"], "heading": h.get("heading") or ""}
        for i, h in enumerate(hits)
    ]

    def gen():
        if state:
            yield f"event: state\ndata: {json.dumps({'state': state})}\n\n"
        yield f"event: sources\ndata: {json.dumps(sources)}\n\n"
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system,
                messages=[
                    {"role": m["role"], "content": m["content"]} for m in req.messages
                ],
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'delta': text})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            return
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
