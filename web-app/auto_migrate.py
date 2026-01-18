#!/usr/bin/env python3
"""
Automatic Migration for Render Deployment
Runs automatically on first deployment to migrate existing data
"""

import os
import sys
from reptile_tracker_db import ReptileDatabase
from flask_bcrypt import Bcrypt

def auto_migrate():
    """
    Automatically migrate existing data on Render deployment
    Creates a default admin user if data exists but no users
    """
    
    # Get database path
    DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(DATA_DIR, 'reptile_tracker.db')
    
    print("[AUTO-MIGRATE] Checking if migration is needed...")
    
    try:
        db = ReptileDatabase(DB_PATH)
        bcrypt = Bcrypt()
        
        # Check if users exist
        db.cursor.execute("SELECT COUNT(*) FROM users")
        user_count = db.cursor.fetchone()[0]
        
        if user_count > 0:
            print(f"[AUTO-MIGRATE] ✅ Migration already completed ({user_count} users exist)")
            db.close()
            return True
        
        # Check if there's existing data to migrate
        db.cursor.execute("SELECT COUNT(*) FROM reptiles")
        reptile_count = db.cursor.fetchone()[0]
        
        if reptile_count == 0:
            print("[AUTO-MIGRATE] ✅ No existing data to migrate")
            db.close()
            return True
        
        print(f"[AUTO-MIGRATE] ⚠️  Found {reptile_count} reptiles without users")
        print("[AUTO-MIGRATE] 🔄 Creating default admin account...")
        
        # Create default admin user
        # User can change these credentials after first login
        default_email = os.environ.get('ADMIN_EMAIL', 'admin@reptiletracker.local')
        default_password = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')
        default_name = os.environ.get('ADMIN_NAME', 'Admin User')
        
        # Hash password
        password_hash = bcrypt.generate_password_hash(default_password).decode('utf-8')
        
        # Create user
        user_id = db.create_user(default_email, password_hash, default_name)
        if not user_id:
            print("[AUTO-MIGRATE] ❌ Failed to create user (email may exist)")
            db.close()
            return False
        
        print(f"[AUTO-MIGRATE] ✅ Created user: {default_name} ({default_email})")
        
        # Create household
        household_id = db.create_household(f"{default_name}'s Household", user_id)
        print(f"[AUTO-MIGRATE] ✅ Created household")
        
        # Check if household_id column exists in reptiles table
        db.cursor.execute("PRAGMA table_info(reptiles)")
        columns = [column[1] for column in db.cursor.fetchall()]
        
        if 'household_id' not in columns:
            print("[AUTO-MIGRATE] 🔧 Adding household_id column to reptiles table...")
            db.cursor.execute("""
                ALTER TABLE reptiles
                ADD COLUMN household_id INTEGER
                REFERENCES households(id)
            """)
            db.conn.commit()
            print("[AUTO-MIGRATE] ✅ household_id column added")
        
        # Assign all existing reptiles to this household
        db.cursor.execute("""
            UPDATE reptiles
            SET household_id = ?
            WHERE household_id IS NULL
        """, (household_id,))
        
        updated_count = db.cursor.rowcount
        db.conn.commit()
        
        print(f"[AUTO-MIGRATE] ✅ Assigned {updated_count} reptiles to household")
        
        # Verify
        db.cursor.execute("""
            SELECT COUNT(*) FROM reptiles 
            WHERE household_id = ?
        """, (household_id,))
        
        verified_count = db.cursor.fetchone()[0]
        
        print("[AUTO-MIGRATE] " + "=" * 50)
        print("[AUTO-MIGRATE] ✅ MIGRATION COMPLETE!")
        print("[AUTO-MIGRATE] " + "=" * 50)
        print(f"[AUTO-MIGRATE] Migrated {verified_count} reptiles")
        print(f"[AUTO-MIGRATE] ")
        print(f"[AUTO-MIGRATE] 🔐 DEFAULT LOGIN CREDENTIALS:")
        print(f"[AUTO-MIGRATE]    Email: {default_email}")
        print(f"[AUTO-MIGRATE]    Password: {default_password}")
        print(f"[AUTO-MIGRATE] ")
        print(f"[AUTO-MIGRATE] ⚠️  IMPORTANT: Change your password after first login!")
        print(f"[AUTO-MIGRATE]    Go to Profile → Change Password")
        print("[AUTO-MIGRATE] " + "=" * 50)
        
        db.close()
        return True
        
    except Exception as e:
        print(f"[AUTO-MIGRATE] ❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = auto_migrate()
    sys.exit(0 if success else 1)

# Made with Bob
