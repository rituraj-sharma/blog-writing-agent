from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from blog_agent import __version__
from blog_agent.api.routes import health_router, blogs_router

def create_app() -> FastAPI:
    app = FastAPI(title="Blog Writing Agent API", version=__version__)
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
    app.include_router(health_router)
    app.include_router(blogs_router)
    return app 

app = create_app()