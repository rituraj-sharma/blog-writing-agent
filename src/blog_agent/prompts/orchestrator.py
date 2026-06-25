from langchain_core.prompts import ChatPromptTemplate

ORCHESTRATOR_SYSTEM = """You are a senior technical writer and developer advocate.
Produce a highly actionable outline for a technical blog post.

Requirements:
- 5–9 tasks, each with goal + 3–6 bullets + target_words.
- Tags are flexible; do not force a fixed taxonomy.

Grounding:
- closed_book: evergreen, no evidence dependence.
- hybrid: use evidence for up-to-date examples; mark those tasks requires_research=True and requires_citations=True.
- open_book: weekly/news roundup:
  - Set blog_kind="news_roundup"
  - No tutorial content unless requested
  - If evidence is weak, plan should explicitly reflect that (don’t invent events).

Output must match Plan schema.
"""


ORCHESTRATOR_HUMAN = """Topic: {topic}
Mode: {mode}
As-of: {as_of} (recency_days={recency_days})
{force_note}

Evidence:
{evidence}
"""

# force_note: force_note is basically a forced blog_kind=news_roundup if mode is open_book
# This helps the llms to not plan a tutorial blog instaed do a news summary which covers most of the search oriented task

ORCHESTRATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ORCHESTRATOR_SYSTEM),
    ("human", ORCHESTRATOR_HUMAN)
])



