"""Web search service.

The graph depends on the ``SearchService`` protocol, not on vendor  directly, so
the provider can be swapped (Tavily → SerpAPI) without touching node logic.
"""

from __future__ import annotations
from typing import Protocol
from blog_agent.core import get_settings, get_logger
from urllib.parse import urlparse

logger = get_logger(__name__)

def _source_from_url(url: str) -> str | None:
    netloc = urlparse(url).netloc        # "www.llm-stats.com"
    return netloc.removeprefix("www.") or None   # "llm-stats.com"


class SearchService(Protocol):
    enabled: bool
    def search(self, query: str, max_results: int, recent: bool) -> list[dict]: ...


class TavilySearchService():
    """Tavily search implementation. Normalizes to common result shape to make it vendor agnostic."""

    def __init__(self, api_key: str | None) -> None:
        self._api_key = api_key

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    def search(self, query: str, max_results: int = 5, recent: bool = False) -> list[dict]:
        if not self.enabled: 
            logger.debug("search.skipped", reason="no_tavily_key", query=query)
            return []
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self._api_key)
            resp = client.search(
                query, 
                max_results=max_results,
                topic="news" if recent else "general",
                include_raw_content=False,   # never pull full page text (huge)
            )

            return [self._normalize(r) for r in resp.get("results", []) or []]
        except Exception as exc:
            logger.warning("search.failed", query=query, error=str(exc))
            return []

    @staticmethod
    def _normalize(r: dict) -> dict:
        url = r.get("url", "")
        return {
                "title": r.get("title", ""),
                "url": url,
                "published_at": r.get("published_date"),
                "snippet": r.get("content"),
                "source": _source_from_url(url),
                "score": r.get("score"),
            }
    
def get_search_service() -> SearchService:
    return TavilySearchService(api_key=get_settings().tavily_api_key)



