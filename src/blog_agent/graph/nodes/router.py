"""Router node: decide whether to research and in which mode."""

from __future__ import annotations
from blog_agent.core.config import get_settings
from blog_agent.llm import get_llm
from blog_agent.prompts import ROUTER_PROMPT
from blog_agent.schemas import RouterDecision, BlogState


def router_node(state: BlogState) -> dict:
    settings = get_settings()
    chain = ROUTER_PROMPT | get_llm().with_structured_output(RouterDecision)
    decision: RouterDecision = chain.invoke({
        "topic": state["topic"],
        "as_of": state["as_of"],
    })

    # Instead of if else, dict method is used to select recency_days
    recency_days = {
        "open_book": settings.recency_open_book_days,
        "hybrid": settings.recency_hybrid_days
    }.get(decision.mode, settings.recency_closed_book_days)

    return {
        "needs_research": decision.needs_research,
        "mode": decision.mode,
        "queries": decision.queries,
        "recency_days": recency_days
    }

def route_next(state: BlogState) -> str:
    return "research" if state["needs_research"] else "orchestrator"

