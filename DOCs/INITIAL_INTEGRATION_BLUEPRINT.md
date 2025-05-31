# Initial Integration Blueprint

**Prepared by:** Integration Architect AI

**Date:** [Current Date]

**Based on Analysis of:** `LOGs.txt`, `api/routers/equipment.py`, `api/main.py`, Project Structure

**Objective:** Provide a prioritized, actionable plan for the Senior Full-Stack Integration Engineer AI to resolve critical frontend-backend integration issues identified in the application logs, focusing initially on the `/api/equipment` endpoint failure and subsequently addressing API performance warnings.

## Overall Integration Strategy

The primary strategy is to address the most critical blocking issue first: the failure to fetch equipment data, which is causing downstream problems in the frontend (e.g., Gantt chart data loading). Once this is resolved, we will investigate and optimize the performance of other API endpoints flagged in the logs.

## Prioritized Integration Tasks

1.  **Resolve Critical `/api/equipment` Fetch Failure (CORS & 500 Internal Server Error)**
    *   **Issue(s) Addressed:** Recurring CORS error and 500 Internal Server Error for GET `/api/equipment`. This prevents equipment data from loading, impacting frontend components like the Gantt chart.
    *   **Frontend Component(s) & Store(s) Involved:** `SchedulingScreen.vue`, `MasterScheduleScreen.vue`, `DashboardScreen.vue`, `GanttChart.vue`, `scheduleStore.js`, potentially `resourceStore.js`.
    *   **Backend API Endpoint(s):** `GET /api/equipment` (defined in `api/routers/equipment.py`).
    *   **Detailed Integration Steps:**
        *   **Backend Investigation (500 Error):** Examine the implementation of the `operating_room_equipment_service.get_equipment` function (likely in `services/operating_room_equipment_service.py`). Look for potential errors in database queries, data processing, or serialization that could lead to a 500 Internal Server Error *before* the response is fully formed and hits the CORS middleware.
        *   **Backend Verification (CORS):** Although `allow_origins=["*"]` is set in `api/main.py`, double-check that no specific middleware or route definition for `/api/equipment` is inadvertently bypassing or misconfiguring CORS for this specific endpoint. Verify the request method (GET) is allowed.
        *   **Frontend Handling:** Ensure the frontend's API call in `scheduleStore.js` (and potentially `resourceStore.js`) correctly handles potential network errors, CORS issues, and 500 errors gracefully. Implement robust error logging and user feedback.
    *   **Data Contract References:** `schemas.Equipment` (defined in `api/schemas.py`).
    *   **Key V1/V2 Document Cross-References:** Review V1/V2 documentation sections related to Equipment management and API endpoints if available.
    *   **Potential Challenges & Considerations:** The 500 error is the primary mystery; it needs thorough backend debugging. The CORS error might be a symptom of the 500 error occurring early in the request lifecycle.
    *   **Assumptions Made:** Assumes the `operating_room_equipment_service.py` file contains the logic for fetching equipment data.

2.  **Investigate and Optimize Slow API Responses**
    *   **Issue(s) Addressed:** Slow API response warnings for `/auth/token`, `/surgery-types`, and `/operating-rooms`.
    *   **Frontend Component(s) & Store(s) Involved:** `AuthStore.js`, `scheduleStore.js`, `resourceStore.js`, and components that trigger these fetches (e.g., login screen, scheduling screen, resource management screen).
    *   **Backend API Endpoint(s):** `POST /api/auth/token`, `GET /api/surgery-types`, `GET /api/operating-rooms`.
    *   **Detailed Integration Steps:**
        *   **Backend Investigation:** Examine the service functions responsible for these endpoints (`auth.py` for token, `services/surgery_type_service.py` for surgery types, `services/operating_room_service.py` for operating rooms). Analyze database queries for inefficiencies (e.g., N+1 selects, missing indexes). Profile the code if necessary to identify bottlenecks.
        *   **Optimization:** Implement query optimizations (e.g., using `selectinload` or `joinedload` in SQLAlchemy), reduce the amount of data fetched if possible, or optimize data serialization.
        *   **Frontend Handling:** While backend optimization is key, ensure frontend components handle loading states appropriately during these potentially slow requests.
    *   **Data Contract References:** Relevant schemas in `api/schemas.py` (e.g., for Auth token, Surgery Type, Operating Room).
    *   **Key V1/V2 Document Cross-References:** Review V1/V2 documentation sections related to Authentication, Surgery Types, and Operating Rooms.
    *   **Potential Challenges & Considerations:** Optimizing database queries requires understanding the data model and potential usage patterns. Need to balance performance with data requirements.
    *   **Assumptions Made:** Assumes standard SQLAlchemy practices are used in the service layer.

## 8. Environmental Prerequisites & Troubleshooting

The QA Engineer has reported `ConnectionRefusedError` during performance testing, indicating potential environmental issues. The FastAPI backend is configured to run on port 8000 by default, as seen in `run_api.py`. Successful integration testing, particularly with tools like Locust, requires the frontend and performance test runner to be able to connect to the backend API on this port.

To address `ConnectionRefusedError` and ensure a stable environment for integration and testing, please perform the following checks:

1.  **Verify FastAPI Server Status:** Ensure the FastAPI application is running and accessible. Check the terminal output where you started the FastAPI server for any error messages during startup.
2.  **Check Port Availability:** Confirm that no other application is currently using port 8000 on your system. You can use system-specific commands to check port usage:
    *   **Windows (PowerShell):** `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess`
    *   **Linux/macOS:** `lsof -i :8000` or `netstat -tulnp | grep 8000`
    If another process is using port 8000, you will need to stop that process or configure the FastAPI application to run on a different port (by setting the `API_PORT` environment variable).
3.  **Verify Firewall Settings:** Ensure your operating system's firewall is not blocking incoming or outgoing connections on port 8000, especially between the machine running Locust/frontend and the machine running the FastAPI backend (if they are different).
4.  **Review System Logs:** Examine system-level logs for any network-related errors or warnings that might provide more insight into connection issues.

Addressing these environmental factors is crucial before proceeding with further integration testing.

## 9. Next Steps

This blueprint provides the foundation. The next steps involve the detailed implementation of the outlined integration points, starting with Authentication & Authorization, followed by Resource Management, and so on, according to the prioritized list.

---

*This document is a living blueprint and will be updated as integration progresses and new insights are gained.*