"""
Test MongoDB connection and student creation
"""
from database_mongo import AttendanceDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/classroom_attendance")

print(f"Testing connection to: {MONGODB_URI}")

try:
    # Initialize database
    db = AttendanceDatabase(connection_string=MONGODB_URI)
    print("✓ Connected to MongoDB successfully!")
    
    # Test adding a student
    test_student_id = "TEST001"
    success = db.add_student(
        student_id=test_student_id,
        name="Test Student",
        email="test@example.com",
        phone="+1234567890"
    )
    
    if success:
        print(f"✓ Successfully added test student: {test_student_id}")
        
        # Retrieve the student
        student = db.get_student(test_student_id)
        print(f"✓ Retrieved student: {student}")
        
        # Clean up
        db.delete_student(test_student_id)
        print(f"✓ Cleaned up test student")
    else:
        print("✗ Failed to add student (might already exist)")
    
    db.close()
    print("\n✓ All tests passed! MongoDB is working correctly.")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure MongoDB is running: docker ps")
    print("2. Check connection string in .env file")
    print("3. Verify credentials match your .env configuration")
