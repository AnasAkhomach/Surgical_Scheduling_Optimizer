#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def test_authentication_fix():
    """Test if the SECRET_KEY fix resolved the authentication issue"""
    print("Authentication Fix Verification")
    print("=" * 35)

    base_url = "http://localhost:5000"

    try:
        # Step 1: Authenticate and get a fresh token
        print("\n1. Getting fresh authentication token...")
        auth_data = {
            "username": "admin",
            "password": "admin123"
        }

        auth_response = requests.post(f"{base_url}/api/auth/token", data=auth_data)
        print(f"Auth Status: {auth_response.status_code}")

        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.text}")
            return False

        token_data = auth_response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Fresh token obtained: {access_token[:30]}...")

        # Step 2: Test /api/current endpoint immediately
        print("\n2. Testing /api/current endpoint with fresh token...")
        headers = {"Authorization": f"Bearer {access_token}"}

        current_response = requests.get(f"{base_url}/api/current", headers=headers)
        print(f"Current endpoint status: {current_response.status_code}")

        if current_response.status_code == 200:
            print("✅ SUCCESS: /api/current working correctly!")
            data = current_response.json()
            print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        elif current_response.status_code == 401:
            print("❌ STILL FAILING: 401 Unauthorized")
            print(f"Response: {current_response.text}")
            return False
        else:
            print(f"❌ Unexpected status: {current_response.status_code}")
            print(f"Response: {current_response.text}")
            return False

        # Step 3: Test with date parameter (the original failing request)
        print("\n3. Testing /api/current with date parameter...")
        date_response = requests.get(f"{base_url}/api/current?date=2023-10-27", headers=headers)
        print(f"Date endpoint status: {date_response.status_code}")

        if date_response.status_code == 200:
            print("✅ SUCCESS: /api/current with date working correctly!")
            print("🎉 AUTHENTICATION ISSUE RESOLVED!")
            return True
        elif date_response.status_code == 401:
            print("❌ STILL FAILING: 401 Unauthorized with date parameter")
            print(f"Response: {date_response.text}")
            return False
        else:
            print(f"❌ Unexpected status: {date_response.status_code}")
            print(f"Response: {date_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_authentication_fix()
    print("\n" + "=" * 35)
    if success:
        print("🎉 AUTHENTICATION FIX VERIFIED!")
        print("The frontend should now work correctly.")
    else:
        print("❌ AUTHENTICATION ISSUE PERSISTS")
        print("Further investigation needed.")