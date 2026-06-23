"""Schemas for the routing + research stage."""

from __future__ import annotations
from typing import Literal
from pydantic import Field, BaseModel

RountingMode = Literal["closed_book", "hybrid", "open_book"]

class RouterDecision(BaseModel):
    needs_research: bool
    mode: RountingMode
    reason: str
    queries: list[str] = Field(default_factory=list)
    max_results_per_query: int = 5

class EvidenceItem(BaseModel):
    title: str
    url: str
    published_at: str | None = None  # ISO date, optional
    snipped: str | None = None
    source: str | None = None

class EvidencePack(BaseModel):
    evidence: list[EvidenceItem] = Field(default_factory=list)
