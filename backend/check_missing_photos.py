"""Check which students are missing photos"""
from database_mongo import AttendanceDatabase
import os

# Initialize database
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
db = AttendanceDatabase(connection_string=MONGODB_URI)

print("=== Student Photo Status ===\n")

# Get all students
students = db.get_all_students()
print(f"Total students in database: {len(students)}\n")

students_with_photos = []
students_without_photos = []

for student in students:
    student_id = student['student_id']
    name = student['name']
    
    # Get photos for this student
    photos = db.get_student_photos(student_id)
    
    if photos and len(photos) > 0:
        students_with_photos.append({
            'id': student_id,
            'name': name,
            'photo_count': len(photos)
        })
    else:
        students_without_photos.append({
            'id': student_id,
            'name': name
        })

print("✅ Students WITH photos:")
print("-" * 60)
if students_with_photos:
    for s in students_with_photos:
        print(f"  {s['id']:20s} | {s['name']:25s} | {s['photo_count']} photo(s)")
else:
    print("  None")

print(f"\n❌ Students WITHOUT photos:")
print("-" * 60)
if students_without_photos:
    for s in students_without_photos:
        print(f"  {s['id']:20s} | {s['name']}")
else:
    print("  None")

print(f"\n📊 Summary:")
print(f"  With photos: {len(students_with_photos)}/{len(students)}")
print(f"  Without photos: {len(students_without_photos)}/{len(students)}")
print(f"  Coverage: {(len(students_with_photos)/len(students)*100):.1f}%")

if students_without_photos:
    print(f"\n⚠️  WARNING: {len(students_without_photos)} student(s) have no photos!")
    print(f"  These students will NOT be recognized by the camera.")
    print(f"  Other people might be incorrectly identified as students with photos.")
    print(f"\n💡 Action Required:")
    print(f"  1. Login to the application")
    print(f"  2. Go to Students page")
    print(f"  3. Click on each student without photos")
    print(f"  4. Upload 3-5 clear photos for each")
    print(f"\n  Students needing photos:")
    for s in students_without_photos:
        print(f"    - {s['name']} ({s['id']})")

print(f"\n📸 Photo Upload Tips:")
print(f"  - Upload 3-5 photos per student")
print(f"  - Include: front, left profile, right profile")
print(f"  - Clear, well-lit photos")
print(f"  - Face clearly visible")
print(f"  - Similar to camera conditions")
