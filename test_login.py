#!/usr/bin/env python3
import requests
import json

def test_login():
    """Test login and get a fresh token"""
    try:
        # Test login
        login_data = {
            'username': 'user',
            'password': 'user123'
        }

        response = requests.post(
            'http://localhost:5000/api/auth/token',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        print(f'Login Status: {response.status_code}')
        print(f'Login Response: {response.text}')

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print(f'\nAccess Token: {access_token}')

            # Test the /api/current endpoint with the new token
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            current_response = requests.get(
                'http://localhost:5000/api/current?date=2023-10-27',
                headers=headers
            )

            print(f'\nCurrent endpoint Status: {current_response.status_code}')
            print(f'Current endpoint Response: {current_response.text}')

        return response.status_code == 200

    except Exception as e:
        print(f'Error: {e}')
        return False

if __name__ == '__main__':
    test_login()