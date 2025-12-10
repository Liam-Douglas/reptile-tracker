# Data Persistence on Render

## Configuration

The Reptile Tracker app is configured to use Render's persistent disk storage to ensure your data is not lost between deployments or restarts.

### Render Configuration (`render.yaml`)

```yaml
disk:
  name: reptile-data
  mountPath: /opt/render/project/data
  sizeGB: 1
```

### Environment Variables

- `DATA_DIR`: `/opt/render/project/data` (set in render.yaml)
- Database file: `/opt/render/project/data/reptile_tracker.db`
- Uploads folder: `/opt/render/project/data/uploads`

## How It Works

1. **Persistent Disk**: Render mounts a 1GB persistent disk at `/opt/render/project/data`
2. **Database Location**: The SQLite database is stored on this persistent disk
3. **Uploads**: All uploaded images are also stored on the persistent disk
4. **Survival**: Data persists through:
   - App restarts
   - Deployments
   - Service updates

## Verifying Data Persistence

### Check Logs on Startup

When the app starts, it logs the database configuration:

```
[INFO] Database path: /opt/render/project/data/reptile_tracker.db
[INFO] Data directory: /opt/render/project/data
[INFO] Upload path: /opt/render/project/data/uploads
[INFO] Database exists: True/False
```

### Test Data Persistence

1. Add a reptile to your tracker
2. Trigger a redeploy (push a commit or manual redeploy)
3. Check if the reptile is still there after redeploy

## Troubleshooting

### Data is Lost After Restart

**Possible Causes:**

1. **Disk Not Mounted**: Check Render dashboard to ensure the disk is properly attached
2. **Wrong Path**: Verify `DATA_DIR` environment variable is set to `/opt/render/project/data`
3. **Disk Full**: Check if the 1GB disk is full (unlikely for this app)

**Solutions:**

1. Go to Render Dashboard → Your Service → Disks
2. Verify "reptile-data" disk is attached
3. Check mount path is `/opt/render/project/data`
4. If disk is missing, recreate it:
   - Name: `reptile-data`
   - Mount Path: `/opt/render/project/data`
   - Size: 1GB

### Check Database Location

SSH into your Render service (if available) or check logs:

```bash
# The app logs will show:
[INFO] Database path: /opt/render/project/data/reptile_tracker.db
```

If the path shows something else (like `/opt/render/project/src/web-app/reptile_tracker.db`), the persistent disk is not being used.

## Important Notes

1. **First Deploy**: On first deployment, the database will be created fresh
2. **Backup**: Use the "Backup Data" feature regularly to download your data
3. **Restore**: If data is lost, use "Restore Data" to upload a backup
4. **Disk Size**: 1GB is sufficient for thousands of records and images

## Manual Backup (Recommended)

1. Go to your app → Click "Backup Data"
2. Save the JSON file to your computer
3. Keep regular backups (weekly recommended)
4. To restore: Go to "Restore Data" and upload the JSON file

---

**Last Updated:** 2025-12-10