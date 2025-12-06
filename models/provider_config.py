"""
ProviderConfig data model for calendar provider configuration.
"""
from dataclasses import dataclass


@dataclass
class ProviderConfig:
    """
    Configuration for a calendar provider's OAuth credentials.
    
    Attributes:
        provider_name: Name of the provider (e.g., 'gmail', 'outlook')
        client_id: OAuth client ID
        client_secret: OAuth client secret
        redirect_uri: OAuth redirect URI for callback
        token_file: Path to file for storing OAuth tokens
    """
    provider_name: str
    client_id: str
    client_secret: str
    redirect_uri: str
    token_file: str
    
    def is_valid(self) -> bool:
        """
        Check if configuration has all required fields.
        
        Returns:
            True if all fields are non-empty, False otherwise
        """
        return all([
            self.provider_name,
            self.client_id,
            self.client_secret,
            self.redirect_uri,
            self.token_file
        ])
