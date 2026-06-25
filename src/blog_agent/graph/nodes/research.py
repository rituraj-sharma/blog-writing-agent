"""Research node: run web search, synthesise + dedupe evidence, filter by recency."""

from __future__ import annotations
from datetime import date, timedelta
from blog_agent.core import get_settings
from blog_agent.llm import get_llm
from blog_agent.prompts import RESEARCH_PROMPT
from blog_agent.schemas import BlogState, EvidencePack
from urllib.parse import urlparse


def _source_from_url(url: str) -> str | None:
    netloc = urlparse(url).netloc        # "www.llm-stats.com"
    return netloc.removeprefix("www.") or None   # "llm-stats.com"


def _tavily_search(query: str, max_results: str, is_news: bool) -> list[dict]:
    """Run one Tavily search. Returns [] on any failure or missing key."""

    settings = get_settings()

    if not settings.tavily_enabled: return []
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.tavily_api_key)
        resp = client.search(
            query, 
            max_results=max_results,
            topic="news" if is_news else "general",
            include_raw_content=False,   # never pull full page text (huge)
        )
        results = resp["results"]

        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "published_at": r.get("published_date") or r.get("published_at"),
                "snippet": r.get("content"),
                "source": _source_from_url(r.get("url", "")),
                "score": r.get("score"),
            }
            for r in results
        ]
    except Exception as e:
        return []
    

def _iso_to_date(s: str | None) -> date | None:
    try:
        return date.fromisoformat(s[:10]) if s else None
    except:
        return None


def _compact(r: dict, snippet_max: int) -> dict:
    """Trims the snippet upto max chars."""
    r["snippet"] = r["snippet"][:snippet_max]
    return r

def research_node(state: BlogState) -> dict:
    settings = get_settings()
    is_news = state.get("mode") == "open_book"
    queries = (state.get("queries") or [])[:settings.research_max_queries]

    # Gather raw results
    raw: list[dict] = []
    for q in queries:
        raw.extend(_tavily_search(q, settings.research_max_results_per_query, is_news))
    if not raw: return {"evidence": []}

    # Dedup by url (keep the higher-scoring duplicate).
    by_url: dict[str, dict] = {}
    for r in raw:
        url = r.get("url")
        if not url:
            continue
        if url not in by_url or ((r.get("score") or 0) > (by_url[url].get("score") or 0)):
            by_url[url] = r
    deduped = list(by_url.values())

    # Relevance floor → drop weak matches.
    top_content = [r for r in deduped if ((r.get("score") or 0) >= settings.research_score_floor)]

    # Rank by score and cap to the max consumer budget
    top_content.sort(key=lambda r: r.get("score") or 0, reverse=True)
    top_content = top_content[: settings.research_max_results_total]   # keep top-N by relevance

    # Compact (trim content, drop heavy fields) BEFORE the LLM call.
    compact_content = [_compact(r, settings.research_snippet_max_chars) for r in top_content]
    if not compact_content:
        return {"evidence": []}
    # print(f"\nraw: {raw}")

    chain = RESEARCH_PROMPT | get_llm().with_structured_output(EvidencePack)
    pack: EvidencePack = chain.invoke({
        "as_of": state["as_of"],
        "recency_days": state["recency_days"],
        "raw_results": str(compact_content),
    })
    evidence = [e for e in pack.evidence if e.url]

    # Throw away evidence that's too old, but only for news-style topics
    if is_news:
        cutoff = date.fromisoformat(state["as_of"]) - timedelta(days=int(state["recency_days"]))
        evidence = [e for e in evidence if (d := _iso_to_date(e.published_at)) and d >= cutoff]
    return {"evidence": evidence}

