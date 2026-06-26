"""The reducer subgraph: merge → decide images → generate & place images."""

from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from blog_agent.schemas import BlogState
from blog_agent.graph.nodes import (
    merge_content_node, 
    decide_images_node, 
    generate_and_place_images_node
)

def build_reducer_subgraph():
    g = StateGraph(BlogState)
    g.add_node("merge_content", merge_content_node)
    g.add_node("decide_images", decide_images_node)
    g.add_node("generate_and_place_images", generate_and_place_images_node)

    g. add_edge(START, "merge_content")
    g.add_edge("merge_content", "decide_images")
    g.add_edge("decide_images", "generate_and_place_images")
    g.add_edge("generate_and_place_images", END)

    return g.compile()



