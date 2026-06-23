"""Centralised, validated application configuration"""

from __future__ import annotations
from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Provider = Literal["groq", "openai", "anthropic", "google"]

class Settings(BaseSettings):
    model_config=SettingsConfigDict(
        env_file=".env",
        env_prefix="BLOG_AGENT",
        extra="ignore"
    )

    # Provider and Model
    llm_provider: Provider = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.3

    # Provider API keys
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")

@lru_cache
def get_settings() -> Settings:
    return Settings()
