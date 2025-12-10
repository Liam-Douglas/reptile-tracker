# 🚀 Deployment Guide - Fixing Data Persistence on Render

## The Problem

When deploying to Render (or similar platforms), your reptile data disappears after each restart or deployment. This happens because:

- **Ephemeral Storage**: By default, Render uses temporary storage that gets wiped on restart
- **SQLite Database**: Your `reptile_tracker.db` file is stored in the container's filesystem
- **No Persistence**: Without persistent disk, all data is lost when the container restarts

## The Solution

We've implemented **persistent disk storage** to keep your data safe across deployments and restarts.

### What Changed

1. **app.py Updates**:
   - Now uses `DATA_DIR` environment variable for storage location
   - Database and uploads are stored in persistent location
   - Falls back to local directory for development

2. **render.yaml Configuration**:
   - Defines a persistent disk (1GB free tier)
   - Mounts disk at `/opt/render/project/data`
   - Sets environment variables automatically

3. **Automatic Directory Creation**:
   - Creates data and upload directories on startup
   - Ensures database can be created in persistent location

## Deployment Steps

### Option 1: Automatic Deployment (Recommended)

1. **Push to GitHub**:
   ```bash
   cd reptile-tracker/web-app
   git add .
   git commit -m "Add persistent storage configuration"
   git push
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` and configure everything automatically
   - Click "Create Web Service"

3. **Done!** Your data will now persist across deployments.

### Option 2: Manual Configuration

If you already have a service deployed:

1. **Go to your Render Dashboard**

2. **Add Persistent Disk**:
   - Navigate to your service
   - Click "Disks" tab
   - Click "Add Disk"
   - Configure:
     - **Name**: `reptile-data`
     - **Mount Path**: `/opt/render/project/data`
     - **Size**: 1 GB (free tier)
   - Click "Save"

3. **Add Environment Variable**:
   - Click "Environment" tab
   - Add new variable:
     - **Key**: `DATA_DIR`
     - **Value**: `/opt/render/project/data`
   - Click "Save Changes"

4. **Redeploy**:
   - Go to "Manual Deploy" → "Deploy latest commit"
   - Your data will now persist!

## Verification

After deployment, test data persistence:

1. **Add a reptile** through the web interface
2. **Trigger a redeploy** (or wait for auto-deploy)
3. **Check if the reptile is still there** after restart

✅ If the reptile persists, you're all set!

## Important Notes

### Free Tier Limits
- **Disk Size**: 1GB included free
- **Storage**: Enough for thousands of reptile records and photos
- **Persistence**: Data survives deployments, restarts, and updates

### What Gets Stored
- `reptile_tracker.db` - Your SQLite database
- `uploads/` - All uploaded reptile photos
- Both are in the persistent disk location

### Backup Recommendations
Even with persistent storage, it's good practice to:
- Export your data periodically
- Keep local backups of important photos
- Consider upgrading to paid tier for automatic backups

## Troubleshooting

### Data Still Disappearing?

1. **Check Disk is Mounted**:
   - Go to Render Dashboard → Your Service → Disks
   - Verify disk is "Active"

2. **Check Environment Variable**:
   - Go to Environment tab
   - Verify `DATA_DIR` is set to `/opt/render/project/data`

3. **Check Logs**:
   - Go to Logs tab
   - Look for "Database path: /opt/render/project/data/reptile_tracker.db"
   - If you see a different path, the environment variable isn't set

4. **Redeploy**:
   - After making changes, always redeploy
   - Go to Manual Deploy → Deploy latest commit

### Migration from Old Deployment

If you had data in an old deployment without persistent storage:

1. **Export your data** before the new deployment (if possible)
2. **Deploy with persistent storage**
3. **Re-enter your data** (unfortunately, old data can't be recovered)

## Railway Alternative

If using Railway instead of Render:

1. Railway also supports persistent volumes
2. Update `nixpacks.toml` or use Railway's volume feature
3. Set `DATA_DIR` environment variable
4. Mount volume to `/opt/railway/data` or similar

## Local Development

The app works locally without any changes:
- Uses current directory for database
- No environment variables needed
- Data stored in `reptile_tracker.db` in the app folder

```bash
python app.py
# Database will be created in current directory
```

## Support

If you continue to have issues:
1. Check Render's documentation on persistent disks
2. Verify your free tier includes disk storage
3. Contact Render support if disk isn't mounting

---

**Made with Bob** 🦎