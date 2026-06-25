"""Worker node + fan-out: each task becomes one blog section, written in parallel."""

from __future__ import annotations
from langchain_core.output_parsers import StrOutputParser
from langgraph.types import Send
from blog_agent.core import get_settings
from blog_agent.llm import get_llm
from blog_agent.prompts import WORKER_PROMPT
from blog_agent.schemas import BlogState, Plan, Task

def fan_out(state: BlogState) -> list[Send]:
    plan = state["plan"]
    assert plan is not None
    return [
        Send(
            "worker",
            {
                "task": task.model_dump(),
                "topic": state["topic"],
                "mode": state["mode"],
                "as_of": state["as_of"],
                "recency_days": state["recency_days"],
                "plan": plan.model_dump(),
                "evidence": [e.model_dump() for e in state.get("evidence", [])]
            },
        )
        for task in state["plan"].tasks
    ]

# model_dump() flattens the object to send it; Model(**dict) re-inflates it to use it. 
# The ** is just the mechanism that feeds the dict's fields into the constructor as keyword arguments.

def worker_node(payload: dict) -> dict:
    settings = get_settings()
    task = Task(**payload["task"])
    plan = Plan(**payload["plan"])
    evidence_text = "\n".join(
        f"- {e['title']} | {e['url']} | {e.get('published_at') or 'date:unknown'}"
        for e in payload["evidence"][:settings.research_max_evidences_total]
    ) or "None"

    chain = WORKER_PROMPT | get_llm() | StrOutputParser()
    section_md = chain.invoke({
        "blog_title": plan.blog_title,
        "audience": plan.audience,
        "tone": plan.tone,
        "blog_kind": plan.blog_kind,
        "constraints": plan.constraints,
        "topic": payload["topic"],
        "mode": payload["mode"],
        "as_of": payload["as_of"],
        "recency_days": payload["recency_days"],
        "section_title": task.title,
        "goal": task.goal,
        "target_words": task.target_words,
        "tags": task.tags,
        "requires_research": task.requires_research,
        "requires_citations": task.requires_citation,
        "requires_code": task.requires_code,
        "bullets_text": "\n".join(f"- {b}" for b in task.bullets),
        "evidence": evidence_text
    }).strip()

    return {"sections": [(task.id, section_md)]}


