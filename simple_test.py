#!/usr/bin/env python3
"""
Simple FastAPI test to isolate the server crash issue.
"""

import logging
import sys
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Configure logging properly
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create a minimal FastAPI app
app = FastAPI(title="Simple Test API")

@app.get("/health")
async def health_check():
    """Simple health check."""
    logger.info("Health check endpoint called")
    return {"status": "healthy", "message": "Simple test working"}

@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint called")
    return {"message": "Simple FastAPI test server"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting simple test server...")
    uvicorn.run(app, host="127.0.0.1", port=5001, log_level="info")