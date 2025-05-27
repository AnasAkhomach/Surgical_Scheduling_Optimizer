"""
Test script to verify the FastAPI setup.

This script tests the FastAPI setup by making a request to the health check endpoint.
"""

import os
import sys
import requests
import time
import subprocess
import signal
import atexit

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# API URL
API_URL = "http://127.0.0.1:8000"

# Start the API server
print("Starting API server...")
api_process = subprocess.Popen(
    ["python", "run_api.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Register cleanup function to kill the API server on exit
def cleanup():
    print("Stopping API server...")
    if api_process.poll() is None:
        api_process.send_signal(signal.SIGTERM)
        api_process.wait()

atexit.register(cleanup)

# Wait for the API server to start
print("Waiting for API server to start...")
max_retries = 15
retry_count = 0
while retry_count < max_retries:
    try:
        # Try to connect to the health check endpoint
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("API server is running!")
            break
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass

    retry_count += 1
    time.sleep(2)
    print(f"Retrying ({retry_count}/{max_retries})...")

if retry_count >= max_retries:
    print("Failed to connect to API server.")
    sys.exit(1)

# Test the health check endpoint
print("\nTesting health check endpoint...")
try:
    response = requests.get(f"{API_URL}/api/health")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 200 and response.json().get("status") == "healthy":
        print("\n✅ API server is healthy!")
    else:
        print("\n❌ API server is not healthy.")
        sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

# Test the API documentation endpoints
print("\nTesting API documentation endpoints...")
try:
    # Test Swagger UI
    response = requests.get(f"{API_URL}/docs")
    print(f"Swagger UI status code: {response.status_code}")

    # Test ReDoc
    response = requests.get(f"{API_URL}/redoc")
    print(f"ReDoc status code: {response.status_code}")

    if response.status_code == 200:
        print("\n✅ API documentation is available!")
    else:
        print("\n❌ API documentation is not available.")
        sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

print("\nAll tests passed! FastAPI setup is working correctly.")
sys.exit(0)
