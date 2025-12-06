"""
Property-based tests for authentication failure reporting.

Feature: calendar-aggregator, Property 12: Authentication failure reporting
Validates: Requirements 6.3
"""
import pytest
import os
import tempfile
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings

from providers.gmail_provider import GmailProvider
from providers.outlook_provider import OutlookProvider
from models.provider_config import ProviderConfig


@st.composite
def provider_config_strategy(draw, provider_name='gmail'):
    """Generate random provider configurations."""
    ascii_alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
    return ProviderConfig(
        provider_name=provider_name,
        client_id=draw(st.text(min_size=10, max_size=50, alphabet=ascii_alphabet)),
        client_secret=draw(st.text(min_size=10, max_size=50, alphabet=ascii_alphabet)),
        redirect_uri=f'http://localhost:8080/oauth/{provider_name}/callback',
        token_file=tempfile.mktemp(suffix='.json')
    )


class TestAuthenticationFailureReporting:
    """
    Property-based tests for authentication failure reporting.
    
    Feature: calendar-aggregator, Property 12: Authentication failure reporting
    """
    
    @given(config=provider_config_strategy(provider_name='gmail'))
    @settings(max_examples=100)
    def test_gmail_auth_failure_identifies_provider(self, config):
        """
        Property: For any provider that fails authentication, the error response
        should explicitly identify which provider failed.
        
        Feature: calendar-aggregator, Property 12: Authentication failure reporting
        Validates: Requirements 6.3
        """
        try:
            # Create Gmail provider without valid credentials
            provider = GmailProvider(config)
            
            # Attempt to get events (should fail with auth error)
            start_date = datetime.now()
            end_date = start_date + timedelta(days=1)
            
            with pytest.raises(Exception) as exc_info:
                provider.get_events(start_date, end_date)
            
            # Error message should identify Gmail provider
            error_message = str(exc_info.value)
            assert 'Gmail provider' in error_message or 'gmail' in error_message.lower()
            assert 'Authentication failed' in error_message or 'auth' in error_message.lower()
            
        finally:
            # Cleanup
            if os.path.exists(config.token_file):
                os.unlink(config.token_file)
    
    @given(config=provider_config_strategy(provider_name='outlook'))
    @settings(max_examples=50, deadline=2000)
    def test_outlook_auth_failure_identifies_provider(self, config):
        """
        Property: For any provider that fails authentication, the error response
        should explicitly identify which provider failed.
        
        Feature: calendar-aggregator, Property 12: Authentication failure reporting
        Validates: Requirements 6.3
        """
        try:
            # Create Outlook provider without valid credentials
            provider = OutlookProvider(config)
            
            # Attempt to get events (should fail with auth error)
            start_date = datetime.now()
            end_date = start_date + timedelta(days=1)
            
            with pytest.raises(Exception) as exc_info:
                provider.get_events(start_date, end_date)
            
            # Error message should identify Outlook provider
            error_message = str(exc_info.value)
            assert 'Outlook provider' in error_message or 'outlook' in error_message.lower()
            assert 'Authentication failed' in error_message or 'auth' in error_message.lower()
            
        finally:
            # Cleanup
            if os.path.exists(config.token_file):
                os.unlink(config.token_file)
    
    @given(
        gmail_config=provider_config_strategy(provider_name='gmail'),
        outlook_config=provider_config_strategy(provider_name='outlook')
    )
    @settings(max_examples=25, deadline=2000)
    def test_different_providers_have_distinct_error_messages(self, gmail_config, outlook_config):
        """
        Property: For any two different providers that fail, their error messages
        should be distinguishable (identify which specific provider failed).
        
        Feature: calendar-aggregator, Property 12: Authentication failure reporting
        Validates: Requirements 6.3
        """
        try:
            # Create both providers
            gmail_provider = GmailProvider(gmail_config)
            outlook_provider = OutlookProvider(outlook_config)
            
            start_date = datetime.now()
            end_date = start_date + timedelta(days=1)
            
            # Get Gmail error
            gmail_error = None
            try:
                gmail_provider.get_events(start_date, end_date)
            except Exception as e:
                gmail_error = str(e)
            
            # Get Outlook error
            outlook_error = None
            try:
                outlook_provider.get_events(start_date, end_date)
            except Exception as e:
                outlook_error = str(e)
            
            # Both should have errors
            assert gmail_error is not None
            assert outlook_error is not None
            
            # Errors should be different (identify different providers)
            assert gmail_error != outlook_error
            
            # Gmail error should mention Gmail
            assert 'Gmail' in gmail_error or 'gmail' in gmail_error.lower()
            
            # Outlook error should mention Outlook
            assert 'Outlook' in outlook_error or 'outlook' in outlook_error.lower()
            
        finally:
            # Cleanup
            for config in [gmail_config, outlook_config]:
                if os.path.exists(config.token_file):
                    os.unlink(config.token_file)
