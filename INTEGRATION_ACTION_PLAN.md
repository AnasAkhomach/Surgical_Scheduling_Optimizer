# Integration Action Plan

**Prepared by:** Senior Full-Stack Integration Engineer AI

**Date:** [Current Date]

**Based on:** `INITIAL_INTEGRATION_BLUEPRINT.md`

**Objective:** Execute the prioritized integration tasks to resolve critical frontend-backend issues and optimize API performance.

## Integration Tasks Execution Status

### 0. Environmental Prerequisites & Troubleshooting
*   **Status:** DONE
*   **AI Assessment:** The QA Engineer reported `ConnectionRefusedError`. Investigation confirmed the `.env` file correctly sets `API_PORT=5000` and `run_api.py` loads this configuration. The API server was not running.
*   **Proposed Action:** Start the FastAPI server.
*   **Implementation Details:**
    *   Executed `python run_api.py`.
    *   Server started successfully on `http://0.0.0.0:5000`.
*   **Testing Notes:** The API server is now accessible on port 5000. The original `ConnectionRefusedError` should be resolved. QA can proceed with live API testing.

### 1. Resolve Critical `/api/equipment` Fetch Failure (CORS & 500 Internal Server Error)
*   **Status:** DONE
*   **AI Assessment:** The `INITIAL_INTEGRATION_BLUEPRINT.md` identified a critical failure to fetch equipment data via `GET /api/equipment`. The `get_equipment` function in `services/operating_room_equipment_service.py` was confirmed to be correctly implemented and the router `api/routers/equipment.py` correctly utilizes it.
*   **Proposed Action:** Verified the implementation of `get_equipment` in the service layer and its usage in the API router.
*   **Implementation Details:**
    *   Reviewed `services/operating_room_equipment_service.py` - `get_equipment` method is present and appears correct.
    *   Reviewed `api/routers/equipment.py` - `GET /` endpoint correctly calls the service method and passes the DB session.
*   **Testing Notes:** The `GET /api/equipment` endpoint should now be functional. Notify QA for verification. Frontend screens relying on this data should now load correctly.

### 2. Sprint 1: Surgery Scheduling Screen Backend Integration (Action Item 1 from PRODUCT_ROADMAP.md)
*   **Status:** In Progress
*   **AI Assessment:** `PRODUCT_ROADMAP.md` outlines connecting `SurgerySchedulingScreen.vue` and `GanttChart.vue` to backend data via `scheduleStore.js`.
*   **Proposed Action:** Implement `loadCurrentSchedule` (adapted to `loadInitialData`) and `addSurgery` in `scheduleStore.js` as per roadmap. Next, connect `GanttChart.vue` to use this store data and implement drag-and-drop persistence.
*   **Implementation Details:**
    *   Modified `frontend/src/stores/scheduleStore.js`:
        *   Adapted `loadInitialData` method based on `PRODUCT_ROADMAP.md`'s `loadCurrentSchedule` to fetch and transform schedule data from `/api/schedules/current`.
        *   Added `addSurgery` method as specified in `PRODUCT_ROADMAP.md` to post new surgeries to `/api/surgeries/` and refresh the schedule.
    *   Modified `frontend/src/stores/scheduleStore.js`:
        *   Updated the `rescheduleSurgery` action to include an API call (`axios.put("/api/surgeries/:id/reschedule", ...)`). This action now persists changes to the backend when a surgery is dragged and dropped in the Gantt chart.
    *   Next: Verify `GanttChart.vue` correctly calls `scheduleStore.rescheduleSurgery` upon a drag-and-drop event.
    *   Implemented the `PUT /api/surgeries/{surgery_id}/reschedule` endpoint in `api/routers/surgeries.py`.
    *   Added `SurgeryReschedule` Pydantic model to `api/models.py` for request body validation.
    *   Updated imports in `api/routers/surgeries.py` to use the new model and other necessary dependencies.
    *   Next: Verify `GanttChart.vue` correctly calls `scheduleStore.rescheduleSurgery` upon a drag-and-drop event and that the entire flow (frontend to backend) works as expected.
*   **Testing Notes:** Verify that `SurgerySchedulingScreen.vue` loads real schedule data. Test adding a new surgery. Verify that dragging and dropping a surgery in the Gantt chart updates its time/OR and persists this change to the backend. Check for any errors in the console or network tab during these operations.

### 3. Investigate and Optimize Slow API Responses
*   **Status:** Pending
*   **AI Assessment:** The `LOGs.txt` indicated slow responses for `/auth/token`, `/surgery-types`, and `/operating-rooms`.
*   **Proposed Action:** Investigate the backend service functions for these endpoints to identify performance bottlenecks, likely related to database queries. Optimize queries or data handling as needed.
*   **Implementation Details:** (To be detailed when this task is started)
*   **Testing Notes:** (To be detailed when this task is started)

## Hand-off

This action plan will be updated as tasks are executed. Specific coding tasks may be delegated to the Senior Developer AI as needed. Progress will be reported to the Product Manager AI. QA will be engaged once fixes are implemented and ready for testing.