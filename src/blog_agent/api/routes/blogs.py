"""Blog generation endpoints (synchronous + streaming)."""

from __future__ import annotations
import json
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from blog_agent.api.models import GenerateBlogRequest, GenerateBlogResponse
from blog_agent.pipeline import generate_blog, stream_blog
from blog_agent.core import get_logger, BlogAgentError

logger = get_logger(__name__)
router = APIRouter(prefix="/blogs", tags=["blogs"])


def _to_response(topic: str, state: dict[str, Any]) -> GenerateBlogResponse:
    return GenerateBlogResponse(
        topic = topic,
        mode = state.get("mode"),
        plan = state.get("plan"),
        evidence = state.get("evidence", []) or [],
        markdown = state.get("final", "") or "",
        output_path = state.get("output_path")
    ) 


@router.post("", response_model=GenerateBlogResponse)
def create_blog(request: GenerateBlogRequest) -> GenerateBlogResponse:
    """Generate a blog and return the full result once complete."""
    try:
        state = generate_blog(topic=request.topic, as_of=request.as_of)
    except BlogAgentError as exc:
        logger.warning("api.generate_failed", error=str(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return _to_response(request.topic, state)

@router.post("/stream")
def create_blog_stream(request: GenerateBlogRequest) -> StreamingResponse:
    def event_stream():
        for update in stream_blog(topic=request.topic, as_of=request.as_of):
            yield json.dumps(update, default=str) + "\n"
    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
