# OpenAI API Setup Guide

This guide explains how to set up the OpenAI API key for the AI food recognition feature.

## Step 1: Get an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section (https://platform.openai.com/api-keys)
4. Click **"Create new secret key"**
5. Give it a name like "Reptile Tracker"
6. Copy the API key (starts with `sk-...`)
7. **IMPORTANT:** Save it somewhere safe - you won't be able to see it again!

## Step 2: Add API Key to Render

### Method 1: Via Render Dashboard (Recommended)

1. Go to your Render dashboard: https://dashboard.render.com/
2. Click on your **reptile-tracker** web service
3. Click on **"Environment"** in the left sidebar
4. Click **"Add Environment Variable"**
5. Add the following:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** Your OpenAI API key (paste the `sk-...` key)
6. Click **"Save Changes"**
7. Render will automatically redeploy your app with the new environment variable

### Method 2: Via render.yaml (Alternative)

If you want to add it to your `render.yaml` file (not recommended for security):

```yaml
services:
  - type: web
    name: reptile-tracker
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn app:app"
    envVars:
      - key: OPENAI_API_KEY
        sync: false  # This means it won't be in git
```

Then add the actual value in the Render dashboard as described in Method 1.

## Step 3: Verify Setup

After adding the API key and redeployment:

1. Go to your reptile profile page
2. Click **"Log Feeding"**
3. Click **"Take Photo of Food"**
4. Take a photo of some reptile food
5. You should see "Analyzing food..." followed by AI results

## Cost Information

### OpenAI Pricing (as of 2024)

**GPT-4o-mini with Vision:**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- Images: ~$0.001-0.002 per image (low detail mode)

### Estimated Costs

- **Per food photo:** ~$0.001-0.003
- **100 photos/month:** ~$0.10-0.30
- **1000 photos/month:** ~$1.00-3.00

Very affordable for personal use!

## Troubleshooting

### "OpenAI API key not configured" Error

**Solution:** Make sure you've added the `OPENAI_API_KEY` environment variable in Render and redeployed.

### "Failed to analyze image" Error

**Possible causes:**
1. API key is invalid or expired
2. OpenAI API is down (check https://status.openai.com/)
3. Image is too large (max 16MB)
4. No credits remaining in OpenAI account

**Solutions:**
1. Verify API key is correct in Render environment variables
2. Check OpenAI account has available credits
3. Try with a smaller image

### Feature Not Working

1. Check Render logs for errors:
   - Go to Render dashboard
   - Click on your service
   - Click "Logs" tab
   - Look for errors related to OpenAI

2. Verify the environment variable is set:
   - In Render dashboard
   - Go to Environment tab
   - Confirm `OPENAI_API_KEY` is listed

## Security Best Practices

✅ **DO:**
- Store API key in Render environment variables
- Keep API key secret and never share it
- Monitor your OpenAI usage dashboard
- Set up usage limits in OpenAI dashboard

❌ **DON'T:**
- Commit API key to git
- Share API key in screenshots or messages
- Use the same key for multiple projects
- Leave API key in code comments

## Optional: Set Usage Limits

To prevent unexpected charges:

1. Go to [OpenAI Usage Limits](https://platform.openai.com/account/limits)
2. Set a monthly budget (e.g., $5/month)
3. Enable email notifications for usage alerts

## Feature Behavior Without API Key

If the API key is not configured:
- The camera button will still appear
- When you try to analyze an image, you'll get an error message
- You can still manually enter food information
- All other features work normally

The AI food recognition is an **optional enhancement** - the app works perfectly fine without it!

## Support

If you need help:
1. Check Render logs for specific error messages
2. Verify OpenAI account has credits
3. Test API key with a simple curl command:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

If this returns a list of models, your API key is working!