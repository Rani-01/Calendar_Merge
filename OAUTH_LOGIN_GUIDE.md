# 🔐 OAuth Login Guide

## New Feature: Complete UI-Based Setup!

You can now **add credentials AND connect your calendars** entirely from the UI - no file editing required!

## 🚀 How to Use

### Step 1: Get OAuth Credentials

First, create OAuth apps to get your credentials:

**Google Calendar:**
1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Add redirect URI: `http://localhost:8080/oauth/google/callback`
6. Copy Client ID and Client Secret

**Microsoft Outlook:**
1. Go to https://portal.azure.com/
2. Register a new app in Azure AD
3. Add redirect URI: `http://localhost:8080/oauth/microsoft/callback`
4. Add Calendar.Read permission
5. Copy Application (client) ID and Client Secret

See `SETUP_CREDENTIALS.md` for detailed instructions.

### Step 2: Start the App

```bash
python app.py
```

### Step 3: Open Settings & Add Credentials

1. Go to http://localhost:8080/
2. Click the **⚙️ Settings** button in the top right
3. In **Step 1**, enter your OAuth credentials:
   - Paste Google Client ID and Secret
   - Paste Outlook Client ID and Secret
4. Click **💾 Save Credentials**
5. Wait for success message

### Step 4: Connect Your Calendars

In **Step 2**, click the **"Connect Google"** or **"Connect Outlook"** button:

1. A popup window will open
2. Sign in with your account
3. Grant calendar permissions
4. The popup will close automatically
5. Your calendar events will appear!

## 📋 Features

### Complete UI-Based Setup:
- ✅ **Add credentials** directly in the UI (no file editing!)
- ✅ **Save credentials** with one click
- ✅ **Connection status** for each provider
- ✅ **"Connect" buttons** to initiate OAuth
- ✅ **"Connected ✓"** when authenticated
- ✅ **Visual feedback** at every step

### OAuth Flow:
- Opens in a popup window (no page redirect)
- Automatically closes on success
- Refreshes calendar to show events
- Stores tokens securely in `tokens/` folder

### Zero File Editing:
- No need to edit `app_secrets.py` manually
- No need to manually run OAuth flows
- No need to copy/paste tokens
- Everything happens in the UI!

## 🔧 Troubleshooting

**"Add Credentials First" button disabled?**
- Click ⚙️ Settings
- Scroll to Step 1
- Enter your OAuth credentials
- Click Save Credentials

**Credentials not saving?**
- Make sure you entered both Client ID and Secret
- Check that app has write permissions to `app_secrets.py`
- Look for error message in the UI

**Popup blocked?**
- Allow popups for localhost:8080
- Try clicking the connect button again

**Connection fails?**
- Verify your credentials are correct
- Check redirect URIs match exactly: `http://localhost:8080/oauth/google/callback`
- Check browser console for errors (F12)

**Already connected but want to reconnect?**
- Delete the token file in `tokens/` folder
- Click connect button again

**Want to change credentials?**
- Just enter new credentials in Settings
- Click Save Credentials
- Old credentials will be replaced

## 🎯 Benefits

### Before (Manual):
1. Edit `app_secrets.py` file
2. Restart app
3. Manually trigger OAuth flow
4. Copy tokens
5. Paste into token files

### Now (Fully Automated):
1. Open Settings in UI
2. Paste credentials
3. Click Save
4. Click Connect
5. Done! ✨

**Everything in the browser - zero file editing!**

## 💡 Tips

- You can connect one or both providers
- Each provider is independent
- Tokens are stored in `tokens/` folder
- Tokens auto-refresh when expired
- Settings panel shows real-time status

Enjoy your seamless calendar integration! 🎉
