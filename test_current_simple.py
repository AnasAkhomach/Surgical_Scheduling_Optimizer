#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def test_current_endpoint():
    base_url = "http://localhost:8000"

    # Test authentication first
    auth_data = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        # Get authentication token
        print("Getting authentication token...")
        auth_response = requests.post(f"{base_url}/api/auth/login", json=auth_data)
        print(f"Auth response status: {auth_response.status_code}")

        if auth_response.status_code != 200:
            print(f"Authentication failed: {auth_response.text}")
            return

        token = auth_response.json().get("access_token")
        if not token:
            print("No access token received")
            return

        print(f"Token received: {token[:20]}...")

        # Test current endpoint
        headers = {"Authorization": f"Bearer {token}"}

        print("\nTesting /api/current endpoint...")
        current_response = requests.get(f"{base_url}/api/current", headers=headers)
        print(f"Current endpoint status: {current_response.status_code}")
        print(f"Response headers: {dict(current_response.headers)}")

        if current_response.status_code == 200:
            data = current_response.json()
            print(f"Response data type: {type(data)}")
            print(f"Response data: {json.dumps(data, indent=2, default=str)}")

            if isinstance(data, dict):
                print(f"Keys in response: {list(data.keys())}")
                if 'surgeries' in data:
                    print(f"Number of surgeries: {len(data['surgeries'])}")

        else:
            print(f"Error response: {current_response.text}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the API server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_current_endpoint()