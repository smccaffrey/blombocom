from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from blombo.connectors.base import Connector, ConnectorConfig, ConnectorMetadata
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class GCalConnectorConfig(ConnectorConfig):
    """Configuration for the Google Calendar connector."""
    credentials_path: str
    token_path: str
    scopes: List[str] = [
        "https://www.googleapis.com/auth/calendar.readonly"
    ]
    calendar_id: str = "primary"
    days_back: int = 30
    days_forward: int = 30
    max_results: int = 100


class GCalConnector(Connector):
    """Connector for Google Calendar."""
    
    def __init__(self, config: GCalConnectorConfig):
        super().__init__(config)
        self._service = None
        self._credentials = None
    
    def _get_metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            name="gcal",
            description="Connector for Google Calendar",
            version="0.1.0",
            supported_features=["read", "search"]
        )
    
    async def connect(self) -> None:
        """Establish connection to Google Calendar."""
        # Load credentials
        self._credentials = self._load_credentials()
        
        # Build the Calendar service
        self._service = build("calendar", "v3", credentials=self._credentials)
    
    async def disconnect(self) -> None:
        """Close connection to Google Calendar."""
        if self._service:
            self._service.close()
            self._service = None
    
    async def fetch_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch events from Google Calendar."""
        if not self._service:
            await self.connect()
        
        # Default time range
        now = datetime.utcnow()
        time_min = (now - timedelta(days=self.config.days_back)).isoformat() + "Z"
        time_max = (now + timedelta(days=self.config.days_forward)).isoformat() + "Z"
        
        # Default query parameters
        params = {
            "calendarId": self.config.calendar_id,
            "timeMin": time_min,
            "timeMax": time_max,
            "maxResults": self.config.max_results,
            "singleEvents": True,
            "orderBy": "startTime"
        }
        
        # Override with user query if provided
        if query:
            params.update(query)
        
        # Get events
        events_result = self._service.events().list(**params).execute()
        events = events_result.get("items", [])
        
        # Parse events
        parsed_events = []
        for event in events:
            parsed_event = self._parse_event(event)
            parsed_events.append(parsed_event)
        
        return parsed_events
    
    def _load_credentials(self) -> Credentials:
        """Load or refresh Google Calendar credentials."""
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
    
    def _parse_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Google Calendar event into a structured format."""
        # Extract start and end times
        start = event.get("start", {})
        end = event.get("end", {})
        
        # Get the actual datetime objects
        start_time = start.get("dateTime", start.get("date", ""))
        end_time = end.get("dateTime", end.get("date", ""))
        
        # Extract attendees
        attendees = []
        for attendee in event.get("attendees", []):
            attendees.append({
                "email": attendee.get("email", ""),
                "name": attendee.get("displayName", ""),
                "response_status": attendee.get("responseStatus", "")
            })
        
        # Extract location
        location = event.get("location", "")
        
        # Extract description
        description = event.get("description", "")
        
        # Create a content field that combines relevant information
        content = f"Event: {event.get('summary', '')}\n"
        if description:
            content += f"Description: {description}\n"
        if location:
            content += f"Location: {location}\n"
        if attendees:
            content += "Attendees:\n"
            for attendee in attendees:
                content += f"- {attendee['name']} ({attendee['email']}): {attendee['response_status']}\n"
        
        return {
            "content": content,
            "metadata": {
                "id": event.get("id", ""),
                "summary": event.get("summary", ""),
                "description": description,
                "location": location,
                "start_time": start_time,
                "end_time": end_time,
                "created": event.get("created", ""),
                "updated": event.get("updated", ""),
                "status": event.get("status", ""),
                "attendees": attendees,
                "organizer": event.get("organizer", {}),
                "recurrence": event.get("recurrence", []),
                "html_link": event.get("htmlLink", "")
            }
        } 