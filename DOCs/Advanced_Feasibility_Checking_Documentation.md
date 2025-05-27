# Advanced Feasibility Checking Documentation (Task 2.3)

## Overview

The Advanced Feasibility Checking system provides comprehensive constraint validation for surgery scheduling, extending beyond basic availability checks to include sophisticated equipment, staff, and specialization constraints with detailed violation reporting.

## Features Implemented

### 1. Enhanced Equipment Availability Checking
- **Advanced Equipment Constraints**: Validates equipment availability with consideration for maintenance windows, concurrent usage limits, and setup/cleanup times
- **Equipment Location Tracking**: Supports mobile equipment and room-specific availability
- **Conflict Detection**: Identifies equipment usage conflicts across multiple surgeries
- **Maintenance Window Awareness**: Prevents scheduling during equipment maintenance periods

### 2. Staff Availability Constraints
- **Role-Based Validation**: Ensures appropriate staff roles are available for specific surgery types
- **Concurrent Assignment Limits**: Prevents staff from being assigned to multiple surgeries simultaneously
- **Working Hours Compliance**: Validates staff assignments against their available working hours
- **Daily Hour Limits**: Enforces maximum daily working hour constraints
- **Qualification Matching**: Verifies staff qualifications for specific surgery types

### 3. Surgeon Specialization Matching
- **Specialization Validation**: Ensures surgeons are qualified for assigned surgery types
- **Experience Level Checking**: Considers surgeon experience levels for complex procedures
- **Restriction Enforcement**: Prevents assignment of restricted surgery types to specific surgeons
- **Supervision Requirements**: Identifies when surgeon supervision is required

### 4. Custom Constraint Configuration API
- **Flexible Rule Engine**: Supports custom constraint rules with configurable conditions
- **Multiple Rule Types**: Time-based, resource-based, and duration-based constraints
- **Priority System**: Allows prioritization of constraint rules
- **Dynamic Configuration**: Runtime addition, modification, and removal of constraints

### 5. Constraint Violation Reporting
- **Detailed Violation Information**: Comprehensive violation details with severity levels
- **Resolution Suggestions**: Automated suggestions for resolving constraint violations
- **Performance Metrics**: Tracks constraint checking performance and statistics
- **Comprehensive Reporting**: Schedule-level violation analysis and recommendations

## API Endpoints

### Feasibility Checking

#### POST `/api/schedules/feasibility/check`
Perform advanced feasibility check with detailed constraint validation.

**Request Body:**
```json
{
  "surgery_id": 1,
  "room_id": 2,
  "start_time": "2024-01-15T09:00:00",
  "end_time": "2024-01-15T11:00:00",
  "current_assignments": [],
  "ignore_surgery_id": null,
  "check_equipment": true,
  "check_staff": true,
  "check_specialization": true,
  "check_custom_constraints": true
}
```

**Response:**
```json
{
  "is_feasible": false,
  "surgery_id": 1,
  "room_id": 2,
  "start_time": "2024-01-15T09:00:00",
  "end_time": "2024-01-15T11:00:00",
  "violations": [
    {
      "constraint_id": "equipment_unavailable_1",
      "constraint_type": "equipment_availability",
      "severity": "critical",
      "description": "Equipment 'Surgical Scalpel' is marked as unavailable",
      "surgery_id": 1,
      "equipment_id": 1,
      "suggested_actions": [
        "Check equipment maintenance status",
        "Find alternative equipment",
        "Reschedule surgery"
      ]
    }
  ],
  "warnings": [],
  "check_duration_ms": 45.2,
  "constraints_checked": 5,
  "equipment_feasible": false,
  "staff_feasible": true,
  "specialization_feasible": true,
  "room_feasible": true,
  "recommendations": [
    "Review equipment requirements and availability",
    "Address critical violations before proceeding"
  ]
}
```

#### POST `/api/schedules/feasibility/validate-schedule`
Validate constraints for an entire schedule.

**Query Parameters:**
- `schedule_date`: Date of schedule to validate (required)

**Response:**
```json
{
  "total_surgeries": 8,
  "feasible_surgeries": 6,
  "feasibility_rate": 0.75,
  "total_violations": 3,
  "critical_violations": 1,
  "violations_by_type": {
    "equipment_availability": 2,
    "staff_availability": 1
  },
  "recommendations": [
    "Review equipment allocation across all surgeries",
    "Address critical violations immediately"
  ]
}
```

### Constraint Configuration Management

#### GET `/api/schedules/constraints/configurations`
Get all constraint configurations.

**Query Parameters:**
- `constraint_type`: Filter by constraint type (optional)
- `enabled_only`: Return only enabled constraints (optional)

#### POST `/api/schedules/constraints/configurations`
Add or update a constraint configuration.

**Request Body:**
```json
{
  "constraint_id": "equipment_availability",
  "constraint_type": "equipment_availability",
  "name": "Equipment Availability",
  "description": "Ensures required equipment is available during surgery time",
  "severity": "critical",
  "enabled": true,
  "parameters": {
    "check_maintenance_windows": true,
    "check_concurrent_usage": true,
    "include_setup_cleanup_time": true
  },
  "applies_to_surgery_types": null,
  "applies_to_rooms": null,
  "applies_to_surgeons": null
}
```

#### DELETE `/api/schedules/constraints/configurations/{constraint_id}`
Remove a constraint configuration.

### Custom Rule Management

#### GET `/api/schedules/constraints/rules`
Get all custom constraint rules.

**Query Parameters:**
- `enabled_only`: Return only enabled rules (optional)
- `rule_type`: Filter by rule type (optional)

#### POST `/api/schedules/constraints/rules`
Add or update a custom constraint rule.

**Request Body:**
```json
{
  "rule_id": "business_hours_only",
  "name": "Business Hours Only",
  "description": "Surgeries must be scheduled during business hours",
  "rule_type": "time_based",
  "conditions": {
    "allowed_hours": {
      "start": "08:00",
      "end": "17:00"
    },
    "allowed_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
  },
  "actions": {},
  "applies_to": {
    "surgery_types": [1, 2, 3],
    "rooms": [1, 2]
  },
  "priority": 100,
  "enabled": true,
  "created_by": "admin"
}
```

#### DELETE `/api/schedules/constraints/rules/{rule_id}`
Remove a custom constraint rule.

### Violation Reporting

#### GET `/api/schedules/constraints/violations/report`
Generate a comprehensive constraint violations report.

**Query Parameters:**
- `schedule_date`: Date to generate report for (required)
- `constraint_types`: Filter by constraint types (optional)
- `severity_levels`: Filter by severity levels (optional)

**Response:**
```json
{
  "schedule_date": "2024-01-15",
  "total_surgeries": 10,
  "violations": [...],
  "summary": {
    "total_violations": 5,
    "critical_violations": 2,
    "violations_by_type": {
      "equipment_availability": 3,
      "staff_availability": 1,
      "surgeon_specialization": 1
    },
    "violations_by_severity": {
      "critical": 2,
      "high": 2,
      "medium": 1
    },
    "affected_surgeries": 4
  },
  "recommendations": [
    "Review equipment allocation and scheduling",
    "Address critical violations immediately"
  ]
}
```

## Constraint Types

### Equipment Availability
- **Type**: `equipment_availability`
- **Severity**: Critical
- **Checks**: Equipment existence, availability status, concurrent usage, maintenance windows

### Staff Availability
- **Type**: `staff_availability`
- **Severity**: Critical
- **Checks**: Staff existence, availability status, concurrent assignments, working hours, qualifications

### Surgeon Specialization
- **Type**: `surgeon_specialization`
- **Severity**: High
- **Checks**: Surgeon qualifications, specialization matching, experience requirements

### Room Capacity
- **Type**: `room_capacity`
- **Severity**: High
- **Checks**: Physical space, equipment space, staff capacity

### Time Window
- **Type**: `time_window`
- **Severity**: Medium
- **Checks**: Allowed time ranges, day restrictions, operational hours

### Resource Conflict
- **Type**: `resource_conflict`
- **Severity**: Critical
- **Checks**: Resource availability conflicts, scheduling overlaps

### Custom
- **Type**: `custom`
- **Severity**: Configurable
- **Checks**: User-defined constraint rules

## Severity Levels

1. **Critical**: Must be satisfied for feasible scheduling
2. **High**: Should be satisfied for optimal scheduling
3. **Medium**: Preferred to be satisfied
4. **Low**: Nice to have constraints

## Custom Rule Types

### Time-Based Rules
- **Allowed Hours**: Restrict surgeries to specific time windows
- **Allowed Days**: Limit surgeries to certain days of the week
- **Blackout Periods**: Prevent scheduling during specific periods

### Resource-Based Rules
- **Room Restrictions**: Limit certain surgeries to specific rooms
- **Equipment Requirements**: Enforce specific equipment for surgery types
- **Staff Requirements**: Mandate specific staff roles for procedures

### Duration-Based Rules
- **Maximum Duration**: Limit surgery duration
- **Minimum Duration**: Ensure adequate time allocation
- **Buffer Time**: Require setup/cleanup time between surgeries

## Integration with Optimization Engine

The Advanced Feasibility Checker integrates seamlessly with the existing optimization engine:

1. **Pre-Optimization Validation**: Validates initial schedules before optimization
2. **Real-Time Constraint Checking**: Evaluates constraints during neighborhood generation
3. **Post-Optimization Verification**: Ensures final schedules meet all constraints
4. **Emergency Surgery Integration**: Validates emergency insertions against all constraints

## Performance Considerations

- **Caching**: Implements intelligent caching for frequently accessed data
- **Batch Processing**: Supports batch validation for entire schedules
- **Parallel Processing**: Constraint checks can be parallelized for better performance
- **Incremental Validation**: Only re-validates affected constraints when schedules change

## Error Handling

The system provides comprehensive error handling:

- **Graceful Degradation**: Continues checking other constraints if one fails
- **Detailed Error Messages**: Provides specific information about constraint failures
- **Recovery Suggestions**: Offers actionable recommendations for resolving violations
- **Logging**: Comprehensive logging for debugging and monitoring

## Future Enhancements

Potential areas for future development:

1. **Machine Learning Integration**: Learn from historical constraint violations
2. **Predictive Constraints**: Anticipate potential violations before they occur
3. **Dynamic Constraint Adjustment**: Automatically adjust constraints based on conditions
4. **Integration with External Systems**: Connect with hospital management systems
5. **Advanced Reporting**: More sophisticated analytics and reporting capabilities
