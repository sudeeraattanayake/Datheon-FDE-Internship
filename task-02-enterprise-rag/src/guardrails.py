from __future__ import annotations
import re

REFUSAL = "I cannot find sufficient authorized source evidence to answer that question."

def grounded_answer(query: str, matches: list[dict]) -> tuple[str, list[dict]]:
    """Extractive answer: only quote actual retrieved source text; never invent facts."""
    if not matches or matches[0]["rerank_score"] < -2.0:
        return REFUSAL, []
    citations = []
    excerpts = []
    for i, match in enumerate(matches[:3], 1):
        meta = match["metadata"]
        text = re.sub(r"\s+", " ", match["text"]).strip()
        if not text:
            continue
        cite = {"id": i, "source": meta["source"], "page": meta["page"],
                "department": meta["department"], "date": meta["date"],
                "excerpt": text[:900]}
        citations.append(cite)
        excerpts.append(f"[{i}] {text[:450]}")
    if not excerpts:
        return REFUSAL, []
    return "Relevant authorized source excerpts (not an independently verified synthesis):\n\n" + "\n\n".join(excerpts), citations
