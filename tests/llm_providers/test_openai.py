from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blombo.llm_providers.base import LLMConfig
from blombo.llm_providers.openai import OpenAIProvider


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response."""
    mock_choice = MagicMock()
    mock_choice.message.content = "Test response"
    mock_choice.finish_reason = "stop"
    
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 20
    mock_usage.total_tokens = 30
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage
    mock_response.model = "gpt-3.5-turbo"
    
    return mock_response


@pytest.fixture
def mock_embeddings_response():
    """Create a mock OpenAI embeddings response."""
    mock_embedding = MagicMock()
    mock_embedding.embedding = [0.1, 0.2, 0.3]
    
    mock_response = MagicMock()
    mock_response.data = [mock_embedding]
    
    return mock_response


@pytest.mark.asyncio
async def test_openai_provider_generate(mock_openai_response):
    """Test text generation with OpenAI provider."""
    config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key="test-key"
    )
    
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_client.return_value.chat.completions.create = AsyncMock(
            return_value=mock_openai_response
        )
        
        provider = OpenAIProvider(config)
        response = await provider.generate("Test prompt")
        
        assert response.text == "Test response"
        assert response.usage["prompt_tokens"] == 10
        assert response.usage["completion_tokens"] == 20
        assert response.usage["total_tokens"] == 30
        assert response.metadata["model"] == "gpt-3.5-turbo"
        assert response.metadata["finish_reason"] == "stop"


@pytest.mark.asyncio
async def test_openai_provider_generate_with_context(mock_openai_response):
    """Test text generation with context."""
    config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key="test-key"
    )
    
    context = [
        {"content": "Context 1"},
        {"content": "Context 2"}
    ]
    
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_client.return_value.chat.completions.create = AsyncMock(
            return_value=mock_openai_response
        )
        
        provider = OpenAIProvider(config)
        response = await provider.generate("Test prompt", context=context)
        
        # Verify that the context was included in the API call
        call_args = mock_client.return_value.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 3  # 2 context messages + 1 prompt
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Context 1"
        assert messages[1]["role"] == "system"
        assert messages[1]["content"] == "Context 2"
        assert messages[2]["role"] == "user"
        assert messages[2]["content"] == "Test prompt"


@pytest.mark.asyncio
async def test_openai_provider_embeddings(mock_embeddings_response):
    """Test getting embeddings from OpenAI provider."""
    config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key="test-key"
    )
    
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_client.return_value.embeddings.create = AsyncMock(
            return_value=mock_embeddings_response
        )
        
        provider = OpenAIProvider(config)
        embeddings = await provider.get_embeddings(["Test text"])
        
        assert len(embeddings) == 1
        assert embeddings[0] == [0.1, 0.2, 0.3]


def test_openai_provider_supported_models():
    """Test that the provider returns the correct list of supported models."""
    config = LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key="test-key"
    )
    
    provider = OpenAIProvider(config)
    supported_models = provider.supported_models
    
    assert "gpt-4" in supported_models
    assert "gpt-3.5-turbo" in supported_models
    assert "text-embedding-ada-002" in supported_models 