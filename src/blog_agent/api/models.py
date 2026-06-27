from __future__ import annotations
from pydantic import BaseModel, Field

from blog_agent.schemas import EvidenceItem, Plan

class GenerateBlogRequest(BaseModel):
    topic: str = Field(min_length=3, examples=["Explain the KV caching in Transformer"])
    as_of: str | None = None

class GenerateBlogResponse(BaseModel):
    topic: str
    mode: str | None = None
    plan: Plan | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    markdown: str
    output_path: str | None = None

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
