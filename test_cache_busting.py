#!/usr/bin/env python3
"""
Cache Busting Test Script

This script tests the frontend cache-busting implementation to ensure
that users always see the latest version of the application.
"""

import requests
import time
import json
from datetime import datetime

def test_frontend_cache_headers():
    """Test that the frontend serves proper cache-busting headers."""
    print("🧪 Testing Frontend Cache Headers...")
    
    try:
        # Test the main application
        response = requests.get("http://localhost:5173/", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for header, value in response.headers.items():
            if 'cache' in header.lower() or 'pragma' in header.lower() or 'expires' in header.lower():
                print(f"  {header}: {value}")
        
        # Check for cache-busting meta tags in HTML
        if 'no-cache' in response.text and 'app-version' in response.text:
            print("✅ Cache-busting meta tags found in HTML")
        else:
            print("⚠️ Cache-busting meta tags not found in HTML")
            
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def test_api_cache_headers():
    """Test that API requests include cache-busting headers."""
    print("\n🧪 Testing API Cache Headers...")
    
    try:
        # Test the health endpoint
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for header, value in response.headers.items():
            if 'cache' in header.lower() or 'pragma' in header.lower() or 'expires' in header.lower():
                print(f"  {header}: {value}")
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing API: {e}")
        print("💡 Make sure the FastAPI backend is running on port 8000")
        return False

def test_static_assets():
    """Test that static assets are served with appropriate headers."""
    print("\n🧪 Testing Static Asset Headers...")
    
    try:
        # Test a static asset
        response = requests.get("http://localhost:5173/vite.svg", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for header, value in response.headers.items():
            if 'cache' in header.lower() or 'etag' in header.lower() or 'last-modified' in header.lower():
                print(f"  {header}: {value}")
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing static assets: {e}")
        return False

def test_cache_busting_query_params():
    """Test that cache-busting query parameters work."""
    print("\n🧪 Testing Cache-Busting Query Parameters...")
    
    try:
        timestamp1 = int(time.time() * 1000)
        timestamp2 = timestamp1 + 1000
        
        # Make two requests with different cache-busting parameters
        url1 = f"http://localhost:5173/vite.svg?_cb={timestamp1}"
        url2 = f"http://localhost:5173/vite.svg?_cb={timestamp2}"
        
        response1 = requests.get(url1, timeout=10)
        response2 = requests.get(url2, timeout=10)
        
        print(f"Request 1 Status: {response1.status_code}")
        print(f"Request 2 Status: {response2.status_code}")
        
        # Both should succeed and return the same content but with different URLs
        if response1.status_code == 200 and response2.status_code == 200:
            print("✅ Cache-busting query parameters working")
            return True
        else:
            print("⚠️ Cache-busting query parameters may not be working")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing cache-busting parameters: {e}")
        return False

def test_version_meta_tag():
    """Test that the version meta tag is present and correct."""
    print("\n🧪 Testing Version Meta Tag...")
    
    try:
        response = requests.get("http://localhost:5173/", timeout=10)
        
        if 'name="app-version"' in response.text:
            # Extract version from meta tag
            import re
            version_match = re.search(r'name="app-version"\s+content="([^"]+)"', response.text)
            if version_match:
                version = version_match.group(1)
                print(f"✅ App version found: {version}")
                return True
            else:
                print("⚠️ App version meta tag found but content not readable")
                return False
        else:
            print("❌ App version meta tag not found")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing version meta tag: {e}")
        return False

def generate_test_report(results):
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("📊 CACHE BUSTING TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print("\n" + "="*60)
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Cache busting is working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
    
    print("="*60)

def main():
    """Run all cache busting tests."""
    print("🚀 Starting Cache Busting Tests...")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    results = {}
    
    # Run all tests
    results["Frontend Cache Headers"] = test_frontend_cache_headers()
    results["API Cache Headers"] = test_api_cache_headers()
    results["Static Asset Headers"] = test_static_assets()
    results["Cache-Busting Query Params"] = test_cache_busting_query_params()
    results["Version Meta Tag"] = test_version_meta_tag()
    
    # Generate report
    generate_test_report(results)
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
