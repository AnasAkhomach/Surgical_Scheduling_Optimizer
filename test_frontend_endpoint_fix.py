#!/usr/bin/env python3
import requests
import json

def test_frontend_endpoint_fix():
    """Test that the frontend endpoint fix works correctly"""
    base_url = "http://localhost:5000"

    print("Testing Frontend Endpoint Fix")
    print("=" * 40)

    # Step 1: Test authentication
    print("\n1. Testing authentication...")
    auth_data = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        auth_response = requests.post(f"{base_url}/api/auth/token", data=auth_data)
        print(f"Auth Status: {auth_response.status_code}")

        if auth_response.status_code == 200:
            token_data = auth_response.json()
            access_token = token_data.get("access_token")
            print(f"Token obtained: {access_token[:20]}...")

            # Step 2: Test the corrected endpoint
            print("\n2. Testing corrected /api/current endpoint...")
            headers = {"Authorization": f"Bearer {access_token}"}

            # Test without date parameter
            current_response = requests.get(f"{base_url}/api/current", headers=headers)
            print(f"GET /api/current Status: {current_response.status_code}")

            if current_response.status_code == 200:
                print("✅ SUCCESS: /api/current endpoint working correctly")
                data = current_response.json()
                print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            else:
                print(f"❌ FAILED: {current_response.status_code} - {current_response.text}")

            # Test with date parameter (like frontend does)
            print("\n3. Testing /api/current with date parameter...")
            date_response = requests.get(f"{base_url}/api/current?date=2023-10-27", headers=headers)
            print(f"GET /api/current?date=2023-10-27 Status: {date_response.status_code}")

            if date_response.status_code == 200:
                print("✅ SUCCESS: /api/current with date parameter working correctly")
                data = date_response.json()
                print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            else:
                print(f"❌ FAILED: {date_response.status_code} - {date_response.text}")

        else:
            print(f"❌ Authentication failed: {auth_response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API server. Is it running on port 5000?")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    print("\n" + "=" * 40)
    print("Test completed")

if __name__ == "__main__":
    test_frontend_endpoint_fix()