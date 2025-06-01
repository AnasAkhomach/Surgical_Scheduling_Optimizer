#!/usr/bin/env python3
"""
Simple diagnostic script to test the /api/current endpoint.
This version avoids complex database operations that might cause hanging.
"""

import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_DATE = "2023-10-27"

def get_auth_token():
    """Get authentication token for API requests."""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }

        print(f"🔐 Attempting login to {BASE_URL}/auth/token")
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data, timeout=10)

        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful")
            return token_data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_current_endpoint():
    """Test the /api/current endpoint."""
    print("\n" + "="*50)
    print("🔍 TESTING /api/current ENDPOINT")
    print("="*50)

    # Get token
    token = get_auth_token()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Test the endpoint
    test_url = f"{BASE_URL}/current"
    print(f"\n🌐 Testing URL: {test_url}")

    try:
        response = requests.get(test_url, headers=headers, timeout=10)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'Not specified')}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📦 Response Type: {type(data).__name__}")

                if isinstance(data, list):
                    print(f"📋 Array Length: {len(data)}")
                    print(f"🚨 ISSUE DETECTED: Response is an array, not an object!")
                    print(f"📄 Expected: Object with 'surgeries' property")
                    print(f"📄 Actual: {data}")
                elif isinstance(data, dict):
                    print(f"📋 Object Keys: {list(data.keys())}")
                    if 'surgeries' in data:
                        print(f"✅ 'surgeries' key found")
                        print(f"📋 Surgeries Count: {len(data['surgeries'])}")
                    else:
                        print(f"🚨 ISSUE: 'surgeries' key missing from response object")

                print(f"\n📄 Full Response:")
                print(json.dumps(data, indent=2, default=str))

            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print(f"📄 Raw Response: {response.text}")
        else:
            print(f"❌ Error Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")

    print("\n" + "="*50)
    print("🏁 TEST COMPLETE")
    print("="*50)

if __name__ == "__main__":
    print("🔧 SIMPLE ENDPOINT TEST")
    print(f"🕒 Timestamp: {datetime.now()}")
    test_current_endpoint()