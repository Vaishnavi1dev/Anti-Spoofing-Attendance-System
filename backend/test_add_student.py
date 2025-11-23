"""
Test adding a student through the API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Login first
print("1. Logging in...")
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "admin@school.com",
    "password": "admin123"
})

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Logged in successfully")

# Try to add a student
print("\n2. Adding student...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

student_data = {
    "student_id": "ST2024001",
    "name": "Test Student",
    "email": "test.student@school.com",
    "phone": "+1234567890"
}

response = requests.post(f"{BASE_URL}/students", json=student_data, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("✅ Student added successfully!")
else:
    print("❌ Failed to add student")
    try:
        error = response.json()
        print(f"Error details: {json.dumps(error, indent=2)}")
    except:
        pass
