import base64
import email
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from blombo.connectors.base import Connector, ConnectorConfig, ConnectorMetadata
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class GmailConnectorConfig(ConnectorConfig):
    """Configuration for the Gmail connector."""
    credentials_path: str
    token_path: str
    scopes: List[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.metadata"
    ]
    max_results: int = 100
    days_back: int = 30


class GmailConnector(Connector):
    """Connector for Gmail."""
    
    def __init__(self, config: GmailConnectorConfig):
        super().__init__(config)
        self._service = None
        self._credentials = None
    
    def _get_metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            name="gmail",
            description="Connector for Gmail",
            version="0.1.0",
            supported_features=["read", "search"]
        )
    
    async def connect(self) -> None:
        """Establish connection to Gmail."""
        # Load credentials
        self._credentials = self._load_credentials()
        
        # Build the Gmail service
        self._service = build("gmail", "v1", credentials=self._credentials)
    
    async def disconnect(self) -> None:
        """Close connection to Gmail."""
        if self._service:
            self._service.close()
            self._service = None
    
    async def fetch_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail."""
        if not self._service:
            await this.connect()
        
        # Default query parameters
        params = {
            "maxResults": self.config.max_results,
            "q": "after:" + (datetime.now() - timedelta(days=self.config.days_back)).strftime("%Y/%m/%d")
        }
        
        # Override with user query if provided
        if query:
            params.update(query)
        
        # Get list of messages
        results = self._service.users().messages().list(userId="me", **params).execute()
        messages = results.get("messages", [])
        
        # Fetch full message details
        emails = []
        for message in messages:
            msg = self._service.users().messages().get(userId="me", id=message["id"], format="full").execute()
            
            # Parse email data
            email_data = self._parse_email(msg)
            emails.append(email_data)
        
        return emails
    
    def _load_credentials(self) -> Credentials:
        """Load or refresh Gmail credentials."""
        creds = None
        
        # Try to load token from file
        if self.config.token_path:
            try:
                creds = Credentials.from_authorized_user_file(self.config.token_path, self.config.scopes)
            except Exception:
                pass
        
        # If credentials are invalid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.credentials_path, self.config.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for future use
            if self.config.token_path:
                with open(self.config.token_path, "w") as token:
                    token.write(creds.to_json())
        
        return creds
    
    def _parse_email(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into a structured format."""
        # Extract headers
        headers = {}
        for header in message.get("payload", {}).get("headers", []):
            headers[header["name"].lower()] = header["value"]
        
        # Get email body
        body = ""
        if "parts" in message.get("payload", {}):
            for part in message["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    break
        elif "body" in message.get("payload", {}):
            if "data" in message["payload"]["body"]:
                body = base64.urlsafe_b64decode(message["payload"]["body"]["data"]).decode("utf-8")
        
        # Extract metadata
        metadata = {
            "id": message["id"],
            "thread_id": message.get("threadId", ""),
            "label_ids": message.get("labelIds", []),
            "snippet": message.get("snippet", ""),
            "internal_date": message.get("internalDate", ""),
            "size_estimate": message.get("sizeEstimate", 0)
        }
        
        # Parse date
        date_str = headers.get("date", "")
        if date_str:
            try:
                date_obj = email.utils.parsedate_to_datetime(date_str)
                metadata["parsed_date"] = date_obj.isoformat()
            except Exception:
                pass
        
        return {
            "content": body,
            "metadata": {
                **metadata,
                "from": headers.get("from", ""),
                "to": headers.get("to", ""),
                "subject": headers.get("subject", ""),
                "date": headers.get("date", ""),
                "message_id": headers.get("message-id", "")
            }
        } 