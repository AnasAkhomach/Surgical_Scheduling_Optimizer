#!/usr/bin/env python3
"""
Simple test to verify operating rooms API fix.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
REGISTER_URL = f"{BASE_URL}/auth/register"
AUTH_URL = f"{BASE_URL}/auth/token"
OR_URL = f"{BASE_URL}/operating-rooms"

# Test user credentials
TEST_USER = {
    "username": "test_simple_user",
    "email": "test_simple@example.com",
    "password": "testpassword123",
    "full_name": "Test Simple User"
}

def main():
    print("🔧 Simple Operating Rooms API Test")
    print("=" * 50)

    try:
        # Register user (ignore if already exists)
        print("1. Registering user...")
        register_response = requests.post(REGISTER_URL, json=TEST_USER, timeout=5)
        if register_response.status_code in [201, 400]:
            print("✅ User registration OK")
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            return

        # Login
        print("2. Logging in...")
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        auth_response = requests.post(AUTH_URL, data=login_data, timeout=5)
        if auth_response.status_code == 200:
            token = auth_response.json().get("access_token")
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {auth_response.status_code}")
            return

        # Test operating rooms endpoint
        print("3. Testing operating rooms endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        or_response = requests.get(OR_URL, headers=headers, timeout=5)

        print(f"Status Code: {or_response.status_code}")

        if or_response.status_code == 200:
            data = or_response.json()
            print(f"✅ Success! Retrieved {len(data)} operating rooms")

            if data:
                print("\nFirst operating room data:")
                first_room = data[0]
                print(json.dumps(first_room, indent=2))

                # Check required fields
                required_fields = ['room_id', 'id', 'name', 'location', 'status']
                missing_fields = [field for field in required_fields if field not in first_room]

                if missing_fields:
                    print(f"❌ Missing fields: {missing_fields}")
                else:
                    print("✅ All required fields present")

                # Check field values
                print("\n🔍 Field Analysis:")
                print(f"   room_id: {first_room.get('room_id')}")
                print(f"   id: {first_room.get('id')}")
                print(f"   name: {first_room.get('name')}")
                print(f"   location: {first_room.get('location')}")
                print(f"   status: {first_room.get('status')}")
                print(f"   primary_service: {first_room.get('primary_service')}")
                print(f"   primaryService: {first_room.get('primaryService')}")

                # Verify id mapping
                if first_room.get('id') == first_room.get('room_id'):
                    print("✅ ID mapping working correctly")
                else:
                    print("❌ ID mapping issue")

            else:
                print("ℹ️  No operating rooms found in database")

        else:
            print(f"❌ Request failed: {or_response.status_code}")
            print(f"Response: {or_response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()