from __future__ import annotations
import json
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from blog_agent.api.models import GenerateBlogRequest, GenerateBlogResponse
from blog_agent.pipeline import generate_blog, stream_blog

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
    state = generate_blog(topic=request.topic, as_of=request.as_of)
    return _to_response(request.topic, state)

@router.post("/stream")
def create_blog_stream(request: GenerateBlogRequest) -> StreamingResponse:
    def event_stream():
        for update in stream_blog(topic=request.topic, as_of=request.as_of):
            yield json.dumps(update, default=str) + "\n"
    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
