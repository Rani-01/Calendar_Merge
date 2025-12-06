# 🔧 Google OAuth Setup - Fix "invalid_client" Error

## Problem: Error 401: invalid_client

This error means Google can't validate your OAuth credentials. Here's the complete fix:

---

## ✅ Complete Setup Guide

### Step 1: Go to Google Cloud Console

1. Open: https://console.cloud.google.com/
2. Sign in with your Google account
3. Select your project (or create a new one)

### Step 2: Enable Google Calendar API

1. Click on "APIs & Services" in the left menu
2. Click "Library"
3. Search for "Google Calendar API"
4. Click on it
5. Click "ENABLE" button
6. Wait for it to enable

### Step 3: Configure OAuth Consent Screen

**IMPORTANT:** This must be done before creating credentials!

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose **"External"** (unless you have Google Workspace)
3. Click "CREATE"

**Fill in the form:**
- App name: `Calendar Aggregator`
- User support email: Your email
- Developer contact: Your email
- Click "SAVE AND CONTINUE"

**Scopes:**
- Click "ADD OR REMOVE SCOPES"
- Search for "Google Calendar API"
- Check: `.../auth/calendar.readonly`
- Click "UPDATE"
- Click "SAVE AND CONTINUE"

**Test users:**
- Click "ADD USERS"
- Add your Gmail address
- Click "ADD"
- Click "SAVE AND CONTINUE"

### Step 4: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" at the top
3. Select "OAuth client ID"

**Configure the OAuth client:**

**Application type:** Select **"Desktop app"** (NOT Web application)
- Why? Desktop app works better for localhost development

**Name:** `Calendar Aggregator Desktop`

Click "CREATE"

### Step 5: Get Your Credentials

After creating:
1. A popup shows your Client ID and Secret
2. **Copy the Client ID** (ends with `.apps.googleusercontent.com`)
3. **Copy the Client Secret** (starts with `GOCSPX-`)
4. Click "OK"

### Step 6: Download JSON (Optional but Recommended)

1. Find your OAuth client in the list
2. Click the download icon (⬇️) on the right
3. Save the JSON file
4. Open it to verify your credentials match

### Step 7: Update Your App

**Option A: Through UI (Recommended)**
1. Go to http://localhost:8080/
2. Click ⚙️ Settings
3. Paste the NEW Client ID
4. Paste the NEW Client Secret
5. Click "Save Credentials"

**Option B: Edit File Directly**
1. Open `app_secrets.py`
2. Replace `GOOGLE_CLIENT_ID` with your new ID
3. Replace `GOOGLE_CLIENT_SECRET` with your new secret
4. Save the file

### Step 8: Restart and Test

1. **Stop the app** (Ctrl+C)
2. **Start the app** again: `python app.py`
3. **Refresh browser** (Ctrl+Shift+R)
4. **Click Settings** → **Connect Google**
5. Should work now!

---

## 🎯 Key Points for Desktop App

When using **"Desktop app"** OAuth type:

✅ **Advantages:**
- No redirect URI configuration needed
- Works with localhost automatically
- Simpler setup

✅ **What to use:**
- Application type: **Desktop app**
- No redirect URIs needed (Google handles it)

---

## 🔄 Alternative: Web Application Setup

If you prefer "Web application" type:

1. **Application type:** Web application
2. **Authorized redirect URIs:** Add these:
   - `http://localhost:8080/oauth/google/callback`
   - `http://127.0.0.1:8080/oauth/google/callback`
3. Click "CREATE"

---

## 🐛 Still Getting Error?

### Check 1: Verify Credentials Format

Your credentials should look like:
```
Client ID: 123456789-abc123xyz.apps.googleusercontent.com
Secret: GOCSPX-abc123xyz789
```

NOT like:
```
Client ID: 123456789-abc123xyz (missing .apps.googleusercontent.com)
Secret: abc123xyz (missing GOCSPX- prefix)
```

### Check 2: Verify OAuth Consent Screen

1. Go to "OAuth consent screen"
2. Status should be "Testing" or "Published"
3. Your email should be in "Test users"

### Check 3: Wait for Propagation

After creating new credentials:
- Wait 5-10 minutes
- Google needs time to propagate changes
- Try again after waiting

### Check 4: Clear Browser Cache

1. Close all browser windows
2. Open new browser window
3. Go to http://localhost:8080/
4. Try connecting again

### Check 5: Check Project

Make sure:
- Calendar API is enabled in the SAME project
- OAuth credentials are in the SAME project
- You're signed in with the SAME Google account

---

## 📋 Checklist

Before trying to connect:

- [ ] Google Calendar API is enabled
- [ ] OAuth consent screen is configured
- [ ] Test user (your email) is added
- [ ] OAuth credentials created (Desktop app recommended)
- [ ] Client ID copied correctly (ends with .apps.googleusercontent.com)
- [ ] Client Secret copied correctly (starts with GOCSPX-)
- [ ] Credentials saved in app
- [ ] App restarted
- [ ] Browser refreshed
- [ ] Waited 5 minutes after creating credentials

---

## 🎯 Quick Fix: Start Fresh

If nothing works, start completely fresh:

1. **Delete old credentials:**
   - Go to Credentials page
   - Delete your old OAuth client

2. **Create new Desktop app:**
   - Create new OAuth client
   - Type: Desktop app
   - Name: Calendar Aggregator v2

3. **Copy new credentials**

4. **Update app with new credentials**

5. **Restart everything**

6. **Try again**

---

## 💡 Pro Tip

Use **Desktop app** type for local development - it's much simpler and doesn't require redirect URI configuration!

---

## Need More Help?

If you're still stuck:

1. Check the downloaded JSON file matches your credentials
2. Make sure you're using the same Google account
3. Verify the project has Calendar API enabled
4. Try creating a completely new project
5. Check Google Cloud Console for any error messages

The most common issues:
- ❌ Wrong OAuth client type (use Desktop app)
- ❌ Credentials from different project than API
- ❌ OAuth consent screen not configured
- ❌ Test user not added
- ❌ Typo in credentials (extra space, missing character)
