"""The shared LangGraph state that flows through every node."""

from __future__ import annotations
import operator
from typing import Annotated, TypedDict
from pydantic import Field, BaseModel
from blog_agent.schemas.blog import Plan
from blog_agent.schemas.research import EvidenceItem

class BlogState(TypedDict, total=False): #total=False means every key in the TypedDict is optional 
    # Input
    topic: str
    as_of: str  # ISO date the post is written "as of"
    
    # Routing / Reserach
    mode: str
    needs_research: bool
    queries: list[str]
    recency_days: int 
    evidence: list[EvidenceItem]

    # Planning
    plan: Plan | None

    # Workers (concurrent append)
    sections: Annotated[list[tuple[int, str]], operator.add] # (task_id, markdown)

    # Reducer / images
    merged_md: str
    md_with_placeholders: str
    image_specs: list[dict]

    # output
    final: str
    output_path: str
