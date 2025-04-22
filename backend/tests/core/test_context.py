from unittest.mock import MagicMock

import pytest

from blombo.core.context import ContextEngine, ContextItem


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider."""
    provider = MagicMock()
    provider.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
    return provider


def test_context_engine_add_context():
    """Test adding context items."""
    engine = ContextEngine()
    
    item1 = ContextItem(
        content="Test content 1",
        source="test1"
    )
    item2 = ContextItem(
        content="Test content 2",
        source="test2"
    )
    
    engine.add_context(item1)
    assert len(engine._context_items) == 1
    assert engine._context_items[0] == item1
    
    engine.add_context_batch([item2])
    assert len(engine._context_items) == 2
    assert engine._context_items[1] == item2


def test_context_engine_get_context():
    """Test retrieving context items."""
    engine = ContextEngine()
    
    items = [
        ContextItem(content=f"Content {i}", source=f"source{i}")
        for i in range(3)
    ]
    
    engine.add_context_batch(items)
    
    # Test getting all items
    all_items = engine.get_context()
    assert len(all_items) == 3
    
    # Test getting limited items
    limited_items = engine.get_context(limit=2)
    assert len(limited_items) == 2
    
    # Test getting items with query (currently just returns all items)
    queried_items = engine.get_context(query="test")
    assert len(queried_items) == 3


def test_context_engine_clear_context():
    """Test clearing context items."""
    engine = ContextEngine()
    
    items = [
        ContextItem(content=f"Content {i}", source=f"source{i}")
        for i in range(3)
    ]
    
    engine.add_context_batch(items)
    assert len(engine._context_items) == 3
    
    engine.clear_context()
    assert len(engine._context_items) == 0


@pytest.mark.asyncio
async def test_context_engine_enrich_context(mock_llm_provider):
    """Test enriching context items with embeddings."""
    engine = ContextEngine()
    
    items = [
        ContextItem(content=f"Content {i}", source=f"source{i}")
        for i in range(2)
    ]
    
    engine.add_context_batch(items)
    
    # Verify no embeddings initially
    assert all(item.embedding is None for item in engine._context_items)
    
    # Enrich with embeddings
    engine.enrich_context(mock_llm_provider)
    
    # Verify embeddings were added
    assert all(item.embedding == [0.1, 0.2, 0.3] for item in engine._context_items)
    
    # Verify provider was called correctly
    assert mock_llm_provider.get_embeddings.call_count == 2
    mock_llm_provider.get_embeddings.assert_any_call(["Content 0"])
    mock_llm_provider.get_embeddings.assert_any_call(["Content 1"]) 