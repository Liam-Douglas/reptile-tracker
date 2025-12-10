# 🚨 URGENT: Fix Data Persistence on Render

## Problem Identified

Your logs show:
```
[INFO] Database path: /opt/render/project/src/web-app/reptile_tracker.db
[INFO] Data directory: /opt/render/project/src/web-app
```

**This is WRONG!** The database is being stored in ephemeral storage, which is why data is lost on restart.

It SHOULD be:
```
[INFO] Database path: /opt/render/project/data/reptile_tracker.db
[INFO] Data directory: /opt/render/project/data
```

## Root Cause

The `DATA_DIR` environment variable from `render.yaml` is not being applied. This happens when:
1. The persistent disk hasn't been created in Render dashboard
2. Environment variables need to be set manually in dashboard

## IMMEDIATE FIX - Follow These Steps

### Step 1: Add Environment Variable in Render Dashboard

1. Go to https://dashboard.render.com
2. Click on your **reptile-tracker** service
3. Click **Environment** in the left sidebar
4. Click **Add Environment Variable**
5. Add:
   - **Key:** `DATA_DIR`
   - **Value:** `/opt/render/project/data`
6. Click **Save Changes**

### Step 2: Create Persistent Disk

1. Still in your service dashboard, click **Disks** in the left sidebar
2. Click **Add Disk** (or **Create Disk**)
3. Configure:
   - **Name:** `reptile-data`
   - **Mount Path:** `/opt/render/project/data`
   - **Size:** 1 GB
4. Click **Create** or **Save**

### Step 3: Redeploy

1. Go to **Manual Deploy** tab
2. Click **Deploy latest commit**
3. Wait for deployment to complete

### Step 4: Verify Fix

After deployment, check the logs. You should see:
```
[INFO] Database path: /opt/render/project/data/reptile_tracker.db
[INFO] Data directory: /opt/render/project/data
[INFO] Upload path: /opt/render/project/data/uploads
[INFO] Database exists: False (first time) or True (after adding data)
```

## After Fix

Once fixed:
1. ✅ Your data will persist between restarts
2. ✅ Deployments won't delete your reptiles
3. ✅ Uploaded images will be saved
4. ✅ Database will survive service updates

## Important Notes

- **First time after fix:** Database will be empty (Database exists: False)
- **Add your reptiles again** - they will now persist!
- **Use Backup feature** regularly as extra safety
- The disk costs ~$0.25/month for 1GB

## Verification Checklist

After completing the steps above, verify:

- [ ] Environment variable `DATA_DIR` = `/opt/render/project/data` is set
- [ ] Disk named `reptile-data` is created and attached
- [ ] Disk mount path is `/opt/render/project/data`
- [ ] Logs show correct database path after redeploy
- [ ] Added a test reptile
- [ ] Triggered a redeploy
- [ ] Test reptile still exists after redeploy ✅

---

**Need Help?** Share your Render dashboard screenshots or logs if issues persist.