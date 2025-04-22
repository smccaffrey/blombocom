from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from blombo.api.server import app
from blombo.llm_providers.base import LLMConfig, LLMResponse
from blombo.core.context import ContextItem


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_generate_endpoint(test_client):
    """Test the generate endpoint."""
    # Mock the LLM provider and context engine
    mock_response = LLMResponse(
        text="Test response",
        usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        metadata={"model": "gpt-3.5-turbo", "finish_reason": "stop"}
    )
    
    mock_context = [
        ContextItem(
            content="Test context",
            source="test",
            metadata={"source": "test"}
        )
    ]
    
    with patch("blombo.api.server.ContextEngine") as mock_context_engine, \
         patch("blombo.api.server.OpenAIProvider") as mock_provider:
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context_instance.get_context.return_value = mock_context
        mock_context_engine.return_value = mock_context_instance
        
        mock_provider_instance = AsyncMock()
        mock_provider_instance.generate.return_value = mock_response
        mock_provider.return_value = mock_provider_instance
        
        # Make request
        request_data = {
            "prompt": "Test prompt",
            "context_query": "test",
            "context_limit": 5,
            "llm_config": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": "test-key"
            },
            "settings": {
                "temperature": 0.7
            }
        }
        
        response = test_client.post("/generate", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["response"]["text"] == "Test response"
        assert data["response"]["usage"]["prompt_tokens"] == 10
        assert data["context_used"][0]["content"] == "Test context"
        assert data["context_used"][0]["source"] == "test"


def test_generate_endpoint_invalid_request(test_client):
    """Test the generate endpoint with invalid request data."""
    # Missing required fields
    request_data = {
        "prompt": "Test prompt"
    }
    
    response = test_client.post("/generate", json=request_data)
    assert response.status_code == 422  # Validation error
    
    # Invalid LLM config
    request_data = {
        "prompt": "Test prompt",
        "llm_config": {
            "provider": "invalid",
            "model": "invalid",
            "api_key": "test-key"
        }
    }
    
    response = test_client.post("/generate", json=request_data)
    assert response.status_code == 422  # Validation error 