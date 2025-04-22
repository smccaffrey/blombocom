from typing import Dict, List, Optional, Type

from blombo.connectors.base import Connector, ConnectorConfig


class ConnectorFactory:
    """Factory for creating and managing connectors."""
    
    def __init__(self):
        self._connectors: Dict[str, Type[Connector]] = {}
        self._instances: Dict[str, Connector] = {}
    
    def register(self, name: str, connector_class: Type[Connector]) -> None:
        """Register a connector class."""
        self._connectors[name] = connector_class
    
    def create(self, config: ConnectorConfig) -> Connector:
        """Create a connector instance from config."""
        connector_class = self._connectors.get(config.name)
        if not connector_class:
            raise ValueError(f"Unknown connector: {config.name}")
        
        # Create a unique ID for this connector instance
        instance_id = f"{config.name}_{id(config)}"
        
        # Create the connector instance
        connector = connector_class(config)
        self._instances[instance_id] = connector
        
        return connector
    
    def get_connector(self, instance_id: str) -> Optional[Connector]:
        """Get a connector instance by ID."""
        return self._instances.get(instance_id)
    
    def get_all_connectors(self) -> List[Connector]:
        """Get all connector instances."""
        return list(self._instances.values())
    
    def get_available_connectors(self) -> List[str]:
        """Get list of available connector types."""
        return list(self._connectors.keys())
    
    def remove_connector(self, instance_id: str) -> bool:
        """Remove a connector instance."""
        if instance_id in self._instances:
            del self._instances[instance_id]
            return True
        return False
    
    def clear_connectors(self) -> None:
        """Clear all connector instances."""
        self._instances.clear()


# Global connector factory instance
connector_factory = ConnectorFactory() 