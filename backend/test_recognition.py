"""Test face recognition setup"""
from database_mongo import AttendanceDatabase
import os

# Initialize database
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
db = AttendanceDatabase(connection_string=MONGODB_URI)

# Check photos
photos = db.get_all_student_photos()
print(f"\n=== PHOTO DATABASE CHECK ===")
print(f"Total photos in database: {len(photos)}")

if photos:
    print("\nPhoto details:")
    for i, photo in enumerate(photos[:10], 1):
        exists = os.path.exists(photo['photo_path'])
        print(f"{i}. Student: {photo['student_id']}")
        print(f"   Path: {photo['photo_path']}")
        print(f"   Type: {photo.get('photo_type', 'N/A')}")
        print(f"   File exists: {exists}")
        if exists:
            size = os.path.getsize(photo['photo_path'])
            print(f"   File size: {size} bytes")
        print()
else:
    print("\nNo photos found in database!")
    print("Please upload photos for students first.")

# Check students
students = db.get_all_students()
print(f"\n=== STUDENT DATABASE CHECK ===")
print(f"Total students: {len(students)}")
for student in students[:5]:
    print(f"- {student['student_id']}: {student['name']}")
