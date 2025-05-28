#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""
import requests
import json
from urllib.parse import urlencode

def test_registration():
    """Test the registration endpoint"""
    print('Testing registration endpoint...')
    try:
        response = requests.post('http://localhost:8000/api/auth/register',
                               json={
                                   'username': 'testuser456',
                                   'email': 'testuser456@example.com',
                                   'password': 'testpass123',
                                   'full_name': 'Test User'
                               })
        print(f'Registration status: {response.status_code}')
        if response.status_code == 201:
            print('Registration successful!')
            user_data = response.json()
            print(f'Created user: {user_data["username"]}')
            return True
        else:
            print(f'Registration failed: {response.text}')
            return False
    except Exception as e:
        print(f'Registration test error: {e}')
        return False

def test_login():
    """Test login with the new user"""
    print('\nTesting login with new user...')
    try:
        data = urlencode({'username': 'testuser456', 'password': 'testpass123'})
        response = requests.post('http://localhost:8000/api/auth/token',
                               data=data,
                               headers={'Content-Type': 'application/x-www-form-urlencoded'})
        print(f'Login status: {response.status_code}')
        if response.status_code == 200:
            print('Login successful!')
            token_data = response.json()
            print(f'Token type: {token_data["token_type"]}')
            return token_data["access_token"]
        else:
            print(f'Login failed: {response.text}')
            return None
    except Exception as e:
        print(f'Login test error: {e}')
        return None

def test_auth_me(token):
    """Test the /auth/me endpoint"""
    print('\nTesting /auth/me endpoint...')
    try:
        me_response = requests.get('http://localhost:8000/api/auth/me',
                                 headers={'Authorization': f'Bearer {token}'})
        print(f'Auth/me status: {me_response.status_code}')
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f'Current user: {user_info["username"]} ({user_info["role"]})')
            return True
        else:
            print(f'Auth/me failed: {me_response.text}')
            return False
    except Exception as e:
        print(f'Auth/me test error: {e}')
        return False

def main():
    """Run all tests"""
    print("=== Authentication Endpoint Tests ===\n")

    # Test registration
    reg_success = test_registration()

    if reg_success:
        # Test login
        token = test_login()

        if token:
            # Test auth/me
            test_auth_me(token)

    print("\n=== Tests Complete ===")

if __name__ == "__main__":
    main()
