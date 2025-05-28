# AI-Powered Surgical Scheduling Optimizer

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4%2B-green.svg)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A comprehensive solution for surgical scheduling in healthcare environments using Python, SQLAlchemy, and a Tabu Search metaheuristic algorithm.

This system optimizes surgery scheduling by considering operating room availability, equipment requirements, surgeon specializations and preferences, surgery urgency, and overall efficiency. Key integrations include **Google Calendar** for real-time updates and an **automated email notification system**.

---

## 🚀 Getting Started

This section provides a minimal set of instructions to get the project running quickly. For more detailed setup instructions, see the [⚙️ Setup & Installation](#️-setup--installation) section.

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```
2.  **Set up a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    # Activate:
    # macOS/Linux
    source venv/bin/activate
    # Windows
    venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure basic environment variables:**
    *   Copy `.env.example` to `.env`.
    *   Ensure `DATABASE_URL` is set for SQLite (default):
        ```dotenv
        DATABASE_URL=sqlite:///./surgery_scheduler.db
        ```
5.  **Initialize the database (SQLite):**
    ```bash
    python initialize_mysql.py 
    python seed_database.py
    ```
    *(Note: `initialize_mysql.py` is used for both SQLite and MySQL in this project for schema creation via SQLAlchemy, despite its name.)*

6.  **Run the backend API:**
    ```bash
    python run_api.py
    ```
    Access the API at `http://localhost:8000`.

7.  **Run the frontend application:**
    ```bash
    cd frontend
    npm install
    npm run serve
    ```
    Access the frontend at `http://localhost:5173`.

---

## Features

* **Automated Surgery Scheduling**
  Optimizes surgery assignments to time slots, operating rooms, and surgeons based on multi-objective criteria.

* **Tabu Search Optimization**
  Uses Tabu Search to find near-optimal schedules while minimizing conflicts and maximizing utilization.

* **Resource Management**
  Tracks OR availability, equipment, and staff.

* **Constraint Handling**
  Handles availability, room suitability, setup/cleanup times, and equipment needs.

* **KPI-Based Evaluation**
  Evaluates schedules using:

  * Room Utilization Efficiency
  * Equipment Utilization
  * Surgeon Workload Balance
  * Surgeon Preference Satisfaction
  * Operational Cost Minimization

* **SQL Database Backend**
  Stores scheduling entities, constraints, and preferences with support for both MySQL and SQLite.

* **Google Calendar Integration**
  Syncs schedules to surgeons’ calendars.

* **Notification System**
  Sends email alerts on changes and daily summaries with priority queuing and retry logic.

* **Audit Logging**
  Tracks all changes to entities and user actions for compliance and security.

* **Transaction Management**
  Ensures data integrity with Unit of Work pattern and proper error handling.

* **Validation Layer**
  Validates input data and business rules before processing.

* **Modular Architecture**
  Service-oriented structure for maintainability with service facades for complex operations.

* **Data Seeding & Migration**
  Scripts included for sample data and database migrations.

---

## Technologies Used

* **Backend:**
  * **Language:** Python 3.9+
  * **Database:** MySQL/SQLite via SQLAlchemy
  * **API Framework:** FastAPI
  * **Algorithm:** Tabu Search
  * **Libraries:**
    * `SQLAlchemy` - ORM for database operations
    * `Alembic` - Database migrations
    * `FastAPI` - Web API framework
    * `Pydantic` - Data validation
    * `google-api-python-client` - Google Calendar integration
    * `python-dotenv` - Environment configuration
    * `pytest` - Testing framework
    * `uvicorn` - ASGI server

* **Frontend:**
  * **Framework:** Vue.js 3
  * **UI Library:** PrimeVue
  * **State Management:** Vuex
  * **Routing:** Vue Router
  * **HTTP Client:** Axios
  * **Charts:** Chart.js

---

## Project Structure

```bash
├── api/                           # FastAPI application (Backend)
│   ├── main.py                    # FastAPI application entry point
│   ├── auth.py                    # Authentication related utilities
│   ├── models.py                  # Pydantic models for API requests/responses
│   ├── routers/                   # API endpoint routers
│   │   ├── auth.py                # Authentication routes
│   │   ├── appointments.py        # Appointment routes
│   │   ├── operating_rooms.py     # Operating room routes
│   │   ├── patients.py            # Patient routes
│   │   ├── schedules.py           # Schedule optimization routes
│   │   ├── staff.py               # Staff routes
│   │   ├── surgeons.py            # Surgeon routes
│   │   ├── surgeries.py           # Surgery routes
│   │   ├── surgery_types.py       # Surgery Type routes
│   │   ├── users.py               # User management routes
│   │   └── websockets.py          # WebSocket routes
│   ├── test_api.py                # General API tests
│   ├── test_auth.py               # Authentication specific tests
│   └── ...                        # Other API tests
├── DOCs/                          # Documentation files
│   ├── DATABASE_SETUP.md          # Database setup guide
│   └── ...                        # Other documentation
├── frontend/                      # Vue.js application (Frontend)
│   ├── public/                    # Static assets (e.g., index.html, favicons)
│   ├── src/                       # Frontend source code
│   │   ├── App.vue                # Root Vue component
│   │   ├── main.js                # Vue application entry point
│   │   ├── assets/                # Static assets like images, global styles
│   │   ├── components/            # Reusable Vue components and page views
│   │   ├── router/                # Vue Router configuration
│   │   ├── services/              # Frontend services (e.g., API communication)
│   │   └── stores/                # Vuex/Pinia state management stores
│   ├── package.json               # NPM dependencies and scripts
│   ├── vite.config.js             # Vite configuration
│   └── README.md                  # Frontend specific README (see for detailed frontend setup)
├── migrations/                    # Alembic database migration scripts
│   ├── versions/                  # Individual migration files
│   ├── env.py                     # Alembic environment configuration
│   └── script.py.mako             # Migration script template
├── services/                      # Core business logic and service layer
│   ├── scheduling_service.py      # Facade for scheduling operations
│   ├── notification_service.py    # Handles notifications (email, etc.)
│   ├── calendar_service.py        # Google Calendar integration
│   ├── audit_service.py           # Audit logging service
│   ├── unit_of_work.py            # Unit of Work pattern for transactions
│   └── ...                        # Other service modules
├── tests/                         # Backend tests (unit, integration)
│   ├── test_tabu_optimizer.py     # Tests for the optimization algorithm
│   ├── test_services.py           # Tests for service layer components
│   ├── test_db_config.py          # Database configuration tests
│   └── ...                        # Other test files
├── utils/                         # Utility modules and helper functions
│   ├── *_calculator.py            # Various KPI calculators
│   └── ...                        # Other utility scripts
├── data/                          # Default data files (e.g., for CLI)
│   ├── rooms.json
│   ├── surgeries.json
│   └── sds_times.json
├── sample_data/                   # Sample data for seeding the database
│   ├── rooms.json
│   ├── surgeries.json
│   └── sds_times.json
├── .env.example                   # Example environment variables file
├── alembic.ini                    # Alembic configuration file
├── app.py                         # Main CLI application entry point
├── db_config.py                   # Database configuration settings
├── feasibility_checker.py         # Core feasibility checking logic
├── initialize_mysql.py            # Script to initialize database schema (SQLAlchemy based)
├── models.py                      # SQLAlchemy ORM models
├── neighborhood_strategies.py     # Strategies for Tabu Search neighborhood generation
├── README.md                      # This file
├── requirements.txt               # Python project dependencies
├── run_api.py                     # Script to run the FastAPI backend server
├── seed_database.py               # Script to seed the database with sample data
├── setup_database.py              # General database setup script
├── solution.py                    # Represents a schedule solution
├── solution_evaluator.py          # Evaluates the quality of a schedule
├── tabu_optimizer.py              # Core Tabu Search optimization algorithm
└── websocket_manager.py           # Manages WebSocket connections
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites

* Python 3.9+
* MySQL (optional, SQLite is used by default)
* Git

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 3. Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
# Activate:
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

* Copy `.env.example` to `.env`
* Update the database configuration:

```dotenv
# For SQLite (default)
DATABASE_URL=sqlite:///./surgery_scheduler.db

# For MySQL (optional)
# DB_USER=username
# DB_PASSWORD=password
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=surgery_scheduler

# SMTP Configuration for notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@example.com

# Google Calendar API
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
CALENDAR_TIMEZONE=America/New_York

# Audit Logging
AUDIT_LOG_TO_FILE=True
AUDIT_LOG_FILE=logs/audit.log

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/surgery_scheduler.log
LOG_FORMAT=text  # text or json
```

### 6. Google Calendar API Setup (Optional)

* Go to [Google Cloud Console](https://console.cloud.google.com/)
* Create a project and enable the **Google Calendar API**
* Create **OAuth 2.0 credentials** (Desktop)
* Download the `credentials.json` and place it in the root directory

#### Authorize the Application

```bash
python consent_handler.py
```

> This opens a browser to authenticate and generate `token.json`
>
> **Security Note**: Add `credentials.json` and `token.json` to `.gitignore`

---

## Database Initialization

### 1. SQLite (Default for Development)

```bash
# Initialize the database schema
python initialize_mysql.py

# Seed the database with sample data
python seed_database.py

# Verify the database setup
python verify_database.py
```

### 2. MySQL (Recommended for Production)

```bash
# Set up MySQL database (interactive)
python setup_mysql.py

# Initialize the database schema
python initialize_mysql.py

# Seed the database with sample data
python seed_database.py

# Verify the database setup
python verify_database.py
```

### 3. Migrating from SQLite to MySQL

If you've been using SQLite and want to migrate to MySQL:

```bash
# Set up MySQL database first
python setup_mysql.py

# Migrate data from SQLite to MySQL
python migrate_sqlite_to_mysql.py
```

For detailed database configuration instructions, see [DATABASE_SETUP.md](DOCs/DATABASE_SETUP.md).

---

## How to Run

### Run the Scheduler CLI

```bash
python app.py --surgeries data/surgeries.json --rooms data/rooms.json --output schedule.json
```

#### Command-line Options

* `--surgeries`: Path to surgeries JSON file
* `--rooms`: Path to operating rooms JSON file
* `--sds`: Path to sequence-dependent setup times JSON file (optional)
* `--output`: Path to output JSON file (optional)
* `--iterations`: Maximum iterations for Tabu Search (default: 100)
* `--tabu-size`: Size of tabu list (default: 10)

#### Output

* Console logs showing:
  * Initialization steps
  * Tabu Search progress
  * Final schedule metrics
* JSON file with the optimized schedule (if `--output` is specified)

### Run the FastAPI Application

```bash
python run_api.py
```

This will start the FastAPI application at http://localhost:8000.

API documentation will be available at:
* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

### Run the Vue.js Frontend

```bash
cd frontend
npm install
npm run serve
```

This will start the Vue.js development server at http://localhost:8080.

---

## 🚀 Deployment

Deploying this application to a production environment involves deploying the backend (FastAPI) and frontend (Vue.js) applications separately. Here are some general considerations:

### Backend (FastAPI)

*   **Database**: While SQLite is suitable for development, a production-grade database like **MySQL** or PostgreSQL is recommended. Ensure your `.env` file is configured with the production database credentials.
*   **WSGI Server**: FastAPI applications are typically served using an ASGI server. For production, use a robust server like **Gunicorn** with Uvicorn workers (e.g., `gunicorn -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py api.main:app`).
*   **Environment Variables**: Securely manage your `.env` file or use environment variables provided by your deployment platform for sensitive information like database credentials and API keys.
*   **HTTPS**: Ensure the application is served over HTTPS. A reverse proxy like Nginx or Caddy can be used to handle HTTPS termination, load balancing, and serving static files.
*   **Logging**: Configure production-level logging to capture important events and errors. The application already includes logging capabilities; ensure the `LOG_LEVEL` and `LOG_FILE` (or a centralized logging solution) are appropriately set.

### Frontend (Vue.js)

*   **Build for Production**: Build the Vue.js application for production. This typically creates optimized static assets (HTML, CSS, JavaScript).
    ```bash
    cd frontend
    npm run build
    ```
*   **Serving Static Files**: The built frontend assets (usually found in the `dist` directory) can be served by a web server like Nginx, Apache, or a CDN. Configure the web server to serve `index.html` for any routes that are part of the Vue.js application to support client-side routing.

### General Considerations

*   **Separate Servers/Services**: The backend API and the frontend application are often deployed on separate servers or services for better scalability and management.
*   **CORS**: Ensure Cross-Origin Resource Sharing (CORS) is correctly configured in the FastAPI application if the frontend and backend are served from different domains.
*   **Monitoring**: Implement monitoring for both backend and frontend to track performance, uptime, and errors.

### Future: Dockerization

*   Dockerization of the application is listed as a [Future Enhancement](#future-enhancements). Using Docker containers would simplify the deployment process by packaging the application and its dependencies together.

---

## Testing

Run the test suite:

```bash
pytest
```

Run specific tests:

```bash
pytest test_tabu_optimizer.py
pytest test_db_config.py
```

---

## Algorithm Spotlight: Tabu Search

A metaheuristic approach tailored for complex scheduling:

* **Solution Representation**: Surgery-room-time-surgeon assignments
* **Neighbor Moves**:
  * Reassign surgery to another time/room
  * Swap surgeries
  * Shift start times
* **Tabu List**: Prevents short-term cycles
* **Evaluation Function**:
  * Room/Equipment Utilization
  * Surgeon Idle Time
  * Preference Satisfaction
  * Cost Minimization
* **Termination**: Iteration count or stagnation

---

## Future Enhancements

* Real-time conflict detection
* ML models for surgery duration prediction
* Advanced constraint configurations
* Dockerization
* Multi-day scheduling
* Recurring surgeries
* Mobile application
* Advanced reporting and analytics
* Integration with hospital EHR systems

---

## 🤝 Contributing

Contributions are welcome and greatly appreciated! This project thrives on community involvement. If you have suggestions for improvements, bug fixes, or new features, please feel free to contribute.

### Steps to Contribute

1.  **Fork the Repository**: Start by forking the project to your own GitHub account.
2.  **Create a Branch**: Create a new branch in your forked repository for your changes. Use a descriptive branch name (e.g., `feature/add-new-reporting-module` or `fix/resolve-scheduling-conflict-bug`).
    ```bash
    git checkout -b feature/your-feature-name
    ```
3.  **Make Your Changes**: Implement your feature or bug fix.
4.  **Commit Your Changes**: Write clear, concise commit messages.
    ```bash
    git commit -m "Add: Brief description of your change"
    ```
5.  **Adhere to Coding Standards**:
    *   Follow existing code style and conventions (e.g., PEP 8 for Python).
    *   Ensure your code is well-commented, especially in complex areas.
6.  **Test Your Changes**:
    *   Ensure all existing tests pass:
        ```bash
        pytest
        ```
    *   Add new tests for any new features or bug fixes to maintain or improve test coverage.
7.  **Push to Your Branch**:
    ```bash
    git push origin feature/your-feature-name
    ```
8.  **Open a Pull Request (PR)**: Go to the original repository and open a Pull Request from your forked branch.
    *   Provide a clear title and detailed description of your changes in the PR.
    *   Reference any relevant issues (e.g., "Closes #123").

### Issue Tracking

*   Before submitting a new issue, please check the existing [issues](<your-repo-url>/issues) to see if a similar one has already been reported.
*   When reporting a new issue, provide as much detail as possible, including steps to reproduce, expected behavior, and actual behavior.

We look forward to your contributions!

---

## License

This project is licensed under the **MIT License**. See the `LICENSE.md` file for details.
