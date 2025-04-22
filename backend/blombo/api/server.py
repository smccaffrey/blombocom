from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from blombo.core.context import ContextItem
from blombo.llm_providers.base import LLMConfig, LLMResponse


app = FastAPI(
    title="Blombo API",
    description="Semantic layer middleware for AI/LLM applications",
    version="0.1.0"
)


class GenerateRequest(BaseModel):
    """Request model for text generation."""
    prompt: str
    context_query: Optional[str] = None
    context_limit: Optional[int] = None
    llm_config: LLMConfig
    settings: Dict[str, Any] = {}


class GenerateResponse(BaseModel):
    """Response model for text generation."""
    response: LLMResponse
    context_used: List[ContextItem]


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate text using the specified LLM provider with context."""
    # TODO: Implement the actual generation logic
    raise HTTPException(status_code=501, detail="Not implemented")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"} 