"""System prompts, isolated from logic so they can be versioned and tuned."""

from blog_agent.prompts.orchestrator import ORCHESTRATOR_PROMPT
from blog_agent.prompts.worker import WORKER_PROMPT

__all__ = ["ORCHESTRATOR_PROMPT", "WORKER_PROMPT"]