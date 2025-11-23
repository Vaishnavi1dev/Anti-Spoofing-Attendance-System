"""
Script to add a student with login credentials
"""

import sys
import os
sys.path.append('..')

from database_mongo import AttendanceDatabase
from auth import get_password_hash

def add_student_with_login():
    """Add a student with login credentials"""
    
    print("🎓 Add Student with Login Credentials")
    print("=" * 60)
    
    # Get MongoDB connection
    mongodb_uri = input("MongoDB URI (press Enter for default): ").strip()
    if not mongodb_uri:
        mongodb_uri = "mongodb://localhost:27017/"
    
    try:
        # Initialize database
        db = AttendanceDatabase(connection_string=mongodb_uri)
        print("✅ Connected to MongoDB")
        
        # Get student details
        print("\n📝 Enter Student Details:")
        student_id = input("Student ID (e.g., STU001): ").strip()
        name = input("Full Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone (optional): ").strip() or None
        password = input("Password (for student login): ").strip()
        
        if not student_id or not name or not email or not password:
            print("❌ Student ID, Name, Email, and Password are required!")
            return
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Add student
        success = db.add_student(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone,
            password=hashed_password
        )
        
        if success:
            print(f"\n✅ Student added successfully!")
            print(f"   Student ID: {student_id}")
            print(f"   Name: {name}")
            print(f"   Email: {email}")
            print(f"\n🔐 Student can now login with:")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"\n📸 Don't forget to add photos using the frontend or setup script!")
        else:
            print("❌ Failed to add student (may already exist)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_student_with_login()
