#!/usr/bin/env python3
"""
Debug script to test authentication and /current endpoint
"""
import requests
import json
from datetime import datetime

def test_current_endpoint_auth():
    base_url = "http://localhost:5000"

    print("🔍 Testing /current endpoint authentication...")

    # Test 1: Check if we can access the endpoint without auth
    print("\n1. Testing without authentication...")
    try:
        response = requests.get(f"{base_url}/api/current")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Try to authenticate
    print("\n2. Testing authentication...")
    auth_data = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        # Try OAuth2 form format first
        print("Trying OAuth2 form authentication...")
        form_data = {
            "username": "admin",
            "password": "admin123",
            "grant_type": "password"
        }

        auth_response = requests.post(
            f"{base_url}/api/auth/token",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Auth status: {auth_response.status_code}")
        print(f"Auth response: {auth_response.text}")

        if auth_response.status_code == 200:
            token_data = auth_response.json()
            token = token_data.get("access_token")

            if token:
                print(f"✅ Token received: {token[:20]}...")

                # Test 3: Use token to access /current endpoint
                print("\n3. Testing /current with valid token...")
                headers = {"Authorization": f"Bearer {token}"}

                current_response = requests.get(f"{base_url}/api/current", headers=headers)
                print(f"Current endpoint status: {current_response.status_code}")

                if current_response.status_code == 200:
                    data = current_response.json()
                    print(f"✅ Success! Response: {json.dumps(data, indent=2, default=str)[:500]}...")
                else:
                    print(f"❌ Failed: {current_response.text}")
            else:
                print("❌ No access token in response")
        else:
            print(f"❌ Authentication failed: {auth_response.text}")

    except Exception as e:
        print(f"❌ Error during authentication: {e}")

    # Test 4: Check if user exists
    print("\n4. Testing user existence...")
    try:
        # Try to get user info (this might not be available, but worth trying)
        response = requests.get(f"{base_url}/api/users")
        print(f"Users endpoint status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"Available users: {len(users) if isinstance(users, list) else 'Unknown'}")
    except Exception as e:
        print(f"Error checking users: {e}")

if __name__ == "__main__":
    test_current_endpoint_auth()