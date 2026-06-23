"""Orchestrator node: turn topic + evidence into a structured Plan."""

from __future__ import annotations
from langchain_core.messages import HumanMessage, SystemMessage
from blog_agent.llm import get_llm
from blog_agent.prompts import ORCHESTRATOR_PROMPT
from blog_agent.schemas import BlogState, Plan

def orchestrator_node(state: BlogState) -> dict:
    mode = state.get("mode", "closed_book")
    evidence = state.get("evidence", []) or [] # or [] for evidence=None
    forced_kind = mode == "open_book"
    force_note = "FORCE blog_kind=news_roundup" if forced_kind else ""
    # evidence_str = str([e.model_dump() for e in evidence][:16])

    evidence_str = "\n".join(
        f"- {e.title} | {e.url} | {e.published_at or 'date:unknown'}" for e in evidence[:20]
    ) or "None"

    chain = ORCHESTRATOR_PROMPT | get_llm().with_structured_output(Plan)
    plan: Plan = chain.invoke({
        "topic": state["topic"],
        "mode": mode,
        "as_of": state["as_of"],
        "recency_days": state["recency_days"],
        "force_note": force_note,
        "evidence": evidence_str
    })

    if forced_kind: plan.blog_kind = "news_roundup"
    return {"plan": plan}

