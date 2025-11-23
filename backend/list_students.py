"""
List all students in the database
"""
from database_mongo import AttendanceDatabase
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/classroom_attendance")

db = AttendanceDatabase(connection_string=MONGODB_URI)

print("=== All Students ===\n")

students = db.get_all_students()

if not students:
    print("No students found.")
else:
    for i, student in enumerate(students, 1):
        print(f"{i}. {student['name']} (ID: {student['student_id']})")
        print(f"   Email: {student.get('email', 'N/A')}")
        print(f"   Phone: {student.get('phone', 'N/A')}")
        
        # Get photos
        photos = db.get_student_photos(student['student_id'])
        print(f"   Photos: {len(photos)}")
        print()

print(f"Total students: {len(students)}")

db.close()
