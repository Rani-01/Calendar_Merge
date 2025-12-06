# Design Document

## Overview

The Calendar Aggregator is a Python Flask REST API application that consolidates calendar events from multiple email providers (Gmail, Outlook, etc.) into a unified view. The system operates statelessly without a database, fetching calendar data in real-time from provider APIs and presenting it in daily, weekly, or monthly formats. The application runs on port 8080 within a Python virtual environment and uses OAuth 2.0 for secure authentication with email providers.

## Architecture

The application follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│         REST API Layer              │
│    (Flask Routes & Controllers)     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Business Logic Layer           │
│  (Schedule Aggregation & Filtering) │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│    Calendar Provider Layer          │
│  (Gmail API, Outlook API Adapters)  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      External Calendar APIs         │
│    (Google Calendar, MS Graph)      │
└─────────────────────────────────────┘
```

**Key Architectural Decisions:**

1. **Adapter Pattern**: Each email provider has a dedicated adapter implementing a common interface, allowing easy addition of new providers
2. **Stateless Design**: No database or persistent storage; all data fetched on-demand from provider APIs
3. **Configuration-Based**: Provider credentials and settings managed through environment variables and configuration files
4. **Synchronous Processing**: Real-time API calls to providers for each request (future enhancement could add caching)

## Components and Interfaces

### 1. API Controller (`app.py`)

**Responsibilities:**
- Initialize Flask application
- Define REST endpoints
- Handle HTTP request/response lifecycle
- Validate input parameters
- Coordinate with business logic layer

**Endpoints:**
- `GET /api/schedules?view={daily|weekly|monthly}` - Retrieve schedules for specified view
- `GET /api/health` - Health check endpoint

### 2. Schedule Aggregator (`services/schedule_aggregator.py`)

**Responsibilities:**
- Coordinate retrieval from multiple calendar providers
- Merge schedules from different sources
- Filter schedules based on time period (daily/weekly/monthly)
- Handle provider failures gracefully

**Interface:**
```python
class ScheduleAggregator:
    def get_schedules(self, view_type: ViewType) -> List[Schedule]
    def _filter_by_date_range(self, schedules: List[Schedule], start: datetime, end: datetime) -> List[Schedule]
```

### 3. Calendar Provider Interface (`providers/base_provider.py`)

**Responsibilities:**
- Define common interface for all calendar providers
- Abstract provider-specific implementation details

**Interface:**
```python
class CalendarProvider(ABC):
    @abstractmethod
    def authenticate(self) -> bool
    
    @abstractmethod
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Schedule]
    
    @abstractmethod
    def is_available(self) -> bool
```

### 4. Gmail Provider (`providers/gmail_provider.py`)

**Responsibilities:**
- Implement Google Calendar API integration
- Handle OAuth 2.0 authentication with Google
- Transform Google Calendar events to internal Schedule format

### 5. Outlook Provider (`providers/outlook_provider.py`)

**Responsibilities:**
- Implement Microsoft Graph API integration
- Handle OAuth 2.0 authentication with Microsoft
- Transform Outlook events to internal Schedule format

### 6. Configuration Manager (`config/config_manager.py`)

**Responsibilities:**
- Load provider credentials from environment variables
- Manage application configuration
- Validate configuration completeness

## Data Models

### Schedule

```python
@dataclass
class Schedule:
    id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    provider: str  # 'gmail', 'outlook', etc.
    location: Optional[str]
    attendees: List[str]
```

### ViewType

```python
class ViewType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
```

### ProviderConfig

```python
@dataclass
class ProviderConfig:
    provider_name: str
    client_id: str
    client_secret: str
    redirect_uri: str
    token_file: str  # Path to store OAuth tokens
```

### APIResponse

```python
@dataclass
class APIResponse:
    success: bool
    data: Optional[List[Schedule]]
    errors: List[str]
    timestamp: datetime
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Multi-provider retrieval completeness
*For any* set of configured calendar providers, when the system receives a schedule request, it should attempt to retrieve events from every configured provider.
**Validates: Requirements 1.1**

### Property 2: Schedule consolidation preserves all events
*For any* set of schedules returned by multiple providers, the consolidated response should contain all schedules from all providers without loss.
**Validates: Requirements 1.2**

### Property 3: Partial failure resilience
*For any* subset of providers that fail, the system should successfully return schedules from available providers and include error information for failed providers.
**Validates: Requirements 1.3**

### Property 4: Event data preservation invariant
*For any* schedule retrieved from a provider, all event fields (time, date, title, description, location, attendees) should be preserved unchanged in the aggregated response.
**Validates: Requirements 1.4**

### Property 5: Duplicate event inclusion
*For any* event that appears in multiple providers, all instances should be included in the response (no automatic deduplication).
**Validates: Requirements 1.5**

### Property 6: Time-based filtering correctness
*For any* set of schedules and any view type (daily/weekly/monthly), only schedules whose time ranges overlap with the requested period should be included in the filtered results.
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 7: Valid request success response
*For any* valid API request with proper parameters, the system should return HTTP status 200 with a JSON response containing the requested schedule data.
**Validates: Requirements 3.2, 3.4**

### Property 8: Invalid parameter error handling
*For any* invalid request parameter (including invalid view types), the system should return HTTP status 400 with a JSON error message describing the validation failure.
**Validates: Requirements 3.3, 7.2, 7.3**

### Property 9: Stateless operation
*For any* sequence of schedule requests, the system should fetch data directly from provider APIs without reading from or writing to any persistent storage.
**Validates: Requirements 5.1, 5.2**

### Property 10: Configuration-based credential management
*For any* provider configuration, credentials should be loaded exclusively from environment variables or configuration files, never hardcoded.
**Validates: Requirements 5.4**

### Property 11: OAuth authentication enforcement
*For any* provider API connection, the system should use OAuth 2.0 authentication flows and include valid access tokens in API requests.
**Validates: Requirements 6.1**

### Property 12: Authentication failure reporting
*For any* provider that fails authentication, the error response should explicitly identify which provider failed and include authentication error details.
**Validates: Requirements 6.3**

### Property 13: Token refresh handling
*For any* expired authentication token, the system should attempt to refresh the token using the refresh token before failing the request.
**Validates: Requirements 6.4**

### Property 14: Response format consistency
*For any* successful API response, the JSON structure should conform to the defined APIResponse schema with consistent field names and types.
**Validates: Requirements 7.4**



## Error Handling

### Error Categories

1. **Provider Errors**
   - Authentication failures (invalid credentials, expired tokens)
   - API rate limiting
   - Network timeouts
   - Provider service unavailability

2. **Validation Errors**
   - Invalid view type parameter
   - Malformed request data
   - Missing required configuration

3. **System Errors**
   - Configuration loading failures
   - Unexpected exceptions during processing

### Error Handling Strategy

**Graceful Degradation:**
- When one provider fails, continue processing other providers
- Include partial results with error information
- Never fail entire request due to single provider failure

**Error Response Format:**
```python
{
    "success": false,
    "data": [],  # or partial data if some providers succeeded
    "errors": [
        "Gmail provider: Authentication failed - token expired",
        "Outlook provider: Network timeout after 30s"
    ],
    "timestamp": "2025-12-06T10:30:00Z"
}
```

**Logging:**
- Log all provider errors with full context
- Log authentication attempts and failures
- Log API request/response times for monitoring

**Retry Logic:**
- Implement exponential backoff for transient network errors
- Retry token refresh once on authentication failure
- Do not retry on validation errors (fail fast)

## Testing Strategy

### Unit Testing

The application will use **pytest** as the testing framework for unit tests.

**Unit Test Coverage:**
- Individual provider adapters (Gmail, Outlook) with mocked API responses
- Schedule aggregator logic with mock providers
- Date filtering functions with specific date ranges
- Configuration loading with various environment variable scenarios
- API endpoint validation with specific valid/invalid inputs
- Error handling for specific error conditions

**Example Unit Tests:**
- Test that GmailProvider correctly transforms Google Calendar API response to Schedule objects
- Test that empty schedule list returns success response
- Test that application binds to port 8080 on startup
- Test that requirements.txt file exists and contains Flask
- Test that application can restart without database initialization

### Property-Based Testing

The application will use **Hypothesis** as the property-based testing framework.

**Configuration:**
- Each property-based test will run a minimum of 100 iterations
- Tests will use Hypothesis strategies to generate random but valid test data

**Property Test Coverage:**
- Multi-provider retrieval with randomly generated provider configurations
- Schedule consolidation with random schedule sets from multiple providers
- Partial failure scenarios with random provider failure combinations
- Event data preservation with randomly generated schedule objects
- Time-based filtering with random date ranges and schedule sets
- API request/response validation with random valid parameters
- Invalid parameter handling with random invalid inputs
- Stateless operation verification across random request sequences
- OAuth flow validation with random token states

**Test Tagging:**
Each property-based test will include a comment tag in this format:
```python
# Feature: calendar-aggregator, Property 1: Multi-provider retrieval completeness
```

This links the test implementation directly to the correctness property in this design document.

### Integration Testing

While not part of the core implementation, integration tests would verify:
- End-to-end flows with real provider APIs (in test/sandbox mode)
- OAuth authentication flows with test accounts
- Multiple concurrent requests to the API

### Test Execution

Tests should be run:
- Before committing code changes
- As part of CI/CD pipeline (if implemented)
- After any dependency updates

## Implementation Notes

### Technology Stack

- **Python**: 3.9 or higher
- **Flask**: 2.3.x - Web framework
- **google-auth**: 2.x - Google OAuth authentication
- **google-api-python-client**: 2.x - Google Calendar API
- **msal**: 1.x - Microsoft Authentication Library for Outlook
- **requests**: 2.x - HTTP client for API calls
- **python-dotenv**: 1.x - Environment variable management
- **pytest**: 7.x - Unit testing framework
- **hypothesis**: 6.x - Property-based testing framework

### Configuration

**Environment Variables:**
```
# Google Calendar
GOOGLE_CLIENT_ID=<client_id>
GOOGLE_CLIENT_SECRET=<client_secret>
GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/google/callback

# Microsoft Outlook
MICROSOFT_CLIENT_ID=<client_id>
MICROSOFT_CLIENT_SECRET=<client_secret>
MICROSOFT_REDIRECT_URI=http://localhost:8080/oauth/microsoft/callback

# Application
FLASK_ENV=development
PORT=8080
```

**Token Storage:**
- OAuth tokens stored in local JSON files (e.g., `tokens/google_token.json`)
- Token files excluded from version control via `.gitignore`
- Token refresh handled automatically when expired

### OAuth Flow

1. User initiates OAuth by visiting `/oauth/{provider}/authorize`
2. Application redirects to provider's authorization URL
3. User grants permissions
4. Provider redirects back to application's callback URL with authorization code
5. Application exchanges code for access token and refresh token
6. Tokens stored in local file for subsequent requests

### API Request Flow

```
Client Request → Flask Route → ScheduleAggregator
                                      ↓
                    ┌─────────────────┴─────────────────┐
                    ↓                                   ↓
              GmailProvider                    OutlookProvider
                    ↓                                   ↓
              Google Calendar API              Microsoft Graph API
                    ↓                                   ↓
                    └─────────────────┬─────────────────┘
                                      ↓
                          Merge & Filter Schedules
                                      ↓
                              JSON Response → Client
```

### Future Enhancements

- Response caching to reduce API calls
- Webhook support for real-time calendar updates
- Additional provider support (Apple Calendar, Yahoo, etc.)
- Calendar event creation/modification capabilities
- Conflict detection across calendars
- Smart scheduling suggestions
