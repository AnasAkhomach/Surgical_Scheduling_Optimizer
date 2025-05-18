# Surgery Scheduler Frontend

This directory contains the Vue.js frontend for the Surgery Scheduler application.

## Overview

The frontend provides a user interface for managing surgeries, operating rooms, surgeons, patients, staff, appointments, and schedule optimization.

## Directory Structure

```
frontend/
├── public/                # Static assets
├── src/                   # Source code
│   ├── assets/            # Images, fonts, etc.
│   ├── components/        # Reusable Vue components
│   ├── router/            # Vue Router configuration
│   ├── store/             # Vuex store modules
│   │   ├── index.js       # Store entry point
│   │   └── modules/       # Store modules
│   ├── views/             # Page components
│   ├── App.vue            # Root component
│   └── main.js            # Application entry point
├── .browserslistrc        # Browser compatibility configuration
├── .eslintrc.js           # ESLint configuration
├── babel.config.js        # Babel configuration
├── package.json           # NPM dependencies and scripts
└── vue.config.js          # Vue CLI configuration
```

## Features

- **Authentication**: Login, logout, and user management
- **Dashboard**: Overview of surgeries, operating rooms, surgeons, and appointments
- **Surgeries**: Create, view, update, and delete surgeries
- **Schedule**: Optimize and manage surgery schedules
- **Operating Rooms**: Manage operating rooms
- **Surgeons**: Manage surgeons
- **Patients**: Manage patients
- **Staff**: Manage staff members
- **Appointments**: Manage appointments
- **Admin**: User management and settings

## Technologies Used

- **Vue.js 3**: Frontend framework
- **Vue Router**: Client-side routing
- **Vuex**: State management
- **PrimeVue**: UI component library
- **Axios**: HTTP client
- **Chart.js**: Data visualization
- **JWT**: Authentication

## Setup and Installation

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Create a `.env.local` file with the following content:

```
VUE_APP_API_URL=http://localhost:8000
```

3. Run the development server:

```bash
npm run serve
```

4. Build for production:

```bash
npm run build
```

## Running the Frontend

To run the frontend in development mode:

```bash
npm run serve
```

This will start the development server at http://localhost:8080.

## Connecting to the API

The frontend expects the API to be running at the URL specified in the `VUE_APP_API_URL` environment variable. Make sure the API is running before using the frontend.

## Testing

To run the frontend tests:

```bash
npm run test
```

## Linting

To lint the code:

```bash
npm run lint
```
