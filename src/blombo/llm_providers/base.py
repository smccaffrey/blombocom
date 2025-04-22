from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """Base configuration for all LLM providers."""
    provider: str
    model: str
    api_key: str
    settings: Dict[str, Any] = {}


class LLMResponse(BaseModel):
    """Standardized response from LLM providers."""
    text: str
    usage: Dict[str, int]
    metadata: Dict[str, Any] = {}


class LLMProvider(ABC):
    """Base class for all LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts."""
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """Get list of supported models."""
        pass 