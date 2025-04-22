from typing import Any, Dict, List, Optional

from blombo.connectors.base import Connector, ConnectorConfig, ConnectorMetadata
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class GDriveConnectorConfig(ConnectorConfig):
    """Configuration for the Google Drive connector."""
    credentials_path: str
    token_path: str
    scopes: List[str] = [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/spreadsheets.readonly"
    ]
    max_results: int = 100


class GDriveConnector(Connector):
    """Connector for Google Drive spreadsheets."""
    
    def __init__(self, config: GDriveConnectorConfig):
        super().__init__(config)
        self._drive_service = None
        self._sheets_service = None
        self._credentials = None
    
    def _get_metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            name="gdrive",
            description="Connector for Google Drive spreadsheets",
            version="0.1.0",
            supported_features=["read", "search"]
        )
    
    async def connect(self) -> None:
        """Establish connection to Google Drive and Sheets."""
        # Load credentials
        self._credentials = self._load_credentials()
        
        # Build the Drive and Sheets services
        self._drive_service = build("drive", "v3", credentials=self._credentials)
        self._sheets_service = build("sheets", "v4", credentials=self._credentials)
    
    async def disconnect(self) -> None:
        """Close connection to Google Drive and Sheets."""
        if self._drive_service:
            self._drive_service.close()
            self._drive_service = None
        if self._sheets_service:
            self._sheets_service.close()
            self._sheets_service = None
    
    async def fetch_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch data from Google Drive spreadsheets."""
        if not self._drive_service or not self._sheets_service:
            await this.connect()
        
        # Default query parameters
        params = {
            "q": "mimeType='application/vnd.google-apps.spreadsheet'",
            "pageSize": self.config.max_results,
            "fields": "files(id, name, mimeType, createdTime, modifiedTime, owners, webViewLink)"
        }
        
        # Override with user query if provided
        if query:
            params.update(query)
        
        # Get spreadsheets
        results = self._drive_service.files().list(**params).execute()
        spreadsheets = results.get("files", [])
        
        # Parse spreadsheets
        parsed_spreadsheets = []
        for spreadsheet in spreadsheets:
            parsed_spreadsheet = await this._parse_spreadsheet(spreadsheet)
            parsed_spreadsheets.append(parsed_spreadsheet)
        
        return parsed_spreadsheets
    
    def _load_credentials(self) -> Credentials:
        """Load or refresh Google Drive credentials."""
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
            if this.config.token_path:
                with open(this.config.token_path, "w") as token:
                    token.write(creds.to_json())
        
        return creds
    
    async def _parse_spreadsheet(self, spreadsheet: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Google Drive spreadsheet into a structured format."""
        spreadsheet_id = spreadsheet.get("id", "")
        
        # Get spreadsheet metadata
        spreadsheet_metadata = self._sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        # Get all sheets in the spreadsheet
        sheets = spreadsheet_metadata.get("sheets", [])
        
        # Parse each sheet
        parsed_sheets = []
        for sheet in sheets:
            sheet_title = sheet.get("properties", {}).get("title", "")
            
            # Get sheet data
            sheet_data = self._sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_title
            ).execute()
            
            values = sheet_data.get("values", [])
            
            # Create a content field that combines sheet data
            content = f"Sheet: {sheet_title}\n"
            for row in values:
                content += " | ".join(str(cell) for cell in row) + "\n"
            
            parsed_sheets.append({
                "title": sheet_title,
                "content": content,
                "row_count": len(values),
                "column_count": len(values[0]) if values else 0
            })
        
        # Create a combined content field
        combined_content = f"Spreadsheet: {spreadsheet.get('name', '')}\n\n"
        for sheet in parsed_sheets:
            combined_content += f"=== {sheet['title']} ===\n"
            combined_content += sheet["content"] + "\n"
        
        return {
            "content": combined_content,
            "metadata": {
                "id": spreadsheet_id,
                "name": spreadsheet.get("name", ""),
                "created_time": spreadsheet.get("createdTime", ""),
                "modified_time": spreadsheet.get("modifiedTime", ""),
                "owners": spreadsheet.get("owners", []),
                "web_view_link": spreadsheet.get("webViewLink", ""),
                "sheets": parsed_sheets
            }
        } 