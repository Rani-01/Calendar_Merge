"""
Configuration manager for loading and validating application settings.
"""
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from models.provider_config import ProviderConfig

# Try to import app_secrets.py if it exists
try:
    import app_secrets
    HAS_SECRETS = True
except ImportError:
    HAS_SECRETS = False


class ConfigManager:
    """
    Manages application configuration from environment variables.
    
    Loads OAuth credentials and application settings from .env file
    and environment variables.
    """
    
    def __init__(self, env_file: str = '.env'):
        """
        Initialize ConfigManager and load environment variables.
        
        Args:
            env_file: Path to .env file (default: '.env')
        """
        # Load environment variables from .env file
        load_dotenv(env_file)
        
        self._providers: Dict[str, ProviderConfig] = {}
        self._load_provider_configs()
    
    def _load_provider_configs(self) -> None:
        """
        Load provider configurations from environment variables.
        
        Loads configurations for Gmail and Outlook providers.
        """
        # Load Gmail configuration
        gmail_config = self._load_gmail_config()
        if gmail_config and gmail_config.is_valid():
            self._providers['gmail'] = gmail_config
        
        # Load Outlook configuration
        outlook_config = self._load_outlook_config()
        if outlook_config and outlook_config.is_valid():
            self._providers['outlook'] = outlook_config
    
    def _load_gmail_config(self) -> Optional[ProviderConfig]:
        """
        Load Gmail provider configuration from environment variables or secrets.py.
        
        Returns:
            ProviderConfig for Gmail or None if not configured
        """
        # Try environment variables first
        client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/oauth/google/callback')
        
        # Fallback to secrets.py if available
        if HAS_SECRETS and (not client_id or not client_secret):
            client_id = getattr(app_secrets, 'GOOGLE_CLIENT_ID', '')
            client_secret = getattr(app_secrets, 'GOOGLE_CLIENT_SECRET', '')
            redirect_uri = getattr(app_secrets, 'GOOGLE_REDIRECT_URI', 'http://localhost:8080/oauth/google/callback')
        
        if not client_id or not client_secret:
            return None
        
        return ProviderConfig(
            provider_name='gmail',
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            token_file='tokens/google_token.json'
        )
    
    def _load_outlook_config(self) -> Optional[ProviderConfig]:
        """
        Load Outlook provider configuration from environment variables or secrets.py.
        
        Returns:
            ProviderConfig for Outlook or None if not configured
        """
        # Try environment variables first
        client_id = os.getenv('MICROSOFT_CLIENT_ID', '')
        client_secret = os.getenv('MICROSOFT_CLIENT_SECRET', '')
        redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI', 'http://localhost:8080/oauth/microsoft/callback')
        
        # Fallback to secrets.py if available
        if HAS_SECRETS and (not client_id or not client_secret):
            client_id = getattr(app_secrets, 'MICROSOFT_CLIENT_ID', '')
            client_secret = getattr(app_secrets, 'MICROSOFT_CLIENT_SECRET', '')
            redirect_uri = getattr(app_secrets, 'MICROSOFT_REDIRECT_URI', 'http://localhost:8080/oauth/microsoft/callback')
        
        if not client_id or not client_secret:
            return None
        
        return ProviderConfig(
            provider_name='outlook',
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            token_file='tokens/microsoft_token.json'
        )
    
    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider_name: Name of the provider ('gmail' or 'outlook')
            
        Returns:
            ProviderConfig if configured, None otherwise
        """
        return self._providers.get(provider_name.lower())
    
    def get_all_provider_configs(self) -> Dict[str, ProviderConfig]:
        """
        Get all configured provider configurations.
        
        Returns:
            Dictionary mapping provider names to their configurations
        """
        return self._providers.copy()
    
    def get_configured_providers(self) -> List[str]:
        """
        Get list of configured provider names.
        
        Returns:
            List of provider names that are configured
        """
        return list(self._providers.keys())
    
    def is_provider_configured(self, provider_name: str) -> bool:
        """
        Check if a provider is configured.
        
        Args:
            provider_name: Name of the provider to check
            
        Returns:
            True if provider is configured, False otherwise
        """
        return provider_name.lower() in self._providers
    
    def validate_configuration(self) -> tuple[bool, List[str]]:
        """
        Validate that at least one provider is configured.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not self._providers:
            errors.append("No calendar providers configured. Please set up at least one provider in .env file.")
        
        # Validate each configured provider
        for provider_name, config in self._providers.items():
            if not config.is_valid():
                errors.append(f"{provider_name} configuration is incomplete")
        
        return len(errors) == 0, errors
    
    def get_port(self) -> int:
        """
        Get the port number for the Flask application.
        
        Returns:
            Port number (default: 8080)
        """
        port = os.getenv('PORT', '')
        if not port and HAS_SECRETS:
            port = str(getattr(app_secrets, 'PORT', '8080'))
        return int(port or '8080')
    
    def get_flask_env(self) -> str:
        """
        Get the Flask environment setting.
        
        Returns:
            Flask environment ('development' or 'production')
        """
        env = os.getenv('FLASK_ENV', '')
        if not env and HAS_SECRETS:
            env = getattr(app_secrets, 'FLASK_ENV', 'development')
        return env or 'development'
    
    def is_debug_mode(self) -> bool:
        """
        Check if application should run in debug mode.
        
        Returns:
            True if in development mode, False otherwise
        """
        return self.get_flask_env() == 'development'
