from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ConnectorConfig(BaseModel):
    """Base configuration for all connectors."""
    name: str
    enabled: bool = True
    settings: Dict[str, Any] = {}


class ConnectorMetadata(BaseModel):
    """Metadata about a connector."""
    name: str
    description: str
    version: str
    supported_features: List[str]


class Connector(ABC):
    """Base class for all data source connectors."""
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self._metadata = self._get_metadata()
    
    @abstractmethod
    def _get_metadata(self) -> ConnectorMetadata:
        """Return metadata about the connector."""
        pass
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data source."""
        pass
    
    @abstractmethod
    async def fetch_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch data from the source based on the query parameters."""
        pass
    
    @property
    def metadata(self) -> ConnectorMetadata:
        """Get connector metadata."""
        return self._metadata 