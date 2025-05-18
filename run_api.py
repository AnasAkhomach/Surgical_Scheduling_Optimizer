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
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() in ("true", "1", "t")

if __name__ == "__main__":
    print(f"Starting API server at http://{API_HOST}:{API_PORT}")
    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT, reload=API_RELOAD)
