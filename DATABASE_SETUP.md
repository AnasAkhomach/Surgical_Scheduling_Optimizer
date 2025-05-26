# Database Setup Guide

This guide explains how to set up and configure the database for the Surgery Scheduling Application. The application supports both SQLite (for development/testing) and MySQL (for production) databases.

## Table of Contents

1. [SQLite Setup (Default)](#sqlite-setup-default)
2. [MySQL Setup](#mysql-setup)
3. [Migrating from SQLite to MySQL](#migrating-from-sqlite-to-mysql)
4. [Verifying Database Configuration](#verifying-database-configuration)
5. [Troubleshooting](#troubleshooting)

## SQLite Setup (Default)

SQLite is the default database for development and testing. It requires no additional setup.

### Automatic Setup

1. The application will automatically create and use an SQLite database file (`surgery_scheduler.db`) in the project root directory.
2. Tables will be created automatically when the application starts.

### Manual Setup

If you want to initialize the database manually:

```bash
# Initialize the database schema
python initialize_mysql.py

# Seed the database with sample data
python seed_database.py
```

## MySQL Setup

For production environments, it's recommended to use MySQL instead of SQLite.

### Prerequisites

- MySQL server installed and running
- MySQL client tools installed
- Python `pymysql` package installed (`pip install pymysql`)

### Automatic Setup

We provide a script to help you set up a MySQL database:

```bash
python setup_mysql.py
```

This script will:
1. Check if MySQL is installed
2. Ask for your MySQL credentials
3. Create a database and user
4. Update your `.env` file with the MySQL configuration

### Manual Setup

If you prefer to set up MySQL manually:

1. Create a MySQL database and user:

```sql
CREATE DATABASE surgery_scheduler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'surgery_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON surgery_scheduler.* TO 'surgery_user'@'%';
FLUSH PRIVILEGES;
```

2. Update your `.env` file with the MySQL configuration:

```
# Option 1: Direct DATABASE_URL
DATABASE_URL=mysql+pymysql://surgery_user:your_password@localhost:3306/surgery_scheduler

# Option 2: Individual MySQL components
DB_USER=surgery_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=surgery_scheduler
```

3. Initialize the database schema:

```bash
python initialize_mysql.py
```

4. Seed the database with sample data:

```bash
python seed_database.py
```

## Migrating from SQLite to MySQL

If you've been using SQLite and want to migrate to MySQL, follow these steps:

1. Set up a MySQL database as described above.
2. Run the migration script:

```bash
python migrate_sqlite_to_mysql.py
```

This script will:
1. Connect to both SQLite and MySQL databases
2. Copy all data from SQLite to MySQL
3. Handle data type conversions

## Verifying Database Configuration

To verify that your database is properly configured:

```bash
python verify_database.py
```

This script will:
1. Check the database connection
2. Verify that all required tables exist
3. Check table constraints and relationships
4. Report on the data in the database

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the database:

1. Check that the database server is running:
   - SQLite: No server needed
   - MySQL: `sudo systemctl status mysql` (Linux) or check MySQL Workbench

2. Verify your connection parameters in the `.env` file.

3. Test the connection directly:
   - SQLite: `sqlite3 surgery_scheduler.db .tables`
   - MySQL: `mysql -u surgery_user -p -h localhost surgery_scheduler`

4. Run the connection test script:
   ```bash
   python test_db_connection.py
   ```

### Schema Issues

If tables are missing or have incorrect structure:

1. Ensure you've run the initialization script:
   ```bash
   python initialize_mysql.py
   ```

2. Check for errors in the console output.

3. Verify the database schema:
   ```bash
   python verify_database.py
   ```

### Data Migration Issues

If you're having trouble migrating data from SQLite to MySQL:

1. Ensure both databases are properly configured.

2. Check that the MySQL database has the correct schema:
   ```bash
   python initialize_mysql.py
   ```

3. Run the migration script with verbose logging:
   ```bash
   python -m logging -v DEBUG migrate_sqlite_to_mysql.py
   ```

### Environment Variables

The application uses the following environment variables for database configuration:

- `DATABASE_URL`: Direct database URL (e.g., `mysql+pymysql://user:pass@host:port/dbname`)
- `DB_USER`: MySQL username
- `DB_PASSWORD`: MySQL password
- `DB_HOST`: MySQL host
- `DB_PORT`: MySQL port
- `DB_NAME`: MySQL database name
- `SQLITE_URL`: SQLite database URL (e.g., `sqlite:///./surgery_scheduler.db`)
- `SQL_ECHO`: Set to `True` to see SQL queries in the console

These can be set in your `.env` file or as system environment variables.
