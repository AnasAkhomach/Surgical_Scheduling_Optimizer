"""
Script to run the optimization test and visualization.

This script runs the optimization accuracy test and then visualizes the results.
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_optimization_test():
    """Run the optimization accuracy test."""
    logger.info("Running optimization accuracy test...")

    try:
        # Get the current Python executable
        python_executable = sys.executable

        # Run the test script
        result = subprocess.run(
            [python_executable, "test_optimization_accuracy.py"],
            check=True,
            capture_output=True,
            text=True
        )

        # Print output
        logger.info("Optimization test output:")
        for line in result.stdout.splitlines():
            logger.info(line)

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Optimization test failed with exit code {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        return False

def run_visualization():
    """Run the visualization script."""
    logger.info("Running visualization...")

    try:
        # Get the current Python executable
        python_executable = sys.executable

        # Run the visualization script
        result = subprocess.run(
            [python_executable, "visualize_optimization_results.py"],
            check=True,
            capture_output=True,
            text=True
        )

        # Print output
        logger.info("Visualization output:")
        for line in result.stdout.splitlines():
            logger.info(line)

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Visualization failed with exit code {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        return False

def main():
    """Main function to run the optimization test and visualization."""
    logger.info("Starting optimization test and visualization...")

    # Run optimization test
    test_success = run_optimization_test()

    if test_success:
        # Run visualization
        visualization_success = run_visualization()

        if visualization_success:
            logger.info("Optimization test and visualization completed successfully")

            # Open the visualization images
            try:
                if os.name == 'nt':  # Windows
                    os.system("start optimization_gantt.png")
                    os.system("start optimization_utilization.png")
                    os.system("start optimization_durations.png")
                elif os.name == 'posix':  # macOS or Linux
                    os.system("open optimization_gantt.png")
                    os.system("open optimization_utilization.png")
                    os.system("open optimization_durations.png")
            except Exception as e:
                logger.error(f"Failed to open visualization images: {e}")
        else:
            logger.error("Visualization failed")
    else:
        logger.error("Optimization test failed")

if __name__ == "__main__":
    main()
