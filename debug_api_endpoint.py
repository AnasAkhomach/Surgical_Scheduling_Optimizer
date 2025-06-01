#!/usr/bin/env python3
"""
Debug script to test the /api/current endpoint and identify the data structure mismatch.
"""

import requests
import json
from datetime import date

BASE_URL = 'http://localhost:5000/api'

def test_current_endpoint():
    """Test the current endpoint and analyze the response structure."""

    # Step 1: Login
    print("Step 1: Attempting login...")
    login_data = {'username': 'admin', 'password': 'admin123'}

    try:
        login_response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        print(f"Login status: {login_response.status_code}")

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return

        token_data = login_response.json()
        token = token_data.get('access_token')
        print(f"Login successful, token received: {token[:20]}...")

    except Exception as e:
        print(f"Login error: {e}")
        return

    # Step 2: Test current endpoint
    print("\nStep 2: Testing /api/current endpoint...")
    headers = {'Authorization': f'Bearer {token}'}

    try:
        # Test without date parameter
        current_response = requests.get(f'{BASE_URL}/current', headers=headers)
        print(f"Current endpoint status: {current_response.status_code}")

        if current_response.status_code == 200:
            response_data = current_response.json()
            print(f"Response type: {type(response_data)}")
            print(f"Response content: {json.dumps(response_data, indent=2, default=str)}")

            # Analyze structure
            if isinstance(response_data, list):
                print("\n❌ ISSUE FOUND: Response is a list, but frontend expects an object!")
                print(f"List length: {len(response_data)}")
            elif isinstance(response_data, dict):
                print("\n✅ Response is an object (correct)")
                if 'surgeries' in response_data:
                    print(f"✅ 'surgeries' key found with {len(response_data['surgeries'])} items")
                else:
                    print("❌ 'surgeries' key missing from response")
        else:
            print(f"Error response: {current_response.text}")

    except Exception as e:
        print(f"Current endpoint error: {e}")

    # Step 3: Test with date parameter
    print("\nStep 3: Testing with date parameter...")
    test_date = '2023-10-27'

    try:
        date_response = requests.get(f'{BASE_URL}/current?date={test_date}', headers=headers)
        print(f"Date filtered status: {date_response.status_code}")

        if date_response.status_code == 200:
            date_data = date_response.json()
            print(f"Date response type: {type(date_data)}")
            print(f"Date response content: {json.dumps(date_data, indent=2, default=str)}")
        else:
            print(f"Date error response: {date_response.text}")

    except Exception as e:
        print(f"Date endpoint error: {e}")

if __name__ == '__main__':
    test_current_endpoint()