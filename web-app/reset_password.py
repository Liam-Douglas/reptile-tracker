#!/usr/bin/env python3
"""
Password Reset Helper Script
Run this from Render shell to reset a user's password
"""

import os
import sys
from reptile_tracker_db import ReptileDatabase
from flask_bcrypt import Bcrypt

def reset_password():
    """Reset a user's password"""
    
    # Get database path
    DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(DATA_DIR, 'reptile_tracker.db')
    
    print("=" * 60)
    print("PASSWORD RESET UTILITY")
    print("=" * 60)
    
    try:
        db = ReptileDatabase(DB_PATH)
        bcrypt = Bcrypt()
        
        # Get user email
        email = input("\nEnter user email: ").strip()
        
        if not email:
            print("❌ Email is required")
            return False
        
        # Check if user exists
        user = db.get_user_by_email(email)
        if not user:
            print(f"❌ No user found with email: {email}")
            return False
        
        print(f"\n✅ Found user: {user['name']} ({user['email']})")
        
        # Get new password
        new_password = input("\nEnter new password (min 8 characters): ").strip()
        
        if len(new_password) < 8:
            print("❌ Password must be at least 8 characters")
            return False
        
        # Confirm password
        confirm_password = input("Confirm new password: ").strip()
        
        if new_password != confirm_password:
            print("❌ Passwords do not match")
            return False
        
        # Hash and update password
        password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        db.cursor.execute("""
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        """, (password_hash, user['id']))
        db.conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ PASSWORD RESET SUCCESSFUL!")
        print("=" * 60)
        print(f"User: {user['name']}")
        print(f"Email: {user['email']}")
        print(f"New password has been set")
        print("\nThe user can now log in with their new password.")
        print("=" * 60)
        
        db.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = reset_password()
    sys.exit(0 if success else 1)

# Made with Bob
