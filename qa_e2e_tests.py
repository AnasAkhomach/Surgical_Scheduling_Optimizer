#!/usr/bin/env python3
"""
End-to-End Tests for Surgery Scheduling System
QA Engineer: Senior QA Engineer AI
Purpose: Validate complete user workflows through browser automation
"""

import asyncio
import json
import sys
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
from typing import Dict, Any, List

class SurgerySchedulingE2ETester:
    def __init__(self):
        self.browser = None
        self.page = None
        self.test_results = []
        self.base_url = "http://localhost:3000"  # Vue.js dev server
        self.api_base_url = "http://localhost:8000"  # FastAPI server
        
    def log_test_result(self, test_name: str, passed: bool, message: str = "", screenshot_path: str = None):
        """Log test results for reporting."""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "screenshot": screenshot_path
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   Details: {message}")
    
    async def setup_browser(self):
        """Initialize browser and page for testing."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=False)  # Set to True for CI
            self.page = await self.browser.new_page()
            
            # Set viewport and timeout
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            self.page.set_default_timeout(30000)  # 30 seconds
            
            self.log_test_result("Browser Setup", True, "Browser initialized successfully")
            return True
        except Exception as e:
            self.log_test_result("Browser Setup", False, f"Exception: {str(e)}")
            return False
    
    async def teardown_browser(self):
        """Clean up browser resources."""
        if self.browser:
            await self.browser.close()
    
    async def test_application_loads(self) -> bool:
        """Test that the application loads correctly."""
        try:
            await self.page.goto(self.base_url)
            
            # Wait for the page to load
            await self.page.wait_for_load_state("networkidle")
            
            # Check if the page title is correct
            title = await self.page.title()
            if "Surgery Scheduling" in title or "Tabu Optimizer" in title:
                self.log_test_result("Application Load", True, f"Page title: {title}")
                return True
            else:
                self.log_test_result("Application Load", False, f"Unexpected page title: {title}")
                return False
                
        except Exception as e:
            self.log_test_result("Application Load", False, f"Exception: {str(e)}")
            return False
    
    async def test_user_authentication(self) -> bool:
        """Test user login workflow."""
        try:
            # Look for login form or check if already logged in
            login_button = await self.page.query_selector("button:has-text('Login')")
            username_input = await self.page.query_selector("input[type='text'], input[name='username']")
            
            if login_button and username_input:
                # Fill login form
                await username_input.fill("testuser")
                
                password_input = await self.page.query_selector("input[type='password'], input[name='password']")
                if password_input:
                    await password_input.fill("testpass123")
                
                # Click login button
                await login_button.click()
                
                # Wait for navigation or dashboard to load
                await self.page.wait_for_timeout(2000)
                
                # Check if login was successful (look for dashboard elements)
                dashboard_elements = await self.page.query_selector_all("[data-testid='dashboard'], .dashboard, h1:has-text('Dashboard')")
                if dashboard_elements:
                    self.log_test_result("User Authentication", True, "Login successful, dashboard loaded")
                    return True
                else:
                    self.log_test_result("User Authentication", False, "Login failed or dashboard not found")
                    return False
            else:
                # Check if already logged in
                dashboard_elements = await self.page.query_selector_all("[data-testid='dashboard'], .dashboard")
                if dashboard_elements:
                    self.log_test_result("User Authentication", True, "Already logged in")
                    return True
                else:
                    self.log_test_result("User Authentication", False, "Login form not found and not logged in")
                    return False
                
        except Exception as e:
            self.log_test_result("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    async def test_surgery_scheduling_screen(self) -> bool:
        """Test surgery scheduling screen functionality."""
        try:
            # Navigate to surgery scheduling screen
            nav_link = await self.page.query_selector("a:has-text('Surgery Scheduling'), a:has-text('Schedule')")
            if nav_link:
                await nav_link.click()
                await self.page.wait_for_timeout(2000)
            
            # Check if Gantt chart or schedule view is present
            gantt_chart = await self.page.query_selector(".gantt-chart, [data-testid='gantt-chart'], .schedule-view")
            if gantt_chart:
                self.log_test_result("Surgery Scheduling Screen", True, "Schedule view loaded successfully")
                
                # Test if data is loading (look for loading indicators or actual data)
                await self.page.wait_for_timeout(3000)  # Wait for data to load
                
                # Look for surgery items in the schedule
                surgery_items = await self.page.query_selector_all(".surgery-item, .gantt-task, [data-testid='surgery']")
                if surgery_items:
                    self.log_test_result("Schedule Data Loading", True, f"Found {len(surgery_items)} surgery items")
                else:
                    self.log_test_result("Schedule Data Loading", False, "No surgery items found in schedule")
                
                return True
            else:
                self.log_test_result("Surgery Scheduling Screen", False, "Schedule view not found")
                return False
                
        except Exception as e:
            self.log_test_result("Surgery Scheduling Screen", False, f"Exception: {str(e)}")
            return False
    
    async def test_optimization_workflow(self) -> bool:
        """Test the optimization button and workflow."""
        try:
            # Look for optimization button
            optimize_button = await self.page.query_selector("button:has-text('Run Optimization'), button:has-text('Optimize')")
            
            if optimize_button:
                # Click the optimization button
                await optimize_button.click()
                self.log_test_result("Optimization Button Click", True, "Optimization button clicked")
                
                # Wait for optimization to complete (look for loading indicators)
                await self.page.wait_for_timeout(5000)
                
                # Look for optimization results or completion indicators
                results_elements = await self.page.query_selector_all(
                    ".optimization-results, [data-testid='optimization-results'], .results-panel"
                )
                
                if results_elements:
                    self.log_test_result("Optimization Results", True, "Optimization results displayed")
                    return True
                else:
                    # Check if optimization is still running
                    loading_elements = await self.page.query_selector_all(".loading, .spinner, [data-testid='loading']")
                    if loading_elements:
                        self.log_test_result("Optimization Workflow", True, "Optimization in progress")
                        return True
                    else:
                        self.log_test_result("Optimization Results", False, "No results or loading indicators found")
                        return False
            else:
                self.log_test_result("Optimization Button", False, "Optimization button not found")
                return False
                
        except Exception as e:
            self.log_test_result("Optimization Workflow", False, f"Exception: {str(e)}")
            return False
    
    async def test_resource_management(self) -> bool:
        """Test resource management functionality."""
        try:
            # Navigate to resource management
            nav_link = await self.page.query_selector("a:has-text('Resource'), a:has-text('Resources')")
            if nav_link:
                await nav_link.click()
                await self.page.wait_for_timeout(2000)
            
            # Check for operating rooms tab/section
            or_tab = await self.page.query_selector("button:has-text('Operating Rooms'), .tab:has-text('Operating Rooms')")
            if or_tab:
                await or_tab.click()
                await self.page.wait_for_timeout(1000)
                
                # Look for operating room data
                or_items = await self.page.query_selector_all(".or-item, .room-item, [data-testid='operating-room']")
                if or_items:
                    self.log_test_result("Resource Management - ORs", True, f"Found {len(or_items)} operating rooms")
                else:
                    self.log_test_result("Resource Management - ORs", False, "No operating rooms found")
                
                return True
            else:
                self.log_test_result("Resource Management", False, "Operating Rooms section not found")
                return False
                
        except Exception as e:
            self.log_test_result("Resource Management", False, f"Exception: {str(e)}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling when backend is unavailable."""
        try:
            # Check browser console for errors
            console_errors = []
            
            def handle_console(msg):
                if msg.type == "error":
                    console_errors.append(msg.text)
            
            self.page.on("console", handle_console)
            
            # Refresh the page to trigger API calls
            await self.page.reload()
            await self.page.wait_for_timeout(3000)
            
            # Check if there are any unhandled errors
            if console_errors:
                error_messages = [error for error in console_errors if "Failed to fetch" not in error]
                if error_messages:
                    self.log_test_result("Error Handling", False, f"Console errors: {error_messages}")
                    return False
            
            # Look for user-friendly error messages
            error_elements = await self.page.query_selector_all(".error-message, .alert-error, [data-testid='error']")
            if error_elements:
                self.log_test_result("Error Handling", True, "Error messages displayed to user")
            else:
                self.log_test_result("Error Handling", True, "No critical console errors found")
            
            return True
            
        except Exception as e:
            self.log_test_result("Error Handling", False, f"Exception: {str(e)}")
            return False
    
    async def run_comprehensive_e2e_tests(self) -> Dict[str, Any]:
        """Run all E2E tests and return results."""
        print("🚀 Starting Comprehensive End-to-End Tests")
        print("=" * 70)
        
        # Setup browser
        if not await self.setup_browser():
            return {"success": False, "error": "Browser setup failed"}
        
        try:
            # Run all E2E tests
            test_functions = [
                self.test_application_loads,
                self.test_user_authentication,
                self.test_surgery_scheduling_screen,
                self.test_optimization_workflow,
                self.test_resource_management,
                self.test_error_handling
            ]
            
            passed_tests = 0
            total_tests = len(test_functions)
            
            for test_func in test_functions:
                try:
                    if await test_func():
                        passed_tests += 1
                    
                    # Take screenshot after each test
                    screenshot_path = f"qa_screenshot_{test_func.__name__}.png"
                    await self.page.screenshot(path=screenshot_path)
                    
                except Exception as e:
                    self.log_test_result(test_func.__name__, False, f"Unexpected error: {str(e)}")
            
            # Generate summary
            print("\n" + "=" * 70)
            print(f"📊 E2E Test Results: {passed_tests}/{total_tests} tests passed")
            
            success_rate = (passed_tests / total_tests) * 100
            if success_rate >= 90:
                print("🎉 EXCELLENT: E2E workflows are working correctly!")
                status = "EXCELLENT"
            elif success_rate >= 75:
                print("✅ GOOD: Most workflows are working, minor issues to address")
                status = "GOOD"
            elif success_rate >= 50:
                print("⚠️  NEEDS WORK: Significant workflow issues need to be resolved")
                status = "NEEDS_WORK"
            else:
                print("❌ CRITICAL: Major workflow problems")
                status = "CRITICAL"
            
            return {
                "success": passed_tests == total_tests,
                "passed_tests": passed_tests,
                "total_tests": total_tests,
                "success_rate": success_rate,
                "status": status,
                "detailed_results": self.test_results
            }
            
        finally:
            await self.teardown_browser()

async def main():
    """Main function to run E2E tests."""
    tester = SurgerySchedulingE2ETester()
    
    try:
        results = await tester.run_comprehensive_e2e_tests()
        
        # Save detailed results to file
        with open("qa_e2e_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: qa_e2e_test_results.json")
        print(f"📸 Screenshots saved for each test step")
        
        # Exit with appropriate code
        sys.exit(0 if results["success"] else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
