"""Application service that wraps the compiled graph. Both the API and the CLI call this."""

from __future__ import annotations
from datetime import date
from typing import Any, Iterator
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

def generate_blog(topic: str, as_of: str | None = None) -> dict[str, Any]:
    """Run the full pipeline and return the final state."""
    return _graph.invoke(_initial_state(topic, as_of))

def stream_blog(topic: str, as_of: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield node-by-node updates as the graph runs."""
    yield from _graph.stream(_initial_state(topic, as_of), stream_mode="updates")