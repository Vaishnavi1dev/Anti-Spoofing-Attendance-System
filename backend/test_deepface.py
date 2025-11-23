"""Test DeepFace recognition"""
from database_mongo import AttendanceDatabase
from deepface import DeepFace
import os
import shutil
import cv2

# Initialize database
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
db = AttendanceDatabase(connection_string=MONGODB_URI)

# Get all photos
all_photos = db.get_all_student_photos()
print(f"Found {len(all_photos)} photos in database")

if not all_photos:
    print("No photos to test with!")
    exit(1)

# Create temp database
temp_db = "temp_test_db"
os.makedirs(temp_db, exist_ok=True)

print("\nCopying photos to temp database...")
for photo in all_photos:
    if os.path.exists(photo['photo_path']):
        dest = os.path.join(temp_db, f"{photo['student_id']}_{os.path.basename(photo['photo_path'])}")
        shutil.copy2(photo['photo_path'], dest)
        print(f"  Copied: {photo['student_id']} -> {dest}")

# Test with the first photo
test_photo = all_photos[0]
print(f"\n=== Testing recognition with photo from {test_photo['student_id']} ===")
print(f"Test photo path: {test_photo['photo_path']}")

try:
    # Try to find the face in the database
    result = DeepFace.find(
        img_path=test_photo['photo_path'],
        db_path=temp_db,
        model_name="VGG-Face",
        enforce_detection=False,
        silent=False
    )
    
    print(f"\nResult type: {type(result)}")
    print(f"Result length: {len(result)}")
    
    if len(result) > 0 and len(result[0]) > 0:
        print("\n=== MATCH FOUND ===")
        print(result[0])
        matched_path = result[0]['identity'].iloc[0]
        print(f"\nMatched path: {matched_path}")
        
        # Extract student ID from filename
        filename = os.path.basename(matched_path)
        student_id = filename.split('_')[0]
        print(f"Extracted student ID: {student_id}")
        
        student = db.get_student(student_id)
        if student:
            print(f"Student found: {student['name']}")
        else:
            print(f"Student not found in database!")
    else:
        print("\n=== NO MATCH FOUND ===")
        print("DeepFace could not find a matching face")
        
except Exception as e:
    print(f"\nError during recognition: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
if os.path.exists(temp_db):
    shutil.rmtree(temp_db)
    print("\nCleaned up temp database")
