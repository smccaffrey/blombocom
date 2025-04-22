import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel


class CacheMetadata(BaseModel):
    """Metadata about a cached item."""
    source: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0


class CacheItem(BaseModel):
    """A cached item with its metadata."""
    data: Dict[str, Any]
    metadata: CacheMetadata


class ContextCache:
    """Cache for context data to avoid refetching."""
    
    def __init__(self, cache_dir: str = ".cache/blombo", default_ttl_hours: int = 24):
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._default_ttl = timedelta(hours=default_ttl_hours)
        self._index_file = self._cache_dir / "index.json"
        self._index: Dict[str, CacheMetadata] = self._load_index()
    
    def _load_index(self) -> Dict[str, CacheMetadata]:
        """Load the cache index from disk."""
        if self._index_file.exists():
            try:
                with open(self._index_file, "r") as f:
                    data = json.load(f)
                    return {
                        key: CacheMetadata(**value)
                        for key, value in data.items()
                    }
            except Exception as e:
                print(f"Error loading cache index: {e}")
        return {}
    
    def _save_index(self) -> None:
        """Save the cache index to disk."""
        try:
            with open(self._index_file, "w") as f:
                json.dump(
                    {key: value.dict() for key, value in self._index.items()},
                    f,
                    default=str
                )
        except Exception as e:
            print(f"Error saving cache index: {e}")
    
    def _get_cache_path(self, cache_id: str) -> Path:
        """Get the path for a cache file."""
        return self._cache_dir / f"{cache_id}.json"
    
    def _generate_cache_id(self, source: str, query: Optional[Dict[str, Any]] = None) -> str:
        """Generate a unique cache ID for a source and query."""
        import hashlib
        
        # Create a string representation of the query
        query_str = json.dumps(query, sort_keys=True) if query else ""
        
        # Create a unique ID based on source and query
        data = f"{source}:{query_str}".encode("utf-8")
        return hashlib.sha256(data).hexdigest()
    
    def get(self, source: str, query: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get data from the cache if it exists and is not expired."""
        cache_id = self._generate_cache_id(source, query)
        
        if cache_id not in self._index:
            return None
        
        metadata = self._index[cache_id]
        
        # Check if the cache has expired
        if metadata.expires_at and metadata.expires_at < datetime.now():
            self.delete(cache_id)
            return None
        
        # Update access metadata
        metadata.last_accessed = datetime.now()
        metadata.access_count += 1
        self._save_index()
        
        # Load the cached data
        cache_path = self._get_cache_path(cache_id)
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cached data: {e}")
            return None
    
    def set(
        self,
        source: str,
        data: Dict[str, Any],
        query: Optional[Dict[str, Any]] = None,
        ttl: Optional[timedelta] = None
    ) -> str:
        """Store data in the cache."""
        cache_id = self._generate_cache_id(source, query)
        cache_path = self._get_cache_path(cache_id)
        
        # Calculate expiration time
        expires_at = None
        if ttl:
            expires_at = datetime.now() + ttl
        elif self._default_ttl:
            expires_at = datetime.now() + self._default_ttl
        
        # Create metadata
        metadata = CacheMetadata(
            source=source,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_accessed=datetime.now(),
            access_count=0,
            size_bytes=len(json.dumps(data).encode("utf-8"))
        )
        
        # Save the data
        try:
            with open(cache_path, "w") as f:
                json.dump(data, f)
            
            # Update index
            self._index[cache_id] = metadata
            self._save_index()
            
            return cache_id
        except Exception as e:
            print(f"Error saving to cache: {e}")
            return ""
    
    def delete(self, cache_id: str) -> bool:
        """Delete a cache entry."""
        if cache_id not in self._index:
            return False
        
        # Remove the cache file
        cache_path = self._get_cache_path(cache_id)
        if cache_path.exists():
            try:
                cache_path.unlink()
            except Exception as e:
                print(f"Error deleting cache file: {e}")
        
        # Remove from index
        del self._index[cache_id]
        self._save_index()
        
        return True
    
    def clear(self, source: Optional[str] = None) -> int:
        """Clear the cache, optionally filtered by source."""
        if source:
            # Clear only items from the specified source
            to_delete = [
                cache_id for cache_id, metadata in self._index.items()
                if metadata.source == source
            ]
        else:
            # Clear all items
            to_delete = list(self._index.keys())
        
        # Delete each item
        for cache_id in to_delete:
            self.delete(cache_id)
        
        return len(to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_size = sum(metadata.size_bytes for metadata in self._index.values())
        total_items = len(self._index)
        
        # Count items by source
        sources: Dict[str, int] = {}
        for metadata in self._index.values():
            sources[metadata.source] = sources.get(metadata.source, 0) + 1
        
        # Count expired items
        expired = sum(
            1 for metadata in self._index.values()
            if metadata.expires_at and metadata.expires_at < datetime.now()
        )
        
        return {
            "total_items": total_items,
            "total_size_bytes": total_size,
            "sources": sources,
            "expired_items": expired
        } 