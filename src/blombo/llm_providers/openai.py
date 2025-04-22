from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI

from blombo.llm_providers.base import LLMConfig, LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._client = AsyncOpenAI(api_key=config.api_key)
    
    async def generate(
        self,
        prompt: str,
        context: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate text using OpenAI's API."""
        messages = []
        
        # Add context if provided
        if context:
            for item in context:
                messages.append({
                    "role": "system",
                    "content": item["content"]
                })
        
        # Add the user's prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Merge default settings with any overrides
        settings = {
            "model": self.config.model,
            "temperature": 0.7,
            "max_tokens": 1000,
            **self.config.settings,
            **kwargs
        }
        
        response = await self._client.chat.completions.create(
            messages=messages,
            **settings
        )
        
        return LLMResponse(
            text=response.choices[0].message.content,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            metadata={
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
        )
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings using OpenAI's API."""
        response = await self._client.embeddings.create(
            model="text-embedding-ada-002",
            input=texts
        )
        
        return [embedding.embedding for embedding in response.data]
    
    @property
    def supported_models(self) -> List[str]:
        """Get list of supported OpenAI models."""
        return [
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "text-embedding-ada-002"
        ] 