"""
Script to create the first admin user
Run this after setting up the database
"""

import os
import sys
sys.path.append('..')

from database_mongo import AttendanceDatabase
from auth import UserManager, UserCreate

def create_admin_user():
    """Create the first admin user"""
    
    print("🔐 Creating Admin User for Smart Classroom Attendance System")
    print("=" * 60)
    
    # Get MongoDB connection
    mongodb_uri = input("MongoDB URI (press Enter for default): ").strip()
    if not mongodb_uri:
        mongodb_uri = "mongodb://localhost:27017/"
    
    try:
        # Initialize database and user manager
        db = AttendanceDatabase(connection_string=mongodb_uri)
        user_manager = UserManager(db)
        
        print("✅ Connected to MongoDB")
        
        # Get admin details
        print("\n📝 Enter Admin Details:")
        email = input("Email: ").strip()
        name = input("Full Name: ").strip()
        password = input("Password: ").strip()
        
        if not email or not name or not password:
            print("❌ All fields are required!")
            return
        
        # Create admin user
        admin_user = UserCreate(
            email=email,
            name=name,
            password=password,
            role="admin"
        )
        
        result = user_manager.create_user(admin_user)
        
        print(f"\n✅ Admin user created successfully!")
        print(f"   Email: {result['email']}")
        print(f"   Name: {result['name']}")
        print(f"   Role: {result['role']}")
        print(f"   Created: {result['created_at']}")
        
        print(f"\n🚀 You can now login at:")
        print(f"   POST /api/auth/login")
        print(f"   Body: {{'email': '{email}', 'password': 'your_password'}}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_admin_user()