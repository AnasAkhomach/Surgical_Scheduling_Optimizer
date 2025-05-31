#!/usr/bin/env python3
"""
Integration test script to verify the surgery scheduling API endpoints work correctly.
This script tests the actual backend API endpoints that the frontend will use.
"""

import requests
import json
import sys
from datetime import datetime, date
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testuser",
    "password": "testpass123"
}

class ScheduleIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self) -> bool:
        """Authenticate with the API and get JWT token."""
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_current_schedule(self) -> bool:
        """Test the /schedules/current endpoint."""
        try:
            print("\n🔍 Testing current schedule endpoint...")
            
            # Test without date parameter
            response = self.session.get(f"{BASE_URL}/schedules/current")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Current schedule retrieved: {len(data)} assignments")
                
                # Print sample data if available
                if data:
                    sample = data[0]
                    print(f"   Sample assignment: Surgery {sample.get('surgery_id')} in {sample.get('room')}")
                
                return True
            else:
                print(f"❌ Current schedule failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Current schedule error: {e}")
            return False
    
    def test_operating_rooms(self) -> bool:
        """Test the /operating-rooms endpoint."""
        try:
            print("\n🔍 Testing operating rooms endpoint...")
            
            response = self.session.get(f"{BASE_URL}/operating-rooms")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Operating rooms retrieved: {len(data)} rooms")
                
                if data:
                    sample = data[0]
                    print(f"   Sample room: OR-{sample.get('room_id')} at {sample.get('location')}")
                
                return True
            else:
                print(f"❌ Operating rooms failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Operating rooms error: {e}")
            return False
    
    def test_staff(self) -> bool:
        """Test the /staff endpoint."""
        try:
            print("\n🔍 Testing staff endpoint...")
            
            response = self.session.get(f"{BASE_URL}/staff")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Staff retrieved: {len(data)} staff members")
                
                if data:
                    sample = data[0]
                    print(f"   Sample staff: {sample.get('name')} ({sample.get('role')})")
                
                return True
            else:
                print(f"❌ Staff failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Staff error: {e}")
            return False
    
    def test_optimization(self) -> bool:
        """Test the /schedules/optimize endpoint."""
        try:
            print("\n🔍 Testing optimization endpoint...")
            
            optimization_params = {
                "schedule_date": date.today().isoformat(),
                "max_iterations": 10,  # Small number for quick test
                "tabu_tenure": 5,
                "max_no_improvement": 5,
                "time_limit_seconds": 10,
                "weights": {
                    "utilization": 0.4,
                    "setup_time": 0.3,
                    "preference": 0.3
                }
            }
            
            response = self.session.post(
                f"{BASE_URL}/schedules/optimize",
                json=optimization_params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Optimization successful: Score {data.get('score')}")
                print(f"   Assignments: {len(data.get('assignments', []))}")
                print(f"   Execution time: {data.get('execution_time_seconds')}s")
                return True
            else:
                print(f"❌ Optimization failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Optimization error: {e}")
            return False
    
    def test_sdst_matrix(self) -> bool:
        """Test the /sdst/matrix endpoint."""
        try:
            print("\n🔍 Testing SDST matrix endpoint...")
            
            response = self.session.get(f"{BASE_URL}/sdst/matrix")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SDST matrix retrieved")
                print(f"   Surgery types: {len(data.get('surgery_types', []))}")
                print(f"   Setup times: {len(data.get('setup_times', []))}")
                return True
            else:
                print(f"❌ SDST matrix failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ SDST matrix error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all integration tests."""
        print("🚀 Starting Surgery Scheduling API Integration Tests")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        tests = [
            ("Current Schedule", self.test_current_schedule),
            ("Operating Rooms", self.test_operating_rooms),
            ("Staff", self.test_staff),
            ("SDST Matrix", self.test_sdst_matrix),
            ("Optimization", self.test_optimization),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    print(f"❌ {test_name} test failed")
            except Exception as e:
                print(f"❌ {test_name} test error: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All integration tests passed! Frontend-backend integration is working.")
            return True
        else:
            print("⚠️  Some tests failed. Check the backend API and database.")
            return False

def main():
    """Main function to run the integration tests."""
    tester = ScheduleIntegrationTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
