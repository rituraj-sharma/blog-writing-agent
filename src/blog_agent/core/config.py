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
        env_prefix="BLOG_AGENT_",
        extra="ignore"
    )

    # output directory to save markdown blog file and images
    output_dir: str = "output"

    # Provider and Model
    llm_provider: Provider = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.3

    # Image generation config
    images_enabled: bool = True
    image_provider: Provider = "openai"
    image_model: str = "gpt-image-1-mini"
    max_images: int = 3


    # Search settings (For guardrailing)
    research_min_queries: int = 3
    research_max_queries: int = 5 #10              # Max number of queries to search (actual number and queries given by Router)
    research_max_results_per_query: int = 3 #6     # Max number of results fetched by search engine
    research_max_results_total: int = 10 #20        # Only keep top N search for evidence
    research_max_evidences_total: int = 10 #20      # ceiling after ranking (consumer budget)
    research_score_floor: float = 0.4           # drop results below this relevance
    research_snippet_max_chars: int = 500       # truncate each result's content

    recency_open_book_days: int = 7             # Open-book mainly used for news volatile/news topics, only keep evidence from the last 7 days
    recency_hybrid_days: int = 45               # Evergreen concepts that need some up-to-date examples. 45 days is looser than news but still recent
    recency_closed_book_days: int = 3650        # Effectively no recency limit. Huge number so the same filtering machinery works without if else. 

    # Provider API keys
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")

    # Search API keys
    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")

    # logging configuration
    log_level: str = "INFO"
    log_json: bool = False

    # if the key is missing, research will just return no evidence rather than crashing (tavily is serach by design)
    @property  # @property enables a function to be called as an attribute like c.tavily_enabled
    def tavily_enabled(self) -> bool:
        return bool(self.tavily_api_key)

@lru_cache
def get_settings() -> Settings:
    return Settings()
