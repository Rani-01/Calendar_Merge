# 📅 Calendar UI Guide

## 🎉 Your Calendar Interface is Ready!

You now have a beautiful visual calendar interface instead of just JSON!

## 🚀 How to Use

### 1. **Start the App**
```bash
python app.py
```

### 2. **Open Your Browser**
Visit: **http://localhost:8080/**

You'll see a beautiful calendar interface with:
- 📅 **Monthly View** - Full month calendar grid
- 📆 **Weekly View** - Next 7 days
- 📋 **Daily View** - Today's schedule

### 3. **Features**

#### **Empty Calendar (No API Configured)**
- Shows an empty calendar with all dates
- Message: "No events scheduled"
- You can still navigate between views

#### **With API Configured**
- Events appear on calendar dates
- Color-coded by provider:
  - 🔴 **Red** = Gmail events
  - 🔵 **Blue** = Outlook events
- Click any event to see full details

#### **Event Details**
Click on any event to see:
- Title
- Provider (Gmail/Outlook)
- Start & End time
- Description
- Location
- Attendees

### 4. **View Options**

**Monthly View:**
- Full calendar grid
- See all events for the month
- Today's date is highlighted

**Weekly View:**
- Next 7 days in a row
- Perfect for planning your week

**Daily View:**
- Today's schedule only
- Events sorted by time
- Detailed view with locations

### 5. **Refresh**
Click the "Refresh" button to reload schedules from your calendars

## 🎨 What You'll See

### Before Adding API Credentials:
```
┌─────────────────────────────────┐
│  📅 Calendar Aggregator         │
│  No providers configured        │
└─────────────────────────────────┘
│  Monthly | Weekly | Daily       │
└─────────────────────────────────┘
│  Empty Calendar Grid            │
│  "No events scheduled"          │
└─────────────────────────────────┘
```

### After Adding API Credentials:
```
┌─────────────────────────────────┐
│  📅 Calendar Aggregator         │
│  Gmail | Outlook                │
└─────────────────────────────────┘
│  Monthly | Weekly | Daily       │
└─────────────────────────────────┘
│  Calendar with Events           │
│  🔴 Team Meeting - 10:00 AM     │
│  🔵 Project Review - 2:00 PM    │
└─────────────────────────────────┘
```

## 🔧 Troubleshooting

**Calendar shows but no events?**
- Make sure you've added credentials to `app_secrets.py`
- Restart the app after adding credentials
- Check that providers show in the header

**Events not loading?**
- Click the "Refresh" button
- Check browser console for errors (F12)
- Verify API is working: http://localhost:8080/api/schedules?view=daily

## 🎯 Next Steps

1. Add your OAuth credentials to `app_secrets.py`
2. Restart the app
3. Authenticate with Google/Outlook (first time only)
4. Enjoy your unified calendar view!

## 💡 Tips

- The calendar automatically shows today's date highlighted
- Events are color-coded by provider for easy identification
- Click any event for full details
- Use view buttons to switch between daily/weekly/monthly
- Refresh button reloads latest events from your calendars

Enjoy your beautiful calendar interface! 🎉
