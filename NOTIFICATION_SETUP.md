# 📧 Email & SMS Notification Setup Guide

## Overview

The Reptile Tracker now supports automatic email and SMS notifications for feeding reminders! Get notified when your reptiles are due for feeding.

## Features

- ✅ Email notifications via SMTP (Gmail, Outlook, etc.)
- ✅ SMS notifications via Twilio
- ✅ Customizable reminder times
- ✅ Advance notice (get notified days before feeding is due)
- ✅ Overdue-only mode
- ✅ Test notifications to verify setup

## Quick Start

### 1. Install Dependencies

The required packages are already in `requirements.txt`:
- `twilio>=8.0.0` - For SMS notifications
- `APScheduler>=3.10.0` - For scheduled reminders

### 2. Email Setup (Gmail Example)

#### Step 1: Create Gmail App Password

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Scroll down to "App passwords"
4. Generate a new app password for "Mail"
5. Save the 16-character password

#### Step 2: Configure Environment Variables in Render

Go to your Render service → Environment tab and add:

```
SMTP_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=your-email@gmail.com
```

### 3. SMS Setup (Twilio)

#### Step 1: Sign Up for Twilio

1. Go to [Twilio](https://www.twilio.com/try-twilio)
2. Sign up for a free trial account
3. Get $15 free credit (enough for ~500 SMS)
4. Get your Account SID, Auth Token, and Phone Number

#### Step 2: Configure Environment Variables in Render

Add these to your Render service:

```
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### 4. Configure Notification Settings

1. Deploy your updated app to Render
2. Go to your app → Notification Settings (add link to navigation)
3. Enter your email and/or phone number
4. Set your preferred reminder time
5. Test the notifications
6. Save settings

## Configuration Options

### Email Settings

- **Email Enabled**: Turn email notifications on/off
- **Email Address**: Where to send notifications
- **Reminder Time**: Daily time to check for overdue feedings (e.g., 09:00)

### SMS Settings

- **SMS Enabled**: Turn SMS notifications on/off
- **Phone Number**: Include country code (e.g., +1 for US, +61 for Australia)

### Notification Preferences

- **Advance Notice**: Get notified X days before feeding is due (0-7 days)
- **Notify Overdue Only**: Only send notifications for overdue feedings

## Supported Email Providers

### Gmail
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Outlook/Hotmail
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

### Yahoo
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

### Custom SMTP
Use your email provider's SMTP settings

## Costs

### Email (SMTP)
- **Free** with Gmail, Outlook, Yahoo, etc.
- No additional costs

### SMS (Twilio)
- **Free Trial**: $15 credit (~500 SMS)
- **After Trial**: ~$0.0075 per SMS in US
- **Monthly**: ~$1/month for phone number
- **Example**: 30 reminders/month = ~$1.23/month

## Troubleshooting

### Email Not Sending

1. **Check SMTP credentials**: Verify username/password in Render environment
2. **App Password**: Gmail requires app password, not regular password
3. **2FA**: Enable 2-factor authentication for app passwords
4. **Firewall**: Ensure Render can access SMTP server (port 587)
5. **Test**: Use "Send Test Email" button in settings

### SMS Not Sending

1. **Twilio Account**: Verify account is active and has credit
2. **Phone Number**: Must include country code (+1, +61, etc.)
3. **Verified Numbers**: Free trial only sends to verified numbers
4. **Credit**: Check Twilio dashboard for remaining credit
5. **Test**: Use "Send Test SMS" button in settings

### Notifications Not Automatic

**Note**: The current implementation requires manual trigger. To make it fully automatic, you need to:

1. Set up a scheduled job (cron) on Render
2. Or use Render's cron jobs feature
3. Or implement APScheduler in the app (advanced)

## Manual Notification Trigger

Until automatic scheduling is set up, you can manually trigger notifications by:

1. Going to Feeding Reminders page
2. Clicking "Send Notifications Now" button (to be added)
3. Or setting up a cron job to call the notification endpoint

## Future Enhancements

- [ ] Automatic daily notifications via APScheduler
- [ ] Webhook support for instant notifications
- [ ] Push notifications (web push)
- [ ] Notification history/logs
- [ ] Per-reptile notification preferences
- [ ] Batch digest emails (daily summary)

## Security Notes

- Never commit SMTP passwords or Twilio tokens to Git
- Always use environment variables
- Use app passwords, not main account passwords
- Rotate credentials periodically
- Monitor Twilio usage to avoid unexpected charges

## Support

For issues or questions:
1. Check Render logs for error messages
2. Verify environment variables are set correctly
3. Test with "Send Test" buttons first
4. Check email spam folder
5. Verify Twilio account status

---

**Last Updated**: 2025-12-10
**Version**: 1.0.0