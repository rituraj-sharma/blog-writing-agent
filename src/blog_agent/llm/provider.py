"""LLM factory.
Swapping providers (OpenAI → Anthropic → a local model) or changing defaults happens.
"""

from __future__ import annotations
from functools import lru_cache
from langchain_core.language_models.chat_models import BaseChatModel
from blog_agent.core import get_settings

@lru_cache
def get_llm(temperature: float | None = None) -> BaseChatModel:
    settings = get_settings()
    temp = settings.llm_temperature if temperature is None else temperature

    if settings.llm_provider=="groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model = settings.llm_model,
            temperature = temp,
            api_key = settings.groq_api_key
        )
    
    if settings.llm_provider=="openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model = settings.llm_model,
            temperature = temp,
            api_key = settings.openai_api_key
        )

    if settings.llm_provider=="anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model = settings.llm_model,
            temperature = temp,
            api_key = settings.anthropic_api_key
        )
    
    if settings.llm_provider=="google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model = settings.llm_model,
            temperature = temp,
            api_key = settings.google_api_key
        )
    
    raise ValueError(f"Unknown llm_provider: {settings.llm_provider}")