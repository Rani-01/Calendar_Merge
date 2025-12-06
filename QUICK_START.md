# 🚀 Quick Start Guide

## Get Your Calendar Running in 5 Minutes!

### 1️⃣ Start the App
```bash
python app.py
```

### 2️⃣ Open in Browser
Go to: **http://localhost:8080/**

You'll see an empty calendar - that's normal!

### 3️⃣ Click Settings Button
Click the **⚙️ Settings** button in the top right corner

### 4️⃣ Add Your Credentials

**Step 1: Add OAuth Credentials**

Enter your OAuth app credentials:

**For Google Calendar:**
- Client ID: `123456789.apps.googleusercontent.com`
- Client Secret: `GOCSPX-abc123xyz...`

**For Outlook Calendar:**
- Client ID: `12345678-1234-1234-1234-123456789abc`
- Client Secret: `abc~123...`

Click **💾 Save Credentials**

Wait for: ✓ Credentials saved!

### 5️⃣ Connect Your Calendars

**Step 2: Connect Your Calendars**

Click **Connect Google** or **Connect Outlook**:
- Popup opens
- Sign in with your account
- Grant calendar permissions
- Popup closes automatically

Status changes to: **Connected ✓**

### 6️⃣ View Your Events!

Close settings and see your calendar populated with events!

---

## 📝 Where to Get Credentials?

### Google Calendar:
1. Visit: https://console.cloud.google.com/
2. Create project → Enable Calendar API
3. Create OAuth credentials
4. Add redirect: `http://localhost:8080/oauth/google/callback`
5. Copy Client ID & Secret

### Outlook Calendar:
1. Visit: https://portal.azure.com/
2. Register app → Add Calendar.Read permission
3. Add redirect: `http://localhost:8080/oauth/microsoft/callback`
4. Copy Application ID & Secret

See `SETUP_CREDENTIALS.md` for detailed instructions.

---

## ✨ That's It!

Your calendar is now connected and will automatically:
- ✅ Show events from all connected calendars
- ✅ Refresh tokens when they expire
- ✅ Color-code events by provider (Red=Gmail, Blue=Outlook)
- ✅ Display in Monthly, Weekly, or Daily views

**No file editing. No manual token management. Just works!** 🎉
