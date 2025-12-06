"""
Outlook calendar provider implementation.
"""
import os
import json
from datetime import datetime
from typing import List, Optional
import msal
import requests

from providers.base_provider import CalendarProvider
from models.schedule import Schedule
from models.provider_config import ProviderConfig


# Microsoft Graph API scopes
SCOPES = ['Calendars.Read']


class OutlookProvider(CalendarProvider):
    """
    Microsoft Outlook calendar provider implementation.
    
    Handles OAuth 2.0 authentication using MSAL and retrieves calendar events
    from Microsoft Graph API.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize Outlook provider with configuration.
        
        Args:
            config: Provider configuration with OAuth credentials
        """
        super().__init__('outlook')
        self.config = config
        self.token_cache = msal.SerializableTokenCache()
        self.app = None
        self._load_token_cache()
    
    def _load_token_cache(self) -> None:
        """Load token cache from file if it exists."""
        if os.path.exists(self.config.token_file):
            with open(self.config.token_file, 'r') as f:
                self.token_cache.deserialize(f.read())
    
    def _save_token_cache(self) -> None:
        """Save token cache to file."""
        # Ensure tokens directory exists
        token_dir = os.path.dirname(self.config.token_file)
        if token_dir and not os.path.exists(token_dir):
            os.makedirs(token_dir)
        
        # Save token cache
        with open(self.config.token_file, 'w') as f:
            f.write(self.token_cache.serialize())
    
    def _get_msal_app(self) -> msal.ConfidentialClientApplication:
        """
        Get or create MSAL application instance.
        
        Returns:
            MSAL ConfidentialClientApplication
        """
        if not self.app:
            self.app = msal.ConfidentialClientApplication(
                self.config.client_id,
                authority="https://login.microsoftonline.com/common",
                client_credential=self.config.client_secret,
                token_cache=self.token_cache
            )
        return self.app
    
    def authenticate(self) -> bool:
        """
        Authenticate with Microsoft Graph API using OAuth 2.0.
        
        Attempts to acquire token silently from cache.
        If token is expired, attempts to refresh it.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            app = self._get_msal_app()
            
            # Try to get token from cache
            accounts = app.get_accounts()
            if accounts:
                # Try to acquire token silently (will refresh if needed)
                result = app.acquire_token_silent(SCOPES, account=accounts[0])
                if result and 'access_token' in result:
                    self._save_token_cache()
                    return True
            
            # No valid token available
            return False
            
        except Exception as e:
            return False
    
    def initiate_oauth_flow(self) -> str:
        """
        Initiate OAuth flow and return authorization URL.
        
        Returns:
            Authorization URL for user to visit
        """
        app = self._get_msal_app()
        auth_url = app.get_authorization_request_url(
            SCOPES,
            redirect_uri=self.config.redirect_uri
        )
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
            app = self._get_msal_app()
            
            # Exchange code for token
            result = app.acquire_token_by_authorization_code(
                authorization_code,
                scopes=SCOPES,
                redirect_uri=self.config.redirect_uri
            )
            
            if 'access_token' in result:
                self._save_token_cache()
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """
        Retrieve calendar events from Microsoft Outlook.
        
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
            raise Exception("Outlook provider: Authentication failed")
        
        try:
            # Get access token
            app = self._get_msal_app()
            accounts = app.get_accounts()
            if not accounts:
                raise Exception("Outlook provider: No accounts found")
            
            result = app.acquire_token_silent(SCOPES, account=accounts[0])
            if not result or 'access_token' not in result:
                raise Exception("Outlook provider: Failed to acquire token")
            
            access_token = result['access_token']
            
            # Format dates for API (ISO 8601)
            start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
            end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Call Microsoft Graph API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Build query parameters
            params = {
                '$filter': f"start/dateTime ge '{start_str}' and end/dateTime le '{end_str}'",
                '$orderby': 'start/dateTime',
                '$select': 'id,subject,bodyPreview,start,end,location,attendees'
            }
            
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me/calendar/events',
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Outlook provider: API error - {response.status_code}")
            
            events = response.json().get('value', [])
            
            # Transform to Schedule objects
            schedules = []
            for event in events:
                schedule = self._transform_event_to_schedule(event)
                if schedule:
                    schedules.append(schedule)
            
            return schedules
            
        except requests.RequestException as e:
            raise Exception(f"Outlook provider: Network error - {str(e)}")
        except Exception as e:
            raise Exception(f"Outlook provider: {str(e)}")
    
    def _transform_event_to_schedule(self, event: dict) -> Optional[Schedule]:
        """
        Transform Microsoft Graph event to Schedule object.
        
        Args:
            event: Microsoft Graph event dictionary
            
        Returns:
            Schedule object or None if event cannot be transformed
        """
        try:
            # Get event ID
            event_id = event.get('id', '')
            
            # Get title (subject in Outlook)
            title = event.get('subject', 'No Title')
            
            # Get description (bodyPreview in Outlook)
            description = event.get('bodyPreview')
            
            # Get start and end times
            start = event.get('start', {})
            end = event.get('end', {})
            
            if 'dateTime' not in start or 'dateTime' not in end:
                return None
            
            # Parse datetime strings
            start_time = datetime.fromisoformat(start['dateTime'])
            end_time = datetime.fromisoformat(end['dateTime'])
            
            # Get location
            location_obj = event.get('location', {})
            location = location_obj.get('displayName') if location_obj else None
            
            # Get attendees
            attendees = []
            if 'attendees' in event:
                attendees = [
                    attendee.get('emailAddress', {}).get('address', '')
                    for attendee in event['attendees']
                    if attendee.get('emailAddress', {}).get('address')
                ]
            
            return Schedule(
                id=event_id,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                provider='outlook',
                location=location,
                attendees=attendees
            )
            
        except Exception as e:
            # Skip events that can't be transformed
            return None
    
    def is_available(self) -> bool:
        """
        Check if Outlook provider is available.
        
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
