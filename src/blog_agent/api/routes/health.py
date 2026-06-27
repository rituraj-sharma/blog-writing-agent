from fastapi import APIRouter
from blog_agent import __version__
from blog_agent.api.models import HealthResponse

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(version=__version__)


