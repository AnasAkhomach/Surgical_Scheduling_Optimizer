# AI-Powered Surgical Scheduling Optimizer

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4%2B-green.svg)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A comprehensive solution for surgical scheduling in healthcare environments using Python, SQLAlchemy, and a Tabu Search metaheuristic algorithm.

This system optimizes surgery scheduling by considering operating room availability, equipment requirements, surgeon specializations and preferences, surgery urgency, and overall efficiency. Key integrations include **Google Calendar** for real-time updates and an **automated email notification system**.

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
├── api/                           # FastAPI application
│   ├── main.py                    # FastAPI entry point
│   ├── auth.py                    # Authentication utilities
│   ├── models.py                  # Pydantic models
│   ├── routers/                   # API route handlers
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── users.py               # User management endpoints
│   │   ├── surgeries.py           # Surgery management endpoints
│   │   ├── operating_rooms.py     # Operating room management endpoints
│   │   ├── surgeons.py            # Surgeon management endpoints
│   │   ├── patients.py            # Patient management endpoints
│   │   ├── staff.py               # Staff management endpoints
│   │   ├── appointments.py        # Appointment management endpoints
│   │   └── schedules.py           # Schedule optimization endpoints
│   └── test_api.py                # API tests
├── frontend/                      # Vue.js frontend
│   ├── public/                    # Static assets
│   ├── src/                       # Source code
│   │   ├── assets/                # Images, fonts, etc.
│   │   ├── components/            # Reusable Vue components
│   │   ├── router/                # Vue Router configuration
│   │   ├── store/                 # Vuex store modules
│   │   ├── views/                 # Page components
│   │   ├── App.vue                # Root component
│   │   └── main.js                # Application entry point
│   └── package.json               # NPM dependencies and scripts
├── migrations/                    # Alembic database migrations
├── services/                      # Domain logic and services
│   ├── appointment_service.py     # Appointment management
│   ├── audit_service.py           # Audit logging
│   ├── calendar_service.py        # Google Calendar integration
│   ├── exceptions.py              # Custom exceptions
│   ├── logger_config.py           # Logging configuration
│   ├── notification_service.py    # Email and notification handling
│   ├── operating_room_service.py  # Operating room management
│   ├── patient_service.py         # Patient management
│   ├── scheduling_service.py      # Scheduling facade
│   ├── staff_service.py           # Staff management
│   ├── surgeon_service.py         # Surgeon management
│   ├── surgery_service.py         # Surgery management
│   ├── unit_of_work.py            # Transaction management
│   ├── validation.py              # Validation framework
│   └── validators.py              # Entity validators
├── utils/                         # KPI calculators and helper utilities
├── .env.example                   # Template for environment variables
├── alembic.ini                    # Alembic configuration
├── app.py                         # CLI application entry point
├── consent_handler.py             # Google OAuth flow
├── daily_notifications.py         # Daily email summary script
├── db_config.py                   # Database configuration
├── feasibility_checker.py         # Constraint checking
├── initialize_data.py             # Initial data population
├── models.py                      # SQLAlchemy models
├── neighborhood_strategies.py     # Tabu Search move strategies
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── run_api.py                     # Script to run the FastAPI application
├── seed_database.py               # DB seeding script
├── setup_database.py              # DB setup and initialization
├── solution.py                    # Solution representation
├── solution_evaluator.py          # Schedule evaluation
├── tabu_optimizer.py              # Tabu Search implementation
└── test_*.py                      # Test files
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

### 1. Create Database and Tables

```bash
python setup_database.py --create-tables
```

### 2. Run Database Migrations

```bash
python setup_database.py --migrations
```

### 3. Seed Sample Data

```bash
python seed_database.py
```

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

## License

This project is licensed under the **MIT License**. See the `LICENSE.md` file for details.
