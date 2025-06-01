#!/usr/bin/env python3
"""
Test script to verify the exact endpoint paths and authentication
"""
import requests
import json

def test_endpoint_paths():
    base_url = "http://localhost:5000"

    print("🔍 Testing endpoint paths and authentication...")

    # First, get a valid token
    print("\n1. Getting authentication token...")
    form_data = {
        "username": "admin",
        "password": "admin123",
        "grant_type": "password"
    }

    try:
        auth_response = requests.post(
            f"{base_url}/api/auth/token",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if auth_response.status_code == 200:
            token = auth_response.json().get("access_token")
            print(f"✅ Token obtained: {token[:20]}...")

            headers = {"Authorization": f"Bearer {token}"}

            # Test different endpoint paths
            endpoints_to_test = [
                "/api/current",
                "/api/current?date=2023-10-27",
                "/api/schedules/current",
                "/api/schedules/current?date=2023-10-27",
                "/current",
                "/current?date=2023-10-27"
            ]

            print("\n2. Testing different endpoint paths...")
            for endpoint in endpoints_to_test:
                try:
                    url = f"{base_url}{endpoint}"
                    print(f"\nTesting: {url}")

                    response = requests.get(url, headers=headers)
                    print(f"Status: {response.status_code}")

                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Success! Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        if isinstance(data, dict) and 'surgeries' in data:
                            print(f"   Surgeries count: {len(data['surgeries'])}")
                    elif response.status_code == 401:
                        print("❌ 401 Unauthorized - Token issue")
                    elif response.status_code == 404:
                        print("❌ 404 Not Found - Endpoint doesn't exist")
                    else:
                        print(f"❌ {response.status_code}: {response.text[:200]}")

                except Exception as e:
                    print(f"❌ Error: {e}")

        else:
            print(f"❌ Authentication failed: {auth_response.status_code} - {auth_response.text}")

    except Exception as e:
        print(f"❌ Error during authentication: {e}")

    # Test CORS preflight
    print("\n3. Testing CORS preflight...")
    try:
        options_response = requests.options(f"{base_url}/api/current")
        print(f"OPTIONS /api/current: {options_response.status_code}")
        print(f"CORS headers: {dict(options_response.headers)}")
    except Exception as e:
        print(f"❌ CORS test error: {e}")

if __name__ == "__main__":
    test_endpoint_paths()