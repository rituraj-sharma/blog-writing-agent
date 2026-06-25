"""Reducer subgraph nodes: merge sections → decide images → generate & persist."""

from __future__ import annotations
from pathlib import Path
from blog_agent.schemas import BlogState

def merge_content_node(state: BlogState) -> dict:
    plan = state['plan']
    assert plan is not None
    ordered = [md for _, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered).strip()
    merged = f"# {plan.blog_title}\n\n{body}\n"

    Path("output").mkdir(exist_ok=True)
    out_path = Path("output") / "blog.md"
    out_path.write_text(merged, encoding="utf-8")

    return {"merged_md": merged, "output_path": str(out_path)}

