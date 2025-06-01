#!/usr/bin/env python3
"""
Test script for enhanced registration functionality
"""
import requests
import json
from urllib.parse import urlencode
import random
import string

def generate_test_user():
    """Generate a unique test user"""
    suffix = ''.join(random.choices(string.digits, k=4))
    return {
        'username': f'testuser{suffix}',
        'email': f'testuser{suffix}@example.com',
        'password': 'TestPass123!',
        'full_name': f'Test User {suffix}'
    }

def test_enhanced_registration():
    """Test the enhanced registration endpoint with full data"""
    print('Testing enhanced registration endpoint...')
    user_data = generate_test_user()

    try:
        response = requests.post('http://localhost:5001/api/auth/register',
                               json=user_data)
        print(f'Registration status: {response.status_code}')
        if response.status_code == 201:
            print('✅ Registration successful!')
            created_user = response.json()
            print(f'Created user: {created_user["username"]} ({created_user["email"]})')
            print(f'Full name: {created_user.get("full_name", "Not provided")}')
            print(f'Role: {created_user["role"]}')
            print(f'Active: {created_user["is_active"]}')
            return user_data
        else:
            print(f'❌ Registration failed: {response.text}')
            return None
    except Exception as e:
        print(f'❌ Registration test error: {e}')
        return None

def test_login_with_new_user(user_data):
    """Test login with the newly created user"""
    print(f'\nTesting login with new user: {user_data["username"]}...')
    try:
        data = urlencode({
            'username': user_data['username'],
            'password': user_data['password']
        })
        response = requests.post('http://localhost:5001/api/auth/token',
                               data=data,
                               headers={'Content-Type': 'application/x-www-form-urlencoded'})
        print(f'Login status: {response.status_code}')
        if response.status_code == 200:
            print('✅ Login successful!')
            token_data = response.json()
            print(f'Token type: {token_data["token_type"]}')
            return token_data["access_token"]
        else:
            print(f'❌ Login failed: {response.text}')
            return None
    except Exception as e:
        print(f'❌ Login test error: {e}')
        return None

def test_user_info(token):
    """Test the /auth/me endpoint"""
    print('\nTesting /auth/me endpoint...')
    try:
        response = requests.get('http://localhost:5001/api/auth/me',
                              headers={'Authorization': f'Bearer {token}'})
        print(f'Auth/me status: {response.status_code}')
        if response.status_code == 200:
            user_info = response.json()
            print('✅ User info retrieved successfully!')
            print(f'Username: {user_info["username"]}')
            print(f'Email: {user_info["email"]}')
            print(f'Full name: {user_info.get("full_name", "Not provided")}')
            print(f'Role: {user_info["role"]}')
            print(f'Active: {user_info["is_active"]}')
            print(f'Created: {user_info.get("created_at", "Not provided")}')
            return True
        else:
            print(f'❌ Auth/me failed: {response.text}')
            return False
    except Exception as e:
        print(f'❌ Auth/me test error: {e}')
        return False

def test_validation_errors():
    """Test validation error handling"""
    print('\nTesting validation error handling...')

    # Test with invalid email
    print('Testing invalid email...')
    try:
        response = requests.post('http://localhost:5001/api/auth/register',
                               json={
                                   'username': 'testuser999',
                                   'email': 'invalid-email',
                                   'password': 'TestPass123!',
                                   'full_name': 'Test User'
                               })
        print(f'Invalid email status: {response.status_code}')
        if response.status_code == 422:
            print('✅ Validation error correctly returned for invalid email')
        else:
            print(f'❌ Expected 422, got {response.status_code}: {response.text}')
    except Exception as e:
        print(f'❌ Validation test error: {e}')

    # Test with missing required fields
    print('Testing missing required fields...')
    try:
        response = requests.post('http://localhost:5001/api/auth/register',
                               json={
                                   'username': 'testuser999'
                                   # Missing email and password
                               })
        print(f'Missing fields status: {response.status_code}')
        if response.status_code == 422:
            print('✅ Validation error correctly returned for missing fields')
        else:
            print(f'❌ Expected 422, got {response.status_code}: {response.text}')
    except Exception as e:
        print(f'❌ Missing fields test error: {e}')

def test_duplicate_user():
    """Test duplicate user handling"""
    print('\nTesting duplicate user handling...')
    user_data = generate_test_user()

    # Create user first time
    try:
        response1 = requests.post('http://localhost:5001/api/auth/register',
                                json=user_data)
        if response1.status_code == 201:
            print('✅ First user creation successful')

            # Try to create same user again
            response2 = requests.post('http://localhost:5001/api/auth/register',
                                    json=user_data)
            print(f'Duplicate user status: {response2.status_code}')
            if response2.status_code == 400:
                print('✅ Duplicate user correctly rejected')
                error_data = response2.json()
                print(f'Error message: {error_data.get("detail", "No detail")}')
            else:
                print(f'❌ Expected 400, got {response2.status_code}: {response2.text}')
        else:
            print(f'❌ First user creation failed: {response1.text}')
    except Exception as e:
        print(f'❌ Duplicate user test error: {e}')

def main():
    """Run all enhanced registration tests"""
    print("=== Enhanced Registration Tests ===\n")

    # Test 1: Enhanced registration
    user_data = test_enhanced_registration()

    if user_data:
        # Test 2: Login with new user
        token = test_login_with_new_user(user_data)

        if token:
            # Test 3: Get user info
            test_user_info(token)

    # Test 4: Validation errors
    test_validation_errors()

    # Test 5: Duplicate user handling
    test_duplicate_user()

    print("\n=== Enhanced Registration Tests Complete ===")

if __name__ == "__main__":
    main()
