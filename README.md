# Blog Writing Agent

**multi-agent technical blog writer** built on **LangGraph** and served with **FastAPI**. Given a topic, it decides whether to research the web, plans an outline, writes every section in parallel, then optionally generates and embeds diagrams — producing a finished, citation-grounded Markdown post.

## Why this design

The agent is a directed graph of specialised nodes rather than one mega-prompt. Each stage is independently testable, swappable, and observable:

```
            ┌──────────┐  needs_research?  ┌──────────┐
  START ──▶ │  router  │ ────────────────▶ │ research │ ─┐
            └──────────┘                   └──────────┘   │
      no research │   ____________________________________│
                  ▼  ▼                                 
            ┌──────────────┐   fan-out (Send)   ┌──────────────────┐
            │ orchestrator │ ─────────────────▶ │ worker × N (∥)   │
            └──────────────┘                    └──────────────────┘
                                                         │
                                                         ▼
                          ┌──────────────── reducer subgraph ───────────────┐
                          │ merge_content → decide_images → generate_images  │
                          └──────────────────────────────────────────────────┘
                                                         │
                                                         ▼
                                                        END
```

- **Router** classifies the topic as `closed_book` / `hybrid` / `open_book` and sets a recency window.
- **Research** (Tavily) gathers, synthesises, dedupes, and date-filters evidence.
- **Orchestrator** emits a structured `Plan` (Pydantic) of 5–9 sections.
- **Workers** fan out via LangGraph `Send` and write each section concurrently.
- **Reducer subgraph** merges sections, decides where diagrams help, generates them (Gemini), and persists the final Markdown.

## Project structure

```
src/blog_agent/
├── core/            # config (pydantic-settings), structured logging, exceptions
├── schemas/         # Pydantic models: blog, research, image, graph state
├── prompts/         # System prompts, versioned separately from logic
├── llm/             # LLM factory (single place to swap providers)
├── services/        # Swappable integrations behind Protocols:
│   ├── search.py            #   Tavily web search
│   ├── image_generation.py  #   Gemini image generation (+ null impl)
│   └── storage.py           #   filesystem persistence (S3/DB-ready)
├── graph/
│   ├── nodes/       # one module per node (router, research, ... , reducer)
│   ├── reducer_graph.py
│   └── builder.py   # assembles & compiles the graph
├── api/             # FastAPI app, routes, request/response models
├── pipeline.py      # application service used by both API and CLI
└── __main__.py      # CLI entrypoint
tests/               # pytest suite (no live LLM/network calls)
```

Design principles: **dependency inversion** (nodes depend on `Protocol`s, not vendors), **single source of config**, **separation of prompts from logic**, and **graceful degradation** (missing keys disable features instead of crashing).

## Quickstart

```bash
# 1. Install (dev + image extras)
make dev          # or: pip install -e ".[dev,images]"

# 2. Configure
cp .env.example .env   # add OPENAI_API_KEY (TAVILY/GOOGLE optional)

# 3a. Run from the CLI
python -m blog_agent "Explain KV caching in transformers"

# 3b. Or serve the API
make api          # uvicorn @ http://localhost:8000  (docs at /docs)
```

Generate via HTTP:

```bash
curl -X POST http://localhost:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{"topic": "Explain KV caching in transformers"}'
```

`POST /blogs/stream` returns NDJSON node-by-node progress for live UIs.

## Docker

```bash
docker compose up --build      # API on :8000, output/ mounted to host
```

## Development

```bash
make test        # pytest
make lint        # ruff
make typecheck   # mypy
make format      # ruff --fix + format
```

CI (GitHub Actions) runs lint, type-check, and tests on Python 3.10–3.12.

## Configuration

All settings load from env vars (prefix `BLOG_AGENT_`) via `pydantic-settings`; see `.env.example`. Key ones:

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | — | LLM access (required) |
| `TAVILY_API_KEY` | — | Web research (optional — research degrades to none) |
| `GOOGLE_API_KEY` | — | Image generation (optional — images disabled if absent) |
| `BLOG_AGENT_LLM_MODEL` | `gpt-4.1-mini` | Chat model |
| `BLOG_AGENT_MAX_IMAGES` | `3` | Image cap per post |
| `BLOG_AGENT_OUTPUT_DIR` | `./output` | Where Markdown + images are written |

