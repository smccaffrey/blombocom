from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from blombo.core.text_processor import TextProcessor
from blombo.core.text_processor_config import TextProcessorConfig

router = APIRouter()


class TextRequest(BaseModel):
    """Text request model."""
    text: str
    max_length: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None


class TextResponse(BaseModel):
    """Text response model."""
    text: str
    tokens: int
    model: str


@router.post("/process", response_model=TextResponse)
async def process_text(request: TextRequest):
    """
    Process text using the configured language model.
    """
    try:
        config = TextProcessorConfig(
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty
        )
        
        processor = TextProcessor(config)
        result = await processor.process_text(request.text)
        
        return TextResponse(
            text=result.text,
            tokens=result.tokens,
            model=result.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 