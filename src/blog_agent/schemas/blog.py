"""Schemas describing the blog outline (the orchestrator's plan)."""

from __future__ import annotations
from typing import Literal
from pydantic import Field, BaseModel

BlogKind = Literal[
    "explainer", 
    "tutorial", 
    "news_roundup",
    "comparison",
    "system_design"
]

class Task(BaseModel):
    id: int
    title: str
    goal: str = Field(..., description="One sentence: what the reader should learn.")
    bullets: list[str] = Field(..., min_length=3, max_length=6)
    target_words: int = Field(..., description="Traget words of blog (120-550)")
    tags: list[str] = Field(default_factory=list)
    requires_research: bool = False
    requires_citation: bool = False
    requires_code: bool = False

class Plan(BaseModel):
    blog_title: str
    audience: str
    tone: str
    blog_kind: BlogKind = "explainer"
    constraints: list[str] = Field(default_factory=list)
    tasks: list[Task]
