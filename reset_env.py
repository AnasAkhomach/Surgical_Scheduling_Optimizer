"""
Reset environment variables script.

This script resets the environment variables by clearing the current ones
and loading them from the .env file.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_env():
    """Reset environment variables."""
    # Clear DATABASE_URL
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
        logger.info("Cleared DATABASE_URL environment variable")
    
    # Clear MySQL components
    for key in ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']:
        if key in os.environ:
            del os.environ[key]
            logger.info(f"Cleared {key} environment variable")
    
    # Reload from .env file
    load_dotenv(override=True)
    logger.info("Reloaded environment variables from .env file")
    
    # Print current DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        logger.info(f"Current DATABASE_URL: {database_url}")
    else:
        logger.info("DATABASE_URL not set")
    
    # Print current MySQL components
    mysql_components = {
        key: os.environ.get(key)
        for key in ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
        if os.environ.get(key)
    }
    if mysql_components:
        logger.info(f"MySQL components: {mysql_components}")
    else:
        logger.info("No MySQL components set")
    
    # Print current SQLITE_URL
    sqlite_url = os.environ.get('SQLITE_URL')
    if sqlite_url:
        logger.info(f"Current SQLITE_URL: {sqlite_url}")
    else:
        logger.info("SQLITE_URL not set")

if __name__ == "__main__":
    reset_env()
