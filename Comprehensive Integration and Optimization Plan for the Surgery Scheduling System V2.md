# **Comprehensive Integration and Optimization Plan for the Surgery Scheduling System**

## **1\. Introduction**

**Purpose of this Document**

This document outlines a comprehensive, step-by-step plan to facilitate the seamless integration of the Vue.js frontend, the FastAPI backend, and the Python-based Tabu Search optimization algorithm for the Surgery Scheduling System. The primary objective is to guide the development process towards a cohesive and fully functional application capable of addressing the complex demands of modern surgical scheduling.

**Key Challenges Addressed**

The development of such a system presents several inherent challenges that this plan aims to systematically address:

* **Seamless Frontend-Backend Communication**: Establishing robust and efficient communication protocols between the Vue.js client and the FastAPI server is paramount. This involves defining clear API contracts and ensuring data is exchanged reliably.  
* **Robust Integration and Execution of the Tabu Search Algorithm**: Integrating the existing Python Tabu Search implementation with the FastAPI backend in a manner that is both efficient and non-blocking requires careful architectural consideration.  
* **Effective Management and Utilization of Sequence-Dependent Setup Times (SDST)**: SDST is a critical factor influencing schedule efficiency. The system must allow for accurate management of SDST data and ensure the optimization algorithm correctly incorporates these dependencies.  
* **Ensuring Data Integrity through Validation**: Implementing comprehensive data validation mechanisms at both frontend and backend levels is crucial to maintain data accuracy and prevent errors.  
* **Comprehensive Testing of the Integrated System**: A thorough testing strategy is necessary to ensure all components function correctly in isolation and as an integrated whole.

The successful execution of this plan depends significantly on the precision of the interfaces and data contracts established between the various components of the system. Even minor discrepancies in data representation or API expectations can propagate through the system, leading to integration failures or incorrect behavior. The complexity introduced by Sequence-Dependent Setup Times further underscores this point, as its consistent representation and calculation across the frontend, backend, and optimization algorithm are vital for the system's accuracy and effectiveness. Therefore, this plan places considerable emphasis on meticulous API design, clear data modeling (particularly using Pydantic for FastAPI interactions), and well-defined data transformation procedures.

**Expected Outcome**

Upon successful implementation of this plan, the Surgery Scheduling System will be a fully functional application. Users will be able to manage essential resources (operating rooms, staff, equipment), define and manage surgery types and their associated SDST matrix, input and manage pending surgeries, trigger the Tabu Search optimization process, and visualize the generated, optimized schedules.

**Document Structure**

This report is structured to provide a logical flow through the integration process:

* **Section 2**: Details the design and implementation of the backend REST API using FastAPI.  
* **Section 3**: Focuses on the frontend integration, including data flow within Vue.js components and state management with Pinia.  
* **Section 4**: Discusses strategies for integrating the Python-based Tabu Search algorithm with the FastAPI backend.  
* **Section 5**: Outlines the end-to-end workflow for managing the SDST matrix.  
* **Section 6**: Describes comprehensive data validation strategies for both frontend and backend.  
* **Section 7**: Details necessary data transformations between different layers of the application.  
* **Section 8**: Provides guidance on refining and operationalizing the existing Python Tabu Search implementation.  
* **Section 9**: Offers a detailed testing strategy for the entire system.  
* **Section 10**: Delves into specific code updates required within the Python Tabu Search implementation files.  
* **Section 11**: Concludes with a summary and recommended next steps.

## **2\. Backend API Design and Implementation (FastAPI)**

**Guiding Principles**

The design of the FastAPI backend will adhere to established best practices to ensure a robust, maintainable, and scalable system:

* **RESTful API Design**: Endpoints will be designed following REST principles, utilizing standard HTTP methods (GET, POST, PUT, DELETE) for resource manipulation.  
* **Clear, Consistent, and Predictable Endpoint Naming**: Endpoint paths will be intuitive and consistently structured (e.g., `/api/resource-name/`, `/api/resource-name/{resource_id}`).  
* **Pydantic Models for Data Contracts**: Pydantic models will be extensively used for request body validation, response serialization, and to establish clear, unambiguous data contracts between the frontend and backend. This is a core strength of FastAPI and significantly aids in maintaining data integrity.    
*   
* **Granularity and Cohesion**: API endpoints will be granular enough to support the specific data needs of individual frontend components, yet consolidated where logically appropriate to minimize unnecessary HTTP requests and improve performance.

The structure of the existing SQLAlchemy models in `models.py` must be meticulously mapped to these Pydantic schemas. Any inconsistencies in field names (e.g., `primaryService` in Vue components versus a Pythonic `primary_service`), data types (e.g., `datetime` objects versus string representations), or optionality between the SQLAlchemy ORM models and the Pydantic schemas can lead to validation errors or data serialization issues. Therefore, careful attention to these details, including the use of `orm_mode = True` in Pydantic response models, is essential for smooth data flow.  

**Defining REST API Endpoints for Core Frontend Screens**

The following API endpoints are proposed to support the functionalities of the key frontend Vue.js components identified in the project :  

**`ResourceManagementScreen.vue` Related Endpoints**  

* **Operating Rooms (ORs)**:  
  * `GET /api/operating-rooms/`: Retrieve a list of all operating rooms.  
  * `POST /api/operating-rooms/`: Create a new operating room.  
  * `GET /api/operating-rooms/{or_id}`: Retrieve details of a specific operating room.  
  * `PUT /api/operating-rooms/{or_id}`: Update an existing operating room.  
  * `DELETE /api/operating-rooms/{or_id}`: Delete an operating room.  
* **Staff**:  
  * `GET /api/staff/`: Retrieve a list of all staff members.  
  * `POST /api/staff/`: Create a new staff member.  
  * `GET /api/staff/{staff_id}`: Retrieve details of a specific staff member.  
  * `PUT /api/staff/{staff_id}`: Update an existing staff member.  
  * `DELETE /api/staff/{staff_id}`: Delete a staff member.  
* **Equipment**:  
  * `GET /api/equipment/`: Retrieve a list of all equipment.  
  * `POST /api/equipment/`: Create new equipment.  
  * `GET /api/equipment/{equipment_id}`: Retrieve details of specific equipment.  
  * `PUT /api/equipment/{equipment_id}`: Update existing equipment.  
  * `DELETE /api/equipment/{equipment_id}`: Delete equipment.

The `ResourceManagementScreen.vue` component features three distinct tabs for ORs, Staff, and Equipment. While separate endpoints for each resource type are logical for CRUD operations, consideration should be given to how data is loaded initially. If each tab switch triggers multiple API calls for slightly different views of the same underlying data, it could lead to an inefficient and "chatty" API, potentially degrading user experience. A strategy might involve fetching all data for a resource type upon first activating its tab, with subsequent filtering and sorting handled client-side, or implementing more sophisticated server-side filtering options within the GET endpoints.  

**`SDSTManagementScreen.vue` / `SDSTDataManagementScreen.vue` Related Endpoints**  

The project documents indicate two components for SDST management: `SDSTManagementScreen.vue` and `SDSTDataManagementScreen.vue`. The latter appears more feature-rich with a tabbed interface for Surgery Types, SDST Matrix, and Initial Setup Times, and integrates modals like `AddEditSurgeryTypeModal.vue` and `AddEditInitialSetupModal.vue`. The API design will cater to these functionalities.  

* **Surgery Types**:  
  * `GET /api/surgery-types/`: List all surgery types.  
  * `POST /api/surgery-types/`: Create a new surgery type.  
  * `GET /api/surgery-types/{type_id}`: Get a specific surgery type.  
  * `PUT /api/surgery-types/{type_id}`: Update a surgery type.  
  * `DELETE /api/surgery-types/{type_id}`: Delete a surgery type.  
* **SDST Matrix Entries / Rules**:  
  * `GET /api/sdst-matrix/`: Retrieve the entire SDST matrix (e.g., as a nested dictionary `{[from_type_id]: {[to_type_id]: time}}`). This aligns with how `scheduleStore.js` structures `sdsRules`.    
  *   
  * `PUT /api/sdst-matrix/`: Update the entire SDST matrix. This is suitable for changes made via `BulkSDSTEditor.vue` or after multiple inline edits in `SDSTDataManagementScreen.vue` followed by a "Save Matrix Changes" action.    
  *   
  * Alternatively, for more granular updates reflecting direct cell edits in the UI:  
    * `POST /api/sdst-rules/`: Create a new SDST rule.  
    * `PUT /api/sdst-rules/{from_type_id}/{to_type_id}`: Update a specific SDST rule (using composite keys).  
    * `DELETE /api/sdst-rules/{from_type_id}/{to_type_id}`: Delete a specific SDST rule.  
* **Initial Setup Times**:  
  * `GET /api/initial-setup-times/`: List all initial setup times (e.g., as a dictionary `{surgery_type_id: time}`).  
  * `POST /api/initial-setup-times/`: Create or update an initial setup time for a specific surgery type. (Request body: `{"surgery_type_id": X, "time_minutes": Y}`).  
  * `GET /api/initial-setup-times/{surgery_type_id}`: Get initial setup time for a specific surgery type.  
  * `DELETE /api/initial-setup-times/{surgery_type_id}`: Delete initial setup time for a surgery type.

**`SurgerySchedulingScreen.vue` Related Endpoints**  

* `GET /api/surgeries/`: List all scheduled surgeries. Query parameters should be supported for filtering by date range, OR, status, surgeon, etc., to support the views in the Gantt chart.  
* `POST /api/surgeries/`: Schedule a new surgery. The request body will contain all necessary surgery details, including patient info, type, duration, resource requirements, and intended start time/OR.  
* `GET /api/surgeries/{surgery_id}`: Retrieve details of a specific scheduled surgery.  
* `PUT /api/surgeries/{surgery_id}`: Update details of or reschedule an existing surgery.  
* `DELETE /api/surgeries/{surgery_id}`: Cancel or delete a scheduled surgery.  
* `GET /api/pending-surgeries/`: List all pending surgeries, supporting filters similar to those in `PendingSurgeriesList.vue`.    
*   
* **Tabu Search Optimization**:  
  * `POST /api/schedule/optimize/`: Initiate the Tabu Search optimization process.  
    * *Request Body*: Should include current unoptimized/partially scheduled surgeries, available operating rooms, the complete SDST matrix, staff and equipment availability, and optimization parameters (e.g., max iterations, tabu tenure).  
    * *Response*: If synchronous (not recommended for long processes), the optimized schedule. If asynchronous, a task ID.  
  * `GET /api/schedule/optimization-status/{task_id}`: (If asynchronous execution is chosen) Check the status of an ongoing optimization task (e.g., pending, running, completed, failed).  
  * `GET /api/schedule/optimized-result/{task_id}`: (If asynchronous) Retrieve the optimized schedule once the task is completed.

**Pydantic Models for Request and Response Payloads**

Pydantic models are crucial for defining the expected structure and data types for API requests and responses. They enable FastAPI's automatic data validation and serialization.

* **Base Resource Models**: For each core entity (OperatingRoom, Staff, Equipment, SurgeryType, SDSTEntry, InitialSetupTime, Surgery), define `Base`, `Create`, `Update`, and `Response` Pydantic models.

   *Example for `OperatingRoom` (referencing `app.py` and `AddOrForm.vue` ):*  

Python  
from pydantic import BaseModel, Field

from typing import Optional, List

from datetime import time \# OperatingRoom in app.py uses time for operational\_start\_time

class OperatingRoomBase(BaseModel):

    name: str

    location: Optional\[str\] \= None

    status: Optional\[str\] \= Field(default="Available", description="e.g., Available, In Use, Maintenance")

    primary\_service: Optional\[str\] \= Field(default=None, alias="primaryService") \# Alias for frontend compatibility

    operational\_start\_time: Optional\[time\] \= None

    \# Add other fields from your SQLAlchemy model models.OperatingRoom as needed

class OperatingRoomCreate(OperatingRoomBase):

    pass \# Inherits all fields, all are required or have defaults

class OperatingRoomUpdate(BaseModel): \# Allow partial updates

    name: Optional\[str\] \= None

    location: Optional\[str\] \= None

    status: Optional\[str\] \= None

    primary\_service: Optional\[str\] \= Field(default=None, alias="primaryService")

    operational\_start\_time: Optional\[time\] \= None

    \# Only include fields that can be updated

class OperatingRoomResponse(OperatingRoomBase):

    id: int \# Assuming integer ID from the database

    class Config:

        orm\_mode \= True \# Allows direct mapping from SQLAlchemy models

        allow\_population\_by\_field\_name \= True \# Allows using alias in response

*   
*   
* **SDST Models**:

  * `SurgeryTypeCreate`, `SurgeryTypeUpdate`, `SurgeryTypeResponse`  
  * `SDSTRuleCreate` (e.g., `from_surgery_type_id: int`, `to_surgery_type_id: int`, `setup_time_minutes: int`)  
  * `SDSTRuleResponse` (similar to create, possibly with an `id`)  
  * `InitialSetupTimeCreate` (e.g., `surgery_type_id: int`, `time_minutes: int`)  
  * `InitialSetupTimeResponse`  
  * `SDSTMatrixUpdate` (e.g., `matrix: Dict]`)  
* **Surgery and Optimization Models**:

  * `SurgeryCreate`, `SurgeryUpdate`, `SurgeryResponse` (including fields like `patient_id`, `surgery_type_id`, `duration_minutes`, `assigned_room_id`, `start_time`, `end_time`, `status`, `surgeon_id`, `required_equipment_ids: List[int]`, etc.)

`OptimizationInput` Pydantic Model:  
 Python  
from typing import List, Dict, Tuple

class SurgeryInputForOptimization(BaseModel):

    surgery\_id: str \# or int

    surgery\_type\_id: str \# or int

    duration\_minutes: int

    surgeon\_id: Optional\[str\] \= None \# or int

    urgency\_level: Optional\[str\] \= "Medium"

    \# Add other relevant fields like required\_equipment, patient\_id etc.

class OperatingRoomInputForOptimization(BaseModel):

    room\_id: str \# or int

    name: Optional\[str\] \= None

    operational\_start\_time: Optional\[time\] \= None \# HH:MM:SS string or time object

    \# Add other relevant fields like available\_equipment

class OptimizationInput(BaseModel):

    surgeries\_to\_schedule: List

    operating\_rooms: List

    \# SDST matrix: {(from\_type\_id, to\_type\_id): setup\_time\_minutes}

    \# Pydantic doesn't directly support tuple keys in dicts for JSON.

    \# A common way is to represent it as List or a Dict\]

    \# Or, if keys are integers, Dict\]

    sds\_times\_matrix\_list: Optional\[List\[dict\]\] \= Field(default=None, description="List of {'from\_type\_id':X, 'to\_type\_id':Y, 'setup\_time\_minutes':Z}")

    \# Alternatively, if using the Python-native dict of tuples for internal processing:

    \# sds\_times\_matrix\_dict\_tuple\_keys: Optional, int\]\] \= None \# This won't serialize to JSON directly

    optimization\_params: Optional\] \= {"max\_iterations": 100, "tabu\_list\_size": 10}

*   
  * 

`OptimizationOutput` Pydantic Model:  
 Python  
class ScheduledSurgeryOutput(BaseModel):

    surgery\_id: str \# or int

    room\_id: str \# or int

    start\_time: str \# ISO datetime string

    end\_time: str   \# ISO datetime string

    \# Add other relevant output fields

class OptimizationOutput(BaseModel):

    optimized\_schedule: List

    statistics: Optional\] \= None \# e.g., makespan, utilization

*   
  * 

**Example FastAPI Route Implementation**

The following provides a conceptual example for creating an Operating Room, demonstrating the use of Pydantic models, SQLAlchemy session, and service layer interaction. The actual service calls need to be mapped to the existing service structure in `services/` from the `anasakhomach-surgical_scheduling_optimizer` project.  

Python

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

\# Assuming Pydantic schemas are in a 'schemas.py' file within the same API module

\# and SQLAlchemy models are in 'models.py' at the project root.

\# Service functions are assumed to be in a 'services.py' or individual service files.

\# Adjust paths based on your actual project structure.

\# from. import schemas \# if schemas.py is in the same directory

\# from.. import models \# if models.py is one level up

\# from..services import operating\_room\_service \# if services is a package one level up

\# from..db\_config import get\_db \# if db\_config.py is one level up

\# Placeholder for actual imports \- these paths need to be correct in your project

\# For example, if your API routes are in 'app/api/routes/resource\_routes.py'

\# and models.py is in 'app/models.py', db\_config.py in 'app/db\_config.py'

\# and services in 'app/services/operating\_room\_service.py'

\# then imports might look like:

\# from app.api import schemas

\# from app import models

\# from app.services import operating\_room\_service

\# from app.db\_config import get\_db

router \= APIRouter(

    prefix="/api", \# Base prefix for all routes in this router

    tags= \# Tag for API documentation

)

\# Dummy schema and service for illustration if actual files are not directly accessible

\# In real use, these would be imported from your project structure.

class OperatingRoomCreateSchema(BaseModel): \# Renamed to avoid conflict if schemas is imported

    name: str

    location: Optional\[str\] \= None

    status: Optional\[str\] \= "Available"

    primary\_service: Optional\[str\] \= None

class OperatingRoomResponseSchema(OperatingRoomCreateSchema):

    id: int

    class Config:

        orm\_mode \= True

def create\_or\_in\_db(db: Session, or\_data: OperatingRoomCreateSchema):

    \# This is a dummy function. Replace with your actual service logic.

    \# Example:

    \# new\_or \= models.OperatingRoom(\*\*or\_data.dict())

    \# db.add(new\_or)

    \# db.commit()

    \# db.refresh(new\_or)

    \# return new\_or

    print(f"Simulating DB create for OR: {or\_data.name}")

    return OperatingRoomResponseSchema(id=1, \*\*or\_data.dict()) \# Dummy response

@router.post("/operating-rooms/", response\_model=OperatingRoomResponseSchema, status\_code=status.HTTP\_201\_CREATED)

def create\_operating\_room\_endpoint(

    or\_data: OperatingRoomCreateSchema,

    db: Session \= Depends(get\_db) \# get\_db from your db\_config.py \[1\]

):

    """

    Create a new operating room.

    """

    \# Example of calling a service function \[1\]

    \# db\_or\_check \= operating\_room\_service.get\_operating\_room\_by\_name(db\_session=db, name=or\_data.name)

    \# if db\_or\_check:

    \#     raise HTTPException(status\_code=400, detail="Operating Room with this name already exists.")

    \#

    \# created\_or \= operating\_room\_service.create\_operating\_room(db\_session=db, or\_create=or\_data)

    \# if not created\_or:

    \#     raise HTTPException(status\_code=500, detail="Failed to create operating room.")

    \# return created\_or

    \# Using the dummy function for now:

    try:

        created\_or \= create\_or\_in\_db(db, or\_data)

        return created\_or

    except Exception as e: \# Catch potential exceptions from service layer

        raise HTTPException(status\_code=500, detail=str(e))

This example illustrates the pattern: define Pydantic schemas for request and response, use FastAPI's dependency injection for the database session, and call service layer functions to handle business logic and database operations. The actual implementation will need to use the specific service functions available in the `services/` directory of the provided backend codebase.  

**API Endpoint Definitions Table**

| Frontend Component/Screen | HTTP Method | Endpoint Path | Brief Description | Request Body (Pydantic Model) | Success Response (Pydantic Model / Status Code) | Error Responses (Common) |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| `ResourceManagementScreen.vue` | GET | `/api/operating-rooms/` | List all ORs | None | `List` / 200 OK | 500 Internal Server Error |
| `ResourceManagementScreen.vue` | POST | `/api/operating-rooms/` | Create a new OR | `OperatingRoomCreate` | `OperatingRoomResponse` / 201 Created | 400 Bad Request, 422 Unprocessable Entity, 500 |
| `ResourceManagementScreen.vue` | GET | `/api/operating-rooms/{or_id}` | Get a specific OR | None | `OperatingRoomResponse` / 200 OK | 404 Not Found, 500 |
| `ResourceManagementScreen.vue` | PUT | `/api/operating-rooms/{or_id}` | Update an OR | `OperatingRoomUpdate` | `OperatingRoomResponse` / 200 OK | 400, 404, 422, 500 |
| `ResourceManagementScreen.vue` | DELETE | `/api/operating-rooms/{or_id}` | Delete an OR | None | 204 No Content | 404, 500 |
| ... (similar entries for Staff and Equipment)... |  |  |  |  |  |  |
| `SDSTManagementScreen.vue` | GET | `/api/surgery-types/` | List all surgery types | None | `List` / 200 OK | 500 |
| `SDSTManagementScreen.vue` | POST | `/api/surgery-types/` | Create new surgery type | `SurgeryTypeCreate` | `SurgeryTypeResponse` / 201 Created | 400, 422, 500 |
| `SDSTManagementScreen.vue` | PUT | `/api/surgery-types/{type_id}` | Update surgery type | `SurgeryTypeUpdate` | `SurgeryTypeResponse` / 200 OK | 400, 404, 422, 500 |
| `SDSTManagementScreen.vue` | GET | `/api/sdst-matrix/` | Get the entire SDST matrix | None | `Dict]` / 200 OK | 500 |
| `SDSTManagementScreen.vue` | PUT | `/api/sdst-matrix/` | Update the entire SDST matrix | `SDSTMatrixUpdate` | `Dict]` / 200 OK | 400, 422, 500 |
| `SDSTManagementScreen.vue` | GET | `/api/initial-setup-times/` | List all initial setup times | None | `Dict[str, int]` / 200 OK | 500 |
| `SDSTManagementScreen.vue` | POST | `/api/initial-setup-times/` | Create/Update initial setup time for a type | `InitialSetupTimeCreate` | `InitialSetupTimeResponse` / 200 or 201 | 400, 422, 500 |
| `SurgerySchedulingScreen.vue` | GET | `/api/surgeries/` | List scheduled surgeries (with filters) | None | `List` / 200 OK | 500 |
| `SurgerySchedulingScreen.vue` | POST | `/api/surgeries/` | Schedule a new surgery | `SurgeryCreate` | `SurgeryResponse` / 201 Created | 400, 422, 500 |
| `SurgerySchedulingScreen.vue` | PUT | `/api/surgeries/{surgery_id}` | Update/Reschedule a surgery | `SurgeryUpdate` | `SurgeryResponse` / 200 OK | 400, 404, 422, 500 |
| `SurgerySchedulingScreen.vue` | POST | `/api/schedule/optimize/` | Initiate Tabu Search optimization | `OptimizationInput` | `OptimizationOutput` or `TaskIDResponse` / 202 Accepted | 400, 422, 500 |
| `SurgerySchedulingScreen.vue` | GET | `/api/schedule/optimization-status/{task_id}` | Check optimization task status (if async) | None | `TaskStatusResponse` / 200 OK | 404, 500 |
| `SurgerySchedulingScreen.vue` | GET | `/api/schedule/optimized-result/{task_id}` | Retrieve optimized schedule (if async) | None | `OptimizationOutput` / 200 OK | 404, 500 |

Export to Sheets

This table serves as a foundational API contract, crucial for both frontend and backend development alignment. It directly addresses the need for clear interface definitions, which is a common point of failure in complex system integrations.

## **3\. Frontend Integration: Vue.js Data Flow and State Management**

**Data Fetching Strategies in Vue Components**

The Vue.js frontend will primarily use `axios` for making HTTP requests to the FastAPI backend. While components can make direct API calls, encapsulating this logic within Pinia store actions is the recommended approach for better state management, code organization, and testability.

1. **Install `axios`**: If not already part of the project, add `axios` to your Vue.js project: `npm install axios`

**API Service Module (Optional but Recommended)**: Create a dedicated service module (e.g., `src/services/api.js`) to configure `axios` instance (base URL, headers) and export functions for each API endpoint.

 JavaScript  
// src/services/api.js

import axios from 'axios';

const apiClient \= axios.create({

  baseURL: '/api', // Proxied by vite.config.js

  headers: {

    'Content-Type': 'application/json',

    // Authorization header can be added here if using token-based auth

  },

});

// Interceptors for global error handling or token attachment can be added here

export default {

  // Operating Rooms

  getOperatingRooms: () \=\> apiClient.get('/operating-rooms/'),

  createOperatingRoom: (data) \=\> apiClient.post('/operating-rooms/', data),

  //... other OR methods

  // Staff

  getStaff: () \=\> apiClient.get('/staff/'),

  //... other staff methods

  // Equipment

  getEquipment: () \=\> apiClient.get('/equipment/'),

  //... other equipment methods

  // Surgery Types

  getSurgeryTypes: () \=\> apiClient.get('/surgery-types/'),

  createSurgeryType: (data) \=\> apiClient.post('/surgery-types/', data),

  //... other surgery type methods

  // SDST Matrix & Rules

  getSdstMatrix: () \=\> apiClient.get('/sdst-matrix/'),

  updateSdstMatrix: (data) \=\> apiClient.put('/sdst-matrix/', data),

  //... other SDST methods

  // Surgeries & Scheduling

  getScheduledSurgeries: (params) \=\> apiClient.get('/surgeries/', { params }),

  createSurgery: (data) \=\> apiClient.post('/surgeries/', data),

  runOptimization: (data) \=\> apiClient.post('/schedule/optimize/', data),

  //... other surgery/schedule methods

};

2.   
3. **Pinia Store Actions**: Components will dispatch actions in Pinia stores. These actions will use the `apiClient` to make requests.

    *Example: Fetching Operating Rooms in `resourceStore.js`*  

JavaScript  
// In src/stores/resourceStore.js

import { defineStore } from 'pinia';

import apiClient from '@/services/api'; // Assuming api.js is in src/services

import { useNotificationStore } from './notificationStore';

export const useResourceStore \= defineStore('resource', {

  state: () \=\> ({

    operatingRooms:,

    staff:,

    equipment:,

    isLoading: false,

    error: null,

    //... other state from \[1\]

  }),

  actions: {

    async loadOperatingRooms() {

      this.isLoading \= true;

      this.error \= null;

      const notificationStore \= useNotificationStore();

      try {

        const response \= await apiClient.getOperatingRooms();

        this.operatingRooms \= response.data;

      } catch (err) {

        this.error \= 'Failed to load operating rooms.';

        console.error(err);

        notificationStore.error(this.error);

      } finally {

        this.isLoading \= false;

      }

    },

    //... other actions for staff, equipment, add, update, delete

    // Example for adding an OR:

    async addOperatingRoom(orData) {

      this.isLoading \= true;

      this.error \= null;

      const notificationStore \= useNotificationStore();

      try {

        const response \= await apiClient.createOperatingRoom(orData);

        this.operatingRooms.push(response.data); // Add to local state

        notificationStore.success('Operating Room added successfully\!');

        return { success: true, data: response.data };

      } catch (err) {

        const errorMessage \= err.response?.data?.detail |

4. 

| 'Failed to add operating room.'; this.error \= errorMessage; notificationStore.error(errorMessage); return { success: false, error: errorMessage }; } finally { this.isLoading \= false; } } } }); \`\`\`

4. **Component Usage**: Components like `ResourceManagementScreen.vue` will call these store actions, typically in `onMounted` for initial data load or in event handlers for CRUD operations.  

JavaScript  
// In ResourceManagementScreen.vue

import { onMounted } from 'vue';

import { useResourceStore } from '@/stores/resourceStore';

import { storeToRefs } from 'pinia';

//... setup...

const resourceStore \= useResourceStore();

const { operatingRooms, isLoading, error } \= storeToRefs(resourceStore);

onMounted(() \=\> {

  resourceStore.loadOperatingRooms(); // Example, or a general loadResources()

  // resourceStore.loadStaff();

  // resourceStore.loadEquipment();

});

const handleSaveOr \= async (orData) \=\> {

  let result;

  if (currentOrToEdit.value) { // currentOrToEdit is a ref holding the OR being edited

    result \= await resourceStore.updateOperatingRoom(currentOrToEdit.value.id, orData);

  } else {

    result \= await resourceStore.addOperatingRoom(orData);

  }

  if (result.success) {

    showAddOrForm.value \= false; // showAddOrForm is a ref controlling form visibility

    currentOrToEdit.value \= null;

  }

  // Notification store would have shown success/error message

};

//...

5. 

**Pinia Store (`resourceStore.js`, `scheduleStore.js`) Adjustments for Backend Interaction**

The existing Pinia stores contain simulated API calls using `setTimeout`. These need to be refactored to use `axios` (via `apiClient`) to interact with the actual FastAPI backend.  

* **`resourceStore.js`** :    
  * **Actions to Refactor**: `loadResources` (or individual load actions like `loadOperatingRooms`, `loadStaff`, `loadEquipment`), `addOperatingRoom`, `updateOperatingRoom`, `deleteOperatingRoom`, `addStaff`, `updateStaff`, `deleteStaff`, `addEquipment`, `updateEquipment`, `deleteEquipment`, `updateResourceAvailability`.  
  * Each action should set `this.isLoading = true` at the start and `this.isLoading = false` in a `finally` block.  
  * Update state (e.g., `this.operatingRooms`) with data from successful API responses.  
  * Set `this.error` and use `notificationStore` for user feedback on errors.  
* **`scheduleStore.js`** :    
  * **Actions to Refactor**: `loadInitialData`, `rescheduleSurgery`, `addSurgeryFromPending`, `updateDateRange`, `updateGanttViewMode`, `navigateGanttDate`, `resetGanttToToday`, `editSurgery`, `cancelSurgery`, `updateSDSTValue`, `updateInitialSetupTime`, `addNewSurgeryType`, `deleteSurgeryType`.  
  * **`loadInitialData`**: This action will fetch scheduled surgeries, pending surgeries, SDST rules, initial setup times, and relevant resource data (like OR names, surgeon names if not embedded in surgery objects) from their respective API endpoints.  
  * **`processScheduleData()` Method**: The current `scheduleStore.js` has a `processScheduleData()` method that calculates `sdsTime` and `conflicts` on the frontend. This is a critical point. While frontend calculations can provide immediate feedback for UI interactions (e.g., during a drag-and-drop operation on the Gantt chart), the **backend must be the ultimate source of truth for persisted SDST calculations and conflict detection**.    
    * **Recommendation**:  
      1. The backend API (e.g., when fetching scheduled surgeries or after an optimization) should return surgeries with `sdsTime` and `conflicts` already calculated.  
      2. The frontend `processScheduleData()` might still be useful for *provisional* calculations during interactive UI operations (like dragging a surgery on the Gantt chart before dropping it) to give the user instant feedback. However, upon confirming an action (like dropping a surgery), the frontend should send the intended change to the backend, and the backend should re-validate, re-calculate SDST/conflicts, and return the updated, authoritative state.  
      3. This ensures consistency and leverages the backend's potentially more robust calculation and validation logic.

**New Action for Optimization**:  
 JavaScript  
// In src/stores/scheduleStore.js

async runOptimization(optimizationPayload) { // optimizationPayload matches OptimizationInput schema

  this.isLoading \= true;

  this.error \= null;

  const notificationStore \= useNotificationStore();

  try {

    // The optimizationPayload needs to be constructed with current surgeries, ORs, SDST matrix etc.

    // This data might come from this.scheduledSurgeries, this.pendingSurgeries,

    // this.operatingRooms (or resourceStore.operatingRooms), this.sdsRules, etc.

    // and transformed into the OptimizationInput schema.

    const response \= await apiClient.runOptimization(optimizationPayload);

    this.scheduledSurgeries \= response.data.optimized\_schedule; // Update with optimized schedule

    this.processScheduleData(); // Or rely on backend to return fully processed data

    notificationStore.success('Schedule optimized successfully\!');

    return { success: true, data: response.data };

  } catch (err) {

    const errorMessage \= err.response?.data?.detail |

* 

| 'Optimization failed.'; this.error \= errorMessage; notificationStore.error(errorMessage); return { success: false, error: errorMessage }; } finally { this.isLoading \= false; } } \`\`\`

**Frontend Error Handling and User Feedback**

Consistent and user-friendly error handling is vital.

1. **`try...catch` in Store Actions**: All API calls within Pinia actions must be wrapped in `try...catch` blocks.  
2. **Update `error` State**: The `catch` block should update an `error` property in the store's state (e.g., `this.error = 'Failed to load data'`). Components can observe this error state to display more persistent error messages if needed.

**Use `notificationStore` and `ToastNotification.vue`**: For transient feedback (success or error messages), use the `notificationStore`.  
 JavaScript  
// Example within a Pinia store action

import { useNotificationStore } from './notificationStore'; // Adjust path

//...

const notificationStore \= useNotificationStore();

try {

  //... API call...

  // const response \= await apiClient.createOperatingRoom(orData);

  notificationStore.success('Operating Room saved successfully\!');

} catch (error) {

  const message \= error.response?.data?.detail |

3.     
4. 

| 'An unexpected error occurred.'; notificationStore.error(message); this.error \= message; // Update store's persistent error state if needed } //... \`\`\` The `ToastNotification.vue` component is designed to handle these messages. Ensure it is correctly initialized in `App.vue` or the main layout component, and that its `ref` is passed to `notificationStore.setToastRef()` so the store can invoke its `addToast` method.  

The existing frontend logic in `scheduleStore.js` for calculating SDST and conflicts (`processScheduleData`) presents a significant architectural consideration. If the backend Tabu Search algorithm and API endpoints also perform these calculations (which they must for accuracy and consistency), there's a risk of divergence. The backend should be the definitive source for such critical data. Frontend calculations can serve as provisional feedback during user interactions, but the final state should always be confirmed and supplied by the backend. This minimizes inconsistencies and ensures that what the user sees aligns with what the optimizer uses and what is stored in the database.  

Furthermore, while full real-time collaboration might be beyond the initial scope, the system should eventually address how concurrent users are handled. Without mechanisms like WebSockets or at least periodic data refreshing with clear "last updated" indicators, users might make decisions based on stale data, leading to conflicts. For the current integration, a manual refresh option and clear timestamps for data could be a pragmatic interim solution.  

## **4\. Tabu Search Algorithm Integration with FastAPI**

**Choosing the Right Integration Approach**

Integrating the Python-based Tabu Search algorithm with the FastAPI backend requires a strategy that balances ease of implementation, performance, and scalability. Two primary options are:

* **Option A: Direct Execution within FastAPI**

  * This involves calling the Python Tabu Search script directly from a FastAPI endpoint. This can be done using Python's `subprocess` module to run the script as a separate process, or if the Tabu Search logic is refactored into a callable Python function/module, it could be imported and called directly.    
  *   
  * **Pros**:  
    * Relatively simpler initial setup, especially if the script is already command-line driven.  
    * Lower architectural complexity for a single-server deployment.  
  * **Cons**:  
    * If the Tabu Search is computationally intensive and long-running (which is typical), a synchronous call (even via `subprocess` without proper async handling) will block the FastAPI event loop. This makes other API endpoints unresponsive.  
    * Managing resources (CPU, memory) for the subprocess and handling its errors can be complex.  
    * Direct module import only works if the Tabu Search code is non-blocking or can be made so.  
* **Option B: Asynchronous Task Queue (e.g., Celery with RabbitMQ/Redis)**

  * This approach offloads the Tabu Search execution to separate worker processes managed by a task queue system like Celery. FastAPI submits an optimization task to the queue, and a Celery worker picks it up and executes it.  
  * **Pros**:  
    * Keeps FastAPI responsive by not blocking the event loop with long-running tasks.  
    * Better scalability, as workers can be distributed across multiple machines.  
    * Improved resilience; if a worker fails, the task can often be retried.  
    * Allows for task monitoring (progress, status).  
  * **Cons**:  
    * Significantly adds to architectural complexity: requires setting up and managing Celery workers and a message broker (like RabbitMQ or Redis).  
    * More initial development and deployment effort.

**Justification for the Selected Option**

For the immediate goal of integrating the "draft Tabu Search Algorithm" and making the system functional \[User Query\], a fully-fledged Celery setup (Option B) might introduce excessive overhead. However, a purely synchronous direct execution (Option A without async considerations) is detrimental to FastAPI's performance.

Therefore, a hybrid approach under **Option A, leveraging FastAPI's asynchronous capabilities to run the blocking Tabu Search script in a separate thread pool**, is recommended as the most pragmatic first step. This can be achieved using `asyncio.to_thread` (Python 3.9+) or `loop.run_in_executor` with `ThreadPoolExecutor` if using `subprocess`. This approach keeps the FastAPI endpoint non-blocking without the immediate need for a full Celery infrastructure. Celery can then be considered as a subsequent enhancement for greater scalability and robustness.

The Tabu Search algorithm, especially when dealing with complex objective functions, numerous neighborhood moves, and sequence-dependent setup times as detailed in the research , is likely to be computationally intensive. Running it directly in the main FastAPI thread would lead to poor API responsiveness. By executing it in a separate thread, FastAPI can continue to handle other requests.  

**Step-by-step Implementation (FastAPI's Asynchronous Execution of Python Script)**

This plan will focus on using `subprocess` to call the `app.py` script , as it appears to be the self-contained "draft" implementation. The `app.py` script uses `argparse` for inputs and can save results to a JSON file.  

1. **Modify `app.py` (if needed)**:

   * Ensure `app.py` can accept all necessary inputs via command-line arguments: paths to JSON files for surgeries, operating rooms, SDST matrix, and optimization parameters (max iterations, tabu tenure).    
   *   
   * Ensure `app.py` writes its optimized schedule to a specified output JSON file. The current `app.py` supports `--output`.    
   *   
   * The SDST data needs to be passed. `app.py` has an `--sds` argument for an SDST JSON file. The FastAPI endpoint will need to create this file from the input payload.    
   *   
2. **FastAPI Endpoint to Trigger Tabu Search**: Create an asynchronous FastAPI endpoint. This endpoint will:

   * Receive surgery data, resource data, SDST matrix, and optimization parameters in the request body (matching the `OptimizationInput` Pydantic model).  
   * Write this input data to temporary JSON files formatted as expected by `app.py`.  
   * Construct the command to execute `app.py` with the paths to these temporary files and other parameters.  
   * Use `asyncio.get_event_loop().run_in_executor()` to run the `subprocess.run()` call in a separate thread from FastAPI's thread pool.  
   * After the script completes, read the output JSON file.  
   * Clean up temporary files.  
   * Return the optimized schedule (matching the `OptimizationOutput` Pydantic model).

Python  
\# In your FastAPI router file (e.g., api/schedule\_routes.py)

import asyncio

from concurrent.futures import ThreadPoolExecutor

import subprocess

import json

import sys

import os

import tempfile \# For managing temporary files

from fastapi import APIRouter, HTTPException, Depends

\# Assuming schemas are defined as per Section 2 (e.g., schemas.OptimizationInput, schemas.OptimizationOutput)

\# from. import schemas 

\# from..db\_config import get\_db \# If DB access is needed directly here, though likely not for this endpoint

router \= APIRouter(prefix="/api/schedule", tags=)

\# Configure a thread pool executor. Adjust max\_workers based on server capacity and expected load.

\# This should ideally be initialized once when the FastAPI app starts.

\# For simplicity here, it's defined globally or can be passed via dependency injection.

executor \= ThreadPoolExecutor(max\_workers=os.cpu\_count() or 1\) 

\# Helper function to transform SDST matrix from API format to app.py's expected list format

def \_transform\_sds\_matrix\_to\_list(sds\_matrix\_dict\_tuple\_keys: dict) \-\> list:

    sds\_data\_list \=

    if isinstance(sds\_matrix\_dict\_tuple\_keys, dict):

        for key\_tuple\_str, time\_val in sds\_matrix\_dict\_tuple\_keys.items():

            \# Assuming key\_tuple\_str is like "from\_id\_to\_id" or needs parsing

            \# Or if the input is already structured correctly as List in Pydantic

            \# For app.py, it expects: \[{"from\_surgery\_type\_id": X, "to\_surgery\_type\_id": Y, "setup\_time\_minutes": Z},...\]

            \# If input\_data.sds\_times\_matrix\_list is already in this format, no transformation is needed.

            \# If it's Dict\], transform it:

            \# Example: if sds\_matrix\_dict\_tuple\_keys is {1: {2: 30, 3: 20}}

            \# for from\_type\_id, to\_rules in sds\_matrix\_dict\_tuple\_keys.items():

            \#     for to\_type\_id, setup\_time in to\_rules.items():

            \#         sds\_data\_list.append({

            \#             "from\_surgery\_type\_id": from\_type\_id,

            \#             "to\_surgery\_type\_id": to\_type\_id,

            \#             "setup\_time\_minutes": setup\_time

            \#         })

            pass \# Implement actual transformation based on OptimizationInput.sds\_times\_matrix\_list

    \# This function needs to be robust based on the chosen Pydantic structure for sds\_times\_matrix\_list

    return sds\_data\_list

@router.post("/optimize/", response\_model=schemas.OptimizationOutput) \# Or a task ID response for true async

async def trigger\_optimization\_async(input\_data: schemas.OptimizationInput):

    loop \= asyncio.get\_event\_loop()

    \# Create temporary files for script input

    \# These will be automatically deleted when the 'with' block exits or on error

    try:

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as surgeries\_file, \\

             tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as rooms\_file, \\

             tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as sds\_times\_file, \\

             tempfile.NamedTemporaryFile(mode="r", delete=False, suffix=".json") as output\_file: \# Output file for reading

            surgeries\_file\_path \= surgeries\_file.name

            rooms\_file\_path \= rooms\_file.name

            sds\_times\_file\_path \= sds\_times\_file.name

            output\_file\_path \= output\_file.name \# Path for script to write to

            json.dump(input\_data.surgeries\_to\_schedule, surgeries\_file)

            surgeries\_file.flush() \# Ensure data is written

            json.dump(input\_data.operating\_rooms, rooms\_file)

            rooms\_file.flush()

            sds\_args \=

            if input\_data.sds\_times\_matrix\_list:

                \# The Pydantic model OptimizationInput should define sds\_times\_matrix\_list

                \# as List matching app.py's expected JSON structure.

                \# If transformation is needed, call \_transform\_sds\_matrix\_to\_list here.

                json.dump(input\_data.sds\_times\_matrix\_list, sds\_times\_file)

                sds\_times\_file.flush()

                sds\_args \= \["--sds", sds\_times\_file\_path\]

            else:

                \# If no SDST data, close the temp file as it won't be used

                sds\_times\_file.close() 

                os.unlink(sds\_times\_file\_path) \# Delete it

                sds\_times\_file\_path \= None \# Clear path

            \# Path to your Tabu Search script \[1\]

            \# IMPORTANT: Adjust this path to be correct for your deployment environment.

            \# It could be an absolute path or relative if app.py is in a known location.

            script\_path \= os.path.join(os.path.dirname(\_\_file\_\_), "..", "..", "anasakhomach-surgical\_scheduling\_optimizer", "app.py")

            script\_path \= os.path.abspath(script\_path) \# Ensure absolute path

            if not os.path.exists(script\_path):

                raise HTTPException(status\_code=500, detail=f"Optimization script not found at {script\_path}")

            command \=

            if sds\_times\_file\_path: \# Only add if SDST data was provided

                command.extend(sds\_args)

            if input\_data.optimization\_params:

                if "max\_iterations" in input\_data.optimization\_params:

                    command.extend(\["--iterations", str(input\_data.optimization\_params\["max\_iterations"\])\])

                if "tabu\_size" in input\_data.optimization\_params: \# app.py uses \--tabu-size

                    command.extend(\["--tabu-size", str(input\_data.optimization\_params\["tabu\_size"\])\])

            \# Close files before subprocess reads them (especially on Windows)

            surgeries\_file.close()

            rooms\_file.close()

            if sds\_times\_file\_path: sds\_times\_file.close()

            \# Output file is opened for reading, its path is passed for writing by script

            process \= await loop.run\_in\_executor(

                executor,

                lambda: subprocess.run(command, capture\_output=True, text=True, check=False) \# check=False to inspect errors

            )

            if process.returncode\!= 0:

                error\_detail \= f"Optimization script failed with exit code {process.returncode}. STDERR: {process.stderr\[:500\]}"

                \# Log full stderr for server logs

                print(f"Tabu Search STDERR ({script\_path}): {process.stderr}")

                print(f"Tabu Search STDOUT ({script\_path}): {process.stdout}")

                raise HTTPException(status\_code=500, detail=error\_detail)

            \# Read the output file written by the script

            \# The output\_file was opened in 'r' mode initially, use its path.

            with open(output\_file\_path, 'r') as f\_out:

                optimized\_schedule\_data \= json.load(f\_out)

            return schemas.OptimizationOutput(optimized\_schedule=optimized\_schedule\_data)

    except FileNotFoundError as e:

        raise HTTPException(status\_code=500, detail=f"File operation error: {str(e)}")

    except subprocess.CalledProcessError as e:

        error\_detail \= f"Optimization script execution error. STDERR: {e.stderr\[:500\]}"

        print(f"Tabu Search CalledProcessError STDERR: {e.stderr}")

        print(f"Tabu Search CalledProcessError STDOUT: {e.stdout}")

        raise HTTPException(status\_code=500, detail=error\_detail)

    except Exception as e:

        print(f"General error during optimization endpoint: {type(e).\_\_name\_\_}: {str(e)}")

        \# Consider logging the full traceback here

        raise HTTPException(status\_code=500, detail=f"An unexpected error occurred: {str(e)}")

    finally:

        \# Clean up temporary files

        if 'surgeries\_file\_path' in locals() and os.path.exists(surgeries\_file\_path): os.unlink(surgeries\_file\_path)

        if 'rooms\_file\_path' in locals() and os.path.exists(rooms\_file\_path): os.unlink(rooms\_file\_path)

        if 'sds\_times\_file\_path' in locals() and sds\_times\_file\_path and os.path.exists(sds\_times\_file\_path): os.unlink(sds\_times\_file\_path)

        if 'output\_file\_path' in locals() and os.path.exists(output\_file\_path): os.unlink(output\_file\_path)

3.   
4.   
5. **Data Passing**:

   * **FastAPI to `app.py`**: The `OptimizationInput` Pydantic model's fields (`surgeries_to_schedule`, `operating_rooms`, `sds_times_matrix_list`, `optimization_params`) are serialized into JSON files. The paths to these files, along with optimization parameters, are passed as command-line arguments to `app.py`. The structure of `sds_times_matrix_list` in `OptimizationInput` should be a `List` matching the format `app.py` expects for its SDST JSON file (i.e., `[{"from_surgery_type_id": X, "to_surgery_type_id": Y, "setup_time_minutes": Z},...]`).  
   * **`app.py` to FastAPI**: The `app.py` script writes its optimized schedule to the JSON file specified by the `--output` argument. The FastAPI endpoint then reads this file to retrieve the results.  
6. **Error Handling**:

   * The `subprocess.run` call should have `check=False` initially to allow manual inspection of `returncode`, `stdout`, and `stderr`. If `process.returncode!= 0`, an `HTTPException` should be raised, including content from `stderr` for debugging.  
   * Wrap file operations and the `subprocess` call in `try...except` blocks to catch `FileNotFoundError`, `subprocess.CalledProcessError`, and other potential exceptions, returning appropriate HTTP 500 errors.  
   * Log `stdout` and `stderr` from the script on the FastAPI server for debugging purposes, regardless of success or failure.

The choice of Tabu Search script for integration is significant. `app.py` with its dependencies (`tabu_optimizer.py`, `scheduler_utils.py`, `simple_feasibility_checker.py`, `simple_models.py`) appears to be the "draft" implementation. It is simpler and uses `simple_models.py`. In contrast, `scheduling_optimizer.py` seems more advanced, directly using the main SQLAlchemy `models.py` and having more modular components like `TabuSearchCore`, `SolutionEvaluator`, and `NeighborhoodStrategies`. For the initial integration using `subprocess`, making `app.py` callable is a direct path. However, for long-term maintainability and to leverage the full database models directly without intermediate `simple_models`, refactoring the `scheduling_optimizer.py` structure to be callable as a Python library function from FastAPI would be a more robust solution. This plan focuses on the `app.py` route for now, aligning with the "draft" context, but the alternative should be considered for future enhancements.  

The format of the SDST data passed to `app.py` is critical. The `SDSTManagementScreen.vue` will likely manage this data in a UI-friendly format (e.g., a nested object or a list of objects). FastAPI receives this and must transform it into the precise JSON file structure that `app.py`'s `load_data_from_json` method expects for SDST (a list of dictionaries: `[{"from_surgery_type_id": X, "to_surgery_type_id": Y, "setup_time_minutes": Z},...]`). This transformation logic needs to be carefully implemented within the FastAPI endpoint.

**Tabu Search Integration Options Comparison Table**

| Feature/Consideration | Option A: Direct Execution (FastAPI Async \+ `subprocess`) | Option B: Asynchronous Task Queue (Celery) |
| ----- | ----- | ----- |
| **Implementation Complexity** | Moderate | High (requires Celery setup, workers, message broker) |
| **FastAPI Responsiveness** | Good (if `subprocess` is run in a thread pool executor) | Excellent (FastAPI only submits task, doesn't wait) |
| **Scalability** | Limited (scales with the FastAPI server instance) | High (workers can be scaled independently across machines) |
| **Resource Management** | Basic (managed by OS for subprocesses) | Better (Celery provides more control over worker resources) |
| **Error Handling/Retries** | Manual implementation within FastAPI endpoint | Robust (Celery has built-in retry mechanisms) |
| **Task Monitoring** | Limited (basic process status) | Good (Celery supports task state tracking, progress updates) |
| **Initial Setup Effort** | Low to Moderate | High |
| **Suitability for Project** | Good for initial integration and getting the draft working. | Ideal for production, long-term scalability, and robustness. |

Export to Sheets

## **5\. SDST Matrix Management: End-to-End Workflow**

Effective management of Sequence-Dependent Setup Times (SDST) is crucial for the accuracy of the scheduling optimization. This section details the workflow from UI interaction to database persistence. The primary frontend component for this is `SDSTManagementScreen.vue` or the more detailed `SDSTDataManagementScreen.vue`. The latter, with its tabbed interface and modal integration, provides a more comprehensive base.  

**UI Interactions in `SDSTDataManagementScreen.vue`**  

1. **Display**:

   * The screen will have tabs for "Manage Surgery Types," "Manage SDST Matrix," and "Manage Initial Setup Times."  
   * **Surgery Types Tab**: Fetches and displays a list of existing surgery types (ID, Name, Code, Description) in a table.  
   * **SDST Matrix Tab**: Displays an N×N grid where N is the number of surgery types. Rows represent "From Surgery Type," columns represent "To Surgery Type," and cells contain the setup time in minutes.  
   * **Initial Setup Times Tab**: Displays a table listing surgery types and their corresponding initial setup times.  
2. **Surgery Type Management**:

   * **Add**: Clicking "Add New Surgery Type" opens `AddEditSurgeryTypeModal.vue`. The user inputs Name, Code, and Description. On save, the modal emits a `save` event. The `SDSTDataManagementScreen.vue` calls a Pinia store action (e.g., `scheduleStore.addNewSurgeryType`), which in turn calls the `POST /api/surgery-types/` backend endpoint.    
   *   
   * **Edit**: Clicking "Edit" for a surgery type opens `AddEditSurgeryTypeModal.vue` pre-filled with the type's data. On save, the modal emits `save`; the parent calls a store action, which calls `PUT /api/surgery-types/{type_id}`.  
   * **Delete**: Clicking "Delete" triggers `ConfirmationModal.vue`. On confirmation, a store action calls `DELETE /api/surgery-types/{type_id}`. The backend must handle cascading effects (e.g., removing related SDST rules).    
   *   
3. **SDST Value Editing (Matrix Tab)**:

   * Users can click on an individual cell `(from_type, to_type)` in the SDST matrix. This should open a simple modal or inline editor (as suggested by `SDSTManagementScreen.vue`'s `openEditModal` ) to input/modify the setup time.    
   *   
   * On saving the cell value, a store action (e.g., `scheduleStore.updateSDSTValue`) calls `PUT /api/sdst-rules/{from_type_id}/{to_type_id}` or contributes to a batch update for `PUT /api/sdst-matrix/`. The `SDSTDataManagementScreen.vue` has a "Save Matrix Changes" button, suggesting a batch update is preferred after multiple cell edits.  
4. **Initial Setup Time Management (Initial Setup Tab)**:

   * **Add/Edit**: Clicking "Add Initial Setup Time" or "Edit" for an existing entry opens `AddEditInitialSetupModal.vue`. The user selects a surgery type (dropdown disabled if editing) and inputs the time. On save, the modal emits `save`; the parent calls a store action (e.g., `scheduleStore.updateInitialSetupTime`), which calls `POST /api/initial-setup-times/` (this endpoint can handle create/update based on existence).    
   *   
   * **Delete**: Similar to surgery type deletion, using `ConfirmationModal.vue` and an API call to `DELETE /api/initial-setup-times/{surgery_type_id}`.  
5. **Bulk Edit (`BulkSDSTEditor.vue`)** :    
   * Triggered from `SDSTManagementScreen.vue`.  
   * Allows pattern-based updates (fixed value, percentage, increment/decrement) to selected categories of SDST values (e.g., all, low, medium, high) or CSV import/export.  
   * On applying changes, `BulkSDSTEditor.vue` should emit an `update` event with the comprehensively modified SDST rules data. The parent screen then calls a store action to send this bulk update to the backend, likely via `PUT /api/sdst-matrix/`.

**API Endpoint Design**

The necessary API endpoints are detailed in Section 2, including:

* CRUD for `/api/surgery-types/`  
* `GET /api/sdst-matrix/` and `PUT /api/sdst-matrix/` for the entire matrix.  
* CRUD for `/api/sdst-rules/` (for more granular control if needed, though batch matrix update is likely more efficient for UI).  
* CRUD for `/api/initial-setup-times/`

**Database Persistence of SDST Data**

The backend database (MySQL) will require tables to store this information. The `models.py` file from the `anasakhomach-surgical_scheduling_optimizer` project should be verified or updated to include these. The `scheduling_optimizer.py` already references `SurgeryType` and `SequenceDependentSetupTime` models, suggesting they might exist or are planned.  

* **`surgery_types` Table**:  
  * `id` (INT, Primary Key, Auto Increment)  
  * `name` (VARCHAR, Unique, Not Null)  
  * `code` (VARCHAR, Unique, Optional)  
  * `description` (TEXT, Optional)  
* **`sequence_dependent_setup_times` (or `sdst_rules`) Table**:  
  * `id` (INT, Primary Key, Auto Increment) \- Optional, composite PK on (from\_, to\_) is also common.  
  * `from_surgery_type_id` (INT, Foreign Key to `surgery_types.id`, Not Null)  
  * `to_surgery_type_id` (INT, Foreign Key to `surgery_types.id`, Not Null)  
  * `setup_time_minutes` (INT, Not Null, Default 0\)  
  * Unique constraint on (`from_surgery_type_id`, `to_surgery_type_id`).  
* **`initial_setup_times` Table**:  
  * `surgery_type_id` (INT, Primary Key, Foreign Key to `surgery_types.id`, Not Null)  
  * `setup_time_minutes` (INT, Not Null, Default 0\)

**Data Format for SDST Matrix Transfer and Storage**

* **API to Frontend**:  
  * Surgery Types: `List`  
  * SDST Matrix: A nested dictionary is often convenient for frontend matrix rendering: `Dict]`. The `scheduleStore.js` uses this structure for `sdsRules`.    
  *   
  * Initial Setup Times: A dictionary: `Dict[str_surgery_type_id, int_setup_time]`. `scheduleStore.js` uses this for `initialSetupTimes`.    
  *   
* **Frontend to API (for updates)**:  
  * For bulk matrix updates (`PUT /api/sdst-matrix/`), the same nested dictionary format is efficient.  
  * For individual rule updates, a model like `SDSTRuleUpdate` would be used.  
  * For initial setup times, `InitialSetupTimeCreate` (containing `surgery_type_id` and `time_minutes`).

Managing a large SDST matrix via a UI presents usability challenges. If a hospital has many distinct surgery types (e.g., 50+), the matrix becomes very large (50x50 \= 2500 cells). Direct cell-by-cell editing can be tedious and error-prone. The `BulkSDSTEditor.vue` component , with its pattern-based updates and CSV import/export capabilities, is therefore a critical feature for practical usability. Its implementation should include robust client-side validation for CSV uploads (e.g., correct format, valid surgery type identifiers, numeric setup times) and clear previews of changes before they are applied. Additionally, the search and filter functionality mentioned for `SDSTManagementScreen.vue` (`searchQuery` ) will be essential for navigating large matrices.  

A significant consideration is the referential integrity when deleting a `SurgeryType`. If a `SurgeryType` is removed, all associated `sdst_rules` (where it is a `from_surgery_type_id` or `to_surgery_type_id`) and its entry in `initial_setup_times` become invalid or orphaned. The backend API endpoint responsible for deleting a `SurgeryType` must implement logic to handle these cascading deletions gracefully. This could be achieved through database-level cascade constraints (`ON DELETE CASCADE`) or by explicit deletion logic within the service layer. The frontend should clearly warn the user about these consequences using the `ConfirmationModal.vue` before proceeding with the deletion.  

## **6\. Comprehensive Data Validation**

Data validation is a cornerstone of a robust application, ensuring data integrity and preventing errors. Validation must occur at multiple levels: frontend for immediate user feedback and backend for authoritative checks.

**Frontend Validation (Vue.js Components)**

* **In-Component Validation**:  
  * Leverage standard HTML5 validation attributes within form inputs (e.g., `<input type="number" required min="0">`).  
  * Implement custom validation logic within the `setup` function of Vue components, particularly for forms like `AddOrForm.vue`, `AddStaffForm.vue`, `AddEquipmentForm.vue`, `AddEditSurgeryTypeModal.vue`, and `AddEditInitialSetupModal.vue`. These components in  

already demonstrate basic validation by maintaining an `errors` ref and a `validateForm` method. *Example in a Vue component :*  
 JavaScript  
// In \<script setup\> of a form component

import { ref } from 'vue';

const formData \= ref({ name: '', status: '' /\*...other fields \*/ });

const errors \= ref({});

const validateForm \= () \=\> {

  errors.value \= {}; // Clear previous errors

  if (\!formData.value.name ||\!formData.value.name.trim()) {

    errors.value.name \= 'Name is required.';

  }

  if (\!formData.value.status) {

    errors.value.status \= 'Status is required.';

  }

  // Add more complex validation rules as needed

  // e.g., for SDST values: if (formData.value.time \< 0\) errors.value.time \= 'Time cannot be negative.'

  return Object.keys(errors.value).length \=== 0;

};

const handleSubmit \= () \=\> {

  if (\!validateForm()) {

    // Optionally show a general error toast if there are multiple errors

    // notificationStore.error('Please correct the errors in the form.');

    return;

  }

  // Emit save event or call store action

  emit('save', formData.value);

};

*     
  *   
* **User Feedback**:  
  * Display error messages dynamically near the respective input fields. The forms in    
  * use `<span v-if="errors.field" class="error-message">{{ errors.field }}</span>`.  
  * Provide clear visual cues for fields with errors (e.g., red borders, icons).  
  * For API submission errors that are not field-specific, or for general success/failure notifications, use the `ToastNotification.vue` component via the `notificationStore`.    
  * 

**Backend Validation (FastAPI)**

* **Pydantic Model Validation**:  
  * FastAPI automatically validates incoming request bodies against the defined Pydantic models (Section 2). If validation fails (e.g., incorrect data type, missing required field), FastAPI returns a HTTP 422 Unprocessable Entity response with a detailed JSON body explaining the errors. This is the primary and most crucial layer of backend validation.  
* **Service-Level Validation (Business Logic)**:  
  * Within the service layer functions , implement business logic validation that Pydantic models cannot cover.    
  *   
  * Examples:  
    * **Uniqueness Checks**: Ensuring an operating room name or surgery type code is unique before creation or update (requires a database query).  
    * **Inter-field Dependencies**: Validating complex relationships between fields.  
    * **Domain-Specific Rules**: Enforcing rules like SDST values must be non-negative and within a reasonable maximum. The `SDSTDataManagementScreen.vue` includes a `validateDataIntegrity` method that checks for negative SDST values; this logic must also reside on the backend.    
    *   
    * **Referential Integrity**: Ensuring foreign keys point to existing records (though the database often handles this, proactive checks can provide better error messages). *Example in a FastAPI service (conceptual):*

Python  
\# In a service file, e.g., services/surgery\_type\_service.py

\# from sqlalchemy.orm import Session

\# from fastapi import HTTPException

\# from.. import models, schemas \# Adjust paths

\# def create\_surgery\_type(db: Session, surgery\_type: schemas.SurgeryTypeCreate):

\#     if surgery\_type.setup\_time\_minutes \< 0: \# Example business rule

\#         raise HTTPException(status\_code=400, detail="Setup time cannot be negative.")

\#     existing\_type\_by\_name \= db.query(models.SurgeryType).filter(models.SurgeryType.name \== surgery\_type.name).first()

\#     if existing\_type\_by\_name:

\#         raise HTTPException(status\_code=400, detail=f"Surgery type with name '{surgery\_type.name}' already exists.")

\#     \#... proceed with creation...

\#     db\_surgery\_type \= models.SurgeryType(\*\*surgery\_type.dict())

\#     db.add(db\_surgery\_type)

\#     db.commit()

\#     db.refresh(db\_surgery\_type)

\#     return db\_surgery\_type

*   
* 

Consistency in validation messages between the frontend and backend is important for a good user experience. If the frontend displays "Name is required," but a backend Pydantic error for the same missing field results in a generic message like "field required" under a `detail` key, it can be confusing. The frontend should be prepared to parse FastAPI's detailed 422 error responses to extract field-specific errors and display them in a user-friendly manner, or a middleware could be used on the backend to standardize error response formats.

The `feasibility_checker.py` (or `simple_feasibility_checker.py` for the draft algorithm) plays a vital role in backend validation related to the operational integrity of a schedule. While Pydantic models validate the structure and type of incoming data, the `FeasibilityChecker` is responsible for enforcing complex business rules like surgeon availability over a specific time period, equipment non-conflicts, and operating room availability. API endpoints that accept schedule data (e.g., for creating a new surgery or for initiating the optimization process) must utilize this `FeasibilityChecker` to validate the input schedule components against these operational constraints before proceeding with persistence or optimization. This prevents the system from attempting to optimize or save schedules that are fundamentally infeasible due to resource clashes or other rule violations.  

## **7\. Data Transformation Requirements**

Data often needs to be transformed as it moves between different layers of the application (Vue.js frontend, FastAPI backend, SQLAlchemy ORM, and the Python Tabu Search algorithm). Clear and accurate transformations are essential for data integrity and correct system operation.

**Mapping Frontend Data (Pinia State/Component Data) to API Payloads (Pydantic Models)**

When data is sent from the Vue.js frontend to the FastAPI backend:

**Case Conversion**: JavaScript commonly uses camelCase for variable names (e.g., `patientName`, `primaryService` as seen in `AddOrForm.vue` ), while Python conventionally uses snake\_case (e.g., `patient_name`, `primary_service`). Pydantic models can handle this automatically using `Field(alias='...')` or by configuring `allow_population_by_field_name = True` in the model's `Config`. Alternatively, manual transformation can be done in the Pinia store action before making the API call.  
 JavaScript  
// Example in Pinia store action before API call (if not using Pydantic alias)

// const payload \= {

//   patient\_name: formData.patientName,

//   primary\_service: formData.primaryService,

//   //... other fields

// };

// await apiClient.createOperatingRoom(payload);

*     
*   
* **Data Types**: Ensure data types are compatible. For example, JavaScript `Date` objects should typically be converted to ISO 8601 string format for JSON transfer if the Pydantic model on the backend expects a `datetime` object (FastAPI handles this conversion for `datetime` fields). Numeric inputs from forms might be strings and need conversion to numbers.  
* **Structure**: Data structures might need to be flattened or restructured. For example, a complex object in Vuex/Pinia state might need to be broken down or remapped to fit the Pydantic model expected by the API.

**Transforming API Responses (JSON from FastAPI) for Frontend Consumption (Pinia Store)**

When data is received from the FastAPI backend:

* **Case Conversion**: If the API returns snake\_case, and the frontend prefers camelCase, transformation will be needed. This can be done in the Pinia store action after receiving the response.  
* **Data Types**: ISO 8601 date strings from the API should be parsed into JavaScript `Date` objects if UI components or date manipulation libraries require them.  
* **Structure**: Adapt the API response structure to fit the Pinia store's state structure if they differ.

**Converting Data from SQLAlchemy Models (`models.py`) to Tabu Search Algorithm's Expected Input Structures**

The Tabu Search algorithm requires input data in a specific format. This data originates from SQLAlchemy model instances fetched from the database. The transformation typically occurs within the FastAPI endpoint that triggers the optimization.  

* **Target Data Structures for the Algorithm**: Based on `app.py` and general Tabu Search principles for scheduling , the algorithm needs:    
  * **List of Surgeries**: Each surgery represented as an object/dictionary with attributes like `surgery_id`, `duration_minutes`, `surgery_type_id`, `surgeon_id`, `urgency_level`. `app.py` uses `simple_models.Surgery` which expects these.  
  * **List of Operating Rooms**: Each OR with `room_id`, `operational_start_time`. `app.py` uses `simple_models.OperatingRoom`.  
  * **SDST Matrix**: Typically a dictionary mapping `(from_surgery_type_id, to_surgery_type_id)` to `setup_time_minutes`. `app.py`'s `SchedulerApp` loads this into `self.sds_times`.  
  * **Resource Availability**: Information about surgeon, staff, and equipment availability over time (if not implicitly handled by pre-filtering surgeries).  
  * The `Implementation Plan for Tabu Search Optimization of Surgery Scheduling with Sequence-Dependent Setup Times.txt` (as described by the user) details the canonical "Representing Data: Surgeries, Operating Rooms, Time, SDST Matrix." This definition must be the target for these transformations.

**Transformation Logic (Conceptual Example in FastAPI Endpoint)**:

 Python  
\# Conceptual transformation within the FastAPI endpoint that calls the Tabu Search

\# from.. import models as sqlalchemy\_models \# Main SQLAlchemy models from \[1\]

\# from..anasakhomach-surgical\_scheduling\_optimizer import simple\_models \# If using app.py's models

\# \# Fetch data using SQLAlchemy

\# db\_surgeries \= db.query(sqlalchemy\_models.Surgery).filter(...).all()

\# db\_operating\_rooms \= db.query(sqlalchemy\_models.OperatingRoom).filter(...).all()

\# \# Fetch SDST rules and convert to the matrix format expected by app.py

\# sdst\_rules\_from\_db \= db.query(sqlalchemy\_models.SequenceDependentSetupTime).all()

\# sds\_times\_matrix\_for\_algo \= {(rule.from\_surgery\_type\_id, rule.to\_surgery\_type\_id): rule.setup\_time\_minutes 

\#                              for rule in sdst\_rules\_from\_db}

\# \# Transform to the format expected by app.py's load\_data\_from\_json (list of dicts)

\# algo\_surgeries\_input \= \[

\#     {

\#         "surgery\_id": s.id, \# Assuming s.id maps to surgery\_id

\#         "surgery\_type\_id": s.surgery\_type\_id,

\#         "duration\_minutes": s.duration\_minutes,

\#         "surgeon\_id": s.surgeon\_id, \# Ensure this field exists and is correctly named

\#         "urgency\_level": s.urgency\_level

\#     } for s in db\_surgeries

\# \]

\# algo\_or\_input \=

\# algo\_sds\_input\_list \=

\# These lists of dicts (algo\_surgeries\_input, algo\_or\_input, algo\_sds\_input\_list)

\# would then be written to the temporary JSON files used by app.py.

*   
* 

The choice of which Python Tabu Search implementation to integrate significantly impacts this transformation step. `app.py` uses `simple_models.py`, which are distinct from the main SQLAlchemy ORM models in `models.py`. If `app.py` is used, data fetched via SQLAlchemy must be converted to fit these simpler structures or the plain Python dictionaries/lists that `app.py`'s `load_data_from_json` method effectively creates from JSON input. This might involve loss of information if `simple_models.py` lacks fields present in the main `models.py` that are crucial for complex feasibility checks or objective function components (e.g., detailed surgeon preferences if `simple_models.Surgery.surgeon_id` is just an integer without relational context). If the more advanced `scheduling_optimizer.py` is adapted to be callable as a library function, it appears to work directly with the full SQLAlchemy models (e.g., `models.Surgery`), which would simplify this specific transformation but requires that script to be refactored for such programmatic calls.  

The "Surgery Representation" detailed in the `Implementation Plan...txt` is the authoritative data structure that the algorithm operates on. All data flowing from the database through FastAPI to the algorithm must precisely converge to this defined representation. Any mismatch will lead to incorrect algorithm behavior or runtime errors. Particular attention must be paid to the SDST matrix format: the algorithm might expect a dictionary with tuple keys `{(from_type_id, to_type_id): time}` as `app.py` seems to build internally, or a list of dictionary objects as its JSON input file for SDST implies. This transformation needs to be exact.

**Data Transformation Map**

| Source System/Layer | Source Data Field/Structure | Transformation Logic/Notes | Destination System/Layer | Destination Data Field/Structure |
| ----- | ----- | ----- | ----- | ----- |
| Vue Component (`AddOrForm.vue`) | `orData.primaryService` (camelCase) | Convert to snake\_case if Pydantic model doesn't use alias. | FastAPI Pydantic Model (`OperatingRoomCreate`) | `primary_service` (snake\_case) or `primaryService` (if aliased) |
| Vue Component (`SurgerySchedulingScreen.vue`) | `selectedSurgery.startTime` (JS Date object) | Format to ISO 8601 string (e.g., `date.toISOString()`). | FastAPI Pydantic Model (`SurgeryUpdate`) | `start_time` (string, for Pydantic `datetime`) |
| FastAPI Pydantic Model (`OperatingRoomResponse`) | `primary_service` (snake\_case from DB/SQLAlchemy) | Convert to camelCase for frontend if Pydantic alias not used for response serialization. | Pinia Store (`resourceStore.js`) | `operatingRoom.primaryService` (camelCase) |
| FastAPI Pydantic Model (`SurgeryResponse`) | `start_time` (ISO string) | Parse into JavaScript `Date` object (`new Date(str)`). | Pinia Store (`scheduleStore.js`) | `surgery.startTime` (JS Date object) |
| SQLAlchemy Model (`models.OperatingRoom`) | `id`, `name`, `location`, `operational_start_time` | Map fields directly. Format `operational_start_time` (Python `time`) to string "HH:MM:SS" if `app.py` expects string. | Algorithm Input (`app.py` via JSON) | `{"room_id":..., "name":..., "operational_start_time":...}` |
| SQLAlchemy Model (`models.Surgery`) | `id`, `duration_minutes`, `surgery_type_id`, `surgeon_id`, `urgency_level` | Map fields directly. | Algorithm Input (`app.py` via JSON) | `{"surgery_id":..., "duration_minutes":..., "surgery_type_id":..., "surgeon_id":..., "urgency_level":...}` |
| SQLAlchemy Models (`SequenceDependentSetupTime`) | List of `(from_id, to_id, time)` rules | Convert to list of dicts: `[{"from_surgery_type_id": X, "to_surgery_type_id": Y, "setup_time_minutes": Z},...]` for `app.py`'s SDST JSON file. | Algorithm Input (`app.py` via JSON for SDST) | JSON array of SDST rule objects. |
| Algorithm Output (`app.py` JSON output) | List of `{"surgery_id":..., "room_id":..., "start_time":..., "end_time":...}` | Parse JSON. Convert `start_time`, `end_time` strings to Pydantic `datetime` compatible format (if needed, FastAPI usually handles string to datetime). | FastAPI Pydantic Model (`OptimizationOutput`) | `List` |

Export to Sheets

This map is critical for ensuring data consistency across the application stack. It highlights potential points of friction where data types or naming conventions differ, requiring explicit transformation logic.

## **8\. Refining and Operationalizing Your Tabu Search Python Implementation**

The user has a "draft Tabu Search Algorithm" that "does not fully work." Based on the `anasakhomach-surgical_scheduling_optimizer` directory structure , this draft likely corresponds to `app.py` and its direct dependencies: `tabu_optimizer.py`, `scheduler_utils.py`, `simple_models.py`, and `simple_feasibility_checker.py`. This section focuses on the necessary updates to these files to make them functional and integrate them with the FastAPI backend, particularly concerning the handling of Sequence-Dependent Setup Times (SDST). The more advanced structure also present in  

(involving `scheduling_optimizer.py`, `tabu_search_core.py`, etc.) could be a target for future evolution but is not the immediate focus for "getting the draft working."  

The existing draft code (`app.py` and its dependencies) is significantly simpler than the advanced concepts detailed in the research document on Tabu Search and likely the `Implementation Plan...txt`. For instance, `tabu_optimizer.py` contains placeholder neighborhood generation and a basic cost function, while `simple_feasibility_checker.py` is rudimentary. A substantial enhancement of this draft code is required, moving beyond minor tweaks to a more significant development effort to align with the project's design goals.  

**Target Python Files and Key Updates**

1. **`app.py` (`SchedulerApp` class)** :    
   * **`load_data_from_json()`**:  
     * **Update**: This method currently loads surgeries, operating rooms, and SDST data from JSON files specified by command-line arguments. It needs to robustly parse these files, ensuring the data structures match what's provided by the FastAPI endpoint (which will create these files from the `OptimizationInput` Pydantic model). The current SDST loading logic `self.sds_times[(from_type, to_type)] = setup_time` is a suitable format for internal use.  
     * **Why**: Correct data ingestion is the first step for the algorithm. FastAPI will generate these JSON files based on user input and database state.  
   * **`run_scheduler()`**:  
     * **Update**: Ensure that `SchedulerUtils` and `FeasibilityChecker` instances are initialized with all necessary data, critically including the `sds_times` loaded from the input. The current instantiation in `app.py` correctly passes `self.sds_times` to `SchedulerUtils`.  
     * **Why**: Both utility and feasibility checking components rely on accurate SDST information to make correct calculations and assessments.  
   * **`main()` (argparse setup)**:  
     * **Update**: Verify that `argparse` is configured to accept all necessary command-line arguments that the FastAPI endpoint will provide. This includes paths to the input JSON files (surgeries, rooms, SDST) and the path for the output JSON file. Optimization parameters like `max_iterations` and `tabu_size` are already handled.  
     * **Why**: This is the primary interface when `app.py` is invoked as a subprocess by FastAPI.  
2. **`simple_models.py`** :    
   * **`Surgery` class**:  
     * **Verification**: Contains `surgery_id`, `surgery_type_id`, `duration_minutes`, and `urgency_level`. These are essential.  
     * **Why**: These attributes are fundamental for scheduling logic, SDST calculations (which depend on `surgery_type_id`), and potentially for ordering in initial solution generation (urgency).  
   * **`OperatingRoom` class**:  
     * **Verification**: Contains `room_id` and `operational_start_time`.  
     * **Why**: Essential for determining room availability and scheduling start times.  
   * **`SurgeryRoomAssignment` class**:  
     * **Verification**: Contains `surgery_id`, `room_id`, `start_time`, `end_time`.  
     * **Why**: This class represents the core output of the scheduling algorithm—the assignment of a surgery to a specific room and time.  
3. The `simple_models.py` used by `app.py` are less detailed than the main SQLAlchemy `models.py`. For example, `simple_models.Surgery` might lack fields like `patient_id` or detailed resource requirements present in the main `models.Surgery`. When transforming data from SQLAlchemy models to be used by `app.py`, care must be taken to include all necessary information, potentially by augmenting `simple_models.py` or ensuring the transformation passes all required data even if not explicitly modeled in `simple_models.py` (e.g., as additional attributes on the objects created by `load_data_from_json`).

4. **`scheduler_utils.py` (`SchedulerUtils` class)** :    
   * **`__init__()`**:  
     * **Verification**: The constructor correctly receives and stores `sds_times`.  
     * **Why**: SDST data is frequently accessed by methods like `find_next_available_time`.  
   * **`initialize_solution()`**:  
     * **Update**: This method is critical for generating a good starting point for Tabu Search. It iterates through surgeries (sorted by urgency, then duration) and attempts to assign them to rooms using `find_next_available_time`. This process *must* correctly account for SDST, both for the initial setup if an OR is empty and for transitions between surgeries. The `Implementation Plan...txt` provides detailed guidance for this.  
     * **Why**: A high-quality initial solution can significantly reduce the search effort for the Tabu algorithm. Incorrect SDST handling here will lead to a flawed starting point.  
     * **Current State**: The `find_next_available_time` method in `scheduler_utils.py` already includes logic to consider `last_surgery_type_in_room_id` and `current_surgery_type_id` by calling `self._get_sds_time()`. This `_get_sds_time` method correctly looks up `self.sds_times.get((last_surgery_type_in_room_id, current_surgery_type_id), 0)`. This is a solid foundation.    
     *   
   * **`find_next_available_time()`**:  
     * **Update**: The core logic for finding a valid time slot. When considering placing a surgery after a `last_assignment` in a room, the `setup_time = self._get_sds_time(...)` is calculated. This `setup_time` must be added to `last_assignment.end_time` to determine the true earliest possible start time for the current surgery.  
     * **Why**: This is where SDST directly impacts the timeline and feasibility of placements.  
     * **Current State**: The implementation `current_time_for_room = DatetimeWrapper.parse_to_datetime(last_assignment.end_time) + timedelta(minutes=setup_time)` correctly incorporates the setup time. This needs to be thoroughly tested.  
   * **Helper `get_surgery_type_id(surgery_id)`**:  
     * **Add**: A helper method to retrieve `surgery_type_id` for a given `surgery_id` from `self.surgeries`.  
     * **Why**: Needed by `calculate_cost` in `tabu_optimizer.py` to determine SDST between sequenced surgeries.  
5. **`tabu_optimizer.py` (`TabuOptimizer` class)** :    
   * **`optimize()` method**:  
     * **Verification**: The main loop structure (generate initial solution, evaluate, generate neighbors, select best non-tabu/aspirational neighbor, update tabu list, update best solution) is standard for Tabu Search.  
     * **Update**: All steps within this loop, especially neighbor generation and cost calculation, must be fully SDST-aware.  
     * **Why**: The entire optimization process hinges on these components correctly reflecting the impact of SDST.  
   * **`generate_neighbors()` method**:  
     * **Update**: This method currently calls `_generate_swap_neighbors` and `_generate_move_neighbors`, which are noted as basic placeholders in    
     * . These need significant enhancement based on the strategies outlined in the `Implementation Plan...txt` and the research on neighborhood structures. Common moves include:    
       * **Swap**: Exchange two surgeries (within the same OR or across different ORs).  
       * **Insert (Shift)**: Move a surgery to a different position in the sequence (within the same OR or to a different OR).  
       * **Reassign Room/Time**: Change the assigned OR or start time for a surgery.  
     * For each generated neighbor solution, the new start and end times of affected surgeries must be recalculated, explicitly considering any changes in SDST due to the altered sequence. The objective function for this neighbor must then use these SDST-aware timings.  
     * The "move" attribute stored in the tabu list (e.g., `('swap', surgery_id1, surgery_id2, new_room1_id, new_room2_id)`) must be carefully designed to effectively prevent cycling, especially in the context of SDST.    
     *   
     * **Why**: Neighborhood generation is the core exploratory mechanism of Tabu Search. If moves are not SDST-aware or are too simplistic, the algorithm will fail to find good quality, practical schedules.  
   * **`calculate_cost()` method**:  
     * **Update**: The current method calculates `makespan`, `idle_time`, and `overtime`. It *must* be augmented to include a component for total SDST costs, as specified in the `Implementation Plan...txt` ("Objective Function: Components (makespan, tardiness, resource utilization, SDST costs, etc.)") and supported by research.    
     *   
     * To implement this, the method needs to iterate through the assignments in each room (sorted by start time). For each surgery, it must identify the type of the preceding surgery in that room (or an "initial" state if it's the first) and its own type. Using this pair of types, the corresponding SDST is retrieved from `self.scheduler_utils.sds_times` and summed up.  
     * **Decision on SDST in Cost**: It's crucial to decide if SDST cost is an *explicit component* added to other costs (like makespan), or if its impact is *implicitly* captured because `initialize_solution` and `generate_neighbors` produce SDST-aware timings (which then affect makespan and idle time). The `Implementation Plan...txt` and    
     * suggest an explicit sum of SDSTs. This makes the impact of SDST directly visible and optimizable in the cost function.

*Conceptual addition to `calculate_cost()` for explicit SDST summation:*  
 Python  
\# Inside TabuOptimizer.calculate\_cost(self, solution):

\#... (existing calculations for makespan, idle\_time, overtime)...

total\_sdst\_minutes \= 0

room\_schedules \= {} 

for assignment in solution:

    room\_schedules.setdefault(assignment.room\_id,).append(assignment)

for room\_id\_key in room\_schedules:

    sorted\_assignments\_in\_room \= sorted(room\_schedules\[room\_id\_key\], key=lambda a: a.start\_time)

    \# Assuming scheduler\_utils has a helper to get surgery\_type\_id from surgery\_id

    \# and sds\_times is accessible via self.scheduler\_utils.sds\_times

    last\_surgery\_type\_id \= None \# Represents state before first surgery (e.g., "initial" or a specific ID like 0\)

                              \# This needs to align with how sds\_times matrix handles initial setups.

                              \# If initial setups are handled by find\_next\_available\_time ensuring the first surgery

                              \# starts after initial setup, then last\_surgery\_type\_id for the first surgery in room

                              \# would effectively be the type of the "virtual" preceding state.

    for idx, current\_assign in enumerate(sorted\_assignments\_in\_room):

        current\_surgery\_obj \= next(s for s in self.scheduler\_utils.surgeries if s.surgery\_id \== current\_assign.surgery\_id)

        current\_surgery\_type\_id \= current\_surgery\_obj.surgery\_type\_id

        actual\_prev\_type\_id\_for\_lookup \= 0 \# Default for "initial" or if no preceding type in matrix

        if idx \== 0:

            \# Handle initial setup for the very first surgery in an OR.

            \# This might be a special key in sds\_times, e.g., (0, current\_surgery\_type\_id)

            \# Or, if initial setup is always fixed and added by find\_next\_available\_time,

            \# this loop might only sum \*inter-surgery\* SDSTs.

            \# For explicit cost:

            actual\_prev\_type\_id\_for\_lookup \= 0 \# Define what '0' or 'None' means in your SDST matrix keys

        else:

            prev\_surgery\_obj \= next(s for s in self.scheduler\_utils.surgeries if s.surgery\_id \== sorted\_assignments\_in\_room\[idx-1\].surgery\_id)

            actual\_prev\_type\_id\_for\_lookup \= prev\_surgery\_obj.surgery\_type\_id

        sdst \= self.scheduler\_utils.sds\_times.get((actual\_prev\_type\_id\_for\_lookup, current\_surgery\_type\_id), 0\)

        total\_sdst\_minutes \+= sdst

\# Add to the overall cost, possibly with a weight

cost \+= total\_sdst\_minutes \# Example: cost\_weight\_sds \* total\_sdst\_minutes

return cost

*   
  *   
    * **Why**: The objective function is the sole guide for the Tabu Search. If SDST is not accurately and explicitly part of this cost, the algorithm cannot optimize for it.  
  * **Tabu List Management**:  
    * **Update**: The current `self.tabu_list` is a simple Python list, and tenure is managed by `self.tabu_list.pop(0)` if `len(self.tabu_list) > self.tabu_list_size`. This is a basic FIFO approach.  
    * The representation of a "move" added to this list needs to be effective. For example, if swapping surgeries S1 (type A) and S2 (type B), simply adding `('swap', S1.id, S2.id)` might not be enough if the benefit came from S1 now following S0 (type C) instead of S2. More descriptive tabu attributes might be needed, as discussed in    
    * (Section III.C).  
    * **Why**: An effective tabu list prevents cycling and guides exploration. SDST considerations can make simple tabu attributes less effective.  
  * **Aspiration Criteria**:  
    * **Update**: The current criterion (`neighbor_cost < best_cost`) allows a tabu move if it improves upon the *current iteration's best known so far for a neighbor*, which is not the standard "global best" aspiration. It should be `neighbor_cost < global_best_solution_cost`.  
    * Implement based on `Implementation Plan...txt` and    
    * (Section I.D), typically allowing a tabu move if it leads to a solution better than the best solution found *in the entire search history so far*.  
    * **Why**: Aspiration criteria provide a mechanism to override tabu status for exceptionally good moves, preventing the loss of high-quality solutions.  
  * **Stopping Criteria**:  
    * **Verification**: Current criteria are `max_iterations` or `max_no_improvement`. These are standard and generally acceptable.    
    *   
    * **Why**: Defines when the computationally intensive search should terminate.  
6. **`simple_feasibility_checker.py` (`FeasibilityChecker` class)** :    
   * **Update**: This component is currently very rudimentary (e.g., `is_surgeon_available` is a placeholder). It needs substantial enhancements to perform actual feasibility checks.  
   * It must validate:  
     * **Resource Availability**: No double-booking of operating rooms.  
     * **Surgeon Availability**: Surgeons are not assigned to overlapping surgeries.  
     * **Staff/Equipment Availability**: (If modeled in detail) Required staff and equipment are available. The more detailed `feasibility_checker.py` has methods like `is_equipment_available_for_period` and `_get_required_equipment_for_surgery` whose logic should be adapted or merged.    
     *   
     * **Temporal Constraints**: Surgeries respect OR operational hours.  
   * The checks should consider the `current_schedule_assignments` passed to its methods, taking into account surgery durations, start times, and end times (which must be SDST-aware).  
   * **Why**: The optimizer must only explore and accept feasible schedules. A weak feasibility checker will lead to invalid solutions.

**Ensuring Python Implementation is Callable and Returns Structured Result**

When the FastAPI endpoint calls `app.py` via `subprocess`:

* **Input**: `app.py` must correctly parse all command-line arguments provided by FastAPI, including paths to the JSON input files (surgeries, ORs, SDST matrix) and any optimization parameters (iterations, tenure).  
* **Output**: `app.py` must write its final optimized schedule to a JSON file (as its `--output` argument facilitates). This JSON should be a list of `SurgeryRoomAssignment` objects (or dictionaries matching that structure), which FastAPI can then parse and return in the `OptimizationOutput` Pydantic model format. The existing `save_solution_to_json` method in `app.py` is suitable for this.

The successful operationalization of this "draft" Python code hinges on these enhancements. The process involves not just minor fixes but a significant upgrade to its core logic to correctly incorporate SDST and ensure robust behavior, guided by the detailed requirements in the `Implementation Plan...txt` and the foundational principles outlined in  

.

## **9\. System Testing Strategy**

A comprehensive testing strategy is essential to ensure the reliability and correctness of the integrated Surgery Scheduling System. This strategy should encompass unit tests for individual components, integration tests for interactions between components, and end-to-end tests for user workflows. The existing test files in  

(e.g., `test_services.py`, `test_tabu_optimizer.py`) and  

(Vue component tests) provide a starting point.

**Unit Testing**

* **Vue Components (`src/components/**/*.vue`)** :    
  * **Framework**: Utilize Vitest (as configured in `vitest.config.js` ) and Vue Test Utils.    
  *   
  * **Scope**: Test props, emits, slots, event handling logic, conditional rendering, and local state changes.  
  * **Examples**:  
    * For `AddOrForm.vue` : Verify that submitting the form with valid data emits a `save` event containing the correct OR details. Test input validation logic by providing invalid data and asserting that error messages are displayed.    
    *   
    * For `SDSTManagementScreen.vue` : Test tab switching, modal opening for adding/editing surgery types and initial setup times, and interactions with the SDST matrix (e.g., data binding to input cells).    
    *   
    * The existing tests in `src/components/__tests__/` should be reviewed, updated for any component changes, and expanded for full coverage.    
    *   
* **Pinia Stores (`src/stores/*.js`)** :    
  * **Framework**: Vitest with `@pinia/testing` or manual store instantiation.  
  * **Scope**: Test actions (mocking API calls made with `axios` using `vi.fn()` or a library like `msw`), state mutations, and getters.  
  * **Examples**:  
    * For `resourceStore.js` : Test the `addOperatingRoom` action. Mock the `apiClient.createOperatingRoom` call to return a successful response. Assert that the `operatingRooms` state array is updated correctly and that a success notification is triggered. Test error handling by mocking an API failure and asserting that the `error` state is set and an error notification is shown.    
    *   
    * For `scheduleStore.js` : Test the `processScheduleData` action (if it remains significantly on the frontend) with various surgery sequences to ensure SDST and basic conflicts are calculated correctly. Test actions like `runOptimization`, mocking the API call to the backend optimization endpoint.    
    *   
* **FastAPI Endpoints & Service Logic** :    
  * **Framework**: `pytest` is recommended for consistency with modern Python practices, used with FastAPI's `TestClient`.  
  * **Scope**:  
    * **API Endpoints**: Test successful responses (2xx status codes), error handling (4xx for client errors like invalid input, 5xx for server errors), request validation against Pydantic models, and authentication/authorization if applicable.  
    * **Service Layer Functions**: Test business logic within service files (e.g., `services/operating_room_service.py` ). Mock database interactions (e.g., using `unittest.mock.patch` or a test database fixture) to isolate service logic. The existing `test_services.py` demonstrates this approach for SQLAlchemy models and service functions.    
    *   
* **Tabu Search Algorithm Modules** :    
  * **Framework**: `pytest` or the existing `unittest` structure.  
  * **Scope**: Test individual functions and methods:  
    * `scheduler_utils.initialize_solution`: Given a set of surgeries, ORs, and SDST data, verify that a feasible initial solution is generated and that SDST is considered.  
    * `tabu_optimizer.generate_neighbors` (and specific move functions): For a given solution, verify that valid neighbor solutions are generated. Test that moves correctly update timings considering SDST.  
    * `tabu_optimizer.calculate_cost`: For a known schedule and SDST matrix, verify that the calculated objective function value is correct, explicitly checking the SDST cost component.  
    * `tabu_optimizer.tabu_list` operations: Test adding moves, checking tabu status, and tenure decrement.  
    * `simple_feasibility_checker.is_feasible`: Test with various valid and invalid schedule snippets to ensure constraints are correctly identified.  
  * The existing tests need significant expansion to cover SDST aspects thoroughly.    
  * 

**Integration Testing**

* **Frontend API Calls to Backend**:  
  * Verify that Vue components (via Pinia stores) correctly call the FastAPI endpoints.  
  * Test that request payloads are formatted correctly and that responses (success and error) are handled appropriately by the frontend (e.g., updating state, displaying notifications).  
  * Tools like `msw` (Mock Service Worker) can be used to mock API responses for frontend integration tests without needing a running backend.  
* **FastAPI Interaction with Tabu Search Python Script**:  
  * Focus on the `/api/schedule/optimize/` endpoint.  
  * Test that input data (surgeries, ORs, SDST matrix, parameters) is correctly written to temporary JSON files for the `app.py` script.  
  * Verify that `app.py` is invoked correctly via `subprocess`.  
  * Test that the JSON output from `app.py` is correctly parsed and returned by the FastAPI endpoint.  
  * Test error handling: script execution errors, file I/O errors, timeouts.  
* **Database Interactions**:  
  * Test that FastAPI service layer functions correctly perform CRUD operations on the MySQL database.  
  * Verify data integrity, foreign key constraints, and uniqueness constraints at the database level.  
  * `test_db_connection.py` is a very basic check; more comprehensive tests are needed for actual data operations.    
  * 

**End-to-End Testing (E2E)**

* **Framework**: Tools like Cypress or Playwright for full browser automation, or a combination of FastAPI's `TestClient` for backend interactions and direct Pinia store manipulations for frontend state if full UI automation is too time-consuming initially.  
* **Scope**: Simulate complete user workflows across the application.  
* **Example Workflows**:  
  1. **Resource Setup**: User logs in \-\> navigates to Resource Management \-\> adds a new Operating Room, a new Staff member, and new Equipment. Verify these resources appear correctly in their respective lists.  
  2. **SDST Configuration**: User navigates to SDST Management \-\> defines a new Surgery Type \-\> adds an SDST rule between two types in the matrix \-\> sets an Initial Setup Time for the new type. Verify all data is saved and displayed correctly.  
  3. **Scheduling and Optimization**: User navigates to Surgery Scheduling \-\> views pending surgeries \-\> drags a pending surgery to the Gantt chart (or manually inputs data for a new surgery) \-\> triggers the optimization process. Verify that an optimized schedule is returned and displayed on the Gantt chart, and that SDST visualization is present.

**Specific Tests for Tabu Search Algorithm Integration**

These tests are crucial for validating the core optimization logic:

* **Correctness of SDST Calculation in Objective Function**: Create test cases with small, manually verifiable schedules and SDST values. Assert that the `calculate_cost` method in `tabu_optimizer.py` computes the total SDST component accurately.  
* **Feasibility of Generated Solutions**: Ensure that any schedule returned by the `optimize` method in `tabu_optimizer.py` passes all checks in the (enhanced) `simple_feasibility_checker.py`.  
* **Improvement Verification**: For small, controllable test instances where a better solution is known or easily calculable, verify that the Tabu Search algorithm can find this improved solution or significantly improve upon a deliberately poor initial solution.  
* **Parameter Sensitivity (Manual or Scripted)**: Experiment with different Tabu Search parameters (tabu tenure, max iterations, neighborhood size if configurable) on representative datasets to understand their impact on solution quality and runtime. This is more exploratory than a strict pass/fail test.  
* **Robustness to Edge Case Inputs**: Test the optimization endpoint with various inputs:  
  * Empty list of surgeries to schedule.  
  * No available operating rooms.  
  * Very restrictive SDST values (e.g., extremely high setup times).  
  * Surgeries with durations longer than OR availability.  
* The existing `test_integration_optimizer.py` and `test_enhanced_objective_function.py` from    
* can serve as a basis for these tests but need substantial expansion to include SDST considerations.

Testing a heuristic algorithm like Tabu Search for "optimality" is generally infeasible, as it does not guarantee finding the global optimum. The focus of testing should therefore be on the correctness of its individual components (e.g., SDST calculation, move generation, tabu list mechanics), the feasibility of the solutions it produces, and its ability to consistently find *better* solutions compared to an initial or random state. Benchmark instances, if available for surgery scheduling with SDST, can be valuable for comparing performance, or improvement can be tracked from a baseline heuristic.

Consistency in testing frameworks can improve developer productivity. While the existing backend tests in  

use `unittest`, FastAPI projects often leverage `pytest` for its flexibility and rich ecosystem. It is advisable to gradually migrate towards or primarily use `pytest` for new backend tests, while ensuring existing `unittest` tests are maintained and expanded.

## **10\. Detailed Explanation of Implementation File (Python Tabu Search Code)**

This section provides a focused analysis of the Python files identified as the "draft" Tabu Search implementation. It details the necessary code updates and the reasons behind them, with a strong emphasis on integrating Sequence-Dependent Setup Times (SDST) and ensuring overall robustness for integration with the FastAPI backend.  

**1\. `app.py` (`SchedulerApp` class)**  

* **`load_data_from_json(self, surgeries_file, rooms_file, sds_times_file=None)`**  
  * **Current State**: Loads surgeries, operating rooms, and optionally SDST data from JSON files. SDST data is stored in `self.sds_times` as `{(from_type, to_type): setup_time}`.  
  * **Required Updates**:  
    * Ensure robust parsing of all input JSON files generated by the FastAPI endpoint. This includes handling potential missing fields or malformed data gracefully, although Pydantic on the FastAPI side should prevent most structural issues.  
    * The current SDST loading format is suitable. Verify that `surgery_type_id`s used in the SDST JSON (from FastAPI) are consistent with those in the surgeries JSON.  
  * **Why**: Data integrity is paramount. The algorithm's performance depends on accurate input.  
* **`run_scheduler(self, max_iterations=100, tabu_list_size=10)`**  
  * **Current State**: Initializes `FeasibilityChecker` and `SchedulerUtils`, then creates and runs `TabuOptimizer`.  
  * **Required Updates**:  
    * Ensure `SchedulerUtils` is initialized with `self.sds_times`. (Currently done).  
    * Ensure `FeasibilityChecker` is also made aware of `self.sds_times` if its feasibility checks need to consider setup times directly (e.g., if checking if a setup time itself is valid or if it pushes a surgery beyond OR limits). The current `simple_feasibility_checker.py` doesn't seem to use SDST directly, but an enhanced version might.  
  * **Why**: Core components must have access to SDST data to perform their functions correctly.  
* **`main()` function (Argument Parsing)**  
  * **Current State**: Uses `argparse` to define command-line arguments (`--surgeries`, `--rooms`, `--sds`, `--output`, `--iterations`, `--tabu-size`).  
  * **Required Updates**: No major changes seem necessary here, as these arguments align well with what the FastAPI `subprocess` call will provide. Ensure default values are sensible if FastAPI doesn't provide certain optional parameters.  
  * **Why**: This is the entry point for the script when called by FastAPI. The interface must match.

**2\. `simple_models.py`**  

* **`Surgery` class**:  
  * **Current State**: Attributes: `surgery_id`, `surgery_type_id`, `duration_minutes`, `surgeon_id`, `urgency_level`.  
  * **Required Updates**: Verify these fields are sufficient for the `Implementation Plan...txt`. If additional attributes (e.g., specific equipment requirements, patient ID for logging/tracking within the algorithm) are needed by the algorithm's logic (especially for feasibility or objective function), they should be added here and populated by `load_data_from_json` in `app.py`.  
  * **Why**: The algorithm operates on these model instances. Missing data can lead to incorrect decisions or errors.  
* **`OperatingRoom` class**:  
  * **Current State**: Attributes: `room_id`, `operational_start_time`, `name`.  
  * **Required Updates**: Similar to `Surgery`, ensure all necessary attributes for the algorithm are present (e.g., operational end time if fixed, any room-specific capabilities affecting SDST or surgery assignment).  
  * **Why**: Accurate OR data is crucial for feasibility and scheduling.  
* **`SurgeryRoomAssignment` class**:  
  * **Current State**: Attributes: `surgery_id`, `room_id`, `start_time`, `end_time`.  
  * **Required Updates**: This structure is standard for representing a scheduled surgery. Ensure `start_time` and `end_time` are consistently handled as `datetime` objects (the `DatetimeWrapper` in `scheduler_utils.py` helps with this).  
  * **Why**: This is the primary output of the algorithm, representing the final schedule.

**3\. `scheduler_utils.py` (`SchedulerUtils` class)**  

* **`__init__(...)`**:  
  * **Current State**: Takes `sds_times` and stores it.  
  * **Required Updates**: Ensure `self.surgeries` (list of `Surgery` objects) is properly populated and accessible, as `get_surgery_type_id` will need it.  
  * **Why**: SDST calculations rely on this data.  
* **`initialize_solution(self)`**:  
  * **Current State**: Sorts surgeries by urgency and duration, then iterates, trying to assign them to rooms using `find_next_available_time`.  
  * **Required Updates**:  
    * The logic within `find_next_available_time` correctly uses `_get_sds_time` to calculate setup time based on `last_surgery_type_in_room_id` and `current_surgery_type_id`. This is good.  
    * Ensure that the `last_surgery_type_in_room_id` for the *very first* surgery in an OR is handled correctly (e.g., using a conventional `None` or `0` key in the `sds_times` matrix if specific initial setup times per type are stored there, or by fetching a separate initial setup time if modeled differently). The `_get_sds_time` method defaults to 0 if the pair is not found, which might be acceptable if initial setup is handled by ensuring the OR's `operational_start_time` is the earliest possible start.  
  * **Why**: A good, SDST-aware initial solution is vital for Tabu Search performance.  
* **`find_next_available_time(self, room_id, preferred_start_time, surgery_duration_minutes,...)`**:  
  * **Current State**: Calculates `setup_time = self._get_sds_time(...)` and adds it to `last_assignment.end_time` to find `current_time_for_room`. This correctly incorporates SDST into the earliest start time calculation.  
  * **Required Updates**: Thoroughly test this method with various scenarios, including empty rooms (initial placement), back-to-back surgeries of same/different types, and varying SDST values. Ensure `DatetimeWrapper` handles time zone considerations correctly if applicable (though likely not an issue for relative scheduling).  
  * **Why**: This is the core function for placing surgeries in a timeline while respecting SDST.  
* **`_get_sds_time(self, from_surgery_type_id, to_surgery_type_id, room_id=None)`**:  
  * **Current State**: Looks up `self.sds_times.get((from_surgery_type_id, to_surgery_type_id), 0)`.  
  * **Required Updates**: This is generally correct. If SDST can be room-specific, the `room_id` parameter would need to be used to consult a more complex SDST data structure (e.g., `self.sds_times[room_id].get(...)`). For the current draft, room-agnostic SDST is assumed by its usage.  
  * **Why**: Accurate retrieval of SDST values is fundamental.  
* **Add `get_surgery_type_id(self, surgery_id)` method**:

**Implementation**:  
 Python  
\# In SchedulerUtils class

def get\_surgery\_type\_id(self, surgery\_id):

    for surgery in self.surgeries:

        if surgery.surgery\_id \== surgery\_id:

            return surgery.surgery\_type\_id

    \# Consider raising an error or returning a specific value if not found

    \# logger.warning(f"Surgery type ID not found for surgery\_id: {surgery\_id}")

    return None \# Or raise ValueError

*   
  *   
  * **Why**: This helper will be needed by `TabuOptimizer.calculate_cost` to determine the types of sequenced surgeries for SDST calculation.

**4\. `tabu_optimizer.py` (`TabuOptimizer` class)**  

* **`generate_neighbors(self, solution)`**:  
  * **Current State**: Calls `_generate_swap_neighbors` and `_generate_move_neighbors`, which are described as basic placeholders.  
  * **Required Updates**:  
    * Implement various neighborhood moves as defined in the `Implementation Plan...txt` and research (e.g., swap surgeries between different time slots/rooms, insert a surgery into a new position).    
    *   
    * **Crucially**: When a move is applied to create a neighbor, the new start/end times of *all affected surgeries* (not just the ones directly moved) must be recalculated considering the new sequence and the corresponding SDSTs. This might involve calling `scheduler_utils.find_next_available_time` or a similar re-evaluation logic for the affected part of the schedule in the new neighbor.  
    * The "move attribute" stored in the tabu list must effectively capture the change to prevent immediate reversal, especially considering SDST implications. For example, `('swap', surgery1_id, surgery2_id, old_room1_id, old_room2_id, new_start_time1, new_start_time2)`.    
    *   
  * **Why**: The quality and diversity of neighborhood moves directly impact the Tabu Search's ability to explore the solution space and find good solutions. SDST awareness here is non-negotiable.  
* **`calculate_cost(self, solution)`**:  
  * **Current State**: Calculates cost based on `makespan`, `idle_time`, and `overtime`. SDST is not explicitly included.  
  * **Required Updates**:  
    * Add an explicit component for `total_sdst_minutes` to the cost function. This involves iterating through the `solution` (which is a list of `SurgeryRoomAssignment` objects). For each room, sort the assignments by `start_time`. Then, for each pair of consecutive surgeries (S\_prev, S\_curr) in that room, find their respective `surgery_type_id`s (using the new helper in `SchedulerUtils`). Look up the SDST value from `self.scheduler_utils.sds_times` for the transition `(S_prev.type_id, S_curr.type_id)`. Sum these values.  
    * For the first surgery in each room, the SDST from an "initial" state (e.g., type `0` or `None`) to its type should be added if your SDST matrix includes such entries.  
    * The research explicitly states: "The objective function must sum... processing times AND associated setup times." This confirms the need for explicit SDST summation in the cost.    
    * 

*Revised conceptual addition for `calculate_cost`*:  
 Python  
\# Inside TabuOptimizer.calculate\_cost(self, solution):

\#... (existing calculations for makespan, idle\_time, overtime)...

total\_sdst\_minutes \= 0

room\_schedules \= {} 

for assignment in solution:

    room\_schedules.setdefault(assignment.room\_id,).append(assignment)

for room\_id\_key in room\_schedules:

    sorted\_assignments\_in\_room \= sorted(room\_schedules\[room\_id\_key\], key=lambda a: a.start\_time)

    previous\_surgery\_type\_id \= 0 \# Convention for "initial state" or "empty room"

                               \# Ensure this key exists in sds\_times for first surgeries, 

                               \# e.g., (0, type\_A) gives initial setup for type\_A.

    for current\_assign in sorted\_assignments\_in\_room:

        \# Get current surgery's type\_id using the new helper

        current\_surgery\_type\_id \= self.scheduler\_utils.get\_surgery\_type\_id(current\_assign.surgery\_id)

        if current\_surgery\_type\_id is None:

            \# logger.error(f"Could not find surgery type for surgery {current\_assign.surgery\_id}, skipping SDST for this pair.")

            continue \# Or handle as a large penalty

        sdst \= self.scheduler\_utils.sds\_times.get((previous\_surgery\_type\_id, current\_surgery\_type\_id), 0\)

        total\_sdst\_minutes \+= sdst

        previous\_surgery\_type\_id \= current\_surgery\_type\_id \# Set for the next iteration

\# Define a weight for the SDST component if desired

weight\_sdst \= 1.0 \# Adjust as needed

cost \+= weight\_sdst \* total\_sdst\_minutes

return cost

*   
  *   
  * **Why**: The objective function guides the search. Without SDST as a direct cost component, the algorithm will not optimize for its minimization.  
* **Aspiration Criteria**:  
  * **Current State**: `if (move not in self.tabu_list or neighbor_cost < best_cost):` \- this `best_cost` refers to the best solution found *so far in the entire search*, which is correct for the common aspiration criterion.  
  * **Required Updates**: No change needed if `best_cost` is indeed the global best score. Ensure `best_cost` is updated only when a new global best is found.  
  * **Why**: Allows overriding tabu status for exceptionally good moves.

**5\. `simple_feasibility_checker.py` (`FeasibilityChecker` class)**  

* **Current State**: Methods like `is_surgeon_available`, `is_equipment_available`, `is_room_available_for_period`, and `is_feasible` are largely placeholders or overly simplistic.  
* **Required Updates**:  
  * These methods need to be fully implemented to perform meaningful checks.  
  * `is_feasible(self, schedule_assignments)`: Should iterate through `schedule_assignments` and for each assignment, check:  
    * Room availability for the given `start_time` and `end_time`.  
    * Surgeon availability (ensure the assigned surgeon is not busy with another surgery during this time).  
    * Equipment availability (if detailed equipment modeling is part of the draft's scope).  
  * The logic from the more detailed `feasibility_checker.py` should be reviewed and its relevant parts incorporated or adapted into this `simple_feasibility_checker.py`.    
  *   
  * The feasibility checks must use the `start_time` and `end_time` from the proposed `schedule_assignments`, which themselves must be SDST-aware if generated by SDST-aware neighborhood moves.  
* **Why**: A robust feasibility checker is critical to ensure that the Tabu Search only explores and considers valid, implementable schedules. Generating neighbors that are inherently infeasible is wasteful.

These updates represent a significant effort to elevate the "draft" implementation to a functional and SDST-aware Tabu Search algorithm, suitable for integration and initial testing.

## **11\. Conclusion and Recommended Next Steps**

**Summary of the Integration Plan**

This document has detailed a comprehensive plan for integrating the Vue.js frontend, FastAPI backend, and the Python-based Tabu Search algorithm for the Surgery Scheduling System. The plan emphasizes:

1. **Clear API Design**: Defining RESTful API endpoints in FastAPI with Pydantic models for robust data contracts, covering resource management, SDST configuration, surgery scheduling, and optimization triggering.  
2. **Frontend-Backend Communication**: Utilizing `axios` within Pinia store actions for data fetching and updates, with a focus on centralized state management and user feedback through notifications.  
3. **Tabu Search Integration**: Employing FastAPI's asynchronous capabilities to run the Python Tabu Search script (`app.py`) via `subprocess` in a non-blocking manner, including mechanisms for data passing and result retrieval.  
4. **SDST Management**: Establishing an end-to-end workflow for managing surgery types, the SDST matrix, and initial setup times, from UI interactions in `SDSTManagementScreen.vue` to backend API calls and database persistence.  
5. **Comprehensive Validation**: Implementing data validation on both the frontend (for immediate feedback) and backend (Pydantic for structural validation, service-layer for business rules, and `FeasibilityChecker` for schedule integrity).  
6. **Data Transformation**: Defining necessary transformations for data flowing between Vue.js, FastAPI (Pydantic), SQLAlchemy models, and the Python Tabu Search algorithm's internal structures.  
7. **Refinement of Tabu Search Code**: Outlining specific updates to the draft Python Tabu Search files (`app.py` and its dependencies) to correctly incorporate SDST into initial solution generation, neighborhood moves, and the objective function, and to enhance feasibility checking.  
8. **Systematic Testing**: Proposing a multi-layered testing strategy including unit, integration, and end-to-end tests, with specific attention to validating the Tabu Search algorithm's SDST handling and solution feasibility.

The core challenge lies in ensuring that each component not only functions correctly in isolation but also interacts seamlessly with others, particularly in how SDST data is managed, transformed, and utilized consistently across all layers.

**Prioritized List of Actions for Implementation**

The following actions are recommended in a prioritized order to achieve a functional integrated system:

1. **Backend API \- Core Resources & SDST Types**:  
   * Implement the FastAPI endpoints (Section 2\) for basic CRUD operations on Operating Rooms (as an initial resource example) and Surgery Types (essential for SDST).  
   * Define the corresponding Pydantic models.  
   * Ensure basic database persistence for these entities using SQLAlchemy models.    
   *   
2. **Frontend Connection \- Core Resources & SDST Types**: \*

