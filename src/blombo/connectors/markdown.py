import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from blombo.connectors.base import Connector, ConnectorConfig, ConnectorMetadata


class MarkdownConnectorConfig(ConnectorConfig):
    """Configuration for the Markdown connector."""
    directory: str
    file_pattern: str = "*.md"
    recursive: bool = True


class MarkdownConnector(Connector):
    """Connector for local Markdown files."""
    
    def __init__(self, config: MarkdownConnectorConfig):
        super().__init__(config)
        self._directory = Path(config.directory)
        if not self._directory.exists():
            raise ValueError(f"Directory {config.directory} does not exist")
    
    def _get_metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            name="markdown",
            description="Connector for local Markdown files",
            version="0.1.0",
            supported_features=["read", "search"]
        )
    
    async def connect(self) -> None:
        """No connection needed for local files."""
        pass
    
    async def disconnect(self) -> None:
        """No disconnection needed for local files."""
        pass
    
    async def fetch_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch Markdown files from the configured directory."""
        pattern = self.config.file_pattern
        files = []
        
        if self.config.recursive:
            files = list(self._directory.rglob(pattern))
        else:
            files = list(self._directory.glob(pattern))
        
        results = []
        for file_path in files:
            try:
                content = file_path.read_text()
                results.append({
                    "content": content,
                    "metadata": {
                        "path": str(file_path),
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    }
                })
            except Exception as e:
                # Log error and continue with other files
                print(f"Error reading {file_path}: {e}")
        
        return results 