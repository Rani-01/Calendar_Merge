# Calendar Aggregator

A Python Flask REST API application that consolidates calendar events from multiple email providers (Gmail, Outlook) into a unified view.

## Requirements

- Python 3.9 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edit `.env` and add your OAuth credentials (see OAuth Setup section below).

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:8080`

## OAuth Setup

### Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Go to "Credentials" and create OAuth 2.0 Client ID
5. Add `http://localhost:8080/oauth/google/callback` as an authorized redirect URI
6. Copy the Client ID and Client Secret to your `.env` file

### Microsoft Outlook API

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Create a new registration
4. Add `http://localhost:8080/oauth/microsoft/callback` as a redirect URI
5. Go to "Certificates & secrets" and create a new client secret
6. Add required API permissions: `Calendars.Read`
7. Copy the Application (client) ID and Client Secret to your `.env` file

## API Documentation

### Endpoints

#### Get Schedules

```
GET /api/schedules?view={daily|weekly|monthly}
```

**Parameters:**
- `view` (required): Time period for schedules
  - `daily`: Current day only
  - `weekly`: Next 7 days starting from today
  - `monthly`: Current month

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "event123",
      "title": "Team Meeting",
      "description": "Weekly sync",
      "start_time": "2025-12-06T10:00:00Z",
      "end_time": "2025-12-06T11:00:00Z",
      "provider": "gmail",
      "location": "Conference Room A",
      "attendees": ["user1@example.com", "user2@example.com"]
    }
  ],
  "errors": [],
  "timestamp": "2025-12-06T09:00:00Z"
}
```

#### Health Check

```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-06T09:00:00Z"
}
```

### Example Requests

```bash
# Get today's schedules
curl http://localhost:8080/api/schedules?view=daily

# Get weekly schedules
curl http://localhost:8080/api/schedules?view=weekly

# Get monthly schedules
curl http://localhost:8080/api/schedules?view=monthly

# Health check
curl http://localhost:8080/api/health
```

## Project Structure

```
calendar-aggregator/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── models/               # Data models
├── providers/            # Calendar provider adapters
├── services/             # Business logic
├── config/               # Configuration management
└── tests/                # Test suite
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_schedule_aggregator.py
```

### Deactivate Virtual Environment

```bash
deactivate
```

## Architecture

The application follows a layered architecture:

- **REST API Layer**: Flask routes and controllers
- **Business Logic Layer**: Schedule aggregation and filtering
- **Provider Layer**: Gmail and Outlook API adapters
- **External APIs**: Google Calendar and Microsoft Graph

## Features

- ✅ Multi-provider calendar aggregation
- ✅ Daily, weekly, and monthly views
- ✅ OAuth 2.0 authentication
- ✅ Stateless operation (no database)
- ✅ Graceful error handling
- ✅ Token refresh automation

## License

MIT
