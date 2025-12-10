# Render Persistent Disk Setup Guide

## Problem
Data is being lost after each deployment because the persistent disk hasn't been created in Render's dashboard.

## Solution: Create Persistent Disk in Render Dashboard

### Step-by-Step Instructions

1. **Log into Render Dashboard**
   - Go to https://dashboard.render.com
   - Navigate to your `reptile-tracker` web service

2. **Create the Persistent Disk**
   - In your service's page, click on the **"Disks"** tab in the left sidebar
   - Click **"Add Disk"** button
   - Fill in the disk details:
     - **Name**: `reptile-data` (must match the name in render.yaml)
     - **Mount Path**: `/opt/render/project/data` (must match render.yaml)
     - **Size**: `1 GB` (or more if needed)
   - Click **"Save"**

3. **Redeploy Your Service**
   - After creating the disk, Render will automatically redeploy your service
   - Wait for the deployment to complete
   - The disk will now persist data between deployments

4. **Verify It's Working**
   - Add some reptile data through your web app
   - Trigger a manual redeploy from Render dashboard
   - Check if your data is still there after redeployment

## Important Notes

- **One-time setup**: You only need to create the disk once
- **Automatic mounting**: Once created, the disk automatically mounts on every deployment
- **Data persistence**: All data in `/opt/render/project/data` will persist across deployments
- **Database location**: Your SQLite database is stored at `/opt/render/project/data/reptile_tracker.db`
- **Uploads folder**: Photo uploads are stored at `/opt/render/project/data/uploads`

## What Gets Persisted

With the disk properly configured, the following will persist:
- ✅ Reptile database (reptile_tracker.db)
- ✅ All reptile records
- ✅ Feeding logs
- ✅ Shed records
- ✅ Weight history
- ✅ Length history
- ✅ Photo uploads (when photo gallery feature is added)

## Troubleshooting

### Data still not persisting?
1. Verify the disk name is exactly `reptile-data`
2. Verify the mount path is exactly `/opt/render/project/data`
3. Check Render logs for any disk mounting errors
4. Ensure the disk is showing as "Active" in the Disks tab

### Can't see the Disks tab?
- Make sure you're on a paid Render plan (persistent disks are not available on free tier)
- If on free tier, consider upgrading or using a different deployment platform

## Alternative: Use Render PostgreSQL

If you prefer a managed database instead of SQLite with persistent disk:
1. Create a Render PostgreSQL database
2. Update the app to use PostgreSQL instead of SQLite
3. This provides better reliability and automatic backups

---
**Created**: 2025-12-10
**Last Updated**: 2025-12-10