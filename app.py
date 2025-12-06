"""
Calendar Aggregator Flask Application.
"""
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
import logging

from config.config_manager import ConfigManager
from services.schedule_aggregator import ScheduleAggregator
from providers.gmail_provider import GmailProvider
from providers.outlook_provider import OutlookProvider
from models.view_type import ViewType
from models.api_response import APIResponse

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for configuration and services
config_manager = None
schedule_aggregator = None


def initialize_app():
    """Initialize application configuration and services."""
    global config_manager, schedule_aggregator
    
    # Load configuration
    config_manager = ConfigManager()
    
    # Validate configuration
    is_valid, errors = config_manager.validate_configuration()
    if not is_valid:
        logger.warning(f"Configuration issues: {', '.join(errors)}")
    
    # Initialize providers
    providers = []
    
    # Initialize Gmail provider if configured
    gmail_config = config_manager.get_provider_config('gmail')
    if gmail_config:
        gmail_provider = GmailProvider(gmail_config)
        providers.append(gmail_provider)
        logger.info("Gmail provider initialized")
    
    # Initialize Outlook provider if configured
    outlook_config = config_manager.get_provider_config('outlook')
    if outlook_config:
        outlook_provider = OutlookProvider(outlook_config)
        providers.append(outlook_provider)
        logger.info("Outlook provider initialized")
    
    # Initialize schedule aggregator
    schedule_aggregator = ScheduleAggregator(providers)
    logger.info(f"Schedule aggregator initialized with {len(providers)} providers")


@app.route('/')
def index():
    """
    Root endpoint - serves the calendar UI.
    
    Returns:
        HTML calendar interface
    """
    return render_template('index.html')


@app.route('/api/info', methods=['GET'])
def api_info():
    """
    API information endpoint.
    
    Returns:
        JSON response with API information
    """
    return jsonify({
        'name': 'Calendar Aggregator API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'schedules': '/api/schedules?view={daily|weekly|monthly}'
        },
        'providers': config_manager.get_configured_providers() if config_manager else []
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'providers': config_manager.get_configured_providers() if config_manager else []
    }), 200


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """
    Check authentication status for all providers.
    
    Returns:
        JSON response with authentication status
    """
    import os
    
    status = {
        'gmail': {
            'configured': False,
            'authenticated': False,
            'has_credentials': False,
            'token_file_exists': False,
            'debug_info': ''
        },
        'outlook': {
            'configured': False,
            'authenticated': False,
            'has_credentials': False,
            'token_file_exists': False,
            'debug_info': ''
        }
    }
    
    # Check Gmail
    gmail_config = config_manager.get_provider_config('gmail') if config_manager else None
    if gmail_config:
        status['gmail']['configured'] = True
        status['gmail']['has_credentials'] = True
        status['gmail']['token_file_exists'] = os.path.exists(gmail_config.token_file)
        status['gmail']['debug_info'] = f"Token file: {gmail_config.token_file}"
        gmail_provider = GmailProvider(gmail_config)
        status['gmail']['authenticated'] = gmail_provider.is_available()
    else:
        status['gmail']['debug_info'] = "No config found - credentials may not be loaded"
    
    # Check Outlook
    outlook_config = config_manager.get_provider_config('outlook') if config_manager else None
    if outlook_config:
        status['outlook']['configured'] = True
        status['outlook']['has_credentials'] = True
        status['outlook']['token_file_exists'] = os.path.exists(outlook_config.token_file)
        status['outlook']['debug_info'] = f"Token file: {outlook_config.token_file}"
        outlook_provider = OutlookProvider(outlook_config)
        status['outlook']['authenticated'] = outlook_provider.is_available()
    else:
        status['outlook']['debug_info'] = "No config found - credentials may not be loaded"
    
    return jsonify(status), 200


@app.route('/api/credentials/save', methods=['POST'])
def save_credentials():
    """
    Save OAuth credentials to app_secrets.py file.
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        # Read current app_secrets.py
        secrets_file = 'app_secrets.py'
        
        # Build new content
        content = '''"""
Application Secrets - DO NOT COMMIT TO VERSION CONTROL
Add your OAuth credentials here.
"""

# Google Calendar Credentials
GOOGLE_CLIENT_ID = "{google_client_id}"
GOOGLE_CLIENT_SECRET = "{google_client_secret}"
GOOGLE_REDIRECT_URI = "http://localhost:8080/oauth/google/callback"

# Microsoft Outlook Credentials
MICROSOFT_CLIENT_ID = "{outlook_client_id}"
MICROSOFT_CLIENT_SECRET = "{outlook_client_secret}"
MICROSOFT_REDIRECT_URI = "http://localhost:8080/oauth/microsoft/callback"

# Application Settings
PORT = 8080
FLASK_ENV = "development"
'''.format(
            google_client_id=data.get('google_client_id', 'your_google_client_id_here'),
            google_client_secret=data.get('google_client_secret', 'your_google_client_secret_here'),
            outlook_client_id=data.get('outlook_client_id', 'your_microsoft_client_id_here'),
            outlook_client_secret=data.get('outlook_client_secret', 'your_microsoft_client_secret_here')
        )
        
        # Write to file
        with open(secrets_file, 'w') as f:
            f.write(content)
        
        # Force Python to reload the module
        import sys
        if 'app_secrets' in sys.modules:
            del sys.modules['app_secrets']
        
        # Reinitialize the app with new credentials
        initialize_app()
        
        return jsonify({
            'success': True,
            'message': 'Credentials saved successfully. You can now connect your calendars.'
        }), 200
        
    except Exception as e:
        logger.error(f"Error saving credentials: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/credentials/get', methods=['GET'])
def get_credentials():
    """
    Get current credentials (masked for security).
    
    Returns:
        JSON response with masked credentials
    """
    try:
        gmail_config = config_manager.get_provider_config('gmail') if config_manager else None
        outlook_config = config_manager.get_provider_config('outlook') if config_manager else None
        
        def mask_secret(secret):
            """Mask secret except first and last 4 characters."""
            if not secret or secret.startswith('your_'):
                return ''
            if len(secret) <= 8:
                return '*' * len(secret)
            return secret[:4] + '*' * (len(secret) - 8) + secret[-4:]
        
        return jsonify({
            'google': {
                'client_id': gmail_config.client_id if gmail_config else '',
                'client_secret_masked': mask_secret(gmail_config.client_secret) if gmail_config else ''
            },
            'outlook': {
                'client_id': outlook_config.client_id if outlook_config else '',
                'client_secret_masked': mask_secret(outlook_config.client_secret) if outlook_config else ''
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting credentials: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/debug/credentials', methods=['GET'])
def debug_credentials():
    """
    Debug endpoint to check credential format.
    
    Returns:
        JSON with credential validation info
    """
    try:
        gmail_config = config_manager.get_provider_config('gmail') if config_manager else None
        
        if not gmail_config:
            return jsonify({
                'error': 'No Gmail config found',
                'help': 'Make sure credentials are saved and app is restarted'
            }), 400
        
        client_id = gmail_config.client_id
        client_secret = gmail_config.client_secret
        
        return jsonify({
            'client_id': {
                'length': len(client_id),
                'starts_with': client_id[:20] if len(client_id) > 20 else client_id,
                'ends_with': client_id[-30:] if len(client_id) > 30 else client_id,
                'has_whitespace': client_id != client_id.strip(),
                'format_ok': client_id.endswith('.apps.googleusercontent.com')
            },
            'client_secret': {
                'length': len(client_secret),
                'starts_with': client_secret[:10],
                'has_whitespace': client_secret != client_secret.strip(),
                'format_ok': client_secret.startswith('GOCSPX-')
            },
            'redirect_uri': gmail_config.redirect_uri,
            'help': 'Check that format_ok is true for both credentials'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/auth/google/login', methods=['GET'])
def google_login():
    """
    Initiate Google OAuth flow.
    
    Returns:
        Redirect to Google authorization URL
    """
    try:
        logger.info("Google login requested")
        gmail_config = config_manager.get_provider_config('gmail')
        if not gmail_config:
            logger.error("Gmail config not found")
            return jsonify({
                'success': False,
                'error': 'Google Calendar not configured. Please restart the app after saving credentials.'
            }), 400
        
        logger.info(f"Gmail config found: {gmail_config.client_id[:20]}...")
        gmail_provider = GmailProvider(gmail_config)
        auth_url = gmail_provider.initiate_oauth_flow()
        logger.info(f"Auth URL generated: {auth_url[:50]}...")
        
        return jsonify({
            'success': True,
            'auth_url': auth_url
        }), 200
        
    except Exception as e:
        logger.error(f"Error initiating Google OAuth: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}. Check console for details.'
        }), 500


@app.route('/oauth/google/callback', methods=['GET'])
def google_callback():
    """
    Handle Google OAuth callback.
    
    Returns:
        Redirect to main page with success/error message
    """
    try:
        # Get authorization code from query parameters
        code = request.args.get('code')
        if not code:
            return render_template('oauth_result.html', 
                                 provider='Google',
                                 success=False,
                                 message='No authorization code received')
        
        # Get Gmail provider
        gmail_config = config_manager.get_provider_config('gmail')
        if not gmail_config:
            return render_template('oauth_result.html',
                                 provider='Google',
                                 success=False,
                                 message='Google Calendar not configured')
        
        gmail_provider = GmailProvider(gmail_config)
        
        # Handle OAuth callback
        success = gmail_provider.handle_oauth_callback(code)
        
        if success:
            # Reinitialize app to pick up new credentials
            initialize_app()
            return render_template('oauth_result.html',
                                 provider='Google',
                                 success=True,
                                 message='Successfully connected to Google Calendar!')
        else:
            return render_template('oauth_result.html',
                                 provider='Google',
                                 success=False,
                                 message='Failed to authenticate with Google')
            
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {str(e)}")
        return render_template('oauth_result.html',
                             provider='Google',
                             success=False,
                             message=f'Error: {str(e)}')


@app.route('/api/auth/outlook/login', methods=['GET'])
def outlook_login():
    """
    Initiate Outlook OAuth flow.
    
    Returns:
        Redirect to Microsoft authorization URL
    """
    try:
        outlook_config = config_manager.get_provider_config('outlook')
        if not outlook_config:
            return jsonify({
                'success': False,
                'error': 'Outlook Calendar not configured. Please add credentials to app_secrets.py'
            }), 400
        
        outlook_provider = OutlookProvider(outlook_config)
        auth_url = outlook_provider.initiate_oauth_flow()
        
        return jsonify({
            'success': True,
            'auth_url': auth_url
        }), 200
        
    except Exception as e:
        logger.error(f"Error initiating Outlook OAuth: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/oauth/microsoft/callback', methods=['GET'])
def outlook_callback():
    """
    Handle Outlook OAuth callback.
    
    Returns:
        Redirect to main page with success/error message
    """
    try:
        # Get authorization code from query parameters
        code = request.args.get('code')
        if not code:
            return render_template('oauth_result.html',
                                 provider='Outlook',
                                 success=False,
                                 message='No authorization code received')
        
        # Get Outlook provider
        outlook_config = config_manager.get_provider_config('outlook')
        if not outlook_config:
            return render_template('oauth_result.html',
                                 provider='Outlook',
                                 success=False,
                                 message='Outlook Calendar not configured')
        
        outlook_provider = OutlookProvider(outlook_config)
        
        # Handle OAuth callback
        success = outlook_provider.handle_oauth_callback(code)
        
        if success:
            # Reinitialize app to pick up new credentials
            initialize_app()
            return render_template('oauth_result.html',
                                 provider='Outlook',
                                 success=True,
                                 message='Successfully connected to Outlook Calendar!')
        else:
            return render_template('oauth_result.html',
                                 provider='Outlook',
                                 success=False,
                                 message='Failed to authenticate with Outlook')
            
    except Exception as e:
        logger.error(f"Error in Outlook OAuth callback: {str(e)}")
        return render_template('oauth_result.html',
                             provider='Outlook',
                             success=False,
                             message=f'Error: {str(e)}')


@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """
    Get calendar schedules for specified view type.
    
    Query Parameters:
        view: View type (daily, weekly, or monthly)
    
    Returns:
        JSON response with schedules or error
    """
    try:
        # Get view parameter
        view_param = request.args.get('view', '').lower()
        
        if not view_param:
            return jsonify({
                'success': False,
                'data': None,
                'errors': ['Missing required parameter: view'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        # Validate view type
        try:
            view_type = ViewType.from_string(view_param)
        except ValueError as e:
            return jsonify({
                'success': False,
                'data': None,
                'errors': [str(e)],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        # Get schedules from aggregator
        schedules, errors = schedule_aggregator.get_schedules(view_type)
        
        # Create response
        if errors and not schedules:
            # All providers failed
            response = APIResponse.error_response(errors)
            return jsonify(response.to_dict()), 500
        elif errors:
            # Partial success
            response = APIResponse.error_response(errors, partial_data=schedules)
            return jsonify(response.to_dict()), 200
        else:
            # Full success
            response = APIResponse.success_response(schedules)
            return jsonify(response.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Error getting schedules: {str(e)}")
        return jsonify({
            'success': False,
            'data': None,
            'errors': [f"Internal server error: {str(e)}"],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'data': None,
        'errors': ['Endpoint not found. Try /api/health or /api/schedules?view=daily'],
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'data': None,
        'errors': ['Internal server error'],
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 500


if __name__ == '__main__':
    # Initialize application
    initialize_app()
    
    # Get port from configuration
    port = config_manager.get_port() if config_manager else 8080
    debug = config_manager.is_debug_mode() if config_manager else True
    
    # Run Flask app
    logger.info(f"Starting Calendar Aggregator on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
