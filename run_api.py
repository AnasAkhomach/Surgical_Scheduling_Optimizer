"""
Script to run the FastAPI application.

This script runs the FastAPI application using uvicorn.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API settings from environment variables
API_HOST = os.getenv("API_HOST", "127.0.0.1")  # Changed from 0.0.0.0 to 127.0.0.1
API_PORT = int(os.getenv("API_PORT", "5000"))  # Default to 5000 if not set
# API_RELOAD is set in .env, but we will force it to False for uvicorn.run

if __name__ == "__main__":
    # Ensure API_PORT is correctly fetched after load_dotenv()
    actual_api_port = int(os.getenv("API_PORT", "5000"))
    print(f"Starting API server at http://{API_HOST}:{actual_api_port} with reload=False")
    # Force reload=False to simplify and avoid potential reloader issues with port
    uvicorn.run("api.main:app", host=API_HOST, port=actual_api_port, reload=False)
