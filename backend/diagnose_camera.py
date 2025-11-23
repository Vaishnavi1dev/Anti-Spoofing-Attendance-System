"""Diagnose camera and face detection"""
import cv2
import numpy as np
from database_mongo import AttendanceDatabase
import os

print("=== Camera and Face Detection Diagnostic ===\n")

# Check database
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
db = AttendanceDatabase(connection_string=MONGODB_URI)

photos = db.get_all_student_photos()
students = db.get_all_students()

print(f"📊 Database Status:")
print(f"   Students: {len(students)}")
print(f"   Photos: {len(photos)}")

if photos:
    print(f"\n📸 Photos in database:")
    for photo in photos:
        exists = os.path.exists(photo['photo_path'])
        size = os.path.getsize(photo['photo_path']) if exists else 0
        print(f"   - {photo['student_id']}: {photo['photo_type']} ({size} bytes) {'✓' if exists else '✗'}")

# Test camera
print(f"\n🎥 Testing camera...")
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("   ✗ Failed to open camera")
    exit(1)

print("   ✓ Camera opened successfully")

# Get camera properties
width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = camera.get(cv2.CAP_PROP_FPS)

print(f"   Resolution: {int(width)}x{int(height)}")
print(f"   FPS: {int(fps)}")

# Capture a frame
ret, frame = camera.read()
if not ret:
    print("   ✗ Failed to capture frame")
    camera.release()
    exit(1)

print(f"   ✓ Frame captured: {frame.shape}")

# Test face detection
print(f"\n👤 Testing face detection...")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, 1.3, 5)

print(f"   Detected {len(faces)} face(s)")

if len(faces) > 0:
    for i, (x, y, w, h) in enumerate(faces, 1):
        print(f"   Face {i}: position=({x}, {y}), size={w}x{h}")
        
        # Save face image for inspection
        face_img = frame[y:y+h, x:x+w]
        face_path = f"diagnostic_face_{i}.jpg"
        cv2.imwrite(face_path, face_img)
        print(f"   Saved to: {face_path}")
else:
    print("   ⚠️  No faces detected in current frame")
    print("   Tips:")
    print("   - Make sure you're in front of the camera")
    print("   - Ensure good lighting")
    print("   - Face the camera directly")

# Save full frame for inspection
frame_path = "diagnostic_frame.jpg"
cv2.imwrite(frame_path, frame)
print(f"\n💾 Full frame saved to: {frame_path}")

camera.release()

print(f"\n✅ Diagnostic complete!")
print(f"\nNext steps:")
print(f"1. Check the saved images (diagnostic_*.jpg)")
print(f"2. If no faces detected, adjust lighting and position")
print(f"3. If faces detected, test recognition with test_camera_recognition.py")
print(f"4. Open frontend/test-recognition.html in browser for live testing")
