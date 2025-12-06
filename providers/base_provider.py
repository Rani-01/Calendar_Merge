"""
Abstract base class for calendar providers.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from models.schedule import Schedule


class CalendarProvider(ABC):
    """
    Abstract base class defining the interface for calendar providers.
    
    All calendar provider implementations (Gmail, Outlook, etc.) must
    implement this interface to ensure consistent behavior across providers.
    """
    
    def __init__(self, provider_name: str):
        """
        Initialize the calendar provider.
        
        Args:
            provider_name: Name of the provider (e.g., 'gmail', 'outlook')
        """
        self.provider_name = provider_name
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the calendar provider using OAuth 2.0.
        
        This method should handle the OAuth flow, including token refresh
        if the current token is expired.
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Schedule]:
        """
        Retrieve calendar events within the specified date range.
        
        Args:
            start_date: Start of the date range (inclusive)
            end_date: End of the date range (inclusive)
            
        Returns:
            List of Schedule objects representing calendar events
            
        Raises:
            Exception: If authentication fails or API call fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and properly configured.
        
        This method should verify that:
        - Configuration is complete
        - Authentication credentials exist
        - The provider service is reachable (optional)
        
        Returns:
            True if provider is available, False otherwise
        """
        pass
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return self.provider_name
