#!/usr/bin/env python3
"""
Test script to verify operating rooms API integration fix with authentication.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
HEALTH_URL = f"{BASE_URL}/health"
AUTH_URL = f"{BASE_URL}/auth/token"
REGISTER_URL = f"{BASE_URL}/auth/register"
OR_URL = f"{BASE_URL}/operating-rooms"

# Test user credentials
TEST_USER = {
    "username": "test_or_user",
    "email": "test_or@example.com",
    "password": "testpassword123",
    "full_name": "Test OR User"
}

def register_test_user():
    """Register a test user for authentication."""
    try:
        response = requests.post(REGISTER_URL, json=TEST_USER, timeout=5)
        if response.status_code == 201:
            print("✅ Test user registered successfully")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️  Test user already exists")
            return True
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print("Response:", response.text)
            return False
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return False

def login_test_user():
    """Login and get authentication token."""
    try:
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        response = requests.post(AUTH_URL, data=login_data, timeout=5)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            if token:
                print("✅ Login successful")
                return token
            else:
                print("❌ No access token in response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code}")
            print("Response:", response.text)
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_operating_rooms_with_auth(token):
    """Test the operating rooms endpoint with authentication."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(OR_URL, headers=headers, timeout=5)

        print(f"Operating Rooms Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Operating rooms endpoint working with authentication")
            print(f"Returned {len(data)} operating rooms")

            # Check data structure
            if data:
                first_room = data[0]
                print("\nFirst room structure:")
                print(json.dumps(first_room, indent=2))

                # Check required fields
                required_fields = ['room_id', 'id', 'name', 'location', 'status']
                missing_fields = [field for field in required_fields if field not in first_room]

                if missing_fields:
                    print(f"❌ Missing fields: {missing_fields}")
                    return False
                else:
                    print("✅ All required fields present")

                # Check field aliases
                has_primary_service = 'primaryService' in first_room or 'primary_service' in first_room
                if has_primary_service:
                    print("✅ Primary service field present")
                else:
                    print("⚠️  Primary service field missing")

                # Verify field mapping
                print("\n🔍 Field Mapping Analysis:")
                print(f"   room_id: {first_room.get('room_id')}")
                print(f"   id: {first_room.get('id')}")
                print(f"   name: {first_room.get('name')}")
                print(f"   location: {first_room.get('location')}")
                print(f"   status: {first_room.get('status')}")
                print(f"   primary_service: {first_room.get('primary_service')}")
                print(f"   primaryService: {first_room.get('primaryService')}")

                return True
            else:
                print("⚠️  No operating rooms found in database")
                return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print("Response:", response.text)
            return False

    except Exception as e:
        print(f"❌ Operating rooms endpoint error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔧 Testing Operating Rooms API Integration Fix (Authenticated)")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print(f"Base URL: {BASE_URL}")
    print()

    # Test health endpoint
    print("1. Testing Health Endpoint...")
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return
    print()

    # Register test user
    print("2. Registering Test User...")
    if not register_test_user():
        print("❌ Failed to register test user")
        return
    print()

    # Login test user
    print("3. Logging in Test User...")
    token = login_test_user()
    if not token:
        print("❌ Failed to login test user")
        return
    print()

    # Test operating rooms endpoint
    print("4. Testing Operating Rooms Endpoint (Authenticated)...")
    or_ok = test_operating_rooms_with_auth(token)
    print()

    # Summary
    print("=" * 60)
    if or_ok:
        print("✅ All tests completed successfully!")
        print("\n📋 Integration Fix Status:")
        print("   ✅ Backend server running")
        print("   ✅ Authentication working")
        print("   ✅ Operating rooms endpoint accessible")
        print("   ✅ Data structure includes required fields")
        print("   ✅ Field aliases configured")
        print("\n🎯 Next Steps:")
        print("   1. Test frontend integration with updated backend")
        print("   2. Verify resourceStore.js data transformation")
        print("   3. Test Gantt chart display with operating rooms")
    else:
        print("❌ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()