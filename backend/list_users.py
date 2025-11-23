"""
List all users in the system
"""
from auth import UserManager
from database_mongo import AttendanceDatabase
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/classroom_attendance")

db = AttendanceDatabase(connection_string=MONGODB_URI)
user_manager = UserManager(db)

print("=== All Users in System ===\n")

users = user_manager.get_all_users()

if not users:
    print("No users found.")
else:
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['name']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user.get('role', 'N/A')}")
        print(f"   Active: {user.get('is_active', True)}")
        print()

print(f"Total users: {len(users)}")
