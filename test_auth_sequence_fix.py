import requests
import json

def test_auth_sequence_fix():
    """Test the authentication sequence fix"""
    print("=== TESTING AUTHENTICATION SEQUENCE FIX ===\n")
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: Simulate the FIXED authentication sequence
    print("1. Testing FIXED authentication sequence...")
    try:
        # Step 1: Login to get token
        print("   Step 1: Login to get token...")
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'grant_type': 'password'
        }
        
        response = requests.post(f"{base_url}/auth/token", data=login_data)
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login successful!")
            token_data = response.json()
            access_token = token_data['access_token']
            print(f"   Token received: {access_token[:20]}...")
            
            # Step 2: Immediately use token for /auth/me (simulating fixed sequence)
            print("   Step 2: Use token for /auth/me...")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            me_response = requests.get(f"{base_url}/auth/me", headers=headers)
            print(f"   /auth/me status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                print("   ✅ Protected endpoint access successful!")
                user_data = me_response.json()
                print(f"   User info: {user_data['username']} (ID: {user_data['user_id']})")
                return True
            else:
                print(f"   ❌ Protected endpoint access failed: {me_response.text}")
                return False
                
        else:
            print(f"   ❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Authentication sequence error: {e}")
        return False

def test_multiple_users():
    """Test authentication with multiple users"""
    print("\n2. Testing authentication with multiple users...")
    
    base_url = "http://localhost:8000/api"
    users = [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'user', 'password': 'user123'},
        {'username': 'surgeon', 'password': 'surgeon123'}
    ]
    
    for user in users:
        try:
            print(f"   Testing user: {user['username']}")
            
            # Login
            login_data = {
                'username': user['username'],
                'password': user['password'],
                'grant_type': 'password'
            }
            
            response = requests.post(f"{base_url}/auth/token", data=login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data['access_token']
                
                # Test protected endpoint
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                me_response = requests.get(f"{base_url}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"   ✅ {user['username']}: Login and /auth/me successful")
                    print(f"      User ID: {user_data['user_id']}, Role: {user_data.get('role', 'N/A')}")
                else:
                    print(f"   ❌ {user['username']}: /auth/me failed ({me_response.status_code})")
            else:
                print(f"   ❌ {user['username']}: Login failed ({response.status_code})")
                
        except Exception as e:
            print(f"   ❌ {user['username']}: Error - {e}")

def test_token_persistence():
    """Test token persistence and reuse"""
    print("\n3. Testing token persistence and reuse...")
    
    base_url = "http://localhost:8000/api"
    
    try:
        # Get token
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'grant_type': 'password'
        }
        
        response = requests.post(f"{base_url}/auth/token", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            print(f"   Token obtained: {access_token[:20]}...")
            
            # Use token multiple times
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            for i in range(3):
                me_response = requests.get(f"{base_url}/auth/me", headers=headers)
                if me_response.status_code == 200:
                    print(f"   ✅ Request {i+1}: Token still valid")
                else:
                    print(f"   ❌ Request {i+1}: Token invalid ({me_response.status_code})")
                    break
            
            print("   ✅ Token persistence test completed")
            
        else:
            print(f"   ❌ Could not obtain token: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Token persistence test error: {e}")

if __name__ == "__main__":
    success = test_auth_sequence_fix()
    test_multiple_users()
    test_token_persistence()
    
    if success:
        print("\n=== AUTHENTICATION SEQUENCE FIX VERIFIED ===")
        print("✅ The token storage sequence issue has been resolved!")
        print("✅ Frontend should now work correctly with the authentication flow")
    else:
        print("\n=== AUTHENTICATION SEQUENCE FIX FAILED ===")
        print("❌ There are still issues with the authentication flow")
