import os
import subprocess
import sys

def run_frontend():
    """Run the frontend application."""
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    
    if not os.path.exists(frontend_dir):
        print(f"Error: Frontend directory not found at {frontend_dir}")
        sys.exit(1)
    
    if not os.path.exists(os.path.join(frontend_dir, 'package.json')):
        print(f"Error: package.json not found in {frontend_dir}")
        sys.exit(1)
    
    print(f"Starting frontend server from {frontend_dir}")
    
    # Change to the frontend directory
    os.chdir(frontend_dir)
    
    # Run npm serve
    try:
        subprocess.run(['npm', 'run', 'serve'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running npm serve: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: npm command not found. Make sure Node.js is installed.")
        sys.exit(1)

if __name__ == "__main__":
    run_frontend()
