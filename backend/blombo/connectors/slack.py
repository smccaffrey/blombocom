from typing import Any, Dict, List, Optional

from blombo.connectors.base import Connector, ConnectorConfig, ConnectorMetadata
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackConnectorConfig(ConnectorConfig):
    """Configuration for the Slack connector."""
    token: str
    channels: List[str] = []
    days_back: int = 30
    max_results: int = 100


class SlackConnector(Connector):
    """Connector for Slack."""
    
    def __init__(self, config: SlackConnectorConfig):
        super().__init__(config)
        self._client = None
    
    def _get_metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            name="slack",
            description="Connector for Slack",
            version="0.1.0",
            supported_features=["read", "search"]
        )
    
    async def connect(self) -> None:
        """Establish connection to Slack."""
        self._client = WebClient(token=self.config.token)
    
    async def disconnect(self) -> None:
        """Close connection to Slack."""
        self._client = None
    
    async def fetch_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch messages from Slack channels."""
        if not self._client:
            await self.connect()
        
        # Default query parameters
        params = {
            "limit": self.config.max_results,
        }
        
        # Override with user query if provided
        if query:
            params.update(query)
        
        # Get messages from each channel
        all_messages = []
        channels = self.config.channels or self._get_all_channels()
        
        for channel in channels:
            try:
                # Get channel history
                result = self._client.conversations_history(
                    channel=channel,
                    **params
                )
                
                # Parse messages
                for message in result.get("messages", []):
                    parsed_message = self._parse_message(message, channel)
                    all_messages.append(parsed_message)
            
            except SlackApiError as e:
                print(f"Error fetching messages from channel {channel}: {e.response['error']}")
        
        return all_messages
    
    def _get_all_channels(self) -> List[str]:
        """Get all accessible channels."""
        try:
            result = self._client.conversations_list(types="public_channel,private_channel")
            return [channel["id"] for channel in result.get("channels", [])]
        except SlackApiError as e:
            print(f"Error fetching channels: {e.response['error']}")
            return []
    
    def _parse_message(self, message: Dict[str, Any], channel_id: str) -> Dict[str, Any]:
        """Parse Slack message into a structured format."""
        # Get user info if available
        user_info = {}
        if "user" in message:
            try:
                user_result = self._client.users_info(user=message["user"])
                user_info = user_result.get("user", {})
            except SlackApiError:
                pass
        
        # Get channel info
        channel_info = {}
        try:
            channel_result = self._client.conversations_info(channel=channel_id)
            channel_info = channel_result.get("channel", {})
        except SlackApiError:
            pass
        
        # Extract message content
        content = message.get("text", "")
        
        # Create a content field that combines relevant information
        formatted_content = f"Message from {user_info.get('name', 'Unknown')} in #{channel_info.get('name', 'Unknown')}:\n{content}"
        
        # Extract thread replies if available
        thread_replies = []
        if "thread_ts" in message and message["thread_ts"] == message["ts"]:
            try:
                thread_result = self._client.conversations_replies(
                    channel=channel_id,
                    ts=message["ts"]
                )
                
                for reply in thread_result.get("messages", [])[1:]:  # Skip the parent message
                    reply_user_info = {}
                    if "user" in reply:
                        try:
                            reply_user_result = self._client.users_info(user=reply["user"])
                            reply_user_info = reply_user_result.get("user", {})
                        except SlackApiError:
                            pass
                    
                    thread_replies.append({
                        "user": reply_user_info.get("name", "Unknown"),
                        "content": reply.get("text", ""),
                        "timestamp": reply.get("ts", "")
                    })
            except SlackApiError:
                pass
        
        return {
            "content": formatted_content,
            "metadata": {
                "id": message.get("client_msg_id", message.get("ts", "")),
                "channel_id": channel_id,
                "channel_name": channel_info.get("name", ""),
                "user_id": message.get("user", ""),
                "user_name": user_info.get("name", ""),
                "timestamp": message.get("ts", ""),
                "thread_ts": message.get("thread_ts", ""),
                "is_thread_reply": "thread_ts" in message and message["thread_ts"] != message["ts"],
                "thread_replies": thread_replies,
                "reactions": message.get("reactions", []),
                "attachments": message.get("attachments", []),
                "files": message.get("files", [])
            }
        } 