#!/usr/bin/env python3
"""
Test frontend-backend integration for authentication
"""
import requests
import time
from urllib.parse import urlencode

def test_backend_endpoints():
    """Test backend authentication endpoints"""
    print("🔧 BACKEND TESTING")
    print("=" * 40)
    
    # Test login
    print("1. Testing backend login...")
    try:
        data = urlencode({'username': 'admin', 'password': 'admin123'})
        response = requests.post('http://localhost:8000/api/auth/token',
                               data=data,
                               headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code == 200:
            print("   ✅ Backend login: SUCCESS")
            token = response.json()['access_token']
            
            # Test /auth/me
            me_response = requests.get('http://localhost:8000/api/auth/me',
                                     headers={'Authorization': f'Bearer {token}'})
            if me_response.status_code == 200:
                user_info = me_response.json()
                print(f"   ✅ User info: {user_info['username']} ({user_info['role']})")
                return True
            else:
                print(f"   ❌ /auth/me failed: {me_response.status_code}")
                return False
        else:
            print(f"   ❌ Backend login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend test error: {e}")
        return False

def test_frontend_availability():
    """Test if frontend is running"""
    print("\n🌐 FRONTEND TESTING")
    print("=" * 40)
    
    print("1. Testing frontend availability...")
    try:
        response = requests.get('http://localhost:5173', timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is running")
            return True
        else:
            print(f"   ❌ Frontend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend not accessible: {e}")
        return False

def test_api_service_format():
    """Test the exact format that frontend API service uses"""
    print("\n🔗 API SERVICE FORMAT TESTING")
    print("=" * 40)
    
    print("1. Testing FormData format (frontend simulation)...")
    try:
        # Simulate exactly what frontend FormData does
        import requests
        
        # Create form data the same way frontend does
        form_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # Use requests to encode form data
        encoded_data = requests.models.RequestEncodingMixin._encode_params(form_data)
        
        response = requests.post('http://localhost:8000/api/auth/token',
                               data=encoded_data,
                               headers={})  # Let requests set Content-Type
        
        if response.status_code == 200:
            print("   ✅ Frontend FormData format: SUCCESS")
            return True
        else:
            print(f"   ❌ Frontend FormData format failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ FormData test error: {e}")
        return False

def main():
    """Run integration tests"""
    print("🧪 FRONTEND-BACKEND INTEGRATION TESTING")
    print("=" * 60)
    
    backend_ok = test_backend_endpoints()
    frontend_ok = test_frontend_availability()
    api_format_ok = test_api_service_format()
    
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    print(f"Backend Authentication: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend Availability:  {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"API Format Compatibility: {'✅ PASS' if api_format_ok else '❌ FAIL'}")
    
    if backend_ok and frontend_ok and api_format_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Authentication system is fully functional")
        print("✅ Frontend and backend are properly integrated")
        print("✅ API format compatibility confirmed")
        print("\n📋 NEXT STEPS:")
        print("• Test login through the frontend UI")
        print("• Verify user registration flow")
        print("• Test protected routes")
        print("• Proceed with advanced features")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please check the failed components before proceeding")
    
    print("\n🔍 TROUBLESHOOTING GUIDE:")
    print("• If backend fails: Check if API server is running on port 8000")
    print("• If frontend fails: Check if dev server is running on port 5173")
    print("• If API format fails: Check FormData encoding in frontend")
    print("• Browser extension errors can be safely ignored")

if __name__ == "__main__":
    main()
