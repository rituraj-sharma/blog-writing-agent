"""Domain-specific exception hierarchy."""

from __future__ import annotations


class BlogAgentError(Exception):
    """Base class for all application errors."""


class ConfigurationError(BlogAgentError):
    """A required setting or credential is missing or invalid."""


class ResearchError(BlogAgentError):
    """Web research failed in a non-recoverable way."""


class ImageGenerationError(BlogAgentError):
    """An image could not be generated."""


class GraphExecutionError(BlogAgentError):
    """The agent graph failed during execution."""
