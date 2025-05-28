# Comprehensive Frontend-Backend Integration Plan for Surgery Scheduling System

## Executive Summary

Based on deep analysis of the existing Vue.js frontend and FastAPI backend codebase, this integration plan provides a prioritized roadmap to connect non-functional UI elements with their corresponding backend services. The system has a solid foundation with:

- **Frontend**: Vue 3 + Pinia state management with comprehensive UI components
- **Backend**: FastAPI with complete CRUD endpoints and optimization services
- **Gap**: Missing integration between frontend stores and backend APIs

## Current State Analysis

### ✅ What's Working
- **Authentication System**: Fully functional login/registration with JWT tokens
- **Backend API Structure**: Complete REST endpoints for all resources
- **Frontend Components**: Rich UI components with proper state management
- **Database Models**: Well-defined SQLAlchemy models with relationships

### ❌ What Needs Integration
- **Resource Management**: Frontend stores use mock data instead of API calls
- **Schedule Optimization**: "Run Optimization" button not connected to backend
- **SDST Management**: Frontend SDST data not synchronized with backend
- **Dashboard Widgets**: KPIs and metrics display placeholder data
- **Real-time Updates**: No WebSocket integration for live schedule changes

## Integration Strategy

**Primary Approach**: Modify existing Pinia store actions to replace mock data with actual API calls, preserving all existing UI components and user interactions.

**Key Principles**:
1. **Build on Existing Code**: Leverage current component structure and state management
2. **Incremental Integration**: Implement in phases to maintain system stability
3. **Data Consistency**: Ensure frontend and backend data models align
4. **Error Handling**: Implement robust error handling and user feedback
5. **Testing**: Validate each integration step before proceeding

## Phase 1: Core Resource Management Integration (Priority: CRITICAL)

### 1.1 Operating Rooms Management
**Issue Addressed**: ResourceManagementScreen.vue OR tab displays mock data
**Components**: `ResourceManagementScreen.vue`, `AddOrForm.vue`
**Store**: `resourceStore.js`
**Backend Endpoints**: `/api/operating-rooms/` (GET, POST, PUT, DELETE)

**Integration Steps**:
1. **Modify resourceStore.js actions**:
   - Replace mock data in `loadOperatingRooms()` with `GET /api/operating-rooms/`
   - Update `addOperatingRoom()` to call `POST /api/operating-rooms/`
   - Update `updateOperatingRoom()` to call `PUT /api/operating-rooms/{id}`
   - Update `deleteOperatingRoom()` to call `DELETE /api/operating-rooms/{id}`

2. **Data Model Alignment**:
   - Frontend expects: `{id, name, location, status, primaryService}`
   - Backend provides: `{room_id, location}` (from OperatingRoom model)
   - **Transform**: Map `room_id` to `id`, generate `name` from room_id, add status logic

3. **Error Handling**:
   - Add try-catch blocks in store actions
   - Display user-friendly error messages via toast notifications
   - Implement loading states during API calls

**Backend Reference**: `api/routers/operating_rooms.py` - Complete CRUD implementation exists
**Frontend Reference**: `frontend/src/stores/resourceStore.js` lines 45-120

### 1.2 Staff Management Integration
**Issue Addressed**: ResourceManagementScreen.vue Staff tab shows placeholder data
**Components**: `ResourceManagementScreen.vue`, `AddStaffForm.vue`
**Store**: `resourceStore.js`
**Backend Endpoints**: `/api/surgeons/` (GET, POST, PUT, DELETE)

**Integration Steps**:
1. **Update resourceStore.js**:
   - Connect `loadStaff()` to `GET /api/surgeons/`
   - Map surgeon data to staff format expected by frontend
   - Implement CRUD operations for staff management

2. **Data Transformation**:
   - Backend: `{surgeon_id, name, specialization, contact_info}`
   - Frontend: `{id, name, role, specializations[], status}`
   - **Transform**: Map surgeon_id to id, split specialization into array

**Backend Reference**: `api/routers/surgeons.py`
**Frontend Reference**: `frontend/src/stores/resourceStore.js` lines 121-200

### 1.3 Equipment Management Integration
**Issue Addressed**: Equipment tab functionality missing
**Components**: `ResourceManagementScreen.vue`, `AddEquipmentForm.vue`
**Store**: `resourceStore.js`
**Backend Endpoints**: Need to create `/api/equipment/` endpoints

**Integration Steps**:
1. **Backend Development Required**: Create equipment router and models
2. **Frontend Integration**: Connect equipment store actions to new endpoints

**Status**: Backend endpoints need to be created first

## Phase 2: Schedule Management Integration (Priority: HIGH)

### 2.1 Surgery Scheduling Screen Integration
**Issue Addressed**: SurgerySchedulingScreen.vue shows mock schedule data
**Components**: `SurgerySchedulingScreen.vue`, `GanttChart.vue`
**Store**: `scheduleStore.js`
**Backend Endpoints**: `/api/schedules/current`, `/api/surgeries/`

**Integration Steps**:
1. **Connect Schedule Display**:
   - Update `loadCurrentSchedule()` to call `GET /api/schedules/current`
   - Transform backend schedule data for Gantt chart display
   - Implement date filtering for schedule views

2. **Surgery Management**:
   - Connect surgery CRUD operations to `/api/surgeries/` endpoints
   - Implement surgery status updates
   - Add real-time schedule conflict detection

**Backend Reference**: `api/routers/schedules.py` lines 261-312
**Frontend Reference**: `frontend/src/stores/scheduleStore.js`

### 2.2 Optimization Engine Integration
**Issue Addressed**: "Run Optimization" button non-functional
**Components**: `SurgerySchedulingScreen.vue`, `OptimizationPanel.vue`
**Store**: `scheduleStore.js`
**Backend Endpoints**: `/api/schedules/optimize`, `/api/schedules/apply`

**Integration Steps**:
1. **Optimization Trigger**:
   - Connect "Run Optimization" button to `POST /api/schedules/optimize`
   - Implement optimization parameters collection from UI
   - Add progress tracking for long-running optimizations

2. **Results Handling**:
   - Display optimization results in existing UI components
   - Implement schedule comparison functionality
   - Add "Apply Schedule" functionality via `/api/schedules/apply`

**Backend Reference**: `api/routers/schedules.py` lines 104-203
**Frontend Reference**: `frontend/src/components/OptimizationPanel.vue`

## Phase 3: SDST Management Integration (Priority: HIGH)

### 3.1 SDST Data Management
**Issue Addressed**: SDST management screen non-functional
**Components**: `SDSTManagementScreen.vue`, `SDSTMatrixEditor.vue`
**Store**: `sdstStore.js`
**Backend Endpoints**: `/api/surgery-types/`, `/api/sdst/`

**Integration Steps**:
1. **Surgery Types Management**:
   - Connect surgery types CRUD to backend
   - Implement surgery type validation
   - Add specialization requirements

2. **SDST Matrix Management**:
   - Implement SDST matrix data synchronization
   - Add matrix validation and conflict detection
   - Implement bulk update operations

**Backend Reference**: Need to verify SDST endpoints exist
**Frontend Reference**: `frontend/src/stores/sdstStore.js`

## Phase 4: Dashboard Integration (Priority: MEDIUM)

### 4.1 Dashboard Widgets Integration
**Issue Addressed**: Dashboard shows placeholder KPIs and metrics
**Components**: `DashboardScreen.vue`, various widget components
**Store**: `dashboardStore.js`
**Backend Endpoints**: `/api/dashboard/metrics`, `/api/dashboard/kpis`

**Integration Steps**:
1. **KPI Integration**:
   - Connect dashboard metrics to backend analytics
   - Implement real-time data updates
   - Add date range filtering for metrics

2. **Widget Functionality**:
   - Connect each widget to appropriate backend data
   - Implement drill-down functionality
   - Add export capabilities

**Backend Reference**: Need to create dashboard analytics endpoints
**Frontend Reference**: `frontend/src/stores/dashboardStore.js`

## Implementation Timeline

### Week 1: Foundation
- [DONE] Phase 1.1: Operating Rooms Integration - Verified alignment between plan, frontend store, and backend API. Existing code largely implements the required functionality.
- [DONE] Phase 1.2: Staff Management Integration (Surgeons)
  - **Original Plan Note:** Plan suggests using `/api/surgeons/` for all staff. Backend API at `api/routers/surgeons.py` is specific to surgeons.
  - **Revised Approach (Surgeons First):** Integrated surgeons using `/api/surgeons/`. Other staff roles (nurses, anesthetists) will require separate backend API development or clarification.
  - **Completed Actions:**
    - Implemented `loadSurgeons` in `frontend/src/stores/resourceStore.js` to fetch surgeons from `/api/surgeons/` and transform data.
    - Modified `addStaff` in `frontend/src/stores/resourceStore.js` to handle surgeon creation via `surgeonAPI.createSurgeon`, including data transformation. Mock behavior retained for other roles.
    - Implemented `updateSurgeon` in `frontend/src/stores/resourceStore.js` to call `surgeonAPI.updateSurgeon` with data transformation.
    - Implemented `deleteSurgeon` in `frontend/src/stores/resourceStore.js` to call `surgeonAPI.deleteSurgeon`.
- [ ] API client configuration and error handling

### Week 2: Core Functionality
- [ ] Phase 2.1: Surgery Scheduling Integration
- [ ] Phase 2.2: Optimization Engine Integration
- [ ] Testing and validation

### Week 3: Advanced Features
- [ ] Phase 3.1: SDST Management Integration
- [ ] Phase 4.1: Dashboard Integration
- [ ] Performance optimization

### Week 4: Polish & Testing
- [ ] End-to-end testing
- [ ] User acceptance testing
- [ ] Documentation updates
- [ ] Deployment preparation

## Technical Considerations

### Data Model Alignment
- **Challenge**: Frontend and backend use different field names
- **Solution**: Implement data transformation layers in store actions
- **Example**: Backend `room_id` → Frontend `id`

### Error Handling Strategy
- **API Errors**: Implement consistent error response handling
- **Network Issues**: Add retry logic and offline indicators
- **Validation**: Client-side validation before API calls

### Performance Optimization
- **Caching**: Implement intelligent data caching in stores
- **Pagination**: Add pagination for large data sets
- **Lazy Loading**: Implement lazy loading for heavy components

### Security Considerations
- **Authentication**: Ensure all API calls include proper JWT tokens
- **Authorization**: Implement role-based access control
- **Data Validation**: Validate all user inputs before API submission

## Success Metrics

### Functional Metrics
- [ ] All CRUD operations working for resources
- [ ] Optimization engine produces valid schedules
- [ ] SDST data properly synchronized
- [ ] Dashboard displays real-time metrics

### Performance Metrics
- [ ] API response times < 200ms for CRUD operations
- [ ] Optimization completes within 30 seconds
- [ ] UI remains responsive during data loading
- [ ] Error rate < 1% for API calls

### User Experience Metrics
- [ ] Intuitive error messages for all failure scenarios
- [ ] Loading indicators for all async operations
- [ ] Consistent data across all views
- [ ] Real-time updates without page refresh

## Risk Mitigation

### High-Risk Areas
1. **Data Consistency**: Implement transaction handling for complex operations
2. **Performance**: Monitor and optimize database queries
3. **User Experience**: Maintain responsive UI during heavy operations

### Contingency Plans
1. **API Failures**: Implement graceful degradation with cached data
2. **Performance Issues**: Add progressive loading and pagination
3. **Data Conflicts**: Implement conflict resolution workflows

## Next Steps

1. **Immediate**: Begin Phase 1.1 Operating Rooms integration
2. **Week 1**: Complete resource management integration
3. **Week 2**: Implement schedule optimization integration
4. **Week 3**: Add SDST and dashboard functionality
5. **Week 4**: Testing, optimization, and deployment

This plan provides a structured approach to integrating the existing frontend and backend components while maintaining system stability and user experience throughout the process.

## Implementation Progress

### DONE - Initial Analysis and Planning
- ✅ Analyzed current frontend and backend codebase structure
- ✅ Identified actual API endpoints and data models
- ✅ Confirmed authentication system is working
- ✅ Validated API service layer exists and is properly structured

### DONE - Phase 1.1: Operating Rooms Integration
**Status**: ✅ COMPLETED
**Implementation Summary**:
- ✅ Added `operatingRoomAPI` import to `resourceStore.js`
- ✅ Implemented `loadOperatingRooms()` method with proper data transformation
- ✅ Updated `addOperatingRoom()` to use real API with backend payload format
- ✅ Updated `updateOperatingRoom()` to use real API with proper state management
- ✅ Updated `deleteOperatingRoom()` to use real API calls
- ✅ Updated `ResourceManagementScreen.vue` to call `loadOperatingRooms()` on mount
- ✅ Data transformation working: `room_id` → `id`, generated `name` from room_id

**Data Model Mapping Implemented**:
- Backend `room_id` → Frontend `id` ✅
- Backend `location` → Frontend `location` ✅
- Frontend `name` = `"OR-" + room_id` ✅
- Frontend `status` = Default "Available" ✅
- Frontend `primaryService` = Default "General" ✅

### IN PROGRESS - Phase 1.2: Staff Management Integration
**Status**: Ready to start
**Next Steps**: Implement staff API integration using surgeon endpoints

## Detailed Action Items

### Action Item 1: Operating Rooms API Integration

**Priority**: CRITICAL
**Estimated Time**: 4-6 hours
**Dependencies**: None

**Current State Analysis**:
- Frontend: `ResourceManagementScreen.vue` displays mock OR data
- Backend: Complete CRUD endpoints exist in `api/routers/operating_rooms.py`
- Store: `resourceStore.js` has placeholder methods

**Specific Changes Required**:

1. **Update resourceStore.js - loadOperatingRooms()**:
```javascript
// Current (mock data):
async loadOperatingRooms() {
  this.operatingRooms = mockOperatingRooms;
}

// New (API integration):
async loadOperatingRooms() {
  try {
    this.isLoading = true;
    const response = await api.get('/operating-rooms/');
    this.operatingRooms = response.data.map(room => ({
      id: room.room_id,
      name: `OR-${room.room_id}`,
      location: room.location,
      status: 'Available', // Default status
      primaryService: 'General' // Default service
    }));
  } catch (error) {
    this.error = error.message;
    throw error;
  } finally {
    this.isLoading = false;
  }
}
```

2. **Update resourceStore.js - addOperatingRoom()**:
```javascript
async addOperatingRoom(orData) {
  try {
    const payload = {
      location: orData.location
    };
    const response = await api.post('/operating-rooms/', payload);
    const newRoom = {
      id: response.data.room_id,
      name: `OR-${response.data.room_id}`,
      location: response.data.location,
      status: 'Available',
      primaryService: orData.primaryService || 'General'
    };
    this.operatingRooms.push(newRoom);
    return { success: true, data: newRoom };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

3. **Update resourceStore.js - updateOperatingRoom()**:
```javascript
async updateOperatingRoom(id, orData) {
  try {
    const payload = {
      location: orData.location
    };
    const response = await api.put(`/operating-rooms/${id}`, payload);
    const index = this.operatingRooms.findIndex(room => room.id === id);
    if (index !== -1) {
      this.operatingRooms[index] = {
        ...this.operatingRooms[index],
        location: response.data.location,
        name: `OR-${response.data.room_id}`
      };
    }
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

4. **Update resourceStore.js - deleteOperatingRoom()**:
```javascript
async deleteOperatingRoom(id) {
  try {
    await api.delete(`/operating-rooms/${id}`);
    this.operatingRooms = this.operatingRooms.filter(room => room.id !== id);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

**Testing Steps**:
1. Verify OR list loads from backend
2. Test adding new operating room
3. Test editing existing operating room
4. Test deleting operating room
5. Verify error handling for network failures

**Backend Endpoints Used**:
- `GET /api/operating-rooms/` - List all operating rooms
- `POST /api/operating-rooms/` - Create new operating room
- `PUT /api/operating-rooms/{room_id}` - Update operating room
- `DELETE /api/operating-rooms/{room_id}` - Delete operating room

**Data Model Mapping**:
- Backend `room_id` → Frontend `id`
- Backend `location` → Frontend `location`
- Frontend `name` = `"OR-" + room_id`
- Frontend `status` = Default "Available"
- Frontend `primaryService` = Default "General"

### Action Item 2: Staff Management API Integration

**Priority**: CRITICAL
**Estimated Time**: 4-6 hours
**Dependencies**: Action Item 1 completed

**Current State Analysis**:
- Frontend: Staff tab in ResourceManagementScreen shows mock data
- Backend: Surgeon endpoints exist in `api/routers/surgeons.py`
- Store: Staff methods in `resourceStore.js` need API integration

**Specific Changes Required**:

1. **Update resourceStore.js - loadStaff()**:
```javascript
async loadStaff() {
  try {
    this.isLoading = true;
    const response = await api.get('/surgeons/');
    this.staff = response.data.map(surgeon => ({
      id: surgeon.surgeon_id,
      name: surgeon.name,
      role: 'Surgeon',
      specializations: surgeon.specialization ? [surgeon.specialization] : [],
      status: 'Available',
      contactInfo: surgeon.contact_info
    }));
  } catch (error) {
    this.error = error.message;
    throw error;
  } finally {
    this.isLoading = false;
  }
}
```

2. **Update resourceStore.js - addStaff()**:
```javascript
async addStaff(staffData) {
  try {
    const payload = {
      name: staffData.name,
      specialization: staffData.specializations.join(', '),
      contact_info: staffData.contactInfo || ''
    };
    const response = await api.post('/surgeons/', payload);
    const newStaff = {
      id: response.data.surgeon_id,
      name: response.data.name,
      role: 'Surgeon',
      specializations: response.data.specialization ? [response.data.specialization] : [],
      status: 'Available',
      contactInfo: response.data.contact_info
    };
    this.staff.push(newStaff);
    return { success: true, data: newStaff };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

**Backend Endpoints Used**:
- `GET /api/surgeons/` - List all surgeons
- `POST /api/surgeons/` - Create new surgeon
- `PUT /api/surgeons/{surgeon_id}` - Update surgeon
- `DELETE /api/surgeons/{surgeon_id}` - Delete surgeon

### Action Item 3: Schedule Optimization Integration

**Priority**: HIGH
**Estimated Time**: 8-10 hours
**Dependencies**: Resource management integration completed

**Current State Analysis**:
- Frontend: "Run Optimization" button in SurgerySchedulingScreen is non-functional
- Backend: Complete optimization endpoint exists at `/api/schedules/optimize`
- Store: `scheduleStore.js` needs optimization methods

**Specific Changes Required**:

1. **Update scheduleStore.js - runOptimization()**:
```javascript
async runOptimization(parameters = {}) {
  try {
    this.isOptimizing = true;
    this.optimizationProgress = 0;

    const payload = {
      schedule_date: parameters.date || new Date().toISOString().split('T')[0],
      max_iterations: parameters.maxIterations || 100,
      tabu_tenure: parameters.tabuTenure || 10,
      max_no_improvement: parameters.maxNoImprovement || 20,
      time_limit_seconds: parameters.timeLimit || 300,
      weights: parameters.weights || null
    };

    const response = await api.post('/schedules/optimize', payload);

    this.lastOptimizationResult = {
      assignments: response.data.assignments,
      score: response.data.score,
      metrics: response.data.metrics,
      executionTime: response.data.execution_time_seconds
    };

    return { success: true, result: this.lastOptimizationResult };
  } catch (error) {
    return { success: false, error: error.message };
  } finally {
    this.isOptimizing = false;
  }
}
```

2. **Update scheduleStore.js - applyOptimizedSchedule()**:
```javascript
async applyOptimizedSchedule(assignments) {
  try {
    await api.post('/schedules/apply', assignments);
    await this.loadCurrentSchedule(); // Refresh schedule display
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

3. **Update SurgerySchedulingScreen.vue - Connect optimization button**:
```javascript
// In the component methods:
async handleRunOptimization() {
  const parameters = {
    date: this.selectedDate,
    maxIterations: this.optimizationSettings.maxIterations,
    timeLimit: this.optimizationSettings.timeLimit
  };

  const result = await scheduleStore.runOptimization(parameters);

  if (result.success) {
    this.showOptimizationResults = true;
    this.optimizationResults = result.result;
    this.$toast.success('Optimization completed successfully!');
  } else {
    this.$toast.error(`Optimization failed: ${result.error}`);
  }
}
```

**Backend Endpoints Used**:
- `POST /api/schedules/optimize` - Run schedule optimization
- `POST /api/schedules/apply` - Apply optimized schedule
- `GET /api/schedules/current` - Get current schedule

### Action Item 4: Current Schedule Display Integration

**Priority**: HIGH
**Estimated Time**: 6-8 hours
**Dependencies**: Basic API integration completed

**Current State Analysis**:
- Frontend: Gantt chart and schedule views show mock data
- Backend: `/api/schedules/current` endpoint provides enriched schedule data
- Store: `scheduleStore.js` needs current schedule loading

**Specific Changes Required**:

1. **Update scheduleStore.js - loadCurrentSchedule()**:
```javascript
async loadCurrentSchedule(date = null) {
  try {
    this.isLoading = true;
    const params = date ? { date: date } : {};
    const response = await api.get('/schedules/current', { params });

    this.currentSchedule = response.data.map(assignment => ({
      surgeryId: assignment.surgery_id,
      roomId: assignment.room_id,
      room: assignment.room,
      surgeonId: assignment.surgeon_id,
      surgeon: assignment.surgeon,
      surgeryType: assignment.surgery_type,
      startTime: new Date(assignment.start_time),
      endTime: new Date(assignment.end_time),
      duration: assignment.duration_minutes,
      patientName: assignment.patient_name,
      urgencyLevel: assignment.urgency_level,
      status: assignment.status
    }));

    return { success: true };
  } catch (error) {
    this.error = error.message;
    return { success: false, error: error.message };
  } finally {
    this.isLoading = false;
  }
}
```

2. **Update GanttChart.vue to use real data**:
```javascript
// Transform schedule data for Gantt display
computed: {
  ganttData() {
    return this.scheduleStore.currentSchedule.map(item => ({
      id: item.surgeryId,
      text: `${item.surgeryType} - ${item.patientName}`,
      start_date: item.startTime,
      end_date: item.endTime,
      room: item.room,
      surgeon: item.surgeon,
      urgency: item.urgencyLevel
    }));
  }
}
```

**Backend Endpoints Used**:
- `GET /api/schedules/current?date=YYYY-MM-DD` - Get current schedule for date

### Action Item 5: SDST Management Integration

**Priority**: MEDIUM
**Estimated Time**: 10-12 hours
**Dependencies**: Core functionality completed

**Current State Analysis**:
- Frontend: SDST management screen exists but not connected
- Backend: Need to verify SDST endpoints exist
- Store: `sdstStore.js` needs complete implementation

**Investigation Required**:
1. Check if SDST endpoints exist in backend
2. Verify surgery types management endpoints
3. Confirm SDST matrix data structure

**Specific Changes Required** (pending backend verification):

1. **Update sdstStore.js - loadSurgeryTypes()**:
```javascript
async loadSurgeryTypes() {
  try {
    this.isLoading = true;
    const response = await api.get('/surgery-types/');
    this.surgeryTypes = response.data;
  } catch (error) {
    this.error = error.message;
    throw error;
  } finally {
    this.isLoading = false;
  }
}
```

2. **Update sdstStore.js - loadSDSTMatrix()**:
```javascript
async loadSDSTMatrix() {
  try {
    const response = await api.get('/sdst/matrix');
    this.sdstMatrix = response.data;
  } catch (error) {
    this.error = error.message;
    throw error;
  }
}
```

**Backend Endpoints Needed**:
- `GET /api/surgery-types/` - List surgery types
- `POST /api/surgery-types/` - Create surgery type
- `GET /api/sdst/matrix` - Get SDST matrix
- `PUT /api/sdst/matrix` - Update SDST matrix

### Action Item 6: Dashboard Metrics Integration

**Priority**: LOW
**Estimated Time**: 6-8 hours
**Dependencies**: Core functionality completed

**Current State Analysis**:
- Frontend: Dashboard widgets show placeholder data
- Backend: Need to create dashboard analytics endpoints
- Store: `dashboardStore.js` needs metrics loading

**Backend Development Required**:
1. Create dashboard analytics endpoints
2. Implement KPI calculation services
3. Add real-time metrics updates

**Specific Changes Required** (pending backend development):

1. **Create dashboard analytics endpoints**:
```python
# In new api/routers/dashboard.py
@router.get("/metrics")
async def get_dashboard_metrics():
    # Calculate and return dashboard KPIs
    pass

@router.get("/utilization")
async def get_resource_utilization():
    # Calculate resource utilization metrics
    pass
```

2. **Update dashboardStore.js**:
```javascript
async loadDashboardMetrics() {
  try {
    const response = await api.get('/dashboard/metrics');
    this.metrics = response.data;
  } catch (error) {
    this.error = error.message;
  }
}
```

## Implementation Priority Matrix

| Action Item | Priority | Complexity | Impact | Dependencies |
|-------------|----------|------------|--------|--------------|
| Operating Rooms API | CRITICAL | Low | High | None |
| Staff Management API | CRITICAL | Low | High | Item 1 |
| Schedule Optimization | HIGH | High | Critical | Items 1,2 |
| Current Schedule Display | HIGH | Medium | High | Items 1,2 |
| SDST Management | MEDIUM | High | Medium | Backend verification |
| Dashboard Metrics | LOW | Medium | Low | Backend development |

## Quality Assurance Checklist

### For Each Action Item:
- [ ] API endpoints tested with Postman/curl
- [ ] Frontend store actions handle success/error cases
- [ ] Loading states implemented in UI
- [ ] Error messages displayed to users
- [ ] Data transformations preserve data integrity
- [ ] Component reactivity works correctly
- [ ] Browser console shows no errors
- [ ] Network tab shows correct API calls

### Integration Testing:
- [ ] End-to-end user workflows function correctly
- [ ] Data consistency across different views
- [ ] Real-time updates work as expected
- [ ] Performance meets requirements (<200ms for CRUD)
- [ ] Error handling graceful and informative

This detailed action plan provides specific code changes, testing steps, and quality assurance measures for each integration task.
