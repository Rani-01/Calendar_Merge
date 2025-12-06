# 🔧 Troubleshooting Guide

## Calendar Not Syncing After Adding Credentials?

Follow these steps in order:

### ✅ Step 1: Verify Credentials Are Saved

Check `app_secrets.py` file - it should have your actual credentials (not placeholder text):

```python
GOOGLE_CLIENT_ID = "920085866710-xxx.apps.googleusercontent.com"  # ✓ Real ID
GOOGLE_CLIENT_SECRET = "GOCSPX-xxxxx"  # ✓ Real secret
```

NOT:
```python
GOOGLE_CLIENT_ID = "your_google_client_id_here"  # ✗ Placeholder
```

### ✅ Step 2: Restart the App

**IMPORTANT:** After saving credentials, you MUST restart the app!

1. Stop the app (Ctrl+C in terminal)
2. Start again: `python app.py`
3. Refresh browser page

### ✅ Step 3: Check Status in Settings

1. Open http://localhost:8080/
2. Click ⚙️ Settings button
3. Look at Step 2 status:

**Should say:**
- ✓ "Ready to connect" (credentials loaded)

**Should NOT say:**
- ✗ "Add Credentials First" (means app didn't reload)
- ✗ "No credentials" (means credentials not saved)

If it still says "Add Credentials First":
- Restart the app again
- Hard refresh browser (Ctrl+Shift+R)

### ✅ Step 4: Click Connect Button

1. In Settings, Step 2, click **"Connect Google"**
2. A popup window should open
3. Sign in with your Google account
4. Grant calendar permissions
5. Popup closes automatically

**Popup blocked?**
- Allow popups for localhost:8080
- Try again

### ✅ Step 5: Verify Connection

After connecting:
- Status should change to **"Connected ✓"**
- Provider badge should appear in header
- Close settings
- Calendar should show events

### ✅ Step 6: Check for Events

If connected but no events showing:
- Make sure you have events in your Google Calendar
- Click "Refresh" button on calendar
- Try different view (Monthly/Weekly/Daily)
- Check browser console (F12) for errors

---

## Common Issues & Solutions

### Issue: "Add Credentials First" button disabled

**Cause:** App hasn't loaded new credentials

**Solution:**
1. Restart the app completely
2. Refresh browser (Ctrl+Shift+R)
3. Check Settings again

### Issue: Popup opens but shows error

**Cause:** OAuth configuration mismatch

**Solution:**
1. Go to Google Cloud Console
2. Check redirect URI is exactly: `http://localhost:8080/oauth/google/callback`
3. Make sure Google Calendar API is enabled
4. Try connecting again

### Issue: Connected but no events

**Cause:** No events in calendar or date range issue

**Solution:**
1. Check you have events in Google Calendar
2. Try different date views (Monthly/Weekly/Daily)
3. Click Refresh button
4. Check browser console (F12) for API errors

### Issue: "Failed to authenticate"

**Cause:** Invalid credentials or API not enabled

**Solution:**
1. Verify credentials are correct in Google Console
2. Enable Google Calendar API in Google Cloud
3. Check redirect URI matches exactly
4. Try generating new credentials

### Issue: Credentials won't save

**Cause:** File permission or validation error

**Solution:**
1. Check app has write permission to `app_secrets.py`
2. Make sure you entered both Client ID AND Secret
3. Look for error message in UI
4. Check terminal for error logs

---

## Debug Checklist

Run through this checklist:

- [ ] Credentials saved in `app_secrets.py` (not placeholders)
- [ ] App restarted after saving credentials
- [ ] Browser page refreshed
- [ ] Settings shows "Ready to connect" (not "Add Credentials First")
- [ ] Clicked "Connect Google" button
- [ ] Popup opened (not blocked)
- [ ] Signed in and granted permissions
- [ ] Popup closed automatically
- [ ] Status shows "Connected ✓"
- [ ] Provider badge appears in header
- [ ] Events appear on calendar

---

## Still Not Working?

### Check Browser Console

1. Press F12 to open developer tools
2. Go to Console tab
3. Look for red error messages
4. Share the error message for help

### Check App Logs

Look at the terminal where app is running:
- Should see: "Gmail provider initialized"
- Should see: "Starting Calendar Aggregator on port 8080"
- Look for any ERROR messages

### Test API Directly

Open these URLs in browser:

1. **Check API info:**
   http://localhost:8080/api/info
   - Should show `"providers": ["gmail"]` if configured

2. **Check auth status:**
   http://localhost:8080/api/auth/status
   - Should show `"has_credentials": true`
   - Should show `"authenticated": true` after connecting

3. **Try to get schedules:**
   http://localhost:8080/api/schedules?view=daily
   - Should return events if connected
   - Should show error if not authenticated

---

## Need More Help?

If you've tried everything above and it's still not working:

1. Check the terminal logs for errors
2. Check browser console (F12) for errors
3. Verify your Google Cloud project setup
4. Make sure Calendar API is enabled
5. Try creating new OAuth credentials

The most common issue is **forgetting to restart the app** after saving credentials!
