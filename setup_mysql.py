"""
MySQL database setup script.

This script helps set up a MySQL database for the surgery scheduling application.
It guides the user through the process of creating a MySQL database and user.
"""

import os
import sys
import logging
import getpass
import pymysql
import subprocess
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def check_mysql_installed():
    """Check if MySQL is installed."""
    print_header("Checking MySQL Installation")
    
    try:
        # Try to run mysql --version
        result = subprocess.run(
            ["mysql", "--version"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ MySQL is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ MySQL command not found.")
            print("Please install MySQL and make sure it's in your PATH.")
            return False
    except FileNotFoundError:
        print("❌ MySQL command not found.")
        print("Please install MySQL and make sure it's in your PATH.")
        return False

def get_mysql_credentials():
    """Get MySQL credentials from the user."""
    print_header("MySQL Credentials")
    
    print("Please enter your MySQL credentials.")
    print("These will be used to create the database and user.")
    
    host = input("MySQL host [localhost]: ") or "localhost"
    port = input("MySQL port [3306]: ") or "3306"
    
    # Get root username and password
    root_user = input("MySQL admin username [root]: ") or "root"
    root_password = getpass.getpass("MySQL admin password: ")
    
    # Test connection
    try:
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=root_user,
            password=root_password
        )
        connection.close()
        print("✅ Successfully connected to MySQL server.")
    except Exception as e:
        print(f"❌ Failed to connect to MySQL server: {e}")
        return None
    
    # Get database name and user credentials
    db_name = input("Database name [surgery_scheduler]: ") or "surgery_scheduler"
    db_user = input("Database user [surgery_user]: ") or "surgery_user"
    db_password = getpass.getpass("Database password: ")
    
    return {
        "host": host,
        "port": port,
        "root_user": root_user,
        "root_password": root_password,
        "db_name": db_name,
        "db_user": db_user,
        "db_password": db_password
    }

def create_database_and_user(credentials):
    """Create the database and user."""
    print_header("Creating Database and User")
    
    host = credentials["host"]
    port = int(credentials["port"])
    root_user = credentials["root_user"]
    root_password = credentials["root_password"]
    db_name = credentials["db_name"]
    db_user = credentials["db_user"]
    db_password = credentials["db_password"]
    
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host=host,
            port=port,
            user=root_user,
            password=root_password
        )
        
        with connection.cursor() as cursor:
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{db_name}' created or already exists.")
            
            # Create user
            try:
                cursor.execute(f"CREATE USER IF NOT EXISTS '{db_user}'@'%' IDENTIFIED BY '{db_password}'")
                print(f"✅ User '{db_user}' created or already exists.")
            except Exception as e:
                print(f"⚠️ Could not create user: {e}")
                print("Trying alternative approach...")
                try:
                    # For MySQL 5.7 and earlier
                    cursor.execute(f"GRANT USAGE ON *.* TO '{db_user}'@'%' IDENTIFIED BY '{db_password}'")
                    print(f"✅ User '{db_user}' created using alternative approach.")
                except Exception as e2:
                    print(f"❌ Failed to create user: {e2}")
                    return False
            
            # Grant privileges
            cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'%'")
            cursor.execute("FLUSH PRIVILEGES")
            print(f"✅ Privileges granted to user '{db_user}'.")
        
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Failed to create database and user: {e}")
        return False

def update_env_file(credentials):
    """Update the .env file with MySQL credentials."""
    print_header("Updating .env File")
    
    # Load existing .env file
    load_dotenv()
    
    # Create new .env content
    env_content = []
    
    # Add MySQL configuration
    env_content.append("# Database Configuration")
    env_content.append(f"DB_USER={credentials['db_user']}")
    env_content.append(f"DB_PASSWORD={credentials['db_password']}")
    env_content.append(f"DB_HOST={credentials['host']}")
    env_content.append(f"DB_PORT={credentials['port']}")
    env_content.append(f"DB_NAME={credentials['db_name']}")
    env_content.append("")
    
    # Add SQLite fallback
    env_content.append("# SQLite fallback (used if MySQL parameters are not set)")
    env_content.append("SQLITE_URL=sqlite:///./surgery_scheduler.db")
    env_content.append("")
    
    # Add other existing environment variables
    for key in os.environ:
        if key not in ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME", "SQLITE_URL"]:
            value = os.environ[key]
            if key.startswith("PYTHON") or key.startswith("PATH"):
                continue
            env_content.append(f"{key}={value}")
    
    # Write to .env file
    with open(".env", "w") as f:
        f.write("\n".join(env_content))
    
    print("✅ .env file updated with MySQL credentials.")
    return True

def run_setup():
    """Run the MySQL setup process."""
    print_header("MySQL Database Setup")
    
    # Check if MySQL is installed
    if not check_mysql_installed():
        return False
    
    # Get MySQL credentials
    credentials = get_mysql_credentials()
    if not credentials:
        return False
    
    # Create database and user
    if not create_database_and_user(credentials):
        return False
    
    # Update .env file
    if not update_env_file(credentials):
        return False
    
    print_header("Setup Complete")
    print("✅ MySQL database setup completed successfully.")
    print("You can now run the application with MySQL as the database backend.")
    print("To initialize the database schema, run:")
    print("  python initialize_mysql.py")
    
    return True

if __name__ == "__main__":
    success = run_setup()
    sys.exit(0 if success else 1)
