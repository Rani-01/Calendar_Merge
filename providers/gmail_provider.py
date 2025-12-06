"""
Gmail calendar provider implementation.
"""
import os
import json
from datetime import datetime
from typing import List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from providers.base_provider import CalendarProvider
from models.schedule import Schedule
from models.provider_config import ProviderConfig


# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GmailProvider(CalendarProvider):
    """
    Google Calendar provider implementation.
    
    Handles OAuth 2.0 authentication and retrieves calendar events
    from Google Calendar API.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize Gmail provider with configuration.
        
        Args:
            config: Provider configuration with OAuth credentials
        """
        super().__init__('gmail')
        self.config = config
        self.credentials: Optional[Credentials] = None
        self.service = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API using OAuth 2.0.
        
        Attempts to load existing credentials from token file.
        If credentials are expired, attempts to refresh them.
        If no valid credentials exist, returns False.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load credentials from token file if it exists
            if os.path.exists(self.config.token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.config.token_file, SCOPES
                )
            
            # If credentials don't exist or are invalid
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    # Refresh expired credentials
                    try:
                        self.credentials.refresh(Request())
                        self._save_credentials()
                        return True
                    except Exception as e:
                        # Refresh failed
                        return False
                else:
                    # No valid credentials available
                    return False
            
            return True
            
        except Exception as e:
            return False
    
    def _save_credentials(self) -> None:
        """
        Save credentials to token file.
        
        Creates the tokens directory if it doesn't exist.
        """
        # Ensure tokens directory exists
        token_dir = os.path.dirname(self.config.token_file)
        if token_dir and not os.path.exists(token_dir):
            os.makedirs(token_dir)
        
        # Save credentials
        with open(self.config.token_file, 'w') as token:
            token.write(self.credentials.to_json())
    
    def initiate_oauth_flow(self) -> str:
        """
        Initiate OAuth flow and return authorization URL.
        
        This is used by the OAuth callback endpoint to start the flow.
        
        Returns:
            Authorization URL for user to visit
        """
        # Strip whitespace from credentials (common issue)
        client_id = self.config.client_id.strip()
        client_secret = self.config.client_secret.strip()
        redirect_uri = self.config.redirect_uri.strip()
        
        # Create OAuth flow
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uris": [redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            SCOPES,
            redirect_uri=redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    
    def handle_oauth_callback(self, authorization_code: str) -> bool:
        """
        Handle OAuth callback with authorization code.
        
        Exchanges authorization code for access token and refresh token.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create OAuth flow
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": self.config.client_id,
                        "client_secret": self.config.client_secret,
                        "redirect_uris": [self.config.redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                SCOPES,
                redirect_uri=self.config.redirect_uri
            )
            
            # Exchange code for credentials
            flow.fetch_token(code=authorization_code)
            self.credentials = flow.credentials
            
            # Save credentials
            self._save_credentials()
            
            return True
            
        except Exception as e:
            return False
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """
        Retrieve calendar events from Google Calendar.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of Schedule objects
            
        Raises:
            Exception: If authentication fails or API call fails
        """
        # Ensure authenticated
        if not self.authenticate():
            raise Exception("Gmail provider: Authentication failed")
        
        try:
            # Build service if not already built
            if not self.service:
                self.service = build('calendar', 'v3', credentials=self.credentials)
            
            # Format dates for API (Google expects RFC3339 format with Z for UTC)
            # Remove timezone info and add Z (Google Calendar API requirement)
            time_min = start_date.replace(tzinfo=None).isoformat() + 'Z'
            time_max = end_date.replace(tzinfo=None).isoformat() + 'Z'
            
            # Call Google Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Transform to Schedule objects
            schedules = []
            for event in events:
                schedule = self._transform_event_to_schedule(event)
                if schedule:
                    schedules.append(schedule)
            
            return schedules
            
        except HttpError as e:
            raise Exception(f"Gmail provider: API error - {str(e)}")
        except Exception as e:
            raise Exception(f"Gmail provider: {str(e)}")
    
    def _transform_event_to_schedule(self, event: dict) -> Optional[Schedule]:
        """
        Transform Google Calendar event to Schedule object.
        
        Args:
            event: Google Calendar event dictionary
            
        Returns:
            Schedule object or None if event cannot be transformed
        """
        try:
            # Get event ID
            event_id = event.get('id', '')
            
            # Get title
            title = event.get('summary', 'No Title')
            
            # Get description
            description = event.get('description')
            
            # Get start and end times
            start = event.get('start', {})
            end = event.get('end', {})
            
            # Handle both datetime and date-only events
            if 'dateTime' in start:
                start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
            elif 'date' in start:
                start_time = datetime.fromisoformat(start['date'] + 'T00:00:00')
            else:
                return None
            
            if 'dateTime' in end:
                end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
            elif 'date' in end:
                end_time = datetime.fromisoformat(end['date'] + 'T23:59:59')
            else:
                return None
            
            # Get location
            location = event.get('location')
            
            # Get attendees
            attendees = []
            if 'attendees' in event:
                attendees = [
                    attendee.get('email', '')
                    for attendee in event['attendees']
                    if 'email' in attendee
                ]
            
            return Schedule(
                id=event_id,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                provider='gmail',
                location=location,
                attendees=attendees
            )
            
        except Exception as e:
            # Skip events that can't be transformed
            return None
    
    def is_available(self) -> bool:
        """
        Check if Gmail provider is available.
        
        Verifies that configuration is valid and credentials exist.
        
        Returns:
            True if available, False otherwise
        """
        # Check configuration
        if not self.config or not self.config.is_valid():
            return False
        
        # Check if token file exists
        if not os.path.exists(self.config.token_file):
            return False
        
        # Try to authenticate
        return self.authenticate()
