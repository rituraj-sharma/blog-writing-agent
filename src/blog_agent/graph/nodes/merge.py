"""Reducer subgraph nodes: merge sections → decide images → generate & persist."""

from __future__ import annotations
from pathlib import Path
from blog_agent.schemas import BlogState
from blog_agent.services import get_storage

def merge_content_node(state: BlogState) -> dict:
    plan = state['plan']
    assert plan is not None
    storage = get_storage()

    ordered = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered).strip()
    merged = f"# {plan.blog_title}\n\n{body}\n"

    output_path = storage.write_markdown(plan.blog_title, merged)
    return {"merged_md": merged, "output_path": str(output_path)}

