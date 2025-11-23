"""
Test API endpoints directly
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# First, login to get token
print("1. Testing login...")
login_data = {
    "email": "admin@school.com",
    "password": "admin123"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print(f"   ✓ Login successful! Token: {token[:20]}...")
        
        # Test creating a student
        print("\n2. Testing student creation...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        student_data = {
            "student_id": "ST001",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890"
        }
        
        response = requests.post(f"{BASE_URL}/students", json=student_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✓ Student created successfully!")
        else:
            print(f"   ✗ Failed to create student")
            
    else:
        print(f"   ✗ Login failed: {response.text}")
        print("\n   Make sure you've created an admin user:")
        print("   python backend/create_admin.py")
        
except requests.exceptions.ConnectionError:
    print("   ✗ Cannot connect to backend!")
    print("   Make sure backend is running: python backend/main.py")
except Exception as e:
    print(f"   ✗ Error: {e}")
