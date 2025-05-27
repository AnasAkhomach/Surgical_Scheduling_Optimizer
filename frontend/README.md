# Surgery Scheduling System - Frontend

A modern Vue.js frontend for the Surgery Scheduling System with Tabu Search optimization.

## Technology Stack

- **Vue.js 3**: Progressive JavaScript framework with Composition API
- **Vite**: Fast build tool and development server
- **Pinia**: Modern state management for Vue.js
- **Vue Router**: Client-side routing
- **Vue Toastification**: Toast notifications
- **Vitest**: Unit testing framework

## Features

- **Modern Architecture**: Built with Vue 3 Composition API and Pinia state management
- **Comprehensive UI**: Complete surgical scheduling interface with dashboard, scheduling, resource management
- **Real-time Updates**: WebSocket support for live schedule updates
- **Responsive Design**: Mobile-friendly interface with accessibility features
- **Advanced Scheduling**: Gantt charts, drag-and-drop scheduling, conflict detection
- **Analytics Dashboard**: KPIs, utilization reports, and performance metrics

## Setup and Installation

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Environment Configuration:

The frontend is configured to connect to the FastAPI backend at `http://localhost:8000`.
You can modify the API URL in the `.env` file if needed:

```
VITE_API_URL=http://localhost:8000/api
```

3. Run the development server:

```bash
npm run dev
```

4. Build for production:

```bash
npm run build
```

## Running the Frontend

To run the frontend in development mode:

```bash
npm run dev
```

This will start the Vite development server at http://localhost:5173.

## Connecting to the API

The frontend is configured to proxy API requests to the FastAPI backend running at http://localhost:8000.
Make sure the backend API is running before using the frontend.

### Authentication

The system uses JWT token-based authentication. Default test credentials:
- Username: `test@example.com`
- Password: `password`

## Testing

To run the frontend tests:

```bash
npm run test
```

To run tests with UI:

```bash
npm run test:ui
```

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/            # Images, fonts, etc.
│   ├── components/        # Vue components
│   │   ├── LoginScreen.vue
│   │   ├── DashboardScreen.vue
│   │   ├── SchedulingScreen.vue
│   │   └── ...
│   ├── router/            # Vue Router configuration
│   ├── services/          # API services
│   │   └── api.js         # API client
│   ├── stores/            # Pinia stores
│   │   ├── authStore.js
│   │   ├── scheduleStore.js
│   │   └── ...
│   ├── App.vue            # Root component
│   ├── main.js            # Application entry point
│   └── style.css          # Global styles
├── package.json
├── vite.config.js         # Vite configuration
└── README.md
```

## Development

### Adding New Components

1. Create component in `src/components/`
2. Add to router if it's a page component
3. Import and use in parent components

### State Management

The application uses Pinia for state management with the following stores:
- `authStore`: Authentication and user management
- `scheduleStore`: Surgery scheduling and optimization
- `resourceStore`: Operating rooms, staff, equipment
- `notificationStore`: System notifications
- `analyticsStore`: Reports and analytics

### API Integration

API calls are centralized in `src/services/api.js`. Each API module exports functions for CRUD operations:

```javascript
import { surgeryAPI } from '@/services/api';

// Get all surgeries
const surgeries = await surgeryAPI.getSurgeries();

// Create new surgery
const newSurgery = await surgeryAPI.createSurgery(surgeryData);
```

## Deployment

1. Build the application:

```bash
npm run build
```

2. The built files will be in the `dist/` directory
3. Deploy the `dist/` directory to your web server
4. Ensure the API URL is correctly configured for production

## Contributing

1. Follow Vue.js style guide
2. Use Composition API for new components
3. Add tests for new functionality
4. Ensure responsive design
5. Follow accessibility guidelines
