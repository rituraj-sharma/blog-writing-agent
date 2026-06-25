"""System prompts, isolated from logic so they can be versioned and tuned."""

from blog_agent.prompts.orchestrator import ORCHESTRATOR_PROMPT
from blog_agent.prompts.worker import WORKER_PROMPT
from blog_agent.prompts.router import ROUTER_PROMPT
from blog_agent.prompts.research import RESEARCH_PROMPT

__all__ = ["ORCHESTRATOR_PROMPT", "WORKER_PROMPT", "ROUTER_PROMPT", "RESEARCH_PROMPT"]