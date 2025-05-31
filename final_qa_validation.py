#!/usr/bin/env python3
"""
Final QA validation test for the surgery scheduling system
"""

import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8000/api"
TEST_USER = {"username": "admin", "password": "admin123"}

def test_authentication():
    """Test authentication"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data=TEST_USER,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Authentication: PASS")
            return token
        else:
            print(f"❌ Authentication: FAIL - {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication: ERROR - {e}")
        return None

def test_critical_endpoints(token):
    """Test critical endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    tests = [
        ("Health Check", "GET", "/health"),
        ("Current Schedule", "GET", "/current"),
        ("Operating Rooms", "GET", "/operating-rooms"),
        ("Staff", "GET", "/staff"),
        ("SDST Matrix", "GET", "/sdst/matrix"),
    ]
    
    results = []
    for name, method, endpoint in tests:
        try:
            start_time = datetime.now()
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                print(f"✅ {name}: PASS ({response_time:.1f}ms)")
                results.append(True)
            else:
                print(f"❌ {name}: FAIL - {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            results.append(False)
    
    return results

def test_optimization_endpoint(token):
    """Test the optimization endpoint that was failing"""
    headers = {"Authorization": f"Bearer {token}"}
    
    optimization_params = {
        "schedule_date": date.today().isoformat(),
        "max_iterations": 5,  # Small number for quick test
        "tabu_tenure": 3,
        "max_no_improvement": 3,
        "time_limit_seconds": 10,
        "weights": {
            "utilization": 0.4,
            "setup_time": 0.3,
            "preference": 0.3
        }
    }
    
    try:
        print("🔄 Testing Optimization API...")
        start_time = datetime.now()
        response = requests.post(
            f"{BASE_URL}/optimize",
            json=optimization_params,
            headers=headers
        )
        response_time = (datetime.now() - start_time).total_seconds()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Optimization API: PASS ({response_time:.1f}s)")
            print(f"   Score: {data.get('score', 'N/A')}")
            print(f"   Assignments: {len(data.get('assignments', []))}")
            return True
        else:
            print(f"❌ Optimization API: FAIL - {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Optimization API: ERROR - {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 Final QA Validation Test")
    print("=" * 50)
    
    # Test authentication
    token = test_authentication()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    # Test critical endpoints
    print("\n📋 Testing Critical Endpoints...")
    endpoint_results = test_critical_endpoints(token)
    
    # Test optimization (the critical fix)
    print("\n🎯 Testing Optimization Engine...")
    optimization_result = test_optimization_endpoint(token)
    
    # Calculate results
    total_tests = len(endpoint_results) + 1  # +1 for optimization
    passed_tests = sum(endpoint_results) + (1 if optimization_result else 0)
    success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 50)
    print(f"📊 Final QA Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT: System ready for production!")
        status = "READY_FOR_PRODUCTION"
    elif success_rate >= 75:
        print("✅ GOOD: Minor issues to address")
        status = "GOOD_WITH_MINOR_ISSUES"
    else:
        print("❌ NEEDS WORK: Significant issues remain")
        status = "NEEDS_WORK"
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": success_rate,
        "status": status,
        "optimization_working": optimization_result
    }
    
    with open("final_qa_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: final_qa_results.json")
    return success_rate >= 90

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
