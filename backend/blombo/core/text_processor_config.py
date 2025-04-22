from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TextProcessorConfig:
    """Configuration for text processors."""

    # API configuration
    api_key: str
    api_base: Optional[str] = None
    api_version: Optional[str] = None

    # Model configuration
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None

    # Embedding configuration
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimensions: int = 1536 