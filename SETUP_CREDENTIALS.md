# 🔐 How to Add Your OAuth Credentials

## Quick Setup (Hardcoded Secrets)

Your credentials are stored in `app_secrets.py` file. This file is already added to `.gitignore` so it won't be committed to version control.

### Step 1: Edit app_secrets.py

Open the `app_secrets.py` file and replace the placeholder values with your actual credentials:

```python
# Google Calendar Credentials
GOOGLE_CLIENT_ID = "paste_your_google_client_id_here"
GOOGLE_CLIENT_SECRET = "paste_your_google_client_secret_here"

# Microsoft Outlook Credentials  
MICROSOFT_CLIENT_ID = "paste_your_microsoft_client_id_here"
MICROSOFT_CLIENT_SECRET = "paste_your_microsoft_client_secret_here"
```

### Step 2: Get Your Credentials

#### For Google Calendar:
1. Go to https://console.cloud.google.com/
2. Create a project
3. Enable "Google Calendar API"
4. Create OAuth 2.0 credentials
5. Add redirect URI: `http://localhost:8080/oauth/google/callback`
6. Copy Client ID and Client Secret to `secrets.py`

#### For Microsoft Outlook:
1. Go to https://portal.azure.com/
2. Register an app
3. Add redirect URI: `http://localhost:8080/oauth/microsoft/callback`
4. Add API permission: `Calendars.Read`
5. Create a client secret
6. Copy Application ID and Client Secret to `secrets.py`

### Step 3: Restart the App

```bash
# Stop the app (Ctrl+C)
# Start it again
python app.py
```

### Step 4: Verify

Visit http://localhost:8080/

You should see your configured providers:
```json
{
  "providers": ["gmail", "outlook"]
}
```

### Step 5: Get Your Schedules

```bash
# Daily schedules
curl http://localhost:8080/api/schedules?view=daily

# Weekly schedules
curl http://localhost:8080/api/schedules?view=weekly

# Monthly schedules
curl http://localhost:8080/api/schedules?view=monthly
```

## ⚠️ Security Note

The `app_secrets.py` file is in `.gitignore` to prevent accidental commits. However:
- Never share this file
- Never commit it to version control
- Keep it secure on your local machine

## 🔄 Alternative: Use .env file

If you prefer, you can still use the `.env` file instead of `app_secrets.py`. The app checks both locations (app_secrets.py takes priority if both exist).
