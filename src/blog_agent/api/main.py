"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from blog_agent.core import get_settings, configure_logging, get_logger, BlogAgentError
from blog_agent import __version__
from blog_agent.api.routes import health_router, blogs_router

def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    logger = get_logger(__name__)

    app = FastAPI(
        title="Blog Writing Agent API", 
        version=__version__,
        summary="Multi-agent technical blog generator built on LangGraph.",
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
    app.include_router(health_router)
    app.include_router(blogs_router)

    @app.exception_handler(BlogAgentError)
    async def _domain_error_handler(_request, exc: BlogAgentError):  # noqa: ANN001
        from fastapi.responses import JSONResponse

        logger.warning("api.domain_error", error=str(exc))
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    logger.info("api.started", version=__version__)
    return app 

app = create_app()