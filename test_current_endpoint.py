#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from api.auth import create_access_token
from datetime import timedelta
import asyncio

# Import the app
from api.main import app

def test_current_endpoint():
    client = TestClient(app)

    # Generate a fresh token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": "user123", "role": "user"},
        expires_delta=access_token_expires
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = client.get("/api/current?date=2023-10-27", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code != 200:
            print(f"Error details: {response.json() if response.text else 'No response body'}")
    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_current_endpoint()
