#!/usr/bin/env python3
"""
Comprehensive API Integration Tests for Surgery Scheduling System
QA Engineer: Senior QA Engineer AI
Purpose: Verify all critical API endpoints work correctly for frontend integration
"""

import requests
import json
import sys
import time
from datetime import datetime, date
from typing import Dict, Any, List
import pytest

# Test Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

class SurgerySchedulingAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []

    def log_test_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test results for reporting."""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   Details: {message}")

    def authenticate(self) -> bool:
        """Test authentication and get JWT token."""
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/token",  # Correct endpoint with /api prefix
                data={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                self.log_test_result("Authentication", True, f"Token received: {self.token[:20]}...")
                return True
            else:
                self.log_test_result("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False

        except Exception as e:
            self.log_test_result("Authentication", False, f"Exception: {str(e)}")
            return False

    def test_health_check(self) -> bool:
        """Test basic health check endpoint."""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            passed = response.status_code == 200
            message = f"Status: {response.status_code}"
            if passed:
                message += f", Response: {response.json()}"
            self.log_test_result("Health Check", passed, message)
            return passed
        except Exception as e:
            self.log_test_result("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_current_schedule_api(self) -> bool:
        """Test the /current endpoint that frontend uses."""
        try:
            # Test without date parameter
            response = self.session.get(f"{BASE_URL}/current")

            if response.status_code == 200:
                data = response.json()
                self.log_test_result("Current Schedule API", True, f"Retrieved {len(data)} schedule items")

                # Validate data structure if data exists
                if data:
                    required_fields = ['surgery_id', 'patient_name', 'surgery_type', 'room_id', 'start_time', 'end_time']
                    sample = data[0]
                    missing_fields = [field for field in required_fields if field not in sample]
                    if missing_fields:
                        self.log_test_result("Schedule Data Structure", False, f"Missing fields: {missing_fields}")
                        return False
                    else:
                        self.log_test_result("Schedule Data Structure", True, "All required fields present")

                return True
            else:
                self.log_test_result("Current Schedule API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False

        except Exception as e:
            self.log_test_result("Current Schedule API", False, f"Exception: {str(e)}")
            return False

    def test_operating_rooms_api(self) -> bool:
        """Test operating rooms CRUD operations."""
        try:
            # Test GET operating rooms
            response = self.session.get(f"{BASE_URL}/operating-rooms")

            if response.status_code == 200:
                data = response.json()
                self.log_test_result("Operating Rooms GET", True, f"Retrieved {len(data)} operating rooms")

                # Test data structure
                if data:
                    required_fields = ['room_id', 'location']
                    sample = data[0]
                    missing_fields = [field for field in required_fields if field not in sample]
                    if missing_fields:
                        self.log_test_result("OR Data Structure", False, f"Missing fields: {missing_fields}")
                        return False
                    else:
                        self.log_test_result("OR Data Structure", True, "All required fields present")

                return True
            else:
                self.log_test_result("Operating Rooms GET", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.log_test_result("Operating Rooms API", False, f"Exception: {str(e)}")
            return False

    def test_staff_api(self) -> bool:
        """Test staff management API."""
        try:
            response = self.session.get(f"{BASE_URL}/staff")

            if response.status_code == 200:
                data = response.json()
                self.log_test_result("Staff API GET", True, f"Retrieved {len(data)} staff members")

                # Test data structure
                if data:
                    required_fields = ['staff_id', 'name', 'role']
                    sample = data[0]
                    missing_fields = [field for field in required_fields if field not in sample]
                    if missing_fields:
                        self.log_test_result("Staff Data Structure", False, f"Missing fields: {missing_fields}")
                        return False
                    else:
                        self.log_test_result("Staff Data Structure", True, "All required fields present")

                return True
            else:
                self.log_test_result("Staff API GET", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.log_test_result("Staff API", False, f"Exception: {str(e)}")
            return False

    def test_optimization_api(self) -> bool:
        """Test the optimization endpoint that frontend calls."""
        try:
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

            start_time = time.time()
            response = self.session.post(
                f"{BASE_URL}/optimize",
                json=optimization_params
            )
            execution_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                required_fields = ['assignments', 'score', 'execution_time_seconds']
                missing_fields = [field for field in required_fields if field not in data]

                if missing_fields:
                    self.log_test_result("Optimization API", False, f"Missing response fields: {missing_fields}")
                    return False

                self.log_test_result("Optimization API", True,
                    f"Score: {data.get('score')}, Assignments: {len(data.get('assignments', []))}, Time: {execution_time:.2f}s")

                # Test performance requirement
                if execution_time > 30:
                    self.log_test_result("Optimization Performance", False, f"Took {execution_time:.2f}s (>30s limit)")
                    return False
                else:
                    self.log_test_result("Optimization Performance", True, f"Completed in {execution_time:.2f}s")

                return True
            else:
                self.log_test_result("Optimization API", False, f"Status: {response.status_code}, Response: {response.text}")
                return False

        except Exception as e:
            self.log_test_result("Optimization API", False, f"Exception: {str(e)}")
            return False

    def test_sdst_matrix_api(self) -> bool:
        """Test SDST matrix endpoint."""
        try:
            response = self.session.get(f"{BASE_URL}/sdst/matrix")

            if response.status_code == 200:
                data = response.json()
                self.log_test_result("SDST Matrix API", True, f"Retrieved SDST data with keys: {list(data.keys())}")
                return True
            else:
                self.log_test_result("SDST Matrix API", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.log_test_result("SDST Matrix API", False, f"Exception: {str(e)}")
            return False

    def test_api_response_times(self) -> bool:
        """Test API response time requirements (<200ms for CRUD operations)."""
        endpoints_to_test = [
            ("GET", "/current"),
            ("GET", "/operating-rooms"),
            ("GET", "/staff"),
            ("GET", "/sdst/matrix")
        ]

        all_passed = True
        for method, endpoint in endpoints_to_test:
            try:
                start_time = time.time()
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

                if response.status_code == 200 and response_time < 200:
                    self.log_test_result(f"Response Time {endpoint}", True, f"{response_time:.1f}ms")
                else:
                    self.log_test_result(f"Response Time {endpoint}", False,
                        f"{response_time:.1f}ms (>200ms limit) or status {response.status_code}")
                    all_passed = False

            except Exception as e:
                self.log_test_result(f"Response Time {endpoint}", False, f"Exception: {str(e)}")
                all_passed = False

        return all_passed

    def run_comprehensive_api_tests(self) -> Dict[str, Any]:
        """Run all API integration tests and return results."""
        print("🚀 Starting Comprehensive API Integration Tests")
        print("=" * 70)

        # Check if backend is running
        try:
            health_response = requests.get(f"{BASE_URL}/health", timeout=5)
            if health_response.status_code != 200:
                print("❌ Backend server is not responding correctly")
                return {"success": False, "error": "Backend not available"}
        except:
            print("❌ Backend server is not running or not accessible")
            print(f"   Please start the FastAPI server at {BASE_URL}")
            return {"success": False, "error": "Backend not accessible"}

        # Run authentication first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with API tests")
            return {"success": False, "error": "Authentication failed"}

        # Run all API tests
        test_functions = [
            self.test_health_check,
            self.test_current_schedule_api,
            self.test_operating_rooms_api,
            self.test_staff_api,
            self.test_sdst_matrix_api,
            self.test_optimization_api,
            self.test_api_response_times
        ]

        passed_tests = 0
        total_tests = len(test_functions)

        for test_func in test_functions:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test_result(test_func.__name__, False, f"Unexpected error: {str(e)}")

        # Generate summary
        print("\n" + "=" * 70)
        print(f"📊 API Integration Test Results: {passed_tests}/{total_tests} tests passed")

        success_rate = (passed_tests / total_tests) * 100
        if success_rate >= 90:
            print("🎉 EXCELLENT: API integration is working correctly!")
            status = "EXCELLENT"
        elif success_rate >= 75:
            print("✅ GOOD: Most API endpoints are working, minor issues to address")
            status = "GOOD"
        elif success_rate >= 50:
            print("⚠️  NEEDS WORK: Significant API issues need to be resolved")
            status = "NEEDS_WORK"
        else:
            print("❌ CRITICAL: Major API integration problems")
            status = "CRITICAL"

        return {
            "success": passed_tests == total_tests,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": success_rate,
            "status": status,
            "detailed_results": self.test_results
        }

def main():
    """Main function to run API integration tests."""
    tester = SurgerySchedulingAPITester()

    try:
        results = tester.run_comprehensive_api_tests()

        # Save detailed results to file
        with open("qa_api_test_results.json", "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n📄 Detailed results saved to: qa_api_test_results.json")

        # Exit with appropriate code
        sys.exit(0 if results["success"] else 1)

    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
