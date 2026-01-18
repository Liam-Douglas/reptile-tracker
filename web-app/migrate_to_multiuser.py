#!/usr/bin/env python3
"""
Migration Script: Single-User to Multi-User System
Converts existing reptile data to the new multi-user household system
"""

import sys
import os
from getpass import getpass

# Add parent directory to path to import database module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reptile_tracker_db import ReptileDatabase
from flask_bcrypt import Bcrypt

def migrate_to_multiuser(db_path='reptile_tracker.db'):
    """
    Migrate existing single-user data to multi-user system
    
    Steps:
    1. Check if migration is needed
    2. Create default user account
    3. Create default household
    4. Assign all existing reptiles to the household
    5. Verify migration
    """
    
    print("=" * 60)
    print("REPTILE TRACKER - MULTI-USER MIGRATION")
    print("=" * 60)
    print()
    
    # Initialize database
    db = ReptileDatabase(db_path)
    bcrypt = Bcrypt()
    
    # Check if users already exist
    db.cursor.execute("SELECT COUNT(*) FROM users")
    user_count = db.cursor.fetchone()[0]
    
    if user_count > 0:
        print("✅ Migration already completed!")
        print(f"   Found {user_count} existing user(s)")
        
        # Show existing users
        db.cursor.execute("SELECT id, name, email FROM users")
        users = db.cursor.fetchall()
        print("\n📋 Existing Users:")
        for user in users:
            print(f"   - {user[1]} ({user[2]})")
        
        print("\n💡 You can log in with your existing credentials.")
        return True
    
    print("🔍 Checking existing data...")
    
    # Count existing reptiles
    db.cursor.execute("SELECT COUNT(*) FROM reptiles")
    reptile_count = db.cursor.fetchone()[0]
    
    # Count existing feeding logs
    db.cursor.execute("SELECT COUNT(*) FROM feeding_logs")
    feeding_count = db.cursor.fetchone()[0]
    
    # Count existing shed records
    db.cursor.execute("SELECT COUNT(*) FROM shed_records")
    shed_count = db.cursor.fetchone()[0]
    
    print(f"\n📊 Found existing data:")
    print(f"   - {reptile_count} reptiles")
    print(f"   - {feeding_count} feeding logs")
    print(f"   - {shed_count} shed records")
    
    if reptile_count == 0:
        print("\n✅ No existing data to migrate.")
        print("   You can start fresh by registering a new account!")
        return True
    
    print("\n" + "=" * 60)
    print("CREATING DEFAULT USER ACCOUNT")
    print("=" * 60)
    print()
    print("To preserve your existing data, we'll create a default user account.")
    print("You can use this account to access all your existing reptiles.")
    print()
    
    # Get user details
    while True:
        name = input("Enter your name: ").strip()
        if name:
            break
        print("❌ Name cannot be empty")
    
    while True:
        email = input("Enter your email: ").strip()
        if email and '@' in email:
            break
        print("❌ Please enter a valid email address")
    
    while True:
        password = getpass("Enter password (min 8 chars, 1 uppercase, 1 lowercase, 1 number): ")
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            continue
        if not any(c.isupper() for c in password):
            print("❌ Password must contain at least one uppercase letter")
            continue
        if not any(c.islower() for c in password):
            print("❌ Password must contain at least one lowercase letter")
            continue
        if not any(c.isdigit() for c in password):
            print("❌ Password must contain at least one number")
            continue
        
        confirm = getpass("Confirm password: ")
        if password == confirm:
            break
        print("❌ Passwords do not match")
    
    print("\n🔄 Starting migration...")
    
    try:
        # Create password hash
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create user
        user_id = db.create_user(email, password_hash, name)
        if not user_id:
            print("❌ Error: Email already exists")
            return False
        
        print(f"✅ Created user account: {name} ({email})")
        
        # Create household
        household_id = db.create_household(f"{name}'s Household", user_id)
        print(f"✅ Created household: {name}'s Household")
        
        # Update all existing reptiles to belong to this household
        db.cursor.execute("""
            UPDATE reptiles 
            SET household_id = ? 
            WHERE household_id IS NULL
        """, (household_id,))
        
        updated_count = db.cursor.rowcount
        db.conn.commit()
        
        print(f"✅ Assigned {updated_count} reptiles to your household")
        
        # Verify migration
        db.cursor.execute("""
            SELECT COUNT(*) FROM reptiles 
            WHERE household_id = ?
        """, (household_id,))
        
        verified_count = db.cursor.fetchone()[0]
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE!")
        print("=" * 60)
        print(f"\n✅ Successfully migrated {verified_count} reptiles")
        print(f"✅ All feeding logs and shed records preserved")
        print(f"\n📧 Login credentials:")
        print(f"   Email: {email}")
        print(f"   Password: (the one you just entered)")
        print(f"\n🏠 Household: {name}'s Household")
        print(f"\n💡 Next steps:")
        print(f"   1. Visit your Reptile Tracker app")
        print(f"   2. Log in with your new credentials")
        print(f"   3. All your reptiles will be there!")
        print(f"   4. Invite your partner using the Profile page")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.conn.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    # Get database path from environment or use default
    db_path = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(db_path, 'reptile_tracker.db')
    
    print(f"Database: {db_path}")
    print()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("   Please run this script from the web-app directory")
        sys.exit(1)
    
    success = migrate_to_multiuser(db_path)
    sys.exit(0 if success else 1)

# Made with Bob
