import os
import tempfile
from pathlib import Path

import pytest

from blombo.connectors.markdown import MarkdownConnector, MarkdownConnectorConfig


@pytest.fixture
def temp_markdown_dir():
    """Create a temporary directory with test Markdown files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some test files
        test_files = {
            "test1.md": "# Test 1\nThis is a test file.",
            "test2.md": "# Test 2\nAnother test file.",
            "subdir/test3.md": "# Test 3\nA test file in a subdirectory."
        }
        
        for filename, content in test_files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        yield temp_dir


@pytest.mark.asyncio
async def test_markdown_connector_metadata(temp_markdown_dir):
    """Test that the connector returns correct metadata."""
    config = MarkdownConnectorConfig(
        name="test",
        directory=temp_markdown_dir
    )
    connector = MarkdownConnector(config)
    
    metadata = connector.metadata
    assert metadata.name == "markdown"
    assert "Connector for local Markdown files" in metadata.description
    assert "read" in metadata.supported_features
    assert "search" in metadata.supported_features


@pytest.mark.asyncio
async def test_markdown_connector_fetch_data(temp_markdown_dir):
    """Test that the connector can fetch Markdown files."""
    config = MarkdownConnectorConfig(
        name="test",
        directory=temp_markdown_dir
    )
    connector = MarkdownConnector(config)
    
    # Test non-recursive fetch
    config.recursive = False
    results = await connector.fetch_data()
    assert len(results) == 2  # Only files in root directory
    
    # Test recursive fetch
    config.recursive = True
    results = await connector.fetch_data()
    assert len(results) == 3  # All files including subdirectory
    
    # Verify content and metadata
    for result in results:
        assert "content" in result
        assert "metadata" in result
        assert "path" in result["metadata"]
        assert "filename" in result["metadata"]
        assert result["metadata"]["filename"].endswith(".md")


@pytest.mark.asyncio
async def test_markdown_connector_invalid_directory():
    """Test that the connector handles invalid directories correctly."""
    config = MarkdownConnectorConfig(
        name="test",
        directory="/nonexistent/directory"
    )
    
    with pytest.raises(ValueError):
        MarkdownConnector(config) 