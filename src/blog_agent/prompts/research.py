from langchain_core.prompts import ChatPromptTemplate


RESEARCH_SYSTEM = """You are a research synthesizer.
Given raw web search results, produce EvidenceItem objects.

Rules:
- Only include items with a non-empty url.
- Prefer relevant + authoritative sources.
- Normalize published_at to ISO YYYY-MM-DD if reliably inferable; else null (do NOT guess).
- Keep snippets short.
- Deduplicate by URL.
"""

RESEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", RESEARCH_SYSTEM),
    ("human",
     "As-of date: {as_of}\nRecency days: {recency_days}\n\n"
     "Raw results:\n{raw_results}"),
])