"""Test camera recognition endpoint"""
import requests
import os

# Get the photo path
photo_path = "photos/students/245524733014/245524733014_front_1763808955.181779.jpg"

if not os.path.exists(photo_path):
    print(f"Photo not found: {photo_path}")
    exit(1)

print(f"Testing recognition with: {photo_path}")
print(f"File size: {os.path.getsize(photo_path)} bytes")

# Send to recognition endpoint
url = "http://localhost:8000/api/camera/recognize"

with open(photo_path, 'rb') as f:
    files = {'file': ('frame.jpg', f, 'image/jpeg')}
    
    print("\nSending request to backend...")
    response = requests.post(url, files=files)
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
