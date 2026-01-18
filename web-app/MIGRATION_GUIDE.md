# Migration Guide: Single-User to Multi-User System

## Overview

This guide explains how to migrate your existing Reptile Tracker data to the new multi-user authentication system.

## What Happens During Migration?

The migration script will:
1. ✅ **Preserve ALL your existing data** (reptiles, feeding logs, shed records, etc.)
2. ✅ Create a user account for you
3. ✅ Create a household for your account
4. ✅ Assign all existing reptiles to your household
5. ✅ Keep all feeding logs, shed records, and other data intact

**Nothing is deleted or lost!**

## Prerequisites

- Python 3.7 or higher
- Flask-Bcrypt installed (already in requirements.txt)
- Access to your reptile_tracker.db file

## Migration Steps

### Option 1: Automatic Migration (Recommended)

The migration will happen automatically when you first try to access the app:

1. **Deploy the updated code** to your server
2. **Visit your app** in a browser
3. You'll be redirected to the **login page**
4. Click **"Register"** to create your account
5. **Important:** Use the migration script first (see Option 2) if you have existing data

### Option 2: Manual Migration (For Existing Data)

If you already have reptiles in your database, run the migration script **before** accessing the app:

```bash
# Navigate to the web-app directory
cd /path/to/reptile-tracker/web-app

# Run the migration script
python3 migrate_to_multiuser.py
```

The script will:
1. Check for existing data
2. Ask you to create a user account
3. Migrate all your reptiles to your new account
4. Show you your login credentials

### Example Migration Session

```
============================================================
REPTILE TRACKER - MULTI-USER MIGRATION
============================================================

🔍 Checking existing data...

📊 Found existing data:
   - 5 reptiles
   - 127 feeding logs
   - 23 shed records

============================================================
CREATING DEFAULT USER ACCOUNT
============================================================

To preserve your existing data, we'll create a default user account.
You can use this account to access all your existing reptiles.

Enter your name: John Smith
Enter your email: john@example.com
Enter password (min 8 chars, 1 uppercase, 1 lowercase, 1 number): ********
Confirm password: ********

🔄 Starting migration...
✅ Created user account: John Smith (john@example.com)
✅ Created household: John Smith's Household
✅ Assigned 5 reptiles to your household

============================================================
MIGRATION COMPLETE!
============================================================

✅ Successfully migrated 5 reptiles
✅ All feeding logs and shed records preserved

📧 Login credentials:
   Email: john@example.com
   Password: (the one you just entered)

🏠 Household: John Smith's Household

💡 Next steps:
   1. Visit your Reptile Tracker app
   2. Log in with your new credentials
   3. All your reptiles will be there!
   4. Invite your partner using the Profile page
```

## After Migration

### Logging In

1. Visit your Reptile Tracker app
2. You'll see the login page
3. Enter your email and password
4. Click "Login"
5. All your reptiles will be there!

### Inviting Your Partner

1. Log in to your account
2. Click your name in the navigation menu
3. Go to **Profile**
4. Click **"Generate Invite Code"**
5. Share the code with your partner
6. Your partner registers with the code
7. You both now share the same reptile collection!

### What Your Partner Sees

When your partner joins your household:
- ✅ All your reptiles
- ✅ All feeding logs
- ✅ All shed records
- ✅ All expenses and inventory
- ✅ Everything you've tracked!

## Troubleshooting

### "Migration already completed"

If you see this message, it means:
- Migration has already run
- You can log in with your existing credentials
- No action needed!

### "Database not found"

Make sure you're running the script from the correct directory:
```bash
cd /path/to/reptile-tracker/web-app
python3 migrate_to_multiuser.py
```

### "Email already exists"

This means a user with that email already exists. You can:
- Use a different email address
- Or log in with the existing account

### Lost Password

If you forget your password after migration:
1. Contact support or
2. Run the migration script again with a new email

## Data Safety

### What's Preserved?
- ✅ All reptiles
- ✅ All feeding logs
- ✅ All shed records
- ✅ All weight measurements
- ✅ All length measurements
- ✅ All photos
- ✅ All expenses
- ✅ All inventory items
- ✅ All feeding reminders
- ✅ All notification settings

### What Changes?
- ✅ Reptiles now belong to a household
- ✅ You need to log in to access the app
- ✅ You can invite others to share your collection

### Backup Recommendation

Before migration, it's always good to backup your database:

```bash
# Create a backup
cp reptile_tracker.db reptile_tracker.db.backup

# If something goes wrong, restore it
cp reptile_tracker.db.backup reptile_tracker.db
```

## Technical Details

### Database Changes

The migration adds:
- `household_id` column to reptiles table
- Links all existing reptiles to your new household
- No data is deleted or modified (except adding household_id)

### Schema Updates

```sql
-- Reptiles now have a household_id
UPDATE reptiles 
SET household_id = <your_household_id> 
WHERE household_id IS NULL;
```

## Support

If you encounter any issues during migration:

1. Check the error message
2. Ensure you're in the correct directory
3. Verify Python 3 is installed
4. Check that Flask-Bcrypt is installed
5. Create a GitHub issue with the error details

## FAQ

**Q: Will I lose my data?**  
A: No! All data is preserved. The migration only adds household information.

**Q: Can I undo the migration?**  
A: Yes, restore your database backup. But you'll need to run migration again to use the new features.

**Q: Do I need to migrate if I'm a new user?**  
A: No! Just register a new account and start fresh.

**Q: Can I have multiple households?**  
A: Currently, each user belongs to one household. You can leave and join different households.

**Q: What if my partner already has an account?**  
A: They can join your household using an invite code. Their existing data will remain in their original household.

## Next Steps

After successful migration:
1. ✅ Log in with your new credentials
2. ✅ Verify all your reptiles are there
3. ✅ Invite your partner
4. ✅ Enable push notifications on all devices
5. ✅ Enjoy the multi-user features!