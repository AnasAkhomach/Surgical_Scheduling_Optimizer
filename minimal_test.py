#!/usr/bin/env python3
"""
Minimal FastAPI test to isolate server issues.
"""

import uvicorn
from fastapi import FastAPI

# Create the most basic FastAPI app possible
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting minimal FastAPI server...")
    uvicorn.run(app, host="127.0.0.1", port=5002, log_level="info")