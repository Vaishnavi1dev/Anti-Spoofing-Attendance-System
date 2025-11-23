"""
Test user registration endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# First, login as admin to get token
print("1. Logging in as admin...")
login_data = {
    "email": "admin@school.com",
    "password": "admin123"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print(f"   ✓ Login successful!")
        
        # Test registering a new user
        print("\n2. Testing user registration...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        user_data = {
            "email": "vishumamidala@gmail.com",
            "password": "test123",
            "name": "sahithi",
            "role": "student"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✓ User registered successfully!")
        else:
            print(f"   ✗ Failed to register user")
            try:
                error_detail = response.json()
                print(f"   Error details: {json.dumps(error_detail, indent=2)}")
            except:
                pass
            
    else:
        print(f"   ✗ Login failed: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("   ✗ Cannot connect to backend!")
except Exception as e:
    print(f"   ✗ Error: {e}")
