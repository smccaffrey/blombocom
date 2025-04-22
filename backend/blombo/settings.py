import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings."""
    # App settings
    APP_NAME: str = "Blombo API"
    APP_DESCRIPTION: str = "Semantic layer middleware for AI/LLM applications"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # Environment
    ENV: str = Field(default_factory=lambda: os.getenv("ENV", "development"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "true").lower() == "true")
    
    # Database settings
    DATABASE_URL: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./blombo.db"))
    
    # Cache settings
    CACHE_DIR: str = Field(default_factory=lambda: os.getenv("CACHE_DIR", ".cache/blombo"))
    DEFAULT_CACHE_TTL_HOURS: int = Field(default_factory=lambda: int(os.getenv("DEFAULT_CACHE_TTL_HOURS", "24")))
    
    # LLM settings
    DEFAULT_LLM_PROVIDER: str = Field(default_factory=lambda: os.getenv("DEFAULT_LLM_PROVIDER", "openai"))
    OPENAI_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    
    # Connector settings
    GOOGLE_CREDENTIALS_PATH: Optional[str] = Field(default_factory=lambda: os.getenv("GOOGLE_CREDENTIALS_PATH"))
    GOOGLE_TOKEN_PATH: Optional[str] = Field(default_factory=lambda: os.getenv("GOOGLE_TOKEN_PATH"))
    SLACK_TOKEN: Optional[str] = Field(default_factory=lambda: os.getenv("SLACK_TOKEN"))


@lru_cache()
def get_settings() -> Settings:
    """Get application settings."""
    return Settings() 