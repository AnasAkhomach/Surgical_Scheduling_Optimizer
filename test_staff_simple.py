#!/usr/bin/env python3
"""
Simple test script to verify staff endpoint connectivity
"""

import requests
import json
from urllib.parse import urlencode

def test_staff_endpoint():
    base_url = "http://localhost:5000"

    try:
        # Step 1: Login to get token
        print("🔑 Attempting to login...")
        login_data = urlencode({'username': 'admin', 'password': 'admin123'})

        login_response = requests.post(
            f"{base_url}/api/auth/token",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        print(f"Login response status: {login_response.status_code}")

        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access_token')
            print(f"✅ Login successful! Token: {access_token[:20]}...")

            # Step 2: Test staff endpoint
            print("\n👥 Testing staff endpoint...")
            staff_response = requests.get(
                f"{base_url}/api/staff",
                headers={'Authorization': f'Bearer {access_token}'}
            )

            print(f"Staff endpoint status: {staff_response.status_code}")

            if staff_response.status_code == 200:
                staff_data = staff_response.json()
                print(f"✅ Staff endpoint working! Found {len(staff_data)} staff members")
                return True
            else:
                print(f"❌ Staff endpoint failed: {staff_response.text}")
                return False

        else:
            print(f"❌ Login failed: {login_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection error - API server may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=== STAFF ENDPOINT TEST ===")
    success = test_staff_endpoint()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")