"""Application service that wraps the compiled graph. Both the API and the CLI call this."""

from __future__ import annotations
from datetime import date
from blog_agent.graph import build_graph

_graph = build_graph()   # compile once, reuse

def _initial_state(topic: str, as_of: str | None) -> dict:
    return {
        "topic": topic.strip(),
        "as_of": as_of or date.today().isoformat(),
        "needs_research": False,
        "queries": [],
        "evidence": [],
    }

def generate_blog(topic: str, as_of: str | None = None) -> dict:
    return _graph.invoke(_initial_state(topic, as_of))