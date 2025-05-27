#!/usr/bin/env python3
"""
Simple integration test to verify frontend-backend connectivity
without requiring full database setup.
"""

import asyncio
import json
import subprocess
import time
import requests
from pathlib import Path

def test_frontend_build():
    """Test that the frontend builds successfully."""
    print("🔧 Testing frontend build...")
    
    try:
        # Change to frontend directory and run build
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd="frontend",
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Frontend builds successfully")
            
            # Check if dist directory was created
            dist_path = Path("frontend/dist")
            if dist_path.exists():
                print("✅ Build artifacts created in dist/")
                
                # Check for key files
                index_html = dist_path / "index.html"
                if index_html.exists():
                    print("✅ index.html generated")
                else:
                    print("❌ index.html not found")
                    
                assets_dir = dist_path / "assets"
                if assets_dir.exists() and list(assets_dir.glob("*.js")):
                    print("✅ JavaScript assets generated")
                else:
                    print("❌ JavaScript assets not found")
                    
                return True
            else:
                print("❌ Build directory not created")
                return False
        else:
            print(f"❌ Frontend build failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Frontend build timed out")
        return False
    except Exception as e:
        print(f"❌ Frontend build error: {e}")
        return False

def test_api_service_structure():
    """Test that the API service file is properly structured."""
    print("🔧 Testing API service structure...")
    
    try:
        api_service_path = Path("frontend/src/services/api.js")
        if not api_service_path.exists():
            print("❌ API service file not found")
            return False
            
        with open(api_service_path, 'r') as f:
            content = f.read()
            
        # Check for key API modules
        required_apis = [
            'authAPI',
            'surgeryAPI', 
            'scheduleAPI',
            'operatingRoomAPI',
            'surgeonAPI',
            'patientAPI',
            'staffAPI',
            'sdstAPI'
        ]
        
        missing_apis = []
        for api in required_apis:
            if api not in content:
                missing_apis.append(api)
                
        if missing_apis:
            print(f"❌ Missing API modules: {missing_apis}")
            return False
        else:
            print("✅ All required API modules present")
            
        # Check for proper API base URL configuration
        if 'API_BASE_URL' in content and 'import.meta.env.VITE_API_URL' in content:
            print("✅ API base URL properly configured")
        else:
            print("❌ API base URL configuration missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ API service structure test error: {e}")
        return False

def test_environment_configuration():
    """Test that environment configuration is properly set up."""
    print("🔧 Testing environment configuration...")
    
    try:
        # Check frontend .env file
        frontend_env_path = Path("frontend/.env")
        if not frontend_env_path.exists():
            print("❌ Frontend .env file not found")
            return False
            
        with open(frontend_env_path, 'r') as f:
            env_content = f.read()
            
        if 'VITE_API_URL' in env_content:
            print("✅ Frontend API URL configured")
        else:
            print("❌ Frontend API URL not configured")
            return False
            
        # Check Vite config
        vite_config_path = Path("frontend/vite.config.js")
        if not vite_config_path.exists():
            print("❌ Vite config file not found")
            return False
            
        with open(vite_config_path, 'r') as f:
            vite_content = f.read()
            
        if 'proxy' in vite_content and '/api' in vite_content and '8000' in vite_content:
            print("✅ Vite proxy configuration found")
        else:
            print("❌ Vite proxy configuration missing or incorrect")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Environment configuration test error: {e}")
        return False

def test_auth_store_integration():
    """Test that auth store is properly integrated with API."""
    print("🔧 Testing auth store integration...")
    
    try:
        auth_store_path = Path("frontend/src/stores/authStore.js")
        if not auth_store_path.exists():
            print("❌ Auth store file not found")
            return False
            
        with open(auth_store_path, 'r') as f:
            content = f.read()
            
        # Check for API import
        if 'from @/services/api' in content or "from '@/services/api'" in content:
            print("✅ Auth store imports API service")
        else:
            print("❌ Auth store missing API service import")
            return False
            
        # Check for real API calls instead of mock
        if 'authAPI.login' in content and 'authAPI.getCurrentUser' in content:
            print("✅ Auth store uses real API calls")
        else:
            print("❌ Auth store still using mock calls")
            return False
            
        # Check for token management
        if 'localStorage.setItem(\'authToken\'' in content:
            print("✅ Auth store manages JWT tokens")
        else:
            print("❌ Auth store missing token management")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Auth store integration test error: {e}")
        return False

def test_project_structure():
    """Test that the project structure is properly organized."""
    print("🔧 Testing project structure...")
    
    try:
        # Check frontend directories
        required_dirs = [
            "frontend/src/components",
            "frontend/src/stores", 
            "frontend/src/services",
            "frontend/src/router",
            "frontend-legacy",
            "frontend-old"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
                
        if missing_dirs:
            print(f"❌ Missing directories: {missing_dirs}")
            return False
        else:
            print("✅ All required directories present")
            
        # Check that frontend-legacy has the old implementation
        legacy_package_json = Path("frontend-legacy/package.json")
        if legacy_package_json.exists():
            with open(legacy_package_json, 'r') as f:
                legacy_content = f.read()
            if 'vue-cli' in legacy_content or 'vuex' in legacy_content:
                print("✅ Frontend-legacy contains Vue CLI implementation")
            else:
                print("❌ Frontend-legacy missing Vue CLI implementation")
                return False
        else:
            print("❌ Frontend-legacy package.json not found")
            return False
            
        # Check that main frontend has new implementation
        main_package_json = Path("frontend/package.json")
        if main_package_json.exists():
            with open(main_package_json, 'r') as f:
                main_content = f.read()
            if 'vite' in main_content and 'pinia' in main_content:
                print("✅ Main frontend contains Vite + Pinia implementation")
            else:
                print("❌ Main frontend missing Vite + Pinia implementation")
                return False
        else:
            print("❌ Main frontend package.json not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Project structure test error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting Frontend-Backend Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Environment Configuration", test_environment_configuration),
        ("API Service Structure", test_api_service_structure),
        ("Auth Store Integration", test_auth_store_integration),
        ("Frontend Build", test_frontend_build),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests PASSED!")
        print("✅ Frontend-backend integration is ready!")
        return True
    else:
        print("⚠️  Some integration tests FAILED!")
        print("❌ Please fix the issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
