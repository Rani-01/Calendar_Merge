"""
Property-based tests for ConfigManager.

Feature: calendar-aggregator, Property 10: Configuration-based credential management
Validates: Requirements 5.4
"""
import pytest
import os
import tempfile
from hypothesis import given, strategies as st, settings
from config.config_manager import ConfigManager


@st.composite
def env_config_strategy(draw):
    """
    Generate random but valid environment configurations.
    
    Returns:
        Dictionary of environment variables
    """
    # Generate random credentials using ASCII-safe characters
    ascii_alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
    google_client_id = draw(st.text(min_size=10, max_size=50, alphabet=ascii_alphabet))
    google_client_secret = draw(st.text(min_size=10, max_size=50, alphabet=ascii_alphabet))
    
    microsoft_client_id = draw(st.text(min_size=10, max_size=50, alphabet=ascii_alphabet))
    microsoft_client_secret = draw(st.text(min_size=10, max_size=50, alphabet=ascii_alphabet))
    
    port = draw(st.integers(min_value=1024, max_value=65535))
    
    return {
        'GOOGLE_CLIENT_ID': google_client_id,
        'GOOGLE_CLIENT_SECRET': google_client_secret,
        'GOOGLE_REDIRECT_URI': 'http://localhost:8080/oauth/google/callback',
        'MICROSOFT_CLIENT_ID': microsoft_client_id,
        'MICROSOFT_CLIENT_SECRET': microsoft_client_secret,
        'MICROSOFT_REDIRECT_URI': 'http://localhost:8080/oauth/microsoft/callback',
        'PORT': str(port),
        'FLASK_ENV': draw(st.sampled_from(['development', 'production']))
    }


class TestConfigurationBasedCredentialManagement:
    """
    Property-based tests for configuration-based credential management.
    
    Feature: calendar-aggregator, Property 10: Configuration-based credential management
    """
    
    @given(env_vars=env_config_strategy())
    @settings(max_examples=100)
    def test_credentials_loaded_from_env_not_hardcoded(self, env_vars):
        """
        Property: For any provider configuration, credentials should be loaded
        exclusively from environment variables, never hardcoded.
        
        Feature: calendar-aggregator, Property 10: Configuration-based credential management
        Validates: Requirements 5.4
        """
        # Create temporary .env file with UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
            temp_env_file = f.name
        
        try:
            # Set environment variables
            for key, value in env_vars.items():
                os.environ[key] = value
            
            # Load configuration
            config_manager = ConfigManager(temp_env_file)
            
            # Verify Gmail config loaded from env vars
            gmail_config = config_manager.get_provider_config('gmail')
            if gmail_config:
                assert gmail_config.client_id == env_vars['GOOGLE_CLIENT_ID']
                assert gmail_config.client_secret == env_vars['GOOGLE_CLIENT_SECRET']
                assert gmail_config.redirect_uri == env_vars['GOOGLE_REDIRECT_URI']
                # Verify no hardcoded values
                assert gmail_config.client_id != ''
                assert gmail_config.client_secret != ''
            
            # Verify Outlook config loaded from env vars
            outlook_config = config_manager.get_provider_config('outlook')
            if outlook_config:
                assert outlook_config.client_id == env_vars['MICROSOFT_CLIENT_ID']
                assert outlook_config.client_secret == env_vars['MICROSOFT_CLIENT_SECRET']
                assert outlook_config.redirect_uri == env_vars['MICROSOFT_REDIRECT_URI']
                # Verify no hardcoded values
                assert outlook_config.client_id != ''
                assert outlook_config.client_secret != ''
            
            # Verify port loaded from env
            assert config_manager.get_port() == int(env_vars['PORT'])
            
        finally:
            # Cleanup
            os.unlink(temp_env_file)
            for key in env_vars.keys():
                os.environ.pop(key, None)
    
    @given(env_vars=env_config_strategy())
    @settings(max_examples=100)
    def test_config_changes_with_different_env_vars(self, env_vars):
        """
        Property: For any different set of environment variables, the configuration
        should reflect those specific values, proving no hardcoding.
        
        Feature: calendar-aggregator, Property 10: Configuration-based credential management
        Validates: Requirements 5.4
        """
        # Create temporary .env file with UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
            temp_env_file = f.name
        
        try:
            # Set environment variables
            for key, value in env_vars.items():
                os.environ[key] = value
            
            # Load configuration
            config_manager = ConfigManager(temp_env_file)
            
            # Get configs
            gmail_config = config_manager.get_provider_config('gmail')
            outlook_config = config_manager.get_provider_config('outlook')
            
            # Verify configs match the specific env vars provided
            if gmail_config:
                # The config should exactly match what we provided
                assert gmail_config.client_id == env_vars['GOOGLE_CLIENT_ID']
                assert gmail_config.client_secret == env_vars['GOOGLE_CLIENT_SECRET']
            
            if outlook_config:
                # The config should exactly match what we provided
                assert outlook_config.client_id == env_vars['MICROSOFT_CLIENT_ID']
                assert outlook_config.client_secret == env_vars['MICROSOFT_CLIENT_SECRET']
            
        finally:
            # Cleanup
            os.unlink(temp_env_file)
            for key in env_vars.keys():
                os.environ.pop(key, None)
    
    def test_missing_env_vars_results_in_no_hardcoded_fallback(self):
        """
        Property: When environment variables are missing, no hardcoded credentials
        should be used as fallback.
        
        Feature: calendar-aggregator, Property 10: Configuration-based credential management
        Validates: Requirements 5.4
        """
        # Create empty .env file with UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
            temp_env_file = f.name
        
        try:
            # Clear any existing env vars
            env_keys = [
                'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REDIRECT_URI',
                'MICROSOFT_CLIENT_ID', 'MICROSOFT_CLIENT_SECRET', 'MICROSOFT_REDIRECT_URI'
            ]
            for key in env_keys:
                os.environ.pop(key, None)
            
            # Load configuration with no env vars
            config_manager = ConfigManager(temp_env_file)
            
            # Verify no providers are configured (no hardcoded fallback)
            assert len(config_manager.get_configured_providers()) == 0
            assert config_manager.get_provider_config('gmail') is None
            assert config_manager.get_provider_config('outlook') is None
            
        finally:
            # Cleanup
            os.unlink(temp_env_file)
    
    @given(
        client_id=st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        client_secret=st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    )
    @settings(max_examples=100)
    def test_partial_config_not_loaded_without_all_required_fields(self, client_id, client_secret):
        """
        Property: For any partial configuration (missing required fields),
        the provider should not be loaded, ensuring no hardcoded defaults fill gaps.
        
        Feature: calendar-aggregator, Property 10: Configuration-based credential management
        Validates: Requirements 5.4
        """
        # Create .env with only client_id (missing client_secret) with UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
            f.write(f"GOOGLE_CLIENT_ID={client_id}\n")
            # Intentionally omit GOOGLE_CLIENT_SECRET
            temp_env_file = f.name
        
        try:
            os.environ['GOOGLE_CLIENT_ID'] = client_id
            os.environ.pop('GOOGLE_CLIENT_SECRET', None)
            
            # Load configuration
            config_manager = ConfigManager(temp_env_file)
            
            # Verify Gmail is not configured (no hardcoded secret filled in)
            assert config_manager.get_provider_config('gmail') is None
            
        finally:
            # Cleanup
            os.unlink(temp_env_file)
            os.environ.pop('GOOGLE_CLIENT_ID', None)
