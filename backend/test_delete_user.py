"""
Test deleting a user through the API
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

# Get all users first
print("\n2. Getting all users...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    users = response.json()["data"]
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"  - {user['name']} ({user['email']}) - ID: {user.get('_id', 'N/A')}")
    
    # Try to delete a user (not admin)
    if len(users) > 1:
        user_to_delete = None
        for user in users:
            if user['email'] != 'admin@school.com':
                user_to_delete = user
                break
        
        if user_to_delete:
            user_id = user_to_delete.get('_id')
            print(f"\n3. Attempting to delete user: {user_to_delete['name']} (ID: {user_id})")
            
            delete_response = requests.delete(
                f"{BASE_URL}/auth/users/{user_id}",
                headers=headers
            )
            
            print(f"Status: {delete_response.status_code}")
            print(f"Response: {delete_response.text}")
            
            if delete_response.status_code == 200:
                print("✅ User deleted successfully!")
            else:
                print("❌ Failed to delete user")
        else:
            print("\n⚠️ No non-admin users to delete")
    else:
        print("\n⚠️ Only admin user exists")
else:
    print(f"❌ Failed to get users: {response.text}")
