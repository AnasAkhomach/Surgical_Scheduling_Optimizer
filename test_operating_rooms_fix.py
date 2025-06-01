#!/usr/bin/env python3
"""
Test script to verify operating rooms API integration fix.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
HEALTH_URL = f"{BASE_URL}/health"
OR_URL = f"{BASE_URL}/operating-rooms"

def test_health_endpoint():
    """Test if the API server is running."""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_operating_rooms_endpoint():
    """Test the operating rooms endpoint without authentication."""
    try:
        response = requests.get(OR_URL, timeout=5)
        print(f"Operating Rooms Response Status: {response.status_code}")

        if response.status_code == 401:
            print("⚠️  Authentication required - this is expected")
            print("Response:", response.text)
            return True
        elif response.status_code == 200:
            data = response.json()
            print("✅ Operating rooms endpoint working")
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
                else:
                    print("✅ All required fields present")

                # Check field aliases
                if 'primaryService' in first_room or 'primary_service' in first_room:
                    print("✅ Primary service field present")
                else:
                    print("⚠️  Primary service field missing")

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
    print("🔧 Testing Operating Rooms API Integration Fix")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print(f"Base URL: {BASE_URL}")
    print()

    # Test health endpoint
    print("1. Testing Health Endpoint...")
    health_ok = test_health_endpoint()
    print()

    if not health_ok:
        print("❌ Server not running. Please start the backend server first.")
        return

    # Test operating rooms endpoint
    print("2. Testing Operating Rooms Endpoint...")
    or_ok = test_operating_rooms_endpoint()
    print()

    # Summary
    print("=" * 50)
    if health_ok and or_ok:
        print("✅ All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Test with proper authentication")
        print("   2. Verify frontend integration")
        print("   3. Check data transformation in resourceStore.js")
    else:
        print("❌ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()