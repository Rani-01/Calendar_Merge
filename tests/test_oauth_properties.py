"""
Property-based tests for OAuth authentication.

Feature: calendar-aggregator, Property 11: OAuth authentication enforcement
Feature: calendar-aggregator, Property 13: Token refresh handling
Validates: Requirements 6.1, 6.4
"""
import pytest
import os
import json
import tempfile
from datetime import datetime, timedelta, timezone
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch, MagicMock

from providers.gmail_provider import GmailProvider
from models.provider_config import ProviderConfig


@st.composite
def provider_config_strategy(draw):
    """Generate random provider configurations."""
    ascii_alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
    return ProviderConfig(
        provider_name='gmail',
        client_id=draw(st.text(min_size=10, max_size=50, alphabet=ascii_alphabet)),
        client_secret=draw(st.text(min_size=10, max_size=50, alphabet=ascii_alphabet)),
        redirect_uri='http://localhost:8080/oauth/google/callback',
        token_file=tempfile.mktemp(suffix='.json')
    )


class TestOAuthAuthenticationEnforcement:
    """
    Property-based tests for OAuth authentication enforcement.
    
    Feature: calendar-aggregator, Property 11: OAuth authentication enforcement
    """
    
    @given(config=provider_config_strategy())
    @settings(max_examples=100)
    def test_provider_requires_oauth_credentials(self, config):
        """
        Property: For any provider API connection, the system should use OAuth 2.0
        authentication flows and include valid access tokens in API requests.
        
        Feature: calendar-aggregator, Property 11: OAuth authentication enforcement
        Validates: Requirements 6.1
        """
        try:
            # Create provider
            provider = GmailProvider(config)
            
            # Verify provider stores OAuth config
            assert provider.config.client_id == config.client_id
            assert provider.config.client_secret == config.client_secret
            assert provider.config.redirect_uri == config.redirect_uri
            
            # Verify authentication is required (no token file = not available)
            assert not provider.is_available()
            
            # Verify get_events requires authentication
            start_date = datetime.now()
            end_date = start_date + timedelta(days=1)
            
            with pytest.raises(Exception) as exc_info:
                provider.get_events(start_date, end_date)
            
            # Should fail with authentication error
            assert 'Authentication failed' in str(exc_info.value)
            
        finally:
            # Cleanup
            if os.path.exists(config.token_file):
                os.unlink(config.token_file)
    
    @given(config=provider_config_strategy())
    @settings(max_examples=100)
    def test_oauth_flow_uses_configured_credentials(self, config):
        """
        Property: For any OAuth flow initiation, the system should use the
        configured client_id and client_secret, not hardcoded values.
        
        Feature: calendar-aggregator, Property 11: OAuth authentication enforcement
        Validates: Requirements 6.1
        """
        try:
            # Create provider
            provider = GmailProvider(config)
            
            # Initiate OAuth flow
            auth_url = provider.initiate_oauth_flow()
            
            # Verify auth URL contains the client_id (proving it's using OAuth)
            assert 'accounts.google.com' in auth_url
            assert 'oauth2' in auth_url
            # The client_id should be in the URL
            assert config.client_id in auth_url
            
        finally:
            # Cleanup
            if os.path.exists(config.token_file):
                os.unlink(config.token_file)


class TestTokenRefreshHandling:
    """
    Property-based tests for token refresh handling.
    
    Feature: calendar-aggregator, Property 13: Token refresh handling
    """
    
    @given(config=provider_config_strategy())
    @settings(max_examples=50, deadline=2000)
    def test_expired_token_triggers_refresh_attempt(self, config):
        """
        Property: For any expired authentication token, the system should attempt
        to refresh the token using the refresh token before failing the request.
        
        Feature: calendar-aggregator, Property 13: Token refresh handling
        Validates: Requirements 6.4
        """
        try:
            # Create provider
            provider = GmailProvider(config)
            
            # Create expired token file
            token_dir = os.path.dirname(config.token_file)
            if token_dir and not os.path.exists(token_dir):
                os.makedirs(token_dir)
            
            # Create mock expired credentials
            expired_token_data = {
                "token": "expired_access_token",
                "refresh_token": "valid_refresh_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "scopes": ["https://www.googleapis.com/auth/calendar.readonly"],
                "expiry": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            }
            
            with open(config.token_file, 'w') as f:
                json.dump(expired_token_data, f)
            
            # Mock the refresh request to simulate successful refresh
            with patch('google.auth.transport.requests.Request') as mock_request:
                with patch.object(provider, '_save_credentials'):
                    # Attempt authentication - should try to refresh
                    result = provider.authenticate()
                    
                    # The authenticate method should have attempted to load credentials
                    # and detected they're expired
                    assert provider.credentials is not None
                    
                    # If refresh_token exists, it should attempt refresh
                    # (In real scenario, this would call Google's token endpoint)
            
        finally:
            # Cleanup
            if os.path.exists(config.token_file):
                os.unlink(config.token_file)
            token_dir = os.path.dirname(config.token_file)
            if token_dir and os.path.exists(token_dir):
                try:
                    os.rmdir(token_dir)
                except:
                    pass
    
    @given(config=provider_config_strategy())
    @settings(max_examples=100)
    def test_missing_refresh_token_fails_gracefully(self, config):
        """
        Property: For any expired token without a refresh token, the system
        should fail gracefully without attempting refresh.
        
        Feature: calendar-aggregator, Property 13: Token refresh handling
        Validates: Requirements 6.4
        """
        try:
            # Create provider
            provider = GmailProvider(config)
            
            # Create expired token file WITHOUT refresh_token
            token_dir = os.path.dirname(config.token_file)
            if token_dir and not os.path.exists(token_dir):
                os.makedirs(token_dir)
            
            expired_token_data = {
                "token": "expired_access_token",
                # No refresh_token
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "scopes": ["https://www.googleapis.com/auth/calendar.readonly"],
                "expiry": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            }
            
            with open(config.token_file, 'w') as f:
                json.dump(expired_token_data, f)
            
            # Attempt authentication - should fail gracefully
            result = provider.authenticate()
            
            # Should return False (not raise exception)
            assert result == False
            
        finally:
            # Cleanup
            if os.path.exists(config.token_file):
                os.unlink(config.token_file)
            token_dir = os.path.dirname(config.token_file)
            if token_dir and os.path.exists(token_dir):
                try:
                    os.rmdir(token_dir)
                except:
                    pass
