"""
Test adding a teacher through the API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Login as admin
print("1. Logging in as admin...")
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "admin@school.com",
    "password": "admin123"
})

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Logged in successfully")

# Try to add a teacher
print("\n2. Adding teacher...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

teacher_data = {
    "email": "teacher.test@school.com",
    "password": "teacher123",
    "name": "Test Teacher",
    "role": "teacher"
}

response = requests.post(f"{BASE_URL}/auth/register", json=teacher_data, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("✅ Teacher added successfully!")
else:
    print("❌ Failed to add teacher")
    try:
        error = response.json()
        print(f"Error details: {json.dumps(error, indent=2)}")
    except:
        pass
