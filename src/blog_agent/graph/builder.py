"""Assemble and compile the full agent graph."""

from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from blog_agent.graph.nodes.orchestrator import orchestrator_node
from blog_agent.graph.nodes.worker import fan_out, worker_node
from blog_agent.graph.nodes.merge import merge_content_node
from blog_agent.schemas import BlogState

def build_graph():
    g = StateGraph(BlogState)
    g.add_node("orchestrator",orchestrator_node)
    g.add_node("worker", worker_node)
    g.add_node("merge", merge_content_node)
    g.add_edge(START, "orchestrator")
    g.add_conditional_edges("orchestrator", fan_out, ["worker"])
    g.add_edge("worker", "merge")
    g.add_edge("merge", END)
    return g.compile()