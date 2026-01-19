#!/usr/bin/env python3
"""
Diagnostic script to check database state
"""
import os
import sqlite3

# Get database path
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DATA_DIR, 'reptile_tracker.db')

print(f"Database path: {DB_PATH}")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check users
print("\n=== USERS ===")
cursor.execute("SELECT id, email, name FROM users")
users = cursor.fetchall()
for user in users:
    print(f"User {user['id']}: {user['name']} ({user['email']})")

# Check households
print("\n=== HOUSEHOLDS ===")
cursor.execute("SELECT id, name, created_by FROM households")
households = cursor.fetchall()
for household in households:
    print(f"Household {household['id']}: {household['name']} (created by user {household['created_by']})")

# Check household members
print("\n=== HOUSEHOLD MEMBERS ===")
cursor.execute("SELECT household_id, user_id, role FROM household_members")
members = cursor.fetchall()
for member in members:
    print(f"Household {member['household_id']} -> User {member['user_id']} ({member['role']})")

# Check reptiles
print("\n=== REPTILES ===")
cursor.execute("SELECT id, name, household_id FROM reptiles")
reptiles = cursor.fetchall()
print(f"Total reptiles: {len(reptiles)}")
for reptile in reptiles:
    print(f"Reptile {reptile['id']}: {reptile['name']} (household_id: {reptile['household_id']})")

# Check if household_id column exists
print("\n=== REPTILES TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(reptiles)")
columns = cursor.fetchall()
for col in columns:
    print(f"Column: {col['name']} ({col['type']})")

conn.close()
print("\n" + "=" * 60)

# Made with Bob
