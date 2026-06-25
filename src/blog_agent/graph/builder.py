"""Assemble and compile the full agent graph."""

from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from blog_agent.graph.nodes import (
    orchestrator_node,
    fan_out,
    worker_node,
    merge_content_node,
    router_node,
    route_next,
    research_node
)
# from blog_agent.graph.nodes import fan_out, worker_node
# from blog_agent.graph.nodes.merge import merge_content_node
# from blog_agent.graph.nodes.router import router_node, route_next
# from blog_agent.graph.nodes.research import research_node
from blog_agent.schemas import BlogState

def build_graph():
    g = StateGraph(BlogState)
    g.add_node("router", router_node)
    g.add_node("research", research_node)
    g.add_node("orchestrator", orchestrator_node)
    g.add_node("worker", worker_node)
    g.add_node("merge", merge_content_node)

    g.add_edge(START, "router")
    g.add_conditional_edges("router", route_next, {"research": "research", "orchestrator": "orchestrator"})
    g.add_edge("research", "orchestrator")
    g.add_conditional_edges("orchestrator", fan_out, ["worker"])
    g.add_edge("worker", "merge")
    g.add_edge("merge", END)
    return g.compile()