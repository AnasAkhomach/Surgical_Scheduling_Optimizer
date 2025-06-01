#!/usr/bin/env python3
import requests
import sys

def verify_endpoint_fix():
    """Verify that the frontend endpoint fix resolves the authentication issue"""
    base_url = "http://localhost:5000"

    print("Verifying Frontend Endpoint Fix")
    print("=" * 35)

    try:
        # Step 1: Get authentication token
        print("\n1. Authenticating...")
        auth_data = {"username": "admin", "password": "admin123"}
        auth_response = requests.post(f"{base_url}/api/auth/token", data=auth_data)

        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return False

        token = auth_response.json().get("access_token")
        print("✅ Authentication successful")

        # Step 2: Test the corrected endpoint with date parameter (like frontend)
        print("\n2. Testing /api/current?date=2023-10-27...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/api/current?date=2023-10-27", headers=headers)

        if response.status_code == 200:
            print("✅ SUCCESS: Frontend endpoint fix working correctly!")
            print(f"   Status: {response.status_code}")
            data = response.json()
            if isinstance(data, dict):
                print(f"   Response contains: {len(data)} keys")
            return True
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text[:100]}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_endpoint_fix()
    print("\n" + "=" * 35)
    if success:
        print("🎉 ENDPOINT FIX VERIFIED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ ENDPOINT FIX VERIFICATION FAILED")
        sys.exit(1)