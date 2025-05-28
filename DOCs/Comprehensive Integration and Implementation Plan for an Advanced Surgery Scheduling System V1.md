# **Comprehensive Integration and Implementation Plan for an Advanced Surgery Scheduling System**

## **Introduction**

This report provides a detailed, step-by-step plan for the integration of a Vue.js frontend, a FastAPI backend, and a MySQL database for an advanced Surgery Scheduling System. A core component of this system is the Tabu Search optimization algorithm, designed to handle complex scheduling requirements, including sequence-dependent setup times (SDST). The objective is to create a robust, well-tested, and efficiently integrated application that addresses the intricate demands of surgical scheduling. This plan covers API endpoint design, frontend data handling, Tabu Search integration strategies, SDST matrix management, data validation, necessary data transformations, and a comprehensive testing strategy, ensuring all components function cohesively. The guidance provided aims to facilitate a structured development process, resulting in a high-quality software solution.

## **Part 1: API Endpoint Design & Implementation**

The design of REST API endpoints is crucial for effective communication between the Vue.js frontend and the FastAPI backend. These endpoints will serve the primary data management and operational functions of the application. Pydantic models will be used for request and response validation, ensuring data integrity. SQLAlchemy models, as defined in the backend project structure and confirmed by analysis of `models.py` , will form the basis for database interactions.  

### **1\. Endpoints for `ResourceManagementScreen.vue`**

This screen handles Operating Rooms (ORs), Staff, and Equipment.  

**a. Operating Rooms (ORs)** (Based on `OperatingRoom` SQLAlchemy model )  

**Pydantic Schemas (Example):**

 Python  
from typing import List, Optional

from pydantic import BaseModel

class OperatingRoomBase(BaseModel):

    name: str

    location: Optional\[str\] \= None

    status: str \# e.g., "Active", "Under Maintenance", "Inactive"

    primary\_service: Optional\[str\] \= None \# Renamed from primaryService for Pythonic convention

class OperatingRoomCreate(OperatingRoomBase):

    pass

class OperatingRoomUpdate(OperatingRoomBase):

    name: Optional\[str\] \= None \# All fields optional for update

    status: Optional\[str\] \= None

class OperatingRoom(OperatingRoomBase):

    room\_id: int \# Changed from id to match SQLAlchemy model

    class Config:

        orm\_mode \= True

*   
*   
* **API Endpoints:**

  * **GET `/api/operating-rooms/`**  
    * Response Body: `List`  
    * Description: Fetches all operating rooms.  
  * **POST `/api/operating-rooms/`**  
    * Request Body: `OperatingRoomCreate`  
    * Response Body: `OperatingRoom`  
    * Description: Creates a new operating room.  
  * **GET `/api/operating-rooms/{room_id}`**  
    * Response Body: `OperatingRoom`  
    * Description: Fetches a specific operating room by ID.  
  * **PUT `/api/operating-rooms/{room_id}`**  
    * Request Body: `OperatingRoomUpdate`  
    * Response Body: `OperatingRoom`  
    * Description: Updates an existing operating room.  
  * **DELETE `/api/operating-rooms/{room_id}`**  
    * Response Body: `{"message": "Operating room deleted successfully"}`  
    * Description: Deletes an operating room.

**b. Staff** (Based on `Staff` SQLAlchemy model )  

**Pydantic Schemas (Example):**  
 Python  
from typing import List, Optional

from pydantic import BaseModel

class StaffBase(BaseModel):

    name: str

    role: str \# e.g., "Surgeon", "Nurse", "Anesthetist"

    contact\_info: Optional\[str\] \= None

    specializations: Optional\[List\[str\]\] \= \# Changed from specialization (string) to list

    status: str \# e.g., "Active", "On Leave", "Inactive" (from AddStaffForm.vue)

class StaffCreate(StaffBase):

    pass

class StaffUpdate(StaffBase):

    name: Optional\[str\] \= None

    role: Optional\[str\] \= None

    status: Optional\[str\] \= None

    \# Allow partial updates

class Staff(StaffBase):

    staff\_id: int

    availability: bool \# From SQLAlchemy model

    class Config:

        orm\_mode \= True

*   
*   
* **API Endpoints:**  
  * **GET `/api/staff/`**  
    * Response Body: `List`  
  * **POST `/api/staff/`**  
    * Request Body: `StaffCreate`  
    * Response Body: `Staff`  
  * **GET `/api/staff/{staff_id}`**  
    * Response Body: `Staff`  
  * **PUT `/api/staff/{staff_id}`**  
    * Request Body: `StaffUpdate`  
    * Response Body: `Staff`  
  * **DELETE `/api/staff/{staff_id}`**  
    * Response Body: `{"message": "Staff member deleted successfully"}`

**c. Equipment** (Based on `SurgeryEquipment` SQLAlchemy model )  

**Pydantic Schemas (Example):**  
 Python  
from typing import List, Optional

from pydantic import BaseModel

class EquipmentBase(BaseModel):

    name: str

    type: str \# e.g., "Ventilator", "Surgical Laser"

    status: str \# e.g., "Available", "In Use", "Maintenance" (from AddEquipmentForm.vue)

    location: Optional\[str\] \= None \# From AddEquipmentForm.vue

class EquipmentCreate(EquipmentBase):

    pass

class EquipmentUpdate(EquipmentBase):

    name: Optional\[str\] \= None

    type: Optional\[str\] \= None

    status: Optional\[str\] \= None

    \# Allow partial updates

class Equipment(EquipmentBase):

    equipment\_id: int

    availability: bool \# From SQLAlchemy model

    class Config:

        orm\_mode \= True

*   
*   
* **API Endpoints:**  
  * **GET `/api/equipment/`**  
    * Response Body: `List[Equipment]`  
  * **POST `/api/equipment/`**  
    * Request Body: `EquipmentCreate`  
    * Response Body: `Equipment`  
  * **GET `/api/equipment/{equipment_id}`**  
    * Response Body: `Equipment`  
  * **PUT `/api/equipment/{equipment_id}`**  
    * Request Body: `EquipmentUpdate`  
    * Response Body: `Equipment`  
  * **DELETE `/api/equipment/{equipment_id}`**  
    * Response Body: `{"message": "Equipment deleted successfully"}`

### **2\. Endpoints for `SDSTManagementScreen.vue`**

This screen manages Surgery Types, the SDST Matrix, and Initial Setup Times. This aligns with functional requirements `FR-SCOPE-011` and `FR-SCOPE-012` for managing SDST data and surgery types.  

**a. Surgery Types** (Based on `SurgeryType` SQLAlchemy model )  

**Pydantic Schemas (Example):**  
 Python  
from typing import Optional, List

from pydantic import BaseModel

class SurgeryTypeBase(BaseModel):

    name: str

    code: Optional\[str\] \= None \# From AddEditSurgeryTypeModal.vue

    description: Optional\[str\] \= None

class SurgeryTypeCreate(SurgeryTypeBase):

    pass

class SurgeryTypeUpdate(SurgeryTypeBase):

    name: Optional\[str\] \= None

    \# Allow partial updates

class SurgeryType(SurgeryTypeBase):

    type\_id: int

    class Config:

        orm\_mode \= True

*   
*   
* **API Endpoints:**  
  * **GET `/api/surgery-types/`**  
    * Response Body: `List`  
  * **POST `/api/surgery-types/`**  
    * Request Body: `SurgeryTypeCreate`  
    * Response Body: `SurgeryType`  
  * **PUT `/api/surgery-types/{type_id}`**  
    * Request Body: `SurgeryTypeUpdate`  
    * Response Body: `SurgeryType`  
  * **DELETE `/api/surgery-types/{type_id}`**  
    * Response Body: `{"message": "Surgery type deleted successfully"}`

**b. SDST Matrix and Initial Setup Times** (Based on `SequenceDependentSetupTime` SQLAlchemy model )  

**Pydantic Schemas (Example):**  
 Python  
from typing import Dict, List

from pydantic import BaseModel, conint

class SDSTEntry(BaseModel):

    from\_surgery\_type\_id: int

    to\_surgery\_type\_id: int

    setup\_time\_minutes: conint(ge=0) \# Must be non-negative

class InitialSetupEntry(BaseModel):

    surgery\_type\_id: int

    setup\_time\_minutes: conint(ge=0)

class SDSTMatrixView(BaseModel): \# For bulk update from the matrix UI

    matrix: Dict\] \# {from\_type\_id\_str: {to\_type\_id\_str: time}}

    initial\_setups: Dict\[str, conint(ge=0)\] \# {type\_id\_str: time}

class SequenceDependentSetupTime(BaseModel):

    id: int

    from\_surgery\_type\_id: Optional\[int\] \= None \# Null for initial setup

    to\_surgery\_type\_id: int

    setup\_time\_minutes: int

    \# Include names for easier display on frontend if needed, joined from SurgeryType

    from\_surgery\_type\_name: Optional\[str\] \= None

    to\_surgery\_type\_name: str

    class Config:

        orm\_mode \= True

*   
*   
* **API Endpoints:**  
  * **GET `/api/sdst/entries`**  
    * Response Body: `List`  
    * Description: Fetches all individual SDST entries (including initial setups, where `from_surgery_type_id` might be null or a special value).  
  * **PUT `/api/sdst/matrix`**  
    * Request Body: `SDSTMatrixView`  
    * Response Body: `{"message": "SDST matrix updated successfully"}`  
    * Description: Allows bulk update of the entire SDST matrix and initial setup times. The backend will parse this and create/update individual `SequenceDependentSetupTime` records.  
  * **POST `/api/sdst/entry`** (For individual entry, less likely used if bulk is primary)  
    * Request Body: `SDSTEntry` or `InitialSetupEntry` (or a union type)  
    * Response Body: `SequenceDependentSetupTime`  
    * Description: Creates or updates a single SDST or initial setup entry.  
  * **DELETE `/api/sdst/entry/{entry_id}`**  
    * Response Body: `{"message": "SDST entry deleted successfully"}`

### **3\. Endpoints for `SurgerySchedulingScreen.vue`**

This screen is the main scheduling interface, displaying the Gantt chart and handling surgery assignments.  

**a. Fetching Schedule Data** (Based on `Surgery` and `SurgeryRoomAssignment` SQLAlchemy models )  

**Pydantic Schemas (Example):**  
 Python  
from typing import List, Optional, Dict

from pydantic import BaseModel

from datetime import datetime

class SurgeryBase(BaseModel):

    patient\_id: str \# Assuming patient\_id is a string identifier

    patient\_name: Optional\[str\] \= None

    surgery\_type\_id: int

    \# surgery\_type\_name: Optional\[str\] \= None \# Can be joined and added

    estimated\_duration\_minutes: int

    priority: str \# e.g., "High", "Medium", "Low"

    status: str \# e.g., "Pending", "Scheduled", "Cancelled"

    required\_resources: Optional\]\] \= {} \# e.g., {"surgeons": , "equipment": }

class SurgeryCreate(SurgeryBase):

    pass

class SurgeryUpdate(SurgeryBase): \# All fields optional for update

    patient\_id: Optional\[str\] \= None

    surgery\_type\_id: Optional\[int\] \= None

    estimated\_duration\_minutes: Optional\[int\] \= None

    priority: Optional\[str\] \= None

    status: Optional\[str\] \= None

class Surgery(SurgeryBase):

    surgery\_id: int

    \# Fields from SurgeryRoomAssignment if scheduled

    room\_id: Optional\[int\] \= None

    \# room\_name: Optional\[str\] \= None \# Can be joined

    start\_time: Optional\[datetime\] \= None \# Actual start of surgery (after setup)

    end\_time: Optional\[datetime\] \= None   \# Actual end of surgery

    \# SDST related fields, calculated by backend before sending to frontend

    sds\_time\_minutes: Optional\[int\] \= None

    preceding\_surgery\_type\_id: Optional\[int\] \= None

    class Config:

        orm\_mode \= True

class PendingSurgery(Surgery): \# Minimal representation for pending list

    pass

class ScheduledSurgery(Surgery): \# Representation for Gantt chart

    room\_id: int

    start\_time: datetime \# This is the start of the \*setup\* time on Gantt

    end\_time: datetime   \# This is the end of the \*surgery\*

    operation\_start\_time: datetime \# Actual start of surgery procedure

    \# surgeon\_name: Optional\[str\] \= None \# Can be joined

class ScheduleView(BaseModel):

    scheduled\_surgeries: List

    pending\_surgeries: List

    operating\_rooms: List \# Basic OR info for Gantt rows

*   
*   
* **API Endpoints:**  
  * **GET `/api/schedule/view`**  
    * Query Parameters: `date_from: date`, `date_to: date`  
    * Response Body: `ScheduleView`  
    * Description: Fetches all scheduled surgeries within the date range, all pending surgeries, and basic OR data for display. The backend will calculate SDST and actual start/end times for scheduled surgeries.

**b. Managing Surgeries**

* **API Endpoints:**  
  * **POST `/api/surgeries/`**  
    * Request Body: `SurgeryCreate`  
    * Response Body: `Surgery` (as a pending surgery)  
    * Description: Creates a new surgery request (initially pending).  
  * **PUT `/api/surgeries/{surgery_id}`**  
    * Request Body: `SurgeryUpdate` (can include scheduling info like `room_id`, `start_time`)  
    * Response Body: `Surgery` (updated, could be scheduled or still pending)  
    * Description: Updates an existing surgery. If `room_id` and `start_time` are provided, it implies scheduling or rescheduling. The backend must validate this move, calculate SDST, and determine the actual `end_time`.  
  * **DELETE `/api/surgeries/{surgery_id}`**  
    * Response Body: `{"message": "Surgery deleted/cancelled successfully"}`  
    * Description: Deletes a pending surgery or cancels a scheduled one.

**c. Triggering Tabu Search Optimization** (Requirement `FR-SCOPE-004` for optimization algorithm )  

**Pydantic Schemas (Example):**  
 Python  
from pydantic import BaseModel

from typing import Optional, List

from datetime import date

class OptimizationParams(BaseModel):

    date\_range\_start: date

    date\_range\_end: date

    \# Tabu search specific parameters

    max\_iterations: Optional\[int\] \= 100

    tabu\_tenure: Optional\[int\] \= 10

    \# other params like objective function weights, etc.

    \# selected\_or\_ids: Optional\[List\[int\]\] \= None \# To optimize for specific ORs

    \# surgeries\_to\_schedule\_ids: Optional\[List\[int\]\] \= None \# To optimize specific pending surgeries

class ScheduleSolution(BaseModel): \# Simplified, actual output might be more detailed

    optimized\_assignments: List \# The new schedule

    metrics: Optional\[dict\] \= None \# e.g., makespan, utilization

    message: str

*   
*   
* **API Endpoint:**  
  * **POST `/api/schedule/optimize`**  
    * Request Body: `OptimizationParams`  
    * Response Body: `ScheduleSolution`  
    * Description: Triggers the Tabu Search algorithm. The backend service will gather necessary data (surgeries, resources, SDST matrix for the given date range), run the optimizer, persist the new schedule (update `SurgeryRoomAssignment` and `Surgery` tables), and return the optimized schedule or relevant metrics.

The definition of these endpoints provides a clear contract for frontend-backend communication, leveraging Pydantic for robust data validation and SQLAlchemy for database interaction. The `orm_mode = True` in Pydantic model configurations allows easy conversion from SQLAlchemy model instances.

## **Part 2: Frontend Data Fetching & State Management**

The Vue.js frontend will use `axios` for making HTTP requests to the FastAPI backend and Pinia for centralized state management. This ensures a reactive and maintainable user interface.

### **4\. Data Fetching with `axios`**

Each relevant Vue.js component or Pinia store action will use `axios` to interact with the API endpoints defined in Part 1\.

**Example: Fetching Operating Rooms in `resourceStore.js` ()**  
 JavaScript  
// src/stores/resourceStore.js

import { defineStore } from 'pinia';

import axios from 'axios'; // Assuming axios is configured globally or imported here

// Axios instance (can be in a separate api.js file)

const apiClient \= axios.create({

  baseURL: '/api', // Matches FastAPI prefix

  headers: {

    'Content-Type': 'application/json',

  },

});

export const useResourceStore \= defineStore('resource', {

  state: () \=\> ({

    operatingRooms:,

    staff:,

    equipment:,

    isLoading: false,

    error: null,

  }),

  actions: {

    async fetchOperatingRooms() {

      this.isLoading \= true;

      this.error \= null;

      try {

        const response \= await apiClient.get('/operating-rooms/');

        this.operatingRooms \= response.data;

      } catch (err) {

        this.error \= err.response?.data?.detail |

*     
* 

| 'Failed to fetch operating rooms'; // Use notificationStore to show error toast // import { useNotificationStore } from './notificationStore'; // const notificationStore \= useNotificationStore(); // notificationStore.error(this.error); console.error(this.error); } finally { this.isLoading \= false; } }, //... other actions for add, update, delete ORs, staff, equipment async addOperatingRoom(orData) { this.isLoading \= true; this.error \= null; try { const response \= await apiClient.post('/operating-rooms/', orData); this.operatingRooms.push(response.data); // notificationStore.success('Operating Room added successfully\!'); return { success: true, data: response.data }; } catch (err) { this.error \= err.response?.data?.detail | | 'Failed to add operating room'; // notificationStore.error(this.error); return { success: false, error: this.error }; } finally { this.isLoading \= false; } }, }, }); \`\`\` This pattern of setting `isLoading`, handling errors, and updating state will be replicated for all data fetching and mutation actions in Pinia stores (`scheduleStore.js`, `resourceStore.js` ).  

### **5\. Pinia State Management**

Pinia stores will manage the application's global state.

* **`resourceStore.js`**: Manages `operatingRooms`, `staff`, `equipment`, and their availability. Actions will fetch, add, update, and delete these resources via API calls.    
*   
* **`scheduleStore.js`**: Manages `scheduledSurgeries`, `pendingSurgeries`, `surgeryTypes`, `sdsRules` (the SDST matrix), `initialSetupTimes`, and UI state like `selectedSurgeryId`, `currentDateRange` for the Gantt chart. Actions will fetch schedule data, trigger optimization, update surgery details, manage SDST data (though some SDST management might have its own store or be directly handled by `SDSTManagementScreen.vue` calling `scheduleStore` actions).    
*   
* **`notificationStore.js`**: Manages toast notifications using `ToastNotification.vue`. It provides methods like `success()`, `error()`, `warning()` that components or other stores can call.    
*   
* **`authStore.js`**: Manages user authentication state and user information.    
* 

Data related to surgeries, resources, and SDST will be fetched by actions in these stores and stored reactively. Vue components will then access this data through store getters or by directly accessing the state. User interactions that modify data will call store actions, which in turn make API requests.

### **6\. Frontend Error Handling**

Error handling is critical for a good user experience.

* **API Call Errors:** `axios` interceptors can be used to globally handle API errors (e.g., network errors, 401 Unauthorized, 403 Forbidden, 500 Internal Server Error).

**Displaying Errors:** The `ToastNotification.vue` component will be used to display user-friendly error messages. The `notificationStore` will be the central mechanism for triggering these toasts.  
 JavaScript  
// Example usage in a Pinia store action (as shown above in fetchOperatingRooms)

// import { useNotificationStore } from './notificationStore';

// const notificationStore \= useNotificationStore();

// notificationStore.error(this.error);

// Example in a component

// \<script setup\>

// import { useNotificationStore } from '@/stores/notificationStore';

// const notificationStore \= useNotificationStore();

//

// const someAction \= async () \=\> {

//   try {

//     //... perform action

//     notificationStore.success('Action completed\!');

//   } catch (e) {

//     notificationStore.error('Action failed. Please try again.');

//   }

// };

// \</script\>

*     
*   
* **Form Validation Errors:** Pydantic validation errors from FastAPI (typically 422 Unprocessable Entity) will have a `detail` field in the response, often a list of specific field errors. The frontend should parse this and display messages next to the relevant form fields, as well as a general error toast.

This setup ensures that data flows predictably through the application, state is managed centrally, and errors are communicated clearly to the user.

## **Part 3: Tabu Search Integration with FastAPI Backend**

Integrating the Python-based Tabu Search algorithm with the FastAPI backend requires careful consideration of execution model, data flow, and performance. The existing Tabu Search implementation is primarily in `app.py` and related modules like `tabu_optimizer.py` and `scheduler_utils.py`.  

### **7\. Tabu Search Integration Options**

Two primary options for integrating the Tabu Search algorithm are:

* **Option A: Direct Execution within FastAPI:**

  * **Sub-option A1 (Synchronous):** The Tabu Search Python script/functions are called directly from within a FastAPI endpoint handler. The HTTP request will block until the optimization completes.  
    * **Pros:** Simpler to implement initially.  
    * **Cons:** Can lead to long request timeouts for complex optimizations, potentially blocking FastAPI's Uvicorn workers and degrading overall application responsiveness. Not suitable for lengthy optimization tasks.  
  * **Sub-option A2 (Asynchronous using `asyncio.to_thread`):** The synchronous Tabu Search function is run in a separate thread using `await asyncio.to_thread(tabu_search_function, args)`. This prevents blocking the main FastAPI event loop.  
    * **Pros:** Relatively simple to implement for existing synchronous code. Avoids blocking the server for other requests.  
    * **Cons:** Still consumes server resources directly during execution. No built-in retry or distributed task management. Error handling within the thread needs careful management.  
* **Option B: Asynchronous Task Queue (e.g., Celery with Redis/RabbitMQ):**

  * **Description:** The FastAPI endpoint submits the optimization task to a message queue (like Redis or RabbitMQ). Separate Celery worker processes pick up tasks from the queue and execute the Tabu Search algorithm. The frontend can poll for results or use WebSockets to get notified upon completion.  
  * **Pros:** Highly scalable and robust. Decouples optimization execution from API requests. Handles long-running tasks gracefully. Supports retries, task monitoring, and distributed workers.  
  * **Cons:** Adds complexity to the architecture (Celery setup, message broker management). Requires more infrastructure.

### **8\. Selected Integration Option and Justification**

**Selected Option: Option A2 \- Direct Execution using `asyncio.to_thread`**

**Reasoning:**

* **Project Scope:** For a capstone project, setting up and managing a full Celery stack (Option B) introduces significant additional complexity and infrastructure overhead that might be beyond the primary focus of integrating the algorithm and core application features. The `Implementation Plan` and existing project structure do not suggest an existing task queue setup.    
*   
* **Performance Considerations:** While Tabu Search can be computationally intensive, for moderately sized scheduling problems typical in a capstone context, running it in a separate thread via `asyncio.to_thread` should provide acceptable responsiveness for the API. The non-functional requirement `NFR-PERF-002` mentions "efficient execution of scheduling optimization algorithms for representative datasets" , which can be targeted with this approach initially.    
*   
* **Complexity:** Option A2 offers a good balance. It leverages Python's `asyncio` capabilities to avoid blocking the main FastAPI server, making it more robust than a purely synchronous call, without the full setup of Celery.  
* **Iterative Improvement:** If, under heavier load or with larger problem instances, this approach proves insufficient, the system can later be migrated to Option B. The core Tabu Search logic would remain largely the same.

The following table compares the options:

Table 1: Tabu Search Integration Options Comparison

| Feature | Option A1: Direct Sync Execution | Option A2: Direct Async Execution (`asyncio.to_thread`) | Option B: Async Task Queue (Celery) |
| ----- | ----- | ----- | ----- |
| **Pros** | Simplest to implement. | Non-blocking API. Good for existing sync code. | Highly scalable, robust. Decouples tasks. Good for long-running processes. Retries, monitoring. |
| **Cons** | Blocks API server. Long timeouts. | Consumes server resources directly. No distributed tasks. | Complex setup. More infrastructure. |
| **Estimated Complexity** | Low | Low-Medium | High |
| **Suitability for Project** | Low (due to blocking) | High (balances simplicity and non-blocking) | Medium (overkill for initial scope) |
| **Recommendation** | Not Recommended | **Recommended** | Future consideration |

Export to Sheets

### **9\. Code Implementation for Tabu Search Execution (Option A2)**

A new FastAPI service function will orchestrate the Tabu Search execution. The existing `app.py` logic, which currently loads data from JSON and runs the optimizer, will be refactored and adapted into this service.  

* **Step 1: Refactor Tabu Search Core Logic** Ensure the main Tabu Search logic (currently in `app.py`'s `SchedulerApp.run_scheduler` and using `tabu_optimizer.py`, `scheduler_utils.py` etc. ) can be called as a function that accepts data (surgeries, rooms, SDST matrix, parameters) and returns the optimized schedule.  

Python  
\# Example: in a new file like \`tabu\_search\_service.py\` or within \`scheduling/service.py\`

from app import SchedulerApp \# Assuming app.py is refactored or its components are directly usable

\# Or directly import/use TabuOptimizer, SchedulerUtils etc.

from models import Surgery as SQLAlchemySurgery, OperatingRoom as SQLAlchemyOR, SequenceDependentSetupTime as SQLAlchemySDST \# SQLAlchemy models

\# Import Pydantic models from scheduling.schemas

from.schemas import OptimizationParams, ScheduleSolution, ScheduledSurgery \# Pydantic schemas

\# Import the algorithm's internal data models (e.g., from simple\_models.py)

from simple\_models import Surgery as AlgoSurgery, OperatingRoom as AlgoOR 

from sqlalchemy.orm import Session

import asyncio

from datetime import datetime

def \_transform\_db\_data\_to\_algo\_format(db\_surgeries: list, 

                                     db\_rooms: list, 

                                     db\_sds\_times: list):

    """

    Transforms SQLAlchemy model instances into the Python data structures

    expected by the Tabu Search algorithm (e.g., simple\_models.Surgery).

    This is a critical step detailed further in Part 6\.

    """

    algo\_surgeries\_list \=

    for db\_s in db\_surgeries:

        \# Example transformation (simplified)

        algo\_surgeries\_list.append(

            AlgoSurgery(

                surgery\_id=db\_s.surgery\_id,

                surgery\_type\_id=db\_s.surgery\_type\_id, \# Assuming AlgoSurgery uses type\_id

                duration\_minutes=db\_s.duration\_minutes,

                surgeon\_id=db\_s.surgeon\_id, \# AlgoSurgery might need surgeon object or just ID

                urgency\_level=db\_s.urgency\_level

            )

        )

    algo\_rooms\_list \=

    for db\_r in db\_rooms:

        op\_start\_time\_obj \= None

        if db\_r.operational\_start\_time: \# This field is in app.py's OR model

            \# Assuming operational\_start\_time is stored as time object or string "HH:MM:SS"

            if isinstance(db\_r.operational\_start\_time, str):

                 op\_start\_time\_obj \= datetime.strptime(db\_r.operational\_start\_time, "%H:%M:%S").time()

            else: \# Assuming it's already a time object

                op\_start\_time\_obj \= db\_r.operational\_start\_time

        algo\_rooms\_list.append(

            AlgoOR(

                room\_id=db\_r.room\_id,

                name=db\_r.name, \# Assuming AlgoOR has name

                operational\_start\_time=op\_start\_time\_obj \# Pass the time object

            )

        )

    sds\_times\_dict \= {} \# {(from\_type\_id, to\_type\_id): setup\_minutes}

    for entry in db\_sds\_times:

        \# Handle initial setup (where from\_surgery\_type\_id might be None)

        from\_key \= entry.from\_surgery\_type\_id if entry.from\_surgery\_type\_id is not None else "initial\_setup" 

        \# The algorithm's sds\_matrix might expect string keys for types or numeric IDs.

        \# For now, assume numeric IDs, and 'initial\_setup' is a special key.

        \# If type names are used, map type\_id to type\_name here.

        if from\_key not in sds\_times\_dict:

            sds\_times\_dict\[from\_key\] \= {}

        sds\_times\_dict\[from\_key\]\[entry.to\_surgery\_type\_id\] \= entry.setup\_time\_minutes

    \# Placeholder for surgery\_equipments, surgery\_equipment\_usages if needed by algo

    \# These would also be fetched from DB and transformed.

    return algo\_surgeries\_list, algo\_rooms\_list, sds\_times\_dict

def \_transform\_algo\_solution\_to\_response\_format(algo\_solution, db: Session):

    """

    Transforms the Tabu Search algorithm's output (list of assignments)

    into the ScheduleSolution Pydantic model, potentially fetching additional

    details from the DB for the response.

    Also handles persisting the solution to SurgeryRoomAssignment table.

    """

    \# algo\_solution is expected to be a list of simple\_models.SurgeryRoomAssignment objects

    \# as returned by app.SchedulerApp.run\_scheduler or tabu\_optimizer.TabuOptimizer.optimize

    \# 1\. Persist the solution (Create/Update SurgeryRoomAssignment records)

    \#    This is a critical step. For each assignment in algo\_solution:

    \#    \- Find or create a SurgeryRoomAssignment in the DB.

    \#    \- Update the main Surgery record's start\_time, end\_time, room\_id.

    \#    db.commit()

    \# 2\. Format for response

    response\_assignments \=

    for assignment in algo\_solution: \# assignment is simple\_models.SurgeryRoomAssignment

        db\_surgery \= db.query(SQLAlchemySurgery).filter(SQLAlchemySurgery.surgery\_id \== assignment.surgery\_id).first()

        if db\_surgery:

            \# The algo\_solution start\_time is likely the setup start.

            \# The operation\_start\_time needs to be calculated based on setup.

            \# This requires knowing the setup time applied by the algorithm for this specific assignment.

            \# The simple\_models.SurgeryRoomAssignment might need to store this.

            \# For now, assume assignment has 'setup\_time\_applied' or we infer it.

            \# Infer setup time (this is complex if not directly in algo\_solution)

            \# For simplicity, let's assume the algorithm has updated the DB surgery or provides enough info.

            \# Or, the algo\_solution itself contains enough detail.

            \# The 'app.py' output format:

            \# { 'surgery\_id': assignment.surgery\_id, 'room\_id': assignment.room\_id,

            \#   'start\_time': assignment.start\_time.isoformat(), \# This is setup start

            \#   'end\_time': assignment.end\_time.isoformat() } \# This is surgery end

            \# To get operation\_start\_time, we need the setup time for this specific assignment.

            \# The Tabu Search output (e.g. list of SurgeryRoomAssignment from simple\_models.py)

            \# should ideally contain the setup time used for that assignment, or enough info to re-calculate it.

            \# Let's assume the \`assignment\` object from \`algo\_solution\` has \`start\_time\` (setup start)

            \# and \`end\_time\` (surgery end), and we need to calculate \`operation\_start\_time\`.

            \# This implies the algo\_solution should also provide the setup\_duration for each assignment.

            \# If not, this transformation is more complex.

            \# The \`scheduler\_utils.initialize\_solution\` in \`app.py\` produces items with:

            \# 'setup\_time', 'start\_time' (setup start), 'operation\_start\_time', 'end\_time' (op end)

            \# We will assume the algo\_solution provides these.

            \# Find the original surgery object from the algo input to get duration

            \# This is a bit convoluted; ideally, the algo\_solution is self-contained or

            \# the persistence step updates the DB objects which are then queried.

            \# For now, let's assume the algo\_solution's assignment object has all necessary fields.

            op\_start\_time \= assignment.start\_time \# Placeholder: this needs to be calculated

            \# if 'operation\_start\_time' in assignment: \# If app.py format is used

            \#    op\_start\_time \= assignment.operation\_start\_time

            \# else: \# Needs calculation based on setup time for this specific assignment

            \#    \# This is non-trivial without setup time for THIS assignment.

            \#    \# The algo\_solution needs to be richer.

            \#    pass

            response\_assignments.append(

                ScheduledSurgery(

                    surgery\_id=db\_surgery.surgery\_id,

                    patient\_id=db\_surgery.patient\_id, \# Assuming patient\_id is on SQLAlchemySurgery

                    patient\_name=db\_surgery.patient.name if db\_surgery.patient else None, \# Example join

                    surgery\_type\_id=db\_surgery.surgery\_type\_id,

                    \# surgery\_type\_name=db\_surgery.surgery\_type\_details.name,

                    estimated\_duration\_minutes=db\_surgery.duration\_minutes,

                    priority=db\_surgery.urgency\_level,

                    status="Scheduled", \# Or from algo\_solution

                    room\_id=assignment.room\_id,

                    \# room\_name=db.query(SQLAlchemyOR).filter(SQLAlchemyOR.room\_id \== assignment.room\_id).first().name,

                    start\_time=assignment.start\_time, \# This is setup start

                    end\_time=assignment.end\_time,     \# This is surgery end

                    operation\_start\_time=op\_start\_time, \# This needs to be accurate

                    sds\_time\_minutes=None, \# This should come from the algo\_solution for this assignment

                    preceding\_surgery\_type\_id=None \# This should come from the algo\_solution

                )

            )

    return ScheduleSolution(optimized\_assignments=response\_assignments, message="Optimization complete.")

def run\_tabu\_search\_synchronous(db: Session, params: OptimizationParams) \-\> list:

    """

    The synchronous function that executes the Tabu Search.

    This will encapsulate the core logic from app.py's run\_scheduler.

    """

    \# 1\. Fetch data from DB based on params.date\_range\_start, params.date\_range\_end

    \#    \- Surgeries to be scheduled (pending or within range)

    \#    \- Operating rooms and their availability

    \#    \- Staff and their availability (if considered by the algorithm)

    \#    \- Equipment and their availability (if considered)

    \#    \- Full SDST matrix (all SequenceDependentSetupTime entries)

    \#    \- Initial setup times (part of SDST entries or separate)

    \# Example fetching (simplified \- real queries would filter by date range, status etc.)

    surgeries\_to\_schedule\_db \= db.query(SQLAlchemySurgery).filter(SQLAlchemySurgery.status \== "Pending").all() \# Or filter by date

    operating\_rooms\_db \= db.query(SQLAlchemyOR).all()

    sds\_times\_db \= db.query(SQLAlchemySDST).all()

    \# Fetch other necessary data like staff, equipment if your Tabu Search uses them.

    \# 2\. Transform data to the format expected by the Tabu Search algorithm

    \#    (e.g., lists of simple Python objects/dictionaries as used in app.py)

    algo\_surgeries, algo\_rooms, algo\_sds\_matrix \= \_transform\_db\_data\_to\_algo\_format(

        surgeries\_to\_schedule\_db, operating\_rooms\_db, sds\_times\_db

    )

    \# 3\. Instantiate and run the Tabu Search optimizer

    \#    This part adapts the logic from app.py's run\_scheduler

    \#    The \`SchedulerApp\` class itself might not be directly used if its state management

    \#    relies on file loading. Instead, its constituent parts (SchedulerUtils, TabuOptimizer)

    \#    will be instantiated with the transformed data.

    \# Assuming FeasibilityChecker, SchedulerUtils, TabuOptimizer are importable

    \# and can be initialized with data directly.

    from simple\_feasibility\_checker import FeasibilityChecker

    from scheduler\_utils import SchedulerUtils

    from tabu\_optimizer import TabuOptimizer

    \# The db\_session for these utils is None as per app.py, they operate on passed data.

    \# The \`surgery\_equipments\` and \`surgery\_equipment\_usages\` are also needed by SchedulerUtils in app.py

    \# These would need to be fetched and transformed if your algorithm uses them.

    \# For this example, passing empty lists or None if not critical for the draft algo.

    \# FeasibilityChecker in app.py takes: db\_session, surgeries\_data, operating\_rooms\_data, all\_surgery\_equipments\_data

    feasibility\_checker \= FeasibilityChecker(

        db\_session=None, \# Operates on in-memory data passed

        surgeries\_data=algo\_surgeries,

        operating\_rooms\_data=algo\_rooms,

        all\_surgery\_equipments\_data= \# Placeholder for equipment data

    )

    \# SchedulerUtils in app.py takes: db\_session, surgeries, operating\_rooms, feasibility\_checker,

    \#                                surgery\_equipments, surgery\_equipment\_usages, sds\_times

    scheduler\_utils \= SchedulerUtils(

        db\_session=None,

        surgeries=algo\_surgeries,

        operating\_rooms=algo\_rooms,

        feasibility\_checker=feasibility\_checker,

        surgery\_equipments=, \# Placeholder

        surgery\_equipment\_usages=, \# Placeholder

        sds\_times=algo\_sds\_matrix

    )

    optimizer \= TabuOptimizer(

        scheduler\_utils=scheduler\_utils,

        tabu\_list\_size=params.tabu\_tenure,

        max\_iterations=params.max\_iterations

        \# max\_no\_improvement can also be a parameter

    )

    \# The initial\_solution for optimizer.optimize() can be generated by scheduler\_utils

    \# or passed in if supporting optimization of an existing partial schedule.

    \# app.py's optimize() call: optimizer.optimize() which calls scheduler\_utils.initialize\_solution()

    optimized\_algo\_solution \= optimizer.optimize() \# This returns list of simple\_models.SurgeryRoomAssignment

    \# 4\. Persist the optimized\_algo\_solution to the database

    \#    \- Create/Update SurgeryRoomAssignment records

    \#    \- Update Surgery records (start\_time, end\_time, room\_id, status)

    \#    This logic will be part of \_transform\_algo\_solution\_to\_response\_format or done here.

    \#    For now, assume \_transform\_algo\_solution\_to\_response\_format handles persistence.

    \# For this example, let's assume persistence happens before formatting the response.

    \# This is a complex step involving mapping algo\_solution back to SQLAlchemy models.

    \# For each assignment in optimized\_algo\_solution:

    \#   existing\_assignment \= db.query(SQLAlchemySurgeryRoomAssignment).filter(...).first()

    \#   if existing\_assignment: update it

    \#   else: create new one

    \#   Update related SQLAlchemySurgery record.

    \# db.commit()

    return optimized\_algo\_solution \# Return the raw algorithm solution for now

*   
* 

**Step 2: Create FastAPI Endpoint**

 Python  
\# In scheduling/router.py

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from..dependencies import get\_db \# Assuming a dependency for DB session

from.schemas import OptimizationParams, ScheduleSolution 

\# Import the synchronous runner and transformation functions

from.service import run\_tabu\_search\_synchronous, \_transform\_algo\_solution\_to\_response\_format

import asyncio

router \= APIRouter(

    prefix="/schedule",

    tags=\["schedule"\],

)

@router.post("/optimize", response\_model=ScheduleSolution)

async def optimize\_schedule\_endpoint(

    params: OptimizationParams,

    db: Session \= Depends(get\_db)

):

    """

    Triggers the Tabu Search optimization.

    This is an asynchronous endpoint that runs the synchronous Tabu Search

    algorithm in a separate thread to avoid blocking the server.

    """

    try:

        \# Run the synchronous Tabu Search function in a separate thread

        \# The run\_tabu\_search\_synchronous function now returns the raw algorithm output

        raw\_algo\_solution \= await asyncio.to\_thread(run\_tabu\_search\_synchronous, db, params)

        if not raw\_algo\_solution:

            \# Handle case where optimization returns no solution or fails internally

            \# This might mean no feasible schedule was found by the algorithm.

            \# The frontend should be prepared for an empty optimized\_assignments list.

            return ScheduleSolution(optimized\_assignments=, message="Optimization ran, but no feasible schedule found or no assignments made.")

        \# Transform the algorithm's solution into the Pydantic response model

        \# This step also handles persisting the solution to the DB.

        \# This transformation needs to be robust.

        schedule\_solution\_response \= \_transform\_algo\_solution\_to\_response\_format(raw\_algo\_solution, db)

        \# Commit database changes after successful transformation and persistence logic

        \# within \_transform\_algo\_solution\_to\_response\_format

        db.commit() 

        return schedule\_solution\_response

    except Exception as e:

        db.rollback() \# Rollback in case of error during processing or persistence

        \# Log the exception e

        print(f"Error during optimization: {e}") \# Replace with proper logging

        raise HTTPException(status\_code=500, detail=f"An error occurred during schedule optimization: {str(e)}")

*   
* The `run_tabu_search_synchronous` function encapsulates the data fetching, transformation to the algorithm's expected format, execution of the Tabu Search (adapted from `app.py` and `tabu_optimizer.py`), and then transformation of the results back into a format suitable for the API response and database persistence. This approach effectively integrates the existing Python Tabu Search code into the FastAPI application in a non-blocking manner. The data transformation steps (detailed further in Part 6\) are crucial for bridging the gap between SQLAlchemy models and the algorithm's internal data structures.

## **Part 4: SDST Matrix Management – UI and Backend Interaction**

Effective management of the Sequence-Dependent Setup Time (SDST) matrix is critical for the accuracy of the scheduling optimization. The `SDSTManagementScreen.vue` component will provide the user interface for this, interacting with dedicated backend APIs. This addresses requirements like `FR-SDST-001` (define/modify SDST), `FR-SDST-002` (setup based on preceding/succeeding types), and `FR-SDST-004` (manage surgery types).  

### **10\. UI Design and Interaction Flow for `SDSTManagementScreen.vue`**

Based on the component structure and UI/UX considerations , the `SDSTManagementScreen.vue` will feature:  

* **Tabs:**

  * **"Manage Surgery Types":**  
    * **Display:** A table listing all defined surgery types with columns for "Surgery Type Name," "Code," and "Description."  
    * **Actions:**  
      * "Add New Surgery Type" button: Opens `AddEditSurgeryTypeModal.vue` () for creating a new type.    
      *   
      * Edit button per row: Opens `AddEditSurgeryTypeModal.vue` pre-filled for modification.  
      * Delete button per row: Prompts for confirmation before deleting a surgery type. Deleting a type will have implications for the SDST matrix and initial setup times, which the backend must handle (e.g., cascade delete related SDST entries or prevent deletion if in use).  
  * **"Manage SDST Matrix":**  
    * **Display:** A grid/table where rows represent "From Surgery Type" and columns represent "To Surgery Type." Surgery type names (and/or codes) will be used as headers.  
    * Each cell at the intersection of a "From" type and a "To" type will display an input field (e.g., `<input type="number">`) showing the current setup time in minutes.  
    * Cells where "From Type" equals "To Type" can be disabled or display a dash ('-'), as intra-type setup is often handled differently or assumed to be minimal (this depends on specific hospital protocol).  
    * The UI should clearly indicate that times are in minutes.  
    * Color-coding of cells based on SDST duration (e.g., green for \<=15 min, yellow for 16-30 min, red for \>30 min) as suggested in `SDSTManagementScreen.vue` and can provide quick visual cues.    
    *   
  * **"Manage Initial Setup Times":**  
    * **Display:** A table listing all defined surgery types in one column. An adjacent column will have an input field for the "Initial Setup Time (minutes)" for that surgery type (i.e., setup if it's the first in an OR or after a significant clean).  
    * **Actions:**  
      * "Add/Edit" button per row (or inline editing): Opens `AddEditInitialSetupModal.vue` () to define or modify the initial setup time for a selected surgery type.    
      *   
* **General Actions on the Screen:**

  * **"Save Matrix Changes" / "Save All Changes":** A prominent button to persist all modifications made in the SDST matrix and initial setup times tabs. This will trigger a bulk update API call.  
  * **"Bulk Edit SDST Values":** Button to open `BulkSDSTEditor.vue` (), allowing users to apply patterns (e.g., set all transitions from Type A to Type B to X minutes) or import/export SDST data via CSV.    
  *   
  * **Search/Filter:** A search bar to filter the list of surgery types in the matrix headers if the number of types is large.

### **11\. API Interaction for SDST Data**

The backend API (defined in Part 1, Section 2b) will handle fetching and updating SDST data.

* **Fetching SDST Data:**

  * `GET /api/surgery-types/`: Populates the surgery type management tab and the headers for the SDST matrix and initial setup times table.  
  * `GET /api/sdst/entries`: Fetches all `SequenceDependentSetupTime` records. The frontend will then transform this list into the matrix view (`sdstMatrix = time`) and the initial setup times list.  
    1. Initial setups can be identified where `from_surgery_type_id` is `None` or a special sentinel value in the `SequenceDependentSetupTime` table, or if a separate field/table is used. The `SequenceDependentSetupTime` Pydantic model includes `from_surgery_type_id: Optional[int]`.  
* **Updating SDST Data (Bulk Update):**

  * When the user clicks "Save Matrix Changes" on `SDSTManagementScreen.vue`:

The frontend compiles all values from the SDST matrix grid and the initial setup times list into the `SDSTMatrixView` Pydantic model format:  
 JSON  
// Request body for PUT /api/sdst/matrix

{

  "matrix": { // Keyed by surgery\_type\_id (as string for JSON keys)

    "1": { "1": 0, "2": 30, "3": 20 }, // From Type 1 to Type 1, 2, 3

    "2": { "1": 25, "2": 0, "3": 15 }  // From Type 2 to Type 1, 2, 3

  },

  "initial\_setups": { // Keyed by surgery\_type\_id (as string)

    "1": 45, // Initial setup for Type 1

    "2": 40  // Initial setup for Type 2

  }

}

1.   
   2. This payload is sent via `PUT /api/sdst/matrix`.  
      3. **Backend Logic (`sdst/service.py`):**  
         * The service function receives the `SDSTMatrixView` data.  
         * It iterates through `data.matrix`:  
           * For each `from_type_id_str, to_type_map` in `data.matrix.items()`:  
             * For each `to_type_id_str, time` in `to_type_map.items()`:  
               * Convert string IDs to integers.  
               * Query the `SequenceDependentSetupTime` table for an existing entry where `from_surgery_type_id == from_id` and `to_surgery_type_id == to_id`.  
               * If an entry exists, update its `setup_time_minutes` to `time`.  
               * If no entry exists and `time` is a valid number (e.g., not null if matrix cells can be empty), create a new `SequenceDependentSetupTime` record.  
               * Consider how to handle cells that might be cleared by the user (e.g., delete the DB entry or set time to a special value like \-1 if allowed, though `conint(ge=0)` prevents this).  
         * It iterates through `data.initial_setups`:  
           * For each `type_id_str, time` in `data.initial_setups.items()`:  
             * Convert string ID to integer.  
             * Query `SequenceDependentSetupTime` for an entry where `to_surgery_type_id == type_id` and `from_surgery_type_id IS NULL` (or matches a special sentinel ID for "initial state").  
             * If exists, update `setup_time_minutes`.  
             * If not, create a new record.  
         * All database operations should be part of a single transaction. If any update/creation fails, rollback all changes.  
         * Return a success message.

This bulk update approach is generally more efficient for managing a matrix than sending individual updates for each cell modification. The frontend provides a user-friendly matrix interface, and the backend translates this view model into operations on the normalized `SequenceDependentSetupTime` database table.  

## **Part 5: Data Validation Strategy**

A robust data validation strategy is essential across both frontend and backend to ensure data integrity, security, and a good user experience.

### **12\. Frontend Validation**

Frontend validation provides immediate feedback to users, improving the user experience and reducing unnecessary API calls for clearly invalid data.

* **Purpose:** Catch basic errors (e.g., empty required fields, incorrect data formats) before data submission.  
* **Techniques:**  
  * **HTML5 Built-in Validation:** Use attributes like `required`, `min`, `max`, `type="number"`, `pattern` on input fields. Browsers provide default UI for these.  
  * **Vue.js Computed Properties and Watchers:** For more complex or cross-field validation logic, computed properties can derive validation states, and watchers can trigger validation functions when data changes.  
  * **Manual Validation Functions:** Triggered on input blur or form submission.  
  * **Error Display:** Show clear, user-friendly error messages next to the problematic fields or in a summary area. The `ToastNotification.vue` component can be used for general submission errors.    
  * 

**Example in `AddOrForm.vue` ():**  
 Code snippet  
\<template\>

  \<form @submit.prevent="submitForm"\>

    \<div class="input-group"\>

      \<label for="or-name"\>Name/ID \<span class="required"\>\*\</span\>\</label\>

      \<input type="text" id="or-name" v-model="formData.name" @blur="validateField('name')"

             :class="{ 'invalid': errors.name }"\>

      \<span v-if="errors.name" class="error-message"\>{{ errors.name }}\</span\>

    \</div\>

    \<button type="submit"\>Save OR\</button\>

  \</form\>

\</template\>

\<script setup\>

import { ref } from 'vue';

// import { useNotificationStore } from '@/stores/notificationStore'; // For toast notifications

// const notificationStore \= useNotificationStore();

const formData \= ref({ name: '', location: '', status: '', primaryService: '' });

const errors \= ref({});

const validateField \= (fieldName) \=\> {

  let isValid \= true;

  // Basic required validation for name

  if (fieldName \=== 'name') {

    if (\!formData.value.name.trim()) {

      errors.value.name \= 'Operating room name is required.';

      isValid \= false;

    } else if (formData.value.name.length \> 100\) { // Example length validation

      errors.value.name \= 'Name cannot exceed 100 characters.';

      isValid \= false;

    } else {

      delete errors.value.name;

    }

  }

  // Add other field validations (e.g., status must be selected)

  if (fieldName \=== 'status') {

    if (\!formData.value.status) {

      errors.value.status \= 'Status is required.';

      isValid \= false;

    } else {

      delete errors.value.status;

    }

  }

  return isValid;

};

const validateForm \= () \=\> {

  let formIsValid \= true;

  formIsValid \= validateField('name') && formIsValid;

  formIsValid \= validateField('status') && formIsValid;

  // Validate other fields

  return formIsValid;

};

const submitForm \= async () \=\> {

  if (validateForm()) {

    // Call Pinia store action to save data

    // e.g., const result \= await resourceStore.addOperatingRoom(formData.value);

    // if (result.success) {

    //   notificationStore.success('OR saved successfully\!');

    //   emit('save'); // Close modal or navigate

    // } else {

    //   notificationStore.error(result.error |

*     
* 

| 'Failed to save OR.'); // } console.log('Form is valid, submitting:', formData.value); } else { // notificationStore.warning('Please correct the errors in the form.'); console.log('Form has errors:', errors.value); } }; \</script\>

\<style scoped\>

.required { color: red; } .error-message { color: red; font-size: 0.8em; } .invalid { border-color: red; } \</style\> \`\`\`

### **13\. Backend Validation**

Backend validation is the authoritative source of truth for data integrity, enforcing business rules and security.

* **Purpose:** Ensure all data stored in the database is valid, consistent, and adheres to business logic, regardless of frontend validation.

**FastAPI with Pydantic Models:** As shown in Part 1, Pydantic models automatically validate the structure, data types, and basic constraints (like `conint(ge=0)`) of incoming request bodies. Custom validators within Pydantic models can handle more complex field-level or cross-field validation.  
 Python  
\# In scheduling/schemas.py (extending example from Part 1\)

from pydantic import BaseModel, validator, root\_validator, conint

from typing import Optional, List

from datetime import time

class OperatingRoomCreate(BaseModel):

    name: str

    location: Optional\[str\] \= None

    status: str

    primary\_service: Optional\[str\] \= None

    \# Example: operational\_start\_time might be added from app.py's model \[1\]

    operational\_start\_time: Optional\[time\] \= None 

    @validator('name')

    def name\_must\_not\_be\_empty(cls, value):

        if not value.strip():

            raise ValueError('Name must not be empty')

        return value.strip()

    @validator('status')

    def status\_must\_be\_valid(cls, value, values): \# 'values' contains other fields if needed

        valid\_statuses \= \["Active", "Under Maintenance", "Inactive", "Available", "In Use"\] \# Consolidate from various forms

        if value not in valid\_statuses:

            raise ValueError(f"Invalid status '{value}'. Must be one of {valid\_statuses}")

        return value

    \# Example root\_validator for cross-field validation

    \# @root\_validator

    \# def check\_location\_if\_active(cls, values):

    \#     name, status, location \= values.get('name'), values.get('status'), values.get('location')

    \#     if status \== "Active" and not location:

    \#         raise ValueError(f"Location is required for Active OR: {name}")

    \#     return values

*   
*   
* **Service Layer Validation:** Business logic that Pydantic models cannot capture should be validated in the service layer before database interaction. Examples:  
  * Ensuring uniqueness for certain fields (e.g., Operating Room name, if required, though the DB can also enforce this).  
  * Checking if referenced entities exist (e.g., if a `surgery_type_id` provided in an SDST entry actually exists in the `SurgeryType` table).  
  * Validating complex interdependencies or business rules (e.g., a surgeon cannot be assigned to two overlapping surgeries).  
* **Database Level Constraints:** The MySQL database schema, defined by SQLAlchemy models , should enforce constraints like `NOT NULL`, `UNIQUE`, `FOREIGN KEY` relationships, and `CHECK` constraints where applicable. These serve as the final line of defense for data integrity. For example, `SurgeryType.name` has `unique=True`. `SequenceDependentSetupTime` has foreign keys to `SurgeryType` with `nullable=False`.    
* 

A multi-layered validation approach (frontend, API/Pydantic, service layer, database) ensures robustness. Errors caught at earlier stages provide better UX, while backend validation guarantees data integrity.

## **Part 6: Data Transformation**

Data transformation is necessary at various points to bridge differences in data structures between the frontend, backend API, database, and the Tabu Search algorithm's internal representation.

### **14\. Frontend (Vue/Pinia) to Backend (FastAPI Pydantic Models)**

* **Process:**  
  * Vue components collect user input into local reactive state (e.g., `formData` in `AddOrForm.vue`).  
  * On submission, this JavaScript object is typically passed to a Pinia store action.  
  * The Pinia store action makes an `axios` call (e.g., `apiClient.post('/operating-rooms/', formData)`).  
  * `axios` automatically serializes the JavaScript object into a JSON string for the request body.  
  * FastAPI receives the JSON request and, based on the endpoint's type hint (e.g., `or_data: OperatingRoomCreate`), Pydantic automatically parses and validates this JSON into an instance of the specified Pydantic model.  
* **Example:**  
  * `AddOrForm.vue` `formData`: `{ name: 'OR X', location: 'Wing C', status: 'Active', primaryService: 'Cardio' }`  
  * Sent as JSON: `{"name": "OR X", "location": "Wing C", "status": "Active", "primary_service": "Cardio"}` (note snake\_case if Pydantic model uses it by default or via alias).  
  * FastAPI endpoint `async def create_or(or_input: OperatingRoomCreate,...)` receives an `OperatingRoomCreate` Pydantic object.

### **15\. Backend (Pydantic/SQLAlchemy) to Frontend (Pinia/Vue)**

* **Process:**  
  * FastAPI service functions return data, often as SQLAlchemy model instances or Pydantic model instances.  
  * If an endpoint has a `response_model` defined (e.g., `response_model=OperatingRoom`), FastAPI automatically serializes the returned object into JSON. If a SQLAlchemy model is returned and `orm_mode = True` is set in the Pydantic `response_model`, Pydantic handles the conversion.  
  * `axios` on the frontend receives the JSON response.  
  * The Pinia store action (that made the `axios` call) parses `response.data` and updates its state.  
  * Vue components bound to this Pinia state reactively update their display.  
* **Example:**  
  * FastAPI endpoint returns an `OperatingRoom` Pydantic model instance.  
  * Serialized to JSON: `{"room_id": 1, "name": "OR X",...}`.  
  * `resourceStore.operatingRooms` array in Pinia is updated with this object.

### **16\. Database (SQLAlchemy Models) to Algorithm (Tabu Search Custom Structures)**

This is a critical transformation for integrating the existing Tabu Search code, which expects specific Python data structures as outlined in the `Implementation Plan` and reflected in files like `simple_models.py` and `app.py`. The SQLAlchemy models represent the database schema.  

* **Context:** The Tabu Search algorithm (e.g., `TabuOptimizer` in `tabu_optimizer.py`) likely expects:  
  1. A list of `Surgery` objects (custom class, e.g., `simple_models.Surgery` with attributes like `surgery_id`, `duration_minutes`, `surgery_type_id`, `surgeon_id`, `urgency_level`).  
  2. A list of `OperatingRoom` objects (custom class, e.g., `simple_models.OperatingRoom` with `room_id`, `name`, `operational_start_time`).  
  3. An SDST matrix as a nested dictionary: `sds_times = {(from_type_id, to_type_id): setup_minutes}` or `{'type_name_1': {'type_name_2': time}}`. The `app.py` uses numeric type IDs as keys in the example.  
  4. Potentially lists of other resources like staff and equipment if the algorithm considers them directly.  
* **Transformation Steps (within the FastAPI service, e.g., `run_tabu_search_synchronous` from Part 3):**

**Fetch Data using SQLAlchemy:**  
 Python  
db\_surgeries \= db.query(SQLAlchemySurgery).filter(...).all()

db\_rooms \= db.query(SQLAlchemyOR).all()

db\_sds\_entries \= db.query(SQLAlchemySDST).all()

db\_surgery\_types \= db.query(SQLAlchemySurgeryType).all() \# Needed for type name/ID mapping

1.   
   2. 

**Map to Algorithm's Structures:**  
 Python  
\# Assuming AlgoSurgery, AlgoOR are defined in simple\_models.py or similar

from simple\_models import Surgery as AlgoSurgery, OperatingRoom as AlgoOR

\# Create a mapping from surgery\_type\_id to surgery\_type\_name if names are needed by algo

\# surgery\_type\_map \= {st.type\_id: st.name for st in db\_surgery\_types}

algo\_surgeries\_list \=

for db\_s in db\_surgeries:

    algo\_surgeries\_list.append(

        AlgoSurgery(

            surgery\_id=db\_s.surgery\_id,

            surgery\_type\_id=db\_s.surgery\_type\_id, \# Algo expects ID

            duration\_minutes=db\_s.duration\_minutes,

            surgeon\_id=db\_s.surgeon\_id, \# Algo might expect just ID

            urgency\_level=db\_s.urgency\_level

            \# Map other required fields like required\_equipment if needed

        )

    )

algo\_rooms\_list \=

for db\_r in db\_rooms:

    op\_start\_time\_obj \= None

    \# The app.py OperatingRoom model has operational\_start\_time as a time object

    \# The SQLAlchemy OperatingRoom model does not have this field directly.

    \# This indicates a potential mismatch or that this data needs to be sourced differently

    \# for the algorithm if it's still required. For now, assume it's not critical or handled.

    \# If it IS needed, the SQLAlchemy model or a related table must store it.

    \# For example, if operational\_start\_time is stored as a string "HH:MM:SS" on db\_r:

    \# if db\_r.operational\_start\_time\_str: 

    \#    op\_start\_time\_obj \= datetime.strptime(db\_r.operational\_start\_time\_str, "%H:%M:%S").time()

    algo\_rooms\_list.append(

        AlgoOR(

            room\_id=db\_r.room\_id,

            name=db\_r.name, \# AlgoOR needs a name attribute

            operational\_start\_time=op\_start\_time\_obj \# Pass as time object

        )

    )

sds\_times\_dict\_algo \= {} \# Format: {(from\_type\_id, to\_type\_id): setup\_minutes}

                        \# This matches app.py's sds\_times structure

for entry in db\_sds\_entries:

    from\_id \= entry.from\_surgery\_type\_id

    to\_id \= entry.to\_surgery\_type\_id

    \# Handle initial setup: In app.py, initial setup uses string keys like 'initial\_setup'

    \# mapped to a dict of {to\_type\_id: time}.

    \# Here, from\_surgery\_type\_id being None could signify initial setup.

    if from\_id is None: \# This is an initial setup time

        \# The algo's sds\_times\_dict needs a specific key for initial setups.

        \# Let's use a convention, e.g., (None, to\_id) or a special string key.

        \# app.py uses: self.sds\_times\[(from\_type, to\_type)\]

        \# and for initial, it might be sds\_times\[('initial\_setup', to\_type\_id)\]

        \# For now, let's assume numeric keys and None for initial.

        \# The Tabu Search's SchedulerUtils will need to handle (None, to\_id\_key).

        \# Or, we adapt to the string key 'initial\_setup' if that's what app.py uses.

        \# The example sds\_times.json uses numeric from\_surgery\_type\_id.

        \# The app.py loader for sds\_times.json:

        \#   self.sds\_times\[(from\_type, to\_type)\] \= setup\_time

        \# The SchedulerUtils uses:

        \#   self.sds\_times\_data.get((last\_surgery\_type\_in\_room\_id, current\_surgery\_type\_id), 0\)

        \#   where last\_surgery\_type\_in\_room\_id can be None for the first surgery.

        \# So, (None, to\_id) seems compatible if None is handled as 'initial\_setup' contextually.

        \# Let's stick to (from\_id, to\_id) tuple keys.

         sds\_times\_dict\_algo\[(None, to\_id)\] \= entry.setup\_time\_minutes

    else:

         sds\_times\_dict\_algo\[(from\_id, to\_id)\] \= entry.setup\_time\_minutes

3.   
   4. This transformation bridges the gap between the structured, relational data from MySQL (via SQLAlchemy) and the potentially simpler, list/dictionary-based structures that the existing Tabu Search Python scripts might expect (as per `app.py`'s data loading from JSON ). The `Implementation Plan` also describes these target structures.    
   5. 

### **17\. Algorithm (Tabu Search Output) to Database (SQLAlchemy Models)**

* **Context:** The Tabu Search algorithm, when run, will produce an optimized schedule. This schedule is likely a list of assignments, where each assignment details which surgery is in which room at what time, including calculated setup times. The `app.py`'s `save_solution_to_json` method serializes assignments like `{'surgery_id':..., 'room_id':..., 'start_time':..., 'end_time':...}`. The `Implementation Plan` also suggests a similar structure for the schedule (`Dict of lists (OR_ID -> [surgery_info])` where `surgery_info` includes ID, start/end times, setup incurred).    
*   
* **Transformation Steps (within the FastAPI service, after Tabu Search execution):**  
  1. The Tabu Search function returns the optimized schedule (e.g., `optimized_algo_solution` from Part 3). This is likely a list of assignment objects/dictionaries.

Iterate through these assignments:  
 Python  
from models import SurgeryRoomAssignment as SQLAlchemySurgeryRoomAssignment

\# Assuming optimized\_algo\_solution is a list of objects/dicts like:

\# { 'surgery\_id': int, 'room\_id': int, 

\#   'start\_time': datetime, \# This is setup start time

\#   'end\_time': datetime,   \# This is surgery end time

\#   'operation\_start\_time': datetime, \# Actual surgery procedure start

\#   'setup\_time\_applied': int \# The setup time for this specific assignment

\# }

\# This structure is richer than app.py's JSON output and more useful.

\# The Tabu Search output should be adapted to provide this.

\# First, clear existing assignments for the optimized period/surgeries (optional, depends on strategy)

\# db.query(SQLAlchemySurgeryRoomAssignment).filter(...).delete()

for assign in optimized\_algo\_solution:

    \# Create or update SurgeryRoomAssignment record

    db\_assignment \= SQLAlchemySurgeryRoomAssignment(

        surgery\_id=assign.surgery\_id, \# or assign\['surgery\_id'\] if dict

        room\_id=assign.room\_id,

        start\_time=assign.start\_time, \# This is the setup start time

        end\_time=assign.end\_time     \# This is the surgery end time

    )

    db.add(db\_assignment)

    \# Update the main Surgery record as well

    db\_surgery \= db.query(SQLAlchemySurgery).filter(SQLAlchemySurgery.surgery\_id \== assign.surgery\_id).first()

    if db\_surgery:

        db\_surgery.room\_id \= assign.room\_id

        db\_surgery.start\_time \= assign.operation\_start\_time \# Store actual operation start

        db\_surgery.end\_time \= assign.end\_time

        db\_surgery.status \= "Scheduled"

        \# db\_surgery.applied\_setup\_time \= assign.setup\_time\_applied \# If you add such a field

db.commit() \# Commit all changes

2.   
   3.   
* This step ensures that the optimized schedule generated by the algorithm is persisted back into the MySQL database using the defined SQLAlchemy models.    
* 

The following table summarizes the key data transformations:

Table 2: Data Transformation Mapping Overview

| Data Source (Component/File) | Source Structure Example | Transformation Point | Target Structure Example | Target System (Component) | Key Transformation Logic/Notes |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Vue Form (`AddOrForm.vue`) | JS Object: `{ name: 'OR1',... }` | Pinia Action (`resourceStore.addOperatingRoom`) / `axios` | JSON: `{"name": "OR1",...}` | FastAPI Endpoint Request Body | JS Object to JSON serialization. |
| FastAPI Endpoint (`/api/operating-rooms/`) | JSON Request Body | FastAPI (Pydantic) | Pydantic Model: `OperatingRoomCreate(name='OR1',...)` | FastAPI Service Function | JSON to Pydantic model parsing and validation. |
| FastAPI Service | Pydantic Model: `OperatingRoomCreate` | SQLAlchemy ORM | SQLAlchemy Model Instance: `models.OperatingRoom(name='OR1',...)` | MySQL Database | Pydantic to SQLAlchemy model mapping, DB insertion. |
| MySQL Database (via SQLAlchemy) | `List` | FastAPI Service / `response_model` | JSON: \`\` | Vue Pinia Store (`resourceStore`) | SQLAlchemy instances to Pydantic (if `response_model` used), then to JSON. |
| MySQL Database (SQLAlchemy Models) | `List`, `List` | FastAPI Service (`_transform_db_data_to_algo_format`) | `List`, `Dict` for SDST (e.g., `{(1,2):30}` for type IDs) | Tabu Search Algorithm (`tabu_optimizer.py`) | Map SQLAlchemy model attributes to simpler Python object attributes or dictionary structures expected by the algorithm. Convert SDST entries to matrix/dict. |
| Tabu Search Algorithm Output | List of assignment dicts/objects (e.g., `[{'surgery_id':1,...}]`) | FastAPI Service (`_transform_algo_solution_to_response_format`) | `List`, update `List` | MySQL Database | Map algorithm output fields to SQLAlchemy model attributes for `SurgeryRoomAssignment` and `Surgery` tables. DB insertion/update. |
| Tabu Search Algorithm Output (Persisted) | `List` (now scheduled) | FastAPI Service / `response_model=ScheduleSolution` | JSON: `{"optimized_assignments": [{"surgery_id":1,...}]}` | Vue Pinia Store (`scheduleStore`) | SQLAlchemy instances to Pydantic `ScheduledSurgery` models, then to JSON for API response. |

Export to Sheets

## **Part 7: Comprehensive Testing Strategy**

A multi-faceted testing strategy is essential to ensure the correctness, robustness, and reliability of the integrated Surgery Scheduling System. This includes unit, integration, and end-to-end tests, with specific attention to the Tabu Search algorithm's integration.

### **18\. Unit Testing**

Unit tests focus on individual components in isolation.

* **Vue Components ():**    
  * **Tool:** Vitest (as per `vitest.config.js` ).    
  *   
  * **Scope:** Test props, emitted events, slots, computed properties, methods, and basic rendering.  
  * **Mocks:** Mock Pinia stores (e.g., using `createTestingPinia`) and API calls (`axios` mocks).  
  * **Example (`AddOrForm.vue` ):** Test that the form correctly binds to `formData`, validation messages appear for invalid input, and the `save` event is emitted with correct data on valid submission. The existing tests in `src/components/__tests__/AddOrForm.test.js` provide a good starting point.    
  *   
* **Pinia Stores ():**    
  * **Tool:** Vitest.  
  * **Scope:** Test actions (including asynchronous ones), mutations (direct state changes if any), and getters.  
  * **Mocks:** Mock API calls made by actions.  
  * **Example (`resourceStore.js` ):** Test the `fetchOperatingRooms` action: verify `isLoading` is set, `apiClient.get` is called, `operatingRooms` state is updated on success, and `error` state is set on failure.    
  *   
* **FastAPI Endpoints & Services ():**    
  * **Tool:** `pytest` with FastAPI's `TestClient`.  
  * **Scope:**  
    * **Endpoints:** Test request/response validation (Pydantic), status codes, and that correct service functions are called.  
    * **Services:** Test business logic within service functions. Mock database interactions (e.g., using `unittest.mock.patch` or by passing a mock DB session) to isolate service logic.  
  * **Example (OR Service):** Test `create_operating_room` service: verify it correctly creates an `OperatingRoom` SQLAlchemy object and calls `db.add()`, `db.commit()`.  
* **Tabu Search Algorithm Components ():**    
  * **Tool:** `pytest` or Python's `unittest`.  
  * **Scope:**  
    * `scheduler_utils.py`: Test functions like `find_next_available_time`, ensuring SDST is correctly factored in. Test `initialize_solution` for generating feasible initial schedules.  
    * `tabu_list.py`: Test methods like `add`, `is_tabu`, `decrement_tenure`, `clear`.  
    * `neighborhood_strategies.py`: Test methods like `generate_neighbor_solutions`. For each move type (swap, insert), verify it produces valid neighbor structures and correctly recalculates affected SDST and timings.  
    * `solution_evaluator.py` (or `tabu_optimizer.py`'s `calculate_cost`): Test `calculate_cost` with various schedule configurations to ensure the objective function (including SDST costs, makespan, idle time, overtime as per `tabu_optimizer.py` ) is calculated correctly.    
    *   
    * `simple_feasibility_checker.py` (or `feasibility_checker.py`): Test methods like `is_feasible`, `is_surgeon_available`, ensuring they correctly identify valid and invalid states, considering SDST's impact on timings.  
    * The existing test files like `test_scheduler_utils.py`, `test_tabu_optimizer.py`, `test_objective_function.py` should be reviewed and significantly expanded, especially to cover SDST aspects.    
    * 

### **19\. Integration Testing**

Integration tests verify interactions between different parts of the system.

* **Frontend-Backend:**  
  * **Scope:** Test Pinia store actions making actual API calls to a test instance of the FastAPI backend (which might use a separate test database).  
  * **Verification:** Ensure data flows correctly from frontend forms/actions to backend services, and responses from the backend correctly update the Pinia store and subsequently the Vue components.  
  * **Example:** In `ResourceManagementScreen.vue`, when adding a new OR, verify the `addOperatingRoom` action in `resourceStore` successfully calls the `POST /api/operating-rooms/` endpoint and the new OR appears in the list.  
* **Backend Service-Algorithm Integration:**  
  * **Scope:** This is a critical integration point. Test the FastAPI service function (e.g., `run_tabu_search_synchronous` from Part 3\) that calls the main Tabu Search execution function.  
  * **Verification:**  
    * Ensure data fetched from the database is correctly transformed into the format expected by the Tabu Search algorithm.  
    * Verify that the Tabu Search algorithm is invoked with the correct parameters.  
    * Ensure the results from the Tabu Search are correctly transformed back and persisted to the database (e.g., `SurgeryRoomAssignment` records are created/updated).  
  * **Example:** Call the `POST /api/schedule/optimize` endpoint with a defined set of surgeries, resources, and SDST data in a test database. Mock the core Tabu Search execution loop (`optimizer.optimize()`) if it's too time-consuming for this specific test, but verify the data preparation leading up to it and the result handling after it.  
* **Algorithm-Database (via Services):**  
  * **Scope:** Test that the data loading part of the optimization service correctly fetches all necessary information (surgeries, ORs, staff, equipment, SDST matrix, initial setups) from the database and that the results are correctly written back.  
  * **Setup:** Use a dedicated test database populated with specific scenarios.

### **20\. End-to-End (E2E) Testing**

E2E tests simulate real user workflows from the UI through the backend and database.

* **Tools:** Cypress or Playwright.  
* **Scope:** Test key user journeys:  
  1. User logs in.  
  2. User navigates to `ResourceManagementScreen.vue`, adds a new Operating Room, verifies it appears in the list.  
  3. User navigates to `SDSTManagementScreen.vue`, defines a new Surgery Type, updates an SDST value in the matrix, saves changes, and verifies the update.  
  4. User navigates to `SurgerySchedulingScreen.vue`, sees pending surgeries, drags a pending surgery to the Gantt chart for a specific OR and time.  
  5. User triggers the optimization process via a button.  
  6. User observes the Gantt chart updating with the optimized schedule, verifying that SDST visualization is present and conflicts (if any) are highlighted.  
  7. User clicks on a scheduled surgery to view its details, including calculated SDST.

### **21\. Specific Tests for Tabu Search Algorithm Integration**

These tests focus on the correctness of the Tabu Search algorithm's integration and its handling of SDST.

* **Data Passing Verification:**  
  * Create a test scenario where the FastAPI optimization endpoint is called.  
  * Inside the service function that invokes the Tabu Search, assert that the data structures (list of surgeries, list of ORs, SDST matrix, algorithm parameters) passed to the main Tabu Search function match exactly what was prepared from the database and request parameters.  
* **Output Structure and Feasibility Validation:**  
  * After the Tabu Search algorithm returns a solution, validate its structure (e.g., list of assignments with required fields like `surgery_id`, `room_id`, `start_time`, `end_time`, `operation_start_time`, `setup_time_applied`).  
  * Use the `FeasibilityChecker` (with correct SDST data) to verify that the returned schedule is indeed feasible according to all defined constraints.  
* **SDST Calculation Verification in Algorithm:**  
  * Design small, specific test cases with 2-3 surgeries and known SDST values.  
  * Manually calculate the expected total setup time and makespan.  
  * Invoke the Tabu Search's objective function (`SolutionEvaluator.calculate_cost` or equivalent) with these scenarios and assert that the calculated cost components related to SDST are correct.  
  * Test neighborhood move evaluations: when a swap or insertion occurs, verify that the change in SDST is correctly calculated and affects the move's evaluation.  
* **Constraint Adherence in Generated Schedules:**  
  * Set up test data with specific resource availabilities (ORs, surgeons).  
  * Run the optimizer and verify that the generated schedule does not violate these availabilities (e.g., no double-booking of an OR or surgeon).  
* **Objective Function Consistency:**  
  * For a fixed input schedule, ensure that repeated calls to the objective function yield the same score.  
  * Verify that improvements in the schedule (e.g., reducing SDST by reordering) lead to a better objective score, and vice-versa.  
* **Basic Performance Check (Optional for initial scope, but good for `NFR-PERF-002` ):**    
  * For the `POST /api/schedule/optimize` endpoint, run it with a representative dataset (e.g., 20-30 surgeries, 3-5 ORs) and measure the response time. This provides a baseline for performance.  
  * The existing test files like `test_integration_optimizer.py` and `test_tabu_optimizer.py` provide examples of setting up mock data for the optimizer, which can be adapted for these more detailed integration tests.    
  * 

This comprehensive testing strategy, covering all layers of the application and specifically targeting the Tabu Search integration with SDST, is crucial for delivering a reliable and correct Surgery Scheduling System.

## **Part 8: Guidance on Updating Tabu Search Implementation Files**

The existing Python-based Tabu Search algorithm, primarily found in `app.py` and its supporting modules (`tabu_optimizer.py`, `scheduler_utils.py`, etc., within the `anasakhomach-surgical_scheduling_optimizer` backend structure ), needs adaptation to integrate seamlessly with the FastAPI backend and MySQL database. The core algorithmic logic is valuable, but its data input/output mechanisms and execution context must change. The `Implementation Plan` and `recap-1.txt` highlight areas needing updates, especially concerning SDST.  

### **22\. Analysis of Existing Tabu Search Python Files**

* **Primary File for Adaptation:** The logic within `app.py` (, content also in ) serves as the current main orchestrator. Its `SchedulerApp` class, particularly the `load_data_from_json` and `run_scheduler` methods, encapsulates the current workflow. This workflow needs to be extracted and transformed into a callable service function within the FastAPI application.    
*   
* **Core Algorithmic Modules:**  
  * `tabu_optimizer.py`: Contains the `TabuOptimizer` class, implementing the main Tabu Search loop, including neighborhood generation calls and solution evaluation.  
  * `scheduler_utils.py`: Provides utility functions for schedule manipulation, such as `initialize_solution` (critical for generating the first schedule) and `find_next_available_time` (which must be SDST-aware).  
  * `simple_feasibility_checker.py` (or `feasibility_checker.py` if more advanced): Checks if a schedule or a move is valid.  
  * `solution_evaluator.py`: Calculates the cost/objective function of a schedule.  
  * `neighborhood_strategies.py`: Defines different ways to generate neighbor solutions.  
  * `tabu_list.py`: Implements the tabu list.  
  * `simple_models.py`: Defines the algorithm's internal, non-SQLAlchemy Python classes for `Surgery`, `OperatingRoom`, and `SurgeryRoomAssignment`. These are distinct from the SQLAlchemy models in the main `models.py`.  
* **Current Data Flow:** `app.py` loads initial data (surgeries, rooms, SDST matrix) from JSON files (`surgeries.json`, `rooms.json`, `sds_times.json` ). This is the most significant part that needs to change to database-driven input.    
* 

### **23\. Specific Code Sections Needing Updates and Why**

The goal is to make the Tabu Search algorithm a callable component that receives all necessary data as input and returns an optimized schedule, without direct file I/O or independent data loading.

* **`app.py` \- `SchedulerApp` class and `main()` function:**

  * **Why Update:** The `SchedulerApp` class and the `main()` function with `argparse` are designed for a standalone script. This structure is not suitable for integration into a FastAPI service. The data loading from JSON files (`load_data_from_json`) must be replaced.  
  * **How to Update:**  
    * The core logic of `SchedulerApp.run_scheduler` should be extracted into a new function (e.g., `execute_tabu_search_optimization(surgeries_data, rooms_data, sds_times_data, equipment_data, params)`) within a FastAPI service module (e.g., `scheduling/service.py`).  
    * This new function will receive all necessary data (surgeries, rooms, SDST matrix, etc.) as parameters, already transformed from SQLAlchemy models (as detailed in Part 6).  
    * The `main()` function and `argparse` should be removed or commented out for the service integration.  
    * The `SchedulerApp` class itself might be dissolved, with its methods becoming helper functions or part of the new service function, or its constituent components (`FeasibilityChecker`, `SchedulerUtils`, `TabuOptimizer`) being instantiated directly within the service function.  
* **Data Input for Algorithm Components (e.g., `TabuOptimizer`, `SchedulerUtils`):**

  * **Why Update:** Currently, these components are instantiated within `SchedulerApp.run_scheduler` using data loaded into `SchedulerApp` instance variables (e.g., `self.surgeries`, `self.operating_rooms`, `self.sds_times`).  
  * **How to Update:** Modify the constructors or main methods of `TabuOptimizer`, `SchedulerUtils`, `FeasibilityChecker`, `SolutionEvaluator`, and `NeighborhoodStrategies` to accept all required data (surgeries, rooms, SDST matrix, etc.) as direct parameters. They should not rely on a global or parent class state for this data.  
    * For example, `TabuOptimizer.__init__(self, scheduler_utils, tabu_list_size, max_iterations)` is fine, but `SchedulerUtils.__init__(self, db_session, surgeries, operating_rooms,... sds_times)` needs to be consistently called with data derived from the database, not from file loads. The `db_session` parameter in `SchedulerUtils` was `None` in `app.py`; it should remain so if the util operates purely on passed-in data structures.  
* **`simple_models.py` (Internal Algorithm Models):**

  * **Why Update:** These classes (`Surgery`, `OperatingRoom`, `SurgeryRoomAssignment`) define the structure the algorithm works with internally. They are currently populated from JSON in `app.py`.  
  * **How to Update:** No direct code changes to `simple_models.py` are likely needed if they correctly represent the data as per the `Implementation Plan`. However, the *instantiation* of these objects will now occur in the data transformation layer (Part 6, Step 16), mapping data from SQLAlchemy models to these `simple_models` instances. Ensure attributes like `surgery_type_id` (for `AlgoSurgery`) and `operational_start_time` (for `AlgoOR`, if still needed and how it's represented) are correctly handled.  
* **`scheduler_utils.py`:**

  * **`initialize_solution` method:**  
    * **Why Update:** As highlighted in `recap-1.txt` , this method must correctly consider SDST when placing initial surgeries. It should use the `sds_times` data (the matrix passed to it) for calculating setup times for the first surgery in an OR (initial setup) and subsequent surgeries.    
    *   
    * **How to Update:** Review and modify the logic to accurately query the `sds_times` dictionary using `(previous_surgery_type_id, current_surgery_type_id)` or `(None, current_surgery_type_id)` for initial setups. Ensure it correctly calculates start and end times including these setup durations.  
  * **`find_next_available_time` method:**  
    * **Why Update:** This is crucial for both initial solution generation and neighborhood moves. It must accurately calculate the earliest possible start time for a surgery in a given room, considering the SDST from the previously scheduled surgery in that room.  
    * **How to Update:** Ensure it correctly uses the `sds_times` parameter to fetch the appropriate setup time and adds it to the previous surgery's end time or the room's earliest availability. It also needs to check against resource availability (`operating_rooms_data`, `all_resources_data` as per `Implementation Plan` ).  
* **`tabu_optimizer.py` (or `solution_evaluator.py` for `calculate_cost`):**

  * **`calculate_cost` method:**  
    * **Why Update:** The objective function must accurately include penalties or costs associated with total SDST. `recap-1.txt` and `Implementation Plan` (, Section 4\) emphasize this. The existing `calculate_cost` in `tabu_optimizer.py` includes makespan, idle time, and overtime but needs explicit SDST cost integration.    
    * 

**How to Update:** Modify the cost calculation to sum up all setup times incurred in the schedule, using the `sds_times` data. This sum should be a component of the total cost.  
 Python  
\# Example snippet for calculate\_cost in TabuOptimizer or SolutionEvaluator

\# def calculate\_cost(self, solution): \# solution is list of simple\_models.SurgeryRoomAssignment

\#     \#... existing cost calculations for makespan, idle\_time, overtime...

\#     total\_sdst\_cost \= 0

\#     \# Group assignments by room and sort by start\_time to find sequences

\#     \# For each surgery in sequence, determine its applied setup\_time

\#     \# This info might be stored on the SurgeryRoomAssignment object by initialize\_solution or neighbor generation

\#     \# Or, it needs to be recalculated here based on sequence and sds\_times matrix

\#     \# For example, if solution items have 'setup\_time\_applied':

\#     \# total\_sdst\_cost \= sum(assignment.setup\_time\_applied for assignment in solution if hasattr(assignment, 'setup\_time\_applied'))

\#

\#     \# cost \= makespan\_weight \* makespan \+ idle\_time\_weight \* idle\_time \+ sdst\_weight \* total\_sdst\_cost

\#     return cost

*   
  *   
* **`neighborhood_strategies.py` (`generate_neighbor_solutions` method):**

  * **Why Update:** When creating neighbor solutions (e.g., by swapping or inserting surgeries), the impact on SDST must be correctly calculated. The start and end times of affected surgeries, and potentially subsequent surgeries in the same OR, will change due to different setup times. This is a key point from `recap-1.txt`.    
  *   
  * **How to Update:** For each generated neighbor:  
    * Identify the surgeries whose preceding or succeeding surgery has changed.  
    * Use the `sds_times` data to find the new setup times.  
    * Recalculate the `start_time` and `end_time` for these surgeries and any subsequent surgeries in the affected OR(s). The `recalculate_schedule_for_or` function from the `Implementation Plan` (, Section 3\) provides a blueprint for this.  
    * Ensure the neighbor solution passed to the `SolutionEvaluator` has these updated, SDST-aware timings.  
* **`simple_feasibility_checker.py` (or `feasibility_checker.py`):**

  * **`is_feasible` method (and related checks like `is_surgeon_available`):**  
    * **Why Update:** Feasibility checks must use SDST-aware timings. A surgery slot is only feasible if there's enough time for both the setup and the surgery itself without violating resource availability or OR operational hours. `recap-1.txt` flags this.    
    *   
    * **How to Update:** When checking if a surgery can be placed at a certain time, ensure the duration being checked includes `setup_time + surgery_duration`. All resource availability checks must use the actual block of time occupied (setup start to surgery end).  
* **General Refactoring:**

  * **Logging:** Adapt `print` statements or existing `logger` usage to integrate with FastAPI's logging mechanisms if desired (e.g., using FastAPI's default logger).  
  * **Error Handling:** Ensure that internal algorithm errors are handled gracefully and can be propagated back to the FastAPI service caller, perhaps via custom exceptions.  
  * **Return Values:** The main optimization function should return the optimized schedule in a well-defined format (e.g., a list of `simple_models.SurgeryRoomAssignment` instances, or dictionaries with all necessary fields like `surgery_id`, `room_id`, `start_time` (setup start), `operation_start_time`, `end_time` (surgery end), and `setup_time_applied`).

The primary shift is from a self-contained, file-driven script to a library-like module whose core optimization logic can be invoked by passing data into it. The most substantial internal changes will revolve around consistently and correctly using the `sds_times` data (derived from the database) throughout all stages: initial solution, neighborhood generation, feasibility checking, and objective function evaluation.

## **Conclusion and Next Steps**

This comprehensive plan outlines the necessary steps to integrate the Vue.js frontend, FastAPI backend, and the Python-based Tabu Search algorithm for the Surgery Scheduling System. The successful execution of this plan will result in a robust application capable of optimizing complex surgery schedules while accurately accounting for sequence-dependent setup times.

**Key Phases of Integration and Development:**

1. **API Endpoint and Pydantic Model Definition:** Establish the full set of API endpoints in FastAPI for all CRUD operations related to resources (Operating Rooms, Staff, Equipment), Surgery Types, SDST entries (individual and matrix), and Surgeries. Define corresponding Pydantic models for request validation and response structuring.  
2. **Database Model Refinement and Services:** Ensure SQLAlchemy models (`models.py` ) are complete and align with Pydantic schemas. Implement FastAPI service layers to encapsulate business logic for each resource type and scheduling operation.    
3.   
4. **Tabu Search Algorithm Adaptation:**  
   * Refactor the existing Tabu Search Python code (`app.py` logic, `tabu_optimizer.py`, `scheduler_utils.py`, etc. ) to be callable as a service function. This involves removing file-based data loading and command-line interfaces.    
   *   
   * Implement the data transformation layer to convert data between SQLAlchemy models and the algorithm's internal Python data structures (as detailed in Part 6).  
   * Critically, integrate SDST calculations thoroughly into all relevant algorithm components: initial solution generation (`scheduler_utils.py`), neighborhood move evaluation (`neighborhood_strategies.py`), objective function (`solution_evaluator.py`), and feasibility checks (`simple_feasibility_checker.py`), as emphasized in `recap-1.txt`.    
   *   
5. **Tabu Search Integration with FastAPI:** Implement the `POST /api/schedule/optimize` endpoint using the chosen strategy (Option A2: `asyncio.to_thread`), which will invoke the adapted Tabu Search algorithm.  
6. **Frontend Development and Integration:**  
   * Connect `ResourceManagementScreen.vue` to its respective backend APIs for managing ORs, staff, and equipment.  
   * Implement `SDSTManagementScreen.vue` to allow users to manage surgery types, the SDST matrix, and initial setup times, connecting it to the backend SDST APIs.  
   * Develop `SurgerySchedulingScreen.vue`, integrating the Gantt chart display, pending surgery list, and detail panel. Connect this screen to APIs for fetching schedule data, managing surgeries, and triggering the `/api/schedule/optimize` endpoint.  
   * Implement robust data fetching, state management (using Pinia stores: `resourceStore`, `scheduleStore` ), and error handling (using `ToastNotification.vue` ) across all frontend components.    
   *   
7. **Validation and Testing:** Implement comprehensive unit, integration, and end-to-end tests as outlined in Part 7, with a strong focus on testing the Tabu Search integration and SDST handling.

**Recommendations for Prioritizing Implementation Tasks:**

To ensure a structured and manageable development process, the following prioritization is recommended:

1. **Backend Foundation \- Data Models & Core CRUD APIs:**  
   * Finalize SQLAlchemy models for `SurgeryType` and `SequenceDependentSetupTime`.  
   * Implement basic FastAPI CRUD endpoints and services for `OperatingRoom`, `Staff`, `Equipment`, `SurgeryType`, and `SequenceDependentSetupTime` (for individual entries initially, matrix update can follow). This establishes the data management backbone.  
2. **Tabu Search Algorithm \- Core Adaptation & Data Flow:**  
   * Refactor the Tabu Search algorithm files (`app.py` logic into a service, `tabu_optimizer.py`, `scheduler_utils.py`, `simple_models.py`) to accept data as parameters and return structured results. This is a significant architectural shift.  
   * Implement the data transformation layer (SQLAlchemy models to algorithm's internal structures, and algorithm output back to structures suitable for DB persistence).  
3. **Tabu Search Algorithm \- SDST Logic Integration:**  
   * Focus on correctly integrating SDST calculations into `scheduler_utils.py` (for `initialize_solution` and `find_next_available_time`), `solution_evaluator.py` (for `calculate_cost`), `neighborhood_strategies.py` (for move evaluation), and `feasibility_checker.py`. This is the most complex part of the algorithm adaptation.  
4. **FastAPI Optimization Endpoint:**  
   * Implement the `POST /api/schedule/optimize` endpoint, including the call to the adapted Tabu Search function using `asyncio.to_thread`. Ensure basic data fetching for the algorithm and persistence of its results.  
5. **Frontend \- SDST Management (`SDSTManagementScreen.vue`):**  
   * Connect the UI for managing surgery types, the SDST matrix (with bulk update to `PUT /api/sdst/matrix`), and initial setup times to their backend APIs. This is crucial as SDST data is a prerequisite for meaningful optimization.  
6. **Frontend \- Resource Management (`ResourceManagementScreen.vue`):**  
   * Connect the UI for ORs, staff, and equipment to their respective CRUD APIs.  
7. **Frontend \- Scheduling Core (`SurgerySchedulingScreen.vue`):**  
   * Implement fetching and display of pending and scheduled surgeries (initially without full Gantt interactivity).  
   * Connect the "Optimize" button to the `POST /api/schedule/optimize` endpoint and display the results (e.g., update the list of scheduled surgeries; full Gantt update can be iterative).  
8. **Iterative Refinement and Full Feature Implementation:**  
   * Enhance Gantt chart interactivity (drag-and-drop, dynamic SDST visualization).  
   * Implement detailed error handling and user feedback mechanisms.  
   * Develop remaining features like reporting, notifications, and advanced Tabu Search parameters.  
9. **Comprehensive Testing:** Conduct unit, integration, and E2E tests iteratively throughout the development process. Pay special attention to testing the Tabu Search logic, SDST calculations, and data transformations.

This phased approach allows for incremental development and testing, reducing risk and enabling earlier feedback. While the integration of the Tabu Search algorithm, especially with accurate SDST handling, presents a significant challenge, adherence to this detailed plan will facilitate the development of a powerful and effective Surgery Scheduling System.

