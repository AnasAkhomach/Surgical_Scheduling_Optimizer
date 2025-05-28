import requests
import json

def test_frontend_fix():
    """Test the frontend authentication fix"""
    print("=== TESTING FRONTEND AUTHENTICATION FIX ===\n")
    
    # Test 1: Simulate the FIXED frontend FormData request
    print("1. Testing FIXED frontend FormData request...")
    try:
        # This simulates what the frontend should now send
        form_data = {
            'username': 'admin',
            'password': 'admin123',
            'grant_type': 'password'
        }

        # Send as form data (what the fixed frontend should do)
        response = requests.post('http://localhost:8000/api/auth/token',
                               data=form_data)

        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Login successful!")
            token_data = response.json()
            print(f"   Token type: {token_data.get('token_type')}")
            print(f"   Access token: {token_data.get('access_token')[:20]}...")
            return token_data.get('access_token')
        else:
            print(f"   ❌ Login failed: {response.text}")
            return None

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_registration():
    """Test registration with new user"""
    print("\n2. Testing registration with new user...")
    try:
        import random
        user_id = random.randint(1000, 9999)
        user_data = {
            'username': f'testuser{user_id}',
            'password': 'testpass123',
            'email': f'test{user_id}@example.com',
            'full_name': f'Test User {user_id}'
        }
        
        response = requests.post('http://localhost:8000/api/auth/register',
                               json=user_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ Registration successful!")
            user_response = response.json()
            print(f"   Created user: {user_response.get('username')}")
            
            # Now test login with the new user
            print("   Testing login with new user...")
            login_data = {
                'username': user_data['username'],
                'password': user_data['password'],
                'grant_type': 'password'
            }
            login_response = requests.post('http://localhost:8000/api/auth/token',
                                         data=login_data)
            if login_response.status_code == 200:
                print("   ✅ New user login successful!")
            else:
                print(f"   ❌ New user login failed: {login_response.text}")
                
        else:
            print(f"   ❌ Registration failed: {response.text}")

    except Exception as e:
        print(f"   ❌ Registration error: {e}")

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    if not token:
        print("\n3. Skipping protected endpoint test (no token)")
        return
        
    print("\n3. Testing protected endpoint access...")
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('http://localhost:8000/api/auth/me', headers=headers)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Protected endpoint access successful!")
            user_data = response.json()
            print(f"   Current user: {user_data.get('username')}")
        else:
            print(f"   ❌ Protected endpoint access failed: {response.text}")

    except Exception as e:
        print(f"   ❌ Protected endpoint error: {e}")

if __name__ == "__main__":
    token = test_frontend_fix()
    test_registration()
    test_protected_endpoint(token)
    print("\n=== TEST COMPLETE ===")
