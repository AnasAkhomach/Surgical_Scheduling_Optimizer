#!/usr/bin/env python3
import jwt
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get the SECRET_KEY from environment
secret_key = os.getenv('SECRET_KEY', 'your-secret-key-for-development-only')
print(f"Using SECRET_KEY: {secret_key}")

# The token from the failed request
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwicm9sZSI6InVzZXIiLCJleHAiOjE3NDg3NzgyMTF9.ZyBkJYDUtf-N5KEOPbjs9s4U4ed_3rVEsuneYUWndIg"

print("\n=== Analyzing the failing token ===")
print(f"Token: {token[:50]}...")

try:
    # Try to decode without verification first to see the payload
    payload = jwt.decode(token, options={"verify_signature": False})
    print(f"\nToken payload (unverified): {payload}")

    # Check expiration
    exp_timestamp = payload.get('exp')
    if exp_timestamp:
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        current_datetime = datetime.now()
        print(f"Token expires at: {exp_datetime}")
        print(f"Current time: {current_datetime}")
        print(f"Token expired: {current_datetime > exp_datetime}")

    # Try to decode with the current SECRET_KEY
    try:
        verified_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        print(f"\nToken successfully verified with current SECRET_KEY!")
        print(f"Verified payload: {verified_payload}")
    except jwt.ExpiredSignatureError:
        print(f"\nToken is EXPIRED but signature is valid with current SECRET_KEY")
    except jwt.InvalidSignatureError:
        print(f"\nToken signature is INVALID with current SECRET_KEY")

        # Try with the old default key
        try:
            old_payload = jwt.decode(token, "your-secret-key-for-development-only", algorithms=["HS256"])
            print(f"Token is valid with old default SECRET_KEY!")
        except jwt.ExpiredSignatureError:
            print(f"Token is EXPIRED but signature is valid with old default SECRET_KEY")
        except jwt.InvalidSignatureError:
            print(f"Token signature is also invalid with old default SECRET_KEY")
    except Exception as e:
        print(f"\nOther error verifying token: {e}")

except Exception as e:
    print(f"Error decoding token: {e}")

print("\n=== Testing fresh authentication ===")
import requests

try:
    # Test fresh login using correct endpoint and form data
    auth_data = {
        'username': 'user123',
        'password': 'password123'
    }
    auth_response = requests.post('http://localhost:5000/api/auth/token', data=auth_data)

    if auth_response.status_code == 200:
        fresh_token = auth_response.json()['access_token']
        print(f"\nFresh token obtained: {fresh_token[:50]}...")

        # Test with fresh token
        headers = {'Authorization': f'Bearer {fresh_token}'}
        current_response = requests.get('http://localhost:5000/api/current?date=2023-10-27', headers=headers)
        print(f"Fresh token test result: {current_response.status_code}")

        if current_response.status_code == 200:
            print("SUCCESS: Fresh token works!")
        else:
            print(f"FAILED: Fresh token also fails: {current_response.text}")
    else:
        print(f"Authentication failed: {auth_response.status_code} - {auth_response.text}")

except Exception as e:
    print(f"Error testing fresh authentication: {e}")