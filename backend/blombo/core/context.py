from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from blombo.core.cache import ContextCache


class ContextItem(BaseModel):
    """A single item of context with metadata."""
    content: str
    source: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None


class ContextEngine:
    """Engine for managing and enriching context for LLMs."""
    
    def __init__(self, cache_dir: str = ".cache/blombo", default_ttl_hours: int = 24):
        self._context_items: List[ContextItem] = []
        self._cache = ContextCache(cache_dir, default_ttl_hours)
    
    def add_context(self, item: ContextItem) -> None:
        """Add a new context item."""
        self._context_items.append(item)
    
    def add_context_batch(self, items: List[ContextItem]) -> None:
        """Add multiple context items."""
        self._context_items.extend(items)
    
    def get_context(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[ContextItem]:
        """Get context items, optionally filtered by query."""
        if query is None:
            return self._context_items[:limit] if limit else self._context_items
        
        # TODO: Implement semantic search when query is provided
        return self._context_items[:limit] if limit else self._context_items
    
    def clear_context(self) -> None:
        """Clear all context items."""
        self._context_items.clear()
    
    def enrich_context(self, llm_provider: Any) -> None:
        """Enrich context items with embeddings from the LLM provider."""
        for item in self._context_items:
            if item.embedding is None:
                embeddings = llm_provider.get_embeddings([item.content])
                item.embedding = embeddings[0]
    
    def get_cached_data(self, source: str, query: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get data from the cache if available."""
        return self._cache.get(source, query)
    
    def cache_data(
        self,
        source: str,
        data: Dict[str, Any],
        query: Optional[Dict[str, Any]] = None,
        ttl_hours: Optional[int] = None
    ) -> str:
        """Cache data for future use."""
        from datetime import timedelta
        
        ttl = timedelta(hours=ttl_hours) if ttl_hours is not None else None
        return self._cache.set(source, data, query, ttl)
    
    def clear_cache(self, source: Optional[str] = None) -> int:
        """Clear the cache, optionally filtered by source."""
        return self._cache.clear(source)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache.get_stats() 