import pytest
from unittest.mock import MagicMock, patch

from blombo.connectors.slack import SlackConnector, SlackConnectorConfig


@pytest.fixture
def slack_config():
    return SlackConnectorConfig(
        token="xoxb-test-token",
        channels=["C1234567890"],
        days_back=7,
        max_results=10
    )


@pytest.fixture
def slack_connector(slack_config):
    return SlackConnector(slack_config)


@pytest.mark.asyncio
async def test_connect(slack_connector):
    """Test connecting to Slack."""
    with patch("slack_sdk.WebClient") as mock_client:
        await slack_connector.connect()
        mock_client.assert_called_once_with(token="xoxb-test-token")
        assert slack_connector._client is not None


@pytest.mark.asyncio
async def test_disconnect(slack_connector):
    """Test disconnecting from Slack."""
    slack_connector._client = MagicMock()
    await slack_connector.disconnect()
    assert slack_connector._client is None


@pytest.mark.asyncio
async def test_fetch_data(slack_connector):
    """Test fetching data from Slack."""
    mock_client = MagicMock()
    slack_connector._client = mock_client
    
    # Mock the conversations_history response
    mock_client.conversations_history.return_value = {
        "messages": [
            {
                "client_msg_id": "msg123",
                "text": "Hello world",
                "user": "U1234567890",
                "ts": "1234567890.123456"
            }
        ]
    }
    
    # Mock the users_info response
    mock_client.users_info.return_value = {
        "user": {
            "id": "U1234567890",
            "name": "testuser"
        }
    }
    
    # Mock the conversations_info response
    mock_client.conversations_info.return_value = {
        "channel": {
            "id": "C1234567890",
            "name": "general"
        }
    }
    
    # Mock the conversations_replies response
    mock_client.conversations_replies.return_value = {
        "messages": [
            {
                "client_msg_id": "msg123",
                "text": "Hello world",
                "user": "U1234567890",
                "ts": "1234567890.123456"
            },
            {
                "text": "Reply to hello",
                "user": "U0987654321",
                "ts": "1234567890.123457"
            }
        ]
    }
    
    # Mock the users_info response for the reply
    mock_client.users_info.side_effect = [
        {
            "user": {
                "id": "U1234567890",
                "name": "testuser"
            }
        },
        {
            "user": {
                "id": "U0987654321",
                "name": "replyuser"
            }
        }
    ]
    
    result = await slack_connector.fetch_data()
    
    assert len(result) == 1
    assert result[0]["content"] == "Message from testuser in #general:\nHello world"
    assert result[0]["metadata"]["id"] == "msg123"
    assert result[0]["metadata"]["channel_name"] == "general"
    assert result[0]["metadata"]["user_name"] == "testuser"
    assert len(result[0]["metadata"]["thread_replies"]) == 1
    assert result[0]["metadata"]["thread_replies"][0]["user"] == "replyuser"
    assert result[0]["metadata"]["thread_replies"][0]["content"] == "Reply to hello"


@pytest.mark.asyncio
async def test_fetch_data_with_query(slack_connector):
    """Test fetching data from Slack with a query."""
    mock_client = MagicMock()
    slack_connector._client = mock_client
    
    # Mock the conversations_history response
    mock_client.conversations_history.return_value = {
        "messages": [
            {
                "client_msg_id": "msg123",
                "text": "Hello world",
                "user": "U1234567890",
                "ts": "1234567890.123456"
            }
        ]
    }
    
    # Mock the users_info response
    mock_client.users_info.return_value = {
        "user": {
            "id": "U1234567890",
            "name": "testuser"
        }
    }
    
    # Mock the conversations_info response
    mock_client.conversations_info.return_value = {
        "channel": {
            "id": "C1234567890",
            "name": "general"
        }
    }
    
    # Mock the conversations_replies response
    mock_client.conversations_replies.return_value = {
        "messages": [
            {
                "client_msg_id": "msg123",
                "text": "Hello world",
                "user": "U1234567890",
                "ts": "1234567890.123456"
            }
        ]
    }
    
    query = {"limit": 5}
    result = await slack_connector.fetch_data(query)
    
    assert len(result) == 1
    mock_client.conversations_history.assert_called_with(channel="C1234567890", limit=5)


@pytest.mark.asyncio
async def test_get_all_channels(slack_connector):
    """Test getting all accessible channels."""
    mock_client = MagicMock()
    slack_connector._client = mock_client
    
    # Mock the conversations_list response
    mock_client.conversations_list.return_value = {
        "channels": [
            {"id": "C1234567890", "name": "general"},
            {"id": "C0987654321", "name": "random"}
        ]
    }
    
    channels = slack_connector._get_all_channels()
    
    assert len(channels) == 2
    assert "C1234567890" in channels
    assert "C0987654321" in channels
    mock_client.conversations_list.assert_called_with(types="public_channel,private_channel")


@pytest.mark.asyncio
async def test_parse_message(slack_connector):
    """Test parsing a Slack message."""
    mock_client = MagicMock()
    slack_connector._client = mock_client
    
    # Mock the users_info response
    mock_client.users_info.return_value = {
        "user": {
            "id": "U1234567890",
            "name": "testuser"
        }
    }
    
    # Mock the conversations_info response
    mock_client.conversations_info.return_value = {
        "channel": {
            "id": "C1234567890",
            "name": "general"
        }
    }
    
    # Mock the conversations_replies response
    mock_client.conversations_replies.return_value = {
        "messages": [
            {
                "client_msg_id": "msg123",
                "text": "Hello world",
                "user": "U1234567890",
                "ts": "1234567890.123456"
            },
            {
                "text": "Reply to hello",
                "user": "U0987654321",
                "ts": "1234567890.123457"
            }
        ]
    }
    
    # Mock the users_info response for the reply
    mock_client.users_info.side_effect = [
        {
            "user": {
                "id": "U1234567890",
                "name": "testuser"
            }
        },
        {
            "user": {
                "id": "U0987654321",
                "name": "replyuser"
            }
        }
    ]
    
    message = {
        "client_msg_id": "msg123",
        "text": "Hello world",
        "user": "U1234567890",
        "ts": "1234567890.123456",
        "thread_ts": "1234567890.123456",
        "reactions": [{"name": "thumbsup", "count": 2}],
        "attachments": [{"text": "Attachment text"}],
        "files": [{"name": "file.txt"}]
    }
    
    result = slack_connector._parse_message(message, "C1234567890")
    
    assert result["content"] == "Message from testuser in #general:\nHello world"
    assert result["metadata"]["id"] == "msg123"
    assert result["metadata"]["channel_name"] == "general"
    assert result["metadata"]["user_name"] == "testuser"
    assert len(result["metadata"]["thread_replies"]) == 1
    assert result["metadata"]["thread_replies"][0]["user"] == "replyuser"
    assert result["metadata"]["thread_replies"][0]["content"] == "Reply to hello"
    assert len(result["metadata"]["reactions"]) == 1
    assert result["metadata"]["reactions"][0]["name"] == "thumbsup"
    assert len(result["metadata"]["attachments"]) == 1
    assert result["metadata"]["attachments"][0]["text"] == "Attachment text"
    assert len(result["metadata"]["files"]) == 1
    assert result["metadata"]["files"][0]["name"] == "file.txt" 