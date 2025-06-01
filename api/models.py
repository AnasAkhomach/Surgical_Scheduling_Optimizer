"""
Pydantic models for the FastAPI application.

This module provides Pydantic models for request and response validation.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import json # Added for field_validator
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator


class SurgeryStatus(str, Enum):
    """Enum for surgery status."""
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class AppointmentStatus(str, Enum):
    """Enum for appointment status."""
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class UrgencyLevel(str, Enum):
    """Enum for surgery urgency level."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EMERGENCY = "Emergency"


class EmergencyType(str, Enum):
    """Enum for emergency surgery types."""
    TRAUMA = "Trauma"
    CARDIAC = "Cardiac"
    NEUROLOGICAL = "Neurological"
    OBSTETRIC = "Obstetric"
    GENERAL = "General"
    OTHER = "Other"


class EmergencyPriority(str, Enum):
    """Enum for emergency priority levels."""
    IMMEDIATE = "Immediate"  # Life-threatening, needs surgery within 15 minutes
    URGENT = "Urgent"       # Needs surgery within 1 hour
    SEMI_URGENT = "Semi-Urgent"  # Needs surgery within 4 hours
    SCHEDULED = "Scheduled"  # Can be scheduled normally


class ConflictResolutionStrategy(str, Enum):
    """Enum for conflict resolution strategies."""
    BUMP_LOWER_PRIORITY = "bump_lower_priority"
    EXTEND_HOURS = "extend_hours"
    USE_BACKUP_ROOM = "use_backup_room"
    SPLIT_SURGERY = "split_surgery"
    MANUAL_REVIEW = "manual_review"


# Base models (for shared attributes)
class PatientBase(BaseModel):
    """Base model for patient data."""
    name: str
    dob: date
    contact_info: Optional[str] = None
    privacy_consent: bool = False


class SurgeonBase(BaseModel):
    """Base model for surgeon data."""
    name: str
    contact_info: Optional[str] = None
    specialization: str
    credentials: str
    availability: bool = True


class StaffBase(BaseModel):
    """Base model for staff data."""
    name: str
    role: str
    contact_info: Optional[str] = None
    specializations: Optional[List[str]] = Field(default_factory=list) # Changed from specialization (string) to list, added default_factory
    status: str = Field(default="Active") # Added status, e.g., "Active", "On Leave", "Inactive"
    availability: bool = True # Kept availability as it's in the original model and StaffResponse

    @field_validator('specializations', mode='before')
    @classmethod
    def parse_specializations_from_db(cls, v):
        if isinstance(v, str):
            try:
                loaded_json = json.loads(v)
                if isinstance(loaded_json, list):
                    return loaded_json
                return [] # Or raise ValueError if structure is wrong
            except json.JSONDecodeError:
                # This case might occur if the string is not valid JSON.
                # Depending on requirements, could return empty list, raise error, or attempt other parsing.
                return [] # Default to empty list on error
        if v is None: # If DB stores NULL for specializations
            return []
        # If it's already a list (e.g. during direct Pydantic model creation/validation, not from DB attribute)
        if isinstance(v, list):
            return v
        # Fallback or error for unexpected types
        return [] # Or raise TypeError


class OperatingRoomBase(BaseModel):
    """Base model for operating room data."""
    name: str = Field(..., description="Name of the operating room")
    location: str
    status: str = Field(default="Active", description="e.g., Active, Under Maintenance, Inactive")
    primary_service: Optional[str] = Field(default=None, alias="primaryService", description="Primary service of the OR")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SurgeryBase(BaseModel):
    """Base model for surgery data."""
    surgery_type_id: int
    duration_minutes: int
    urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM
    patient_id: Optional[int] = None
    surgeon_id: Optional[int] = None
    room_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: SurgeryStatus = SurgeryStatus.SCHEDULED


class SurgeryTypeBase(BaseModel):
    """Base model for surgery type data."""
    name: str = Field(..., min_length=1, max_length=100, description="Surgery type name")
    description: Optional[str] = Field(None, max_length=500, description="Surgery type description")
    average_duration: int = Field(..., gt=0, le=1440, description="Average duration in minutes (1-1440)")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Surgery type name cannot be empty')
        return v.strip()


class SequenceDependentSetupTimeBase(BaseModel):
    """Base model for sequence-dependent setup time data."""
    from_surgery_type_id: int = Field(..., gt=0, description="Source surgery type ID")
    to_surgery_type_id: int = Field(..., gt=0, description="Target surgery type ID")
    setup_time_minutes: int = Field(..., ge=0, le=480, description="Setup time in minutes (0-480)")

    @field_validator('to_surgery_type_id')
    @classmethod
    def validate_different_surgery_types(cls, v, info):
        if 'from_surgery_type_id' in info.data and v == info.data['from_surgery_type_id']:
            raise ValueError('From and to surgery types must be different')
        return v


class AppointmentBase(BaseModel):
    """Base model for appointment data."""
    patient_id: int
    surgeon_id: int
    room_id: Optional[int] = None
    appointment_date: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None


class UserBase(BaseModel):
    """Base model for user data."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = None  # Made optional for public registration
    staff_id: Optional[int] = None


# Create models (for request payloads)
class PatientCreate(PatientBase):
    """Model for creating a patient."""
    pass


class SurgeonCreate(SurgeonBase):
    """Model for creating a surgeon."""
    pass


class StaffCreate(StaffBase):
    """Model for creating a staff member."""
    pass


class OperatingRoomCreate(OperatingRoomBase):
    """Model for creating an operating room."""
    pass


class OperatingRoomEquipmentBase(BaseModel):
    """Base model for operating room equipment data."""
    name: str
    type: str
    serial_number: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None


class OperatingRoomEquipmentCreate(OperatingRoomEquipmentBase):
    """Model for creating operating room equipment."""
    pass


class OperatingRoomEquipment(OperatingRoomEquipmentBase):
    """Model for operating room equipment with ID."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class SurgeryCreate(SurgeryBase):
    pass


class SurgeryReschedule(BaseModel):
    """Model for rescheduling a surgery."""
    or_id: int = Field(..., description="The ID of the new operating room.")
    start_time: datetime = Field(..., description="The new start time for the surgery.")
    end_time: datetime = Field(..., description="The new end time for the surgery.")

    model_config = ConfigDict(from_attributes=True)


class SurgeryUpdate(SurgeryBase): # Assuming SurgeryUpdate might exist or be needed
    """Model for updating an existing surgery's details (excluding reschedule specific fields)."""
    # Add fields that can be updated generally, excluding or_id, start_time, end_time if they are only for reschedule
    # For example:
    surgery_type_id: Optional[int] = None
    duration_minutes: Optional[int] = None
    urgency_level: Optional[UrgencyLevel] = None
    patient_id: Optional[int] = None
    surgeon_id: Optional[int] = None
    # room_id: Optional[int] = None # Handled by reschedule
    # start_time: Optional[datetime] = None # Handled by reschedule
    # end_time: Optional[datetime] = None # Handled by reschedule
    status: Optional[SurgeryStatus] = None
    notes: Optional[str] = None
    # Ensure this model does not conflict with how updates are handled elsewhere

    model_config = ConfigDict(from_attributes=True)


class Surgery(SurgeryBase):
    """Model for surgery response, including ID."""
    surgery_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SurgeryCreate(SurgeryBase):
    """Model for creating a surgery."""
    pass


class SurgeryTypeCreate(SurgeryTypeBase):
    """Model for creating a surgery type."""
    pass


class SequenceDependentSetupTimeCreate(SequenceDependentSetupTimeBase):
    """Model for creating sequence-dependent setup time data."""
    pass


class AppointmentCreate(AppointmentBase):
    """Model for creating an appointment."""
    pass


class UserCreate(UserBase):
    """Model for creating a user."""
    password: str


# Response models (for API responses)
class Patient(PatientBase):
    """Model for patient response."""
    patient_id: int

    model_config = ConfigDict(from_attributes=True)


class Surgeon(SurgeonBase):
    """Model for surgeon response."""
    surgeon_id: int = Field(alias="surgeonId")
    id: Optional[int] = Field(default=None, alias="id")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    def model_post_init(self, __context) -> None:
        """Post-initialization to set computed fields."""
        # Map surgeon_id to id for frontend compatibility
        if self.id is None and self.surgeon_id is not None:
            self.id = self.surgeon_id


class Staff(StaffBase):
    """Model for staff response."""
    staff_id: int = Field(alias="staffId")
    id: Optional[int] = Field(default=None, alias="id")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    def model_post_init(self, __context) -> None:
        """Post-initialization to set computed fields."""
        # Map staff_id to id for frontend compatibility
        if self.id is None and self.staff_id is not None:
            self.id = self.staff_id


class OperatingRoom(OperatingRoomBase):
    """Model for operating room response."""
    room_id: int = Field(alias="roomId")
    id: Optional[int] = Field(default=None, alias="id")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    def model_post_init(self, __context) -> None:
        """Post-initialization to set computed fields."""
        # Map room_id to id for frontend compatibility
        if self.id is None and self.room_id is not None:
            self.id = self.room_id

        # Ensure all required fields have default values if missing from database
        if not self.name:
            self.name = f"OR {self.room_id or 'Unknown'}"
        if not self.status:
            self.status = "Active"
        if self.primary_service is None:
            self.primary_service = None


class SurgeryType(SurgeryTypeBase):
    """Model for surgery type response."""
    type_id: int

    model_config = ConfigDict(from_attributes=True)


class SequenceDependentSetupTime(SequenceDependentSetupTimeBase):
    """Model for sequence-dependent setup time response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class Surgery(SurgeryBase):
    """Model for surgery response."""
    surgery_id: int
    id: Optional[int] = Field(default=None, alias="id")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    def model_post_init(self, __context) -> None:
        """Post-initialization to set computed fields."""
        # Map surgery_id to id for frontend compatibility
        if self.id is None and self.surgery_id is not None:
            self.id = self.surgery_id


class Appointment(AppointmentBase):
    """Model for appointment response."""
    appointment_id: int
    id: Optional[int] = Field(default=None, alias="id")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    def model_post_init(self, __context) -> None:
        """Post-initialization to set computed fields."""
        # Map appointment_id to id for frontend compatibility
        if self.id is None and self.appointment_id is not None:
            self.id = self.appointment_id


class User(UserBase):
    """Model for user response."""
    user_id: int
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Authentication models
class Token(BaseModel):
    """Model for authentication token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Model for token data."""
    username: Optional[str] = None
    role: Optional[str] = None


# Update models (for partial updates)
class PatientUpdate(BaseModel):
    """Model for updating a patient."""
    name: Optional[str] = None
    contact_info: Optional[str] = None
    privacy_consent: Optional[bool] = None


class SurgeonUpdate(BaseModel):
    """Model for updating a surgeon."""
    name: Optional[str] = None
    contact_info: Optional[str] = None
    specialization: Optional[str] = None
    credentials: Optional[str] = None
    availability: Optional[bool] = None


class StaffUpdate(BaseModel):
    """Model for updating a staff member."""
    name: Optional[str] = None
    role: Optional[str] = None
    contact_info: Optional[str] = None
    specializations: Optional[List[str]] = None # Changed from specialization
    status: Optional[str] = None # Added status
    availability: Optional[bool] = None


class OperatingRoomUpdate(BaseModel):
    """Model for updating an operating room."""
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    primary_service: Optional[str] = Field(None, alias="primaryService")

    class Config:
        populate_by_name = True  # Allow both field name and alias


class SurgeryUpdate(BaseModel):
    """Model for updating a surgery."""
    surgery_type_id: Optional[int] = None
    duration_minutes: Optional[int] = None
    urgency_level: Optional[UrgencyLevel] = None
    patient_id: Optional[int] = None
    surgeon_id: Optional[int] = None
    room_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[SurgeryStatus] = None


class SurgeryTypeUpdate(BaseModel):
    """Model for updating a surgery type."""
    name: Optional[str] = None
    description: Optional[str] = None
    average_duration: Optional[int] = None


class SequenceDependentSetupTimeUpdate(BaseModel):
    """Model for updating a sequence-dependent setup time."""
    from_surgery_type_id: Optional[int] = None
    to_surgery_type_id: Optional[int] = None
    setup_time_minutes: Optional[int] = None


class UserUpdate(BaseModel):
    """Model for updating a user."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    staff_id: Optional[int] = None
    is_active: Optional[bool] = None


# Bulk operation models
class BulkSDSTImport(BaseModel):
    """Model for bulk importing SDST data."""
    sdst_data: List[SequenceDependentSetupTimeCreate]
    overwrite_existing: bool = False


class BulkSDSTExport(BaseModel):
    """Model for bulk exporting SDST data."""
    surgery_type_ids: Optional[List[int]] = None  # If None, export all


class SDSTMatrix(BaseModel):
    """Model for SDST matrix representation."""
    surgery_types: List[SurgeryType]
    setup_times: List[SequenceDependentSetupTime]
    matrix: Dict[str, Dict[str, int]]  # from_type_id -> to_type_id -> setup_time


# Enhanced response models for frontend consumption
class ScheduleAssignment(BaseModel):
    """Model for schedule assignment with enriched data."""
    surgery_id: int
    room_id: int
    room: str  # e.g., "OR-1"
    surgeon_id: Optional[int] = None
    surgeon: Optional[str] = None  # e.g., "Dr. Smith"
    surgery_type_id: int
    surgery_type: str  # e.g., "Appendectomy"
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    urgency_level: Optional[UrgencyLevel] = None
    status: Optional[SurgeryStatus] = None


class CurrentScheduleResponse(BaseModel):
    """Response model for current schedule endpoint."""
    surgeries: List[ScheduleAssignment]
    date: Optional[str] = None
    total_count: int
    status: str


class SurgeryEnriched(BaseModel):
    """Enhanced surgery model with related entity names for frontend consumption."""
    surgery_id: int
    surgery_type_id: int
    surgery_type: str  # Surgery type name
    duration_minutes: int
    urgency_level: UrgencyLevel
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    surgeon_id: Optional[int] = None
    surgeon_name: Optional[str] = None
    room_id: Optional[int] = None
    room_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: SurgeryStatus

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Model for error responses."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ScheduleConflict(BaseModel):
    """Model for schedule conflicts."""
    conflict_type: str
    surgery_id: int
    conflicting_surgery_id: Optional[int] = None
    resource_type: str
    resource_id: int
    conflict_start: datetime
    conflict_end: datetime
    severity: str
    message: str


class ScheduleValidationResult(BaseModel):
    """Model for schedule validation results."""
    is_valid: bool
    conflicts: List[ScheduleConflict]
    warnings: List[str]
    total_conflicts: int
    critical_conflicts: int


class ManualScheduleAdjustment(BaseModel):
    """Model for manual schedule adjustments."""
    surgery_id: int
    new_room_id: Optional[int] = None
    new_surgeon_id: Optional[int] = None
    new_start_time: Optional[datetime] = None
    new_duration_minutes: Optional[int] = None
    reason: str
    force_override: bool = False


class ScheduleComparison(BaseModel):
    """Model for schedule comparison."""
    current_schedule: List[ScheduleAssignment]
    proposed_schedule: List[ScheduleAssignment]
    changes: List[Dict[str, Any]]
    metrics_comparison: Dict[str, Dict[str, float]]
    improvement_summary: str


class ScheduleHistoryEntry(BaseModel):
    """Model for schedule history entries."""
    history_id: int
    schedule_date: date
    created_at: datetime
    created_by_user_id: int
    created_by_username: str
    action_type: str
    changes_summary: str
    affected_surgeries: List[int]
    schedule_snapshot: List[ScheduleAssignment]





# Enhanced Optimization Models for Task 2.1
class OptimizationAlgorithm(str, Enum):
    """Enum for optimization algorithm types."""
    BASIC_TABU = "basic_tabu"
    ADAPTIVE_TABU = "adaptive_tabu"
    REACTIVE_TABU = "reactive_tabu"
    HYBRID_TABU = "hybrid_tabu"


class OptimizationStatus(str, Enum):
    """Enum for optimization status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AdvancedOptimizationParameters(BaseModel):
    """Enhanced model for advanced optimization parameters."""
    # Basic parameters
    schedule_date: Optional[date] = None
    max_iterations: int = Field(default=100, ge=10, le=10000, description="Maximum number of iterations")
    tabu_tenure: int = Field(default=10, ge=1, le=100, description="Base tabu tenure")
    max_no_improvement: int = Field(default=20, ge=5, le=1000, description="Max iterations without improvement")
    time_limit_seconds: int = Field(default=300, ge=10, le=3600, description="Time limit in seconds")

    # Algorithm selection
    algorithm: OptimizationAlgorithm = Field(default=OptimizationAlgorithm.BASIC_TABU, description="Algorithm variant to use")

    # Advanced tabu parameters
    min_tabu_tenure: Optional[int] = Field(default=None, ge=1, le=50, description="Minimum tabu tenure for adaptive algorithms")
    max_tabu_tenure: Optional[int] = Field(default=None, ge=10, le=200, description="Maximum tabu tenure for adaptive algorithms")
    tenure_adaptation_factor: float = Field(default=1.2, ge=1.0, le=3.0, description="Factor for tenure adaptation")

    # Diversification parameters
    diversification_threshold: int = Field(default=50, ge=10, le=500, description="Iterations before diversification")
    diversification_strength: float = Field(default=0.3, ge=0.1, le=1.0, description="Strength of diversification (0.1-1.0)")

    # Intensification parameters
    intensification_threshold: int = Field(default=25, ge=5, le=200, description="Iterations for intensification")
    intensification_factor: float = Field(default=0.8, ge=0.1, le=1.0, description="Factor for intensification")

    # Multi-objective weights
    weights: Optional[Dict[str, float]] = Field(default=None, description="Custom weights for evaluation criteria")

    # Performance parameters
    enable_progress_tracking: bool = Field(default=True, description="Enable real-time progress tracking")
    progress_update_interval: int = Field(default=10, ge=1, le=100, description="Progress update interval (iterations)")
    enable_detailed_logging: bool = Field(default=False, description="Enable detailed optimization logging")

    # Caching parameters
    cache_results: bool = Field(default=True, description="Cache optimization results")
    cache_key: Optional[str] = Field(default=None, description="Custom cache key")


class OptimizationProgress(BaseModel):
    """Model for optimization progress tracking."""
    optimization_id: str
    status: OptimizationStatus
    current_iteration: int
    total_iterations: int
    best_score: float
    current_score: float
    iterations_without_improvement: int
    elapsed_time_seconds: float
    estimated_remaining_seconds: Optional[float] = None
    progress_percentage: float
    algorithm_used: OptimizationAlgorithm
    last_update: datetime


class OptimizationResult(BaseModel):
    """Enhanced model for optimization result response."""
    optimization_id: str
    assignments: List[ScheduleAssignment]
    score: float
    detailed_metrics: Dict[str, float]
    iteration_count: int
    execution_time_seconds: float
    algorithm_used: OptimizationAlgorithm
    parameters_used: AdvancedOptimizationParameters
    convergence_data: List[Dict[str, Any]] = Field(default_factory=list, description="Score progression data")
    solution_quality_analysis: Dict[str, Any] = Field(default_factory=dict, description="Quality analysis")
    cached: bool = Field(default=False, description="Whether result was retrieved from cache")


class OptimizationComparison(BaseModel):
    """Model for comparing optimization results."""
    baseline_result: OptimizationResult
    comparison_results: List[OptimizationResult]
    performance_comparison: Dict[str, Dict[str, float]]
    recommendation: str
    best_algorithm: OptimizationAlgorithm
    improvement_summary: str


class OptimizationResultEnriched(BaseModel):
    """Enhanced optimization result with additional analysis."""
    optimization_id: str
    assignments: List[ScheduleAssignment]
    score: float
    detailed_metrics: Dict[str, float]
    iteration_count: int
    execution_time_seconds: float
    algorithm_used: OptimizationAlgorithm
    parameters_used: AdvancedOptimizationParameters
    convergence_data: List[Dict[str, Any]] = Field(default_factory=list)
    solution_quality_analysis: Dict[str, Any] = Field(default_factory=dict)
    cached: bool = Field(default=False)
    resource_utilization: Dict[str, float] = Field(default_factory=dict)
    constraint_violations: List[str] = Field(default_factory=list)


class OptimizationAnalysis(BaseModel):
    """Model for detailed optimization analysis."""
    optimization_id: str
    solution_quality_score: float
    constraint_violations: List[str]
    resource_utilization: Dict[str, float]
    bottleneck_analysis: Dict[str, Any]
    improvement_suggestions: List[str]
    sensitivity_analysis: Dict[str, float]


# Emergency Surgery Models for Task 2.2
class EmergencyType(str, Enum):
    """Enum for emergency types."""
    TRAUMA = "trauma"
    CARDIAC = "cardiac"
    NEUROLOGICAL = "neurological"
    OBSTETRIC = "obstetric"
    GENERAL = "general"
    PEDIATRIC = "pediatric"


class EmergencyPriority(str, Enum):
    """Enum for emergency priority levels."""
    IMMEDIATE = "immediate"  # Life-threatening, requires immediate attention
    URGENT = "urgent"        # Serious condition, requires prompt attention
    SEMI_URGENT = "semi_urgent"  # Stable but needs timely intervention
    NON_URGENT = "non_urgent"    # Can wait for scheduled time


class ConflictResolutionStrategy(str, Enum):
    """Enum for conflict resolution strategies."""
    BUMP_LOWER_PRIORITY = "bump_lower_priority"
    USE_BACKUP_ROOM = "use_backup_room"
    EXTEND_HOURS = "extend_hours"
    RESCHEDULE_ELECTIVE = "reschedule_elective"
    MANUAL_REVIEW = "manual_review"


class EmergencySurgeryRequest(BaseModel):
    """Model for emergency surgery insertion request."""
    patient_id: int = Field(..., description="Patient requiring emergency surgery")
    surgery_type_id: int = Field(..., description="Type of emergency surgery")
    emergency_type: EmergencyType = Field(..., description="Category of emergency")
    emergency_priority: EmergencyPriority = Field(..., description="Emergency priority level")
    urgency_level: UrgencyLevel = Field(default=UrgencyLevel.EMERGENCY, description="Surgery urgency")
    duration_minutes: int = Field(..., gt=0, le=1440, description="Estimated duration in minutes")

    # Timing constraints
    arrival_time: datetime = Field(..., description="Patient arrival time")
    max_wait_time_minutes: Optional[int] = Field(None, gt=0, description="Maximum acceptable wait time")
    preferred_start_time: Optional[datetime] = Field(None, description="Preferred start time if any")

    # Resource requirements
    required_surgeon_id: Optional[int] = Field(None, description="Specific surgeon required")
    required_room_type: Optional[str] = Field(None, description="Specific room type required")
    required_equipment: Optional[List[str]] = Field(default_factory=list, description="Required equipment")

    # Clinical information
    clinical_notes: Optional[str] = Field(None, description="Clinical notes and requirements")
    contraindications: Optional[List[str]] = Field(default_factory=list, description="Medical contraindications")

    # Conflict resolution preferences
    allow_bumping: bool = Field(default=True, description="Allow bumping lower priority surgeries")
    allow_overtime: bool = Field(default=True, description="Allow scheduling in overtime hours")
    allow_backup_rooms: bool = Field(default=True, description="Allow using backup operating rooms")


class EmergencyInsertionResult(BaseModel):
    """Model for emergency surgery insertion result."""
    success: bool = Field(..., description="Whether insertion was successful")
    emergency_surgery_id: int = Field(..., description="ID of the created emergency surgery")
    assigned_room_id: Optional[int] = Field(None, description="Assigned operating room")
    assigned_surgeon_id: Optional[int] = Field(None, description="Assigned surgeon")
    scheduled_start_time: Optional[datetime] = Field(None, description="Scheduled start time")
    scheduled_end_time: Optional[datetime] = Field(None, description="Scheduled end time")

    # Impact analysis
    bumped_surgeries: List[int] = Field(default_factory=list, description="Surgeries that were rescheduled")
    conflicts_resolved: List[Dict[str, Any]] = Field(default_factory=list, description="Conflicts that were resolved")
    resolution_strategy: Optional[ConflictResolutionStrategy] = Field(None, description="Strategy used for resolution")

    # Notifications
    notifications_sent: List[str] = Field(default_factory=list, description="Notifications sent")
    affected_staff: List[int] = Field(default_factory=list, description="Staff members affected")

    # Metrics
    insertion_time_seconds: float = Field(..., description="Time taken to insert emergency surgery")
    wait_time_minutes: Optional[float] = Field(None, description="Patient wait time")
    schedule_disruption_score: float = Field(..., description="Score indicating schedule disruption (0-1)")


class EmergencyConflictResolution(BaseModel):
    """Model for emergency conflict resolution options."""
    conflict_id: str = Field(..., description="Unique conflict identifier")
    conflict_type: str = Field(..., description="Type of conflict")
    affected_surgery_id: int = Field(..., description="Surgery affected by emergency insertion")
    emergency_surgery_id: int = Field(..., description="Emergency surgery causing conflict")

    # Resolution options
    available_strategies: List[ConflictResolutionStrategy] = Field(..., description="Available resolution strategies")
    recommended_strategy: ConflictResolutionStrategy = Field(..., description="Recommended strategy")

    # Strategy details
    bump_options: Optional[List[Dict[str, Any]]] = Field(None, description="Options for bumping surgeries")
    room_alternatives: Optional[List[Dict[str, Any]]] = Field(None, description="Alternative room options")
    time_alternatives: Optional[List[Dict[str, Any]]] = Field(None, description="Alternative time slots")

    # Impact assessment
    impact_score: float = Field(..., ge=0, le=1, description="Impact score of resolution (0-1)")
    affected_patients: List[int] = Field(default_factory=list, description="Patients affected by resolution")
    cost_implications: Optional[Dict[str, float]] = Field(None, description="Cost implications")


class EmergencyScheduleUpdate(BaseModel):
    """Model for emergency schedule update notification."""
    update_id: str = Field(..., description="Unique update identifier")
    emergency_surgery_id: int = Field(..., description="Emergency surgery ID")
    update_type: str = Field(..., description="Type of update (insertion, modification, cancellation)")
    timestamp: datetime = Field(..., description="Update timestamp")

    # Schedule changes
    schedule_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed schedule changes")
    affected_surgeries: List[int] = Field(default_factory=list, description="Affected surgery IDs")

    # Notifications
    notification_recipients: List[str] = Field(default_factory=list, description="Recipients to notify")
    notification_priority: str = Field(..., description="Notification priority level")
    message: str = Field(..., description="Update message")


class EmergencyMetrics(BaseModel):
    """Model for emergency surgery metrics and analytics."""
    date_range_start: date = Field(..., description="Start date for metrics")
    date_range_end: date = Field(..., description="End date for metrics")

    # Volume metrics
    total_emergencies: int = Field(..., description="Total emergency surgeries")
    emergencies_by_type: Dict[str, int] = Field(default_factory=dict, description="Emergencies by type")
    emergencies_by_priority: Dict[str, int] = Field(default_factory=dict, description="Emergencies by priority")

    # Performance metrics
    average_wait_time_minutes: float = Field(..., description="Average patient wait time")
    average_insertion_time_seconds: float = Field(..., description="Average insertion processing time")
    successful_insertions_rate: float = Field(..., ge=0, le=1, description="Success rate for insertions")

    # Impact metrics
    surgeries_bumped: int = Field(..., description="Total surgeries rescheduled due to emergencies")
    overtime_hours_generated: float = Field(..., description="Overtime hours generated")
    average_disruption_score: float = Field(..., ge=0, le=1, description="Average schedule disruption")

    # Resource utilization
    rooms_used_for_emergencies: Dict[str, int] = Field(default_factory=dict, description="Room usage for emergencies")
    surgeons_involved: Dict[str, int] = Field(default_factory=dict, description="Surgeon involvement in emergencies")


# Advanced Feasibility Checking Models for Task 2.3
class ConstraintType(str, Enum):
    """Enum for constraint types."""
    EQUIPMENT_AVAILABILITY = "equipment_availability"
    STAFF_AVAILABILITY = "staff_availability"
    SURGEON_SPECIALIZATION = "surgeon_specialization"
    ROOM_CAPACITY = "room_capacity"
    TIME_WINDOW = "time_window"
    RESOURCE_CONFLICT = "resource_conflict"
    CUSTOM = "custom"


class ConstraintSeverity(str, Enum):
    """Enum for constraint violation severity."""
    CRITICAL = "critical"  # Must be satisfied
    HIGH = "high"         # Should be satisfied
    MEDIUM = "medium"     # Preferred to be satisfied
    LOW = "low"          # Nice to have


class ConstraintViolation(BaseModel):
    """Model for constraint violation details."""
    constraint_id: str = Field(..., description="Unique constraint identifier")
    constraint_type: ConstraintType = Field(..., description="Type of constraint")
    severity: ConstraintSeverity = Field(..., description="Severity of violation")
    description: str = Field(..., description="Human-readable description")

    # Violation details
    surgery_id: Optional[int] = Field(None, description="Surgery involved in violation")
    room_id: Optional[int] = Field(None, description="Room involved in violation")
    surgeon_id: Optional[int] = Field(None, description="Surgeon involved in violation")
    equipment_id: Optional[int] = Field(None, description="Equipment involved in violation")
    staff_id: Optional[int] = Field(None, description="Staff member involved in violation")

    # Time-related details
    start_time: Optional[datetime] = Field(None, description="Start time of violation")
    end_time: Optional[datetime] = Field(None, description="End time of violation")

    # Resolution suggestions
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested resolution actions")
    alternative_options: Optional[Dict[str, Any]] = Field(None, description="Alternative options")


class ConstraintConfiguration(BaseModel):
    """Model for constraint configuration."""
    constraint_id: str = Field(..., description="Unique constraint identifier")
    constraint_type: ConstraintType = Field(..., description="Type of constraint")
    name: str = Field(..., description="Human-readable constraint name")
    description: str = Field(..., description="Detailed constraint description")
    severity: ConstraintSeverity = Field(..., description="Default severity level")

    # Configuration parameters
    enabled: bool = Field(default=True, description="Whether constraint is enabled")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Constraint-specific parameters")

    # Scope and applicability
    applies_to_surgery_types: Optional[List[int]] = Field(None, description="Surgery types this constraint applies to")
    applies_to_rooms: Optional[List[int]] = Field(None, description="Rooms this constraint applies to")
    applies_to_surgeons: Optional[List[int]] = Field(None, description="Surgeons this constraint applies to")

    # Timing
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class FeasibilityCheckRequest(BaseModel):
    """Model for feasibility check request."""
    surgery_id: int = Field(..., description="Surgery to check")
    room_id: int = Field(..., description="Proposed room")
    start_time: datetime = Field(..., description="Proposed start time")
    end_time: datetime = Field(..., description="Proposed end time")

    # Optional context
    current_assignments: Optional[List[Dict[str, Any]]] = Field(None, description="Current schedule assignments")
    ignore_surgery_id: Optional[int] = Field(None, description="Surgery ID to ignore in checks")

    # Check options
    check_equipment: bool = Field(default=True, description="Check equipment availability")
    check_staff: bool = Field(default=True, description="Check staff availability")
    check_specialization: bool = Field(default=True, description="Check surgeon specialization")
    check_custom_constraints: bool = Field(default=True, description="Check custom constraints")


class FeasibilityCheckResult(BaseModel):
    """Model for feasibility check result."""
    is_feasible: bool = Field(..., description="Overall feasibility result")
    surgery_id: int = Field(..., description="Surgery that was checked")
    room_id: int = Field(..., description="Room that was checked")
    start_time: datetime = Field(..., description="Start time that was checked")
    end_time: datetime = Field(..., description="End time that was checked")

    # Detailed results
    violations: List[ConstraintViolation] = Field(default_factory=list, description="Constraint violations found")
    warnings: List[ConstraintViolation] = Field(default_factory=list, description="Non-critical warnings")

    # Performance metrics
    check_duration_ms: float = Field(..., description="Time taken for feasibility check")
    constraints_checked: int = Field(..., description="Number of constraints evaluated")

    # Summary by constraint type
    equipment_feasible: bool = Field(..., description="Equipment availability result")
    staff_feasible: bool = Field(..., description="Staff availability result")
    specialization_feasible: bool = Field(..., description="Surgeon specialization result")
    room_feasible: bool = Field(..., description="Room availability result")

    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")


class StaffAvailabilityConstraint(BaseModel):
    """Model for staff availability constraint."""
    staff_id: int = Field(..., description="Staff member ID")
    role: str = Field(..., description="Staff role (nurse, anesthesiologist, etc.)")

    # Availability windows
    available_days: List[str] = Field(..., description="Days of week available")
    available_start_time: str = Field(..., description="Daily start time (HH:MM)")
    available_end_time: str = Field(..., description="Daily end time (HH:MM)")

    # Capacity constraints
    max_concurrent_surgeries: int = Field(default=1, description="Maximum concurrent surgeries")
    max_daily_hours: float = Field(default=8.0, description="Maximum daily working hours")

    # Specialization
    qualified_surgery_types: Optional[List[int]] = Field(None, description="Surgery types staff is qualified for")
    required_certifications: Optional[List[str]] = Field(None, description="Required certifications")


class SurgeonSpecializationConstraint(BaseModel):
    """Model for surgeon specialization constraint."""
    surgeon_id: int = Field(..., description="Surgeon ID")
    specializations: List[str] = Field(..., description="Surgeon specializations")

    # Qualification mapping
    qualified_surgery_types: List[int] = Field(..., description="Surgery types surgeon is qualified for")
    preferred_surgery_types: Optional[List[int]] = Field(None, description="Preferred surgery types")

    # Experience levels
    experience_level: str = Field(default="experienced", description="Experience level")
    years_experience: Optional[int] = Field(None, description="Years of experience")

    # Restrictions
    restricted_surgery_types: Optional[List[int]] = Field(None, description="Surgery types surgeon cannot perform")
    requires_supervision: bool = Field(default=False, description="Whether surgeon requires supervision")


class EquipmentAvailabilityConstraint(BaseModel):
    """Model for equipment availability constraint."""
    equipment_id: int = Field(..., description="Equipment ID")
    equipment_name: str = Field(..., description="Equipment name")
    equipment_type: str = Field(..., description="Equipment type")

    # Availability
    is_available: bool = Field(default=True, description="General availability status")
    maintenance_windows: Optional[List[Dict[str, datetime]]] = Field(None, description="Maintenance time windows")

    # Capacity and usage
    max_concurrent_usage: int = Field(default=1, description="Maximum concurrent usage")
    setup_time_minutes: int = Field(default=0, description="Setup time required")
    cleanup_time_minutes: int = Field(default=0, description="Cleanup time required")

    # Location and mobility
    is_mobile: bool = Field(default=False, description="Whether equipment is mobile")
    current_location: Optional[str] = Field(None, description="Current equipment location")
    available_rooms: Optional[List[int]] = Field(None, description="Rooms where equipment is available")


class CustomConstraintRule(BaseModel):
    """Model for custom constraint rule."""
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")

    # Rule definition
    rule_type: str = Field(..., description="Type of rule (time_based, resource_based, etc.)")
    conditions: Dict[str, Any] = Field(..., description="Rule conditions")
    actions: Dict[str, Any] = Field(..., description="Actions when rule is violated")

    # Applicability
    applies_to: Dict[str, List[int]] = Field(default_factory=dict, description="What this rule applies to")
    priority: int = Field(default=100, description="Rule priority (lower = higher priority)")

    # Status
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    created_by: Optional[str] = Field(None, description="User who created the rule")


# WebSocket Models for Task 3.1
class WebSocketMessageType(str, Enum):
    """Enum for WebSocket message types."""
    SCHEDULE_UPDATE = "schedule_update"
    OPTIMIZATION_PROGRESS = "optimization_progress"
    CONFLICT_NOTIFICATION = "conflict_notification"
    USER_PRESENCE = "user_presence"
    EMERGENCY_ALERT = "emergency_alert"
    SYSTEM_NOTIFICATION = "system_notification"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    """Base model for WebSocket messages."""
    type: WebSocketMessageType = Field(..., description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    user_id: Optional[int] = Field(None, description="User ID who triggered the message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")


class ScheduleUpdateMessage(BaseModel):
    """Model for schedule update WebSocket messages."""
    type: WebSocketMessageType = Field(default=WebSocketMessageType.SCHEDULE_UPDATE, description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    user_id: int = Field(..., description="User who made the update")

    # Update details
    action: str = Field(..., description="Action performed (create, update, delete)")
    surgery_id: Optional[int] = Field(None, description="Surgery ID affected")
    room_id: Optional[int] = Field(None, description="Room ID affected")
    schedule_date: Optional[date] = Field(None, description="Schedule date affected")

    # Change details
    changes: Dict[str, Any] = Field(default_factory=dict, description="Details of changes made")
    affected_surgeries: List[int] = Field(default_factory=list, description="Other surgeries affected")

    # Metadata
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")


class OptimizationProgressMessage(BaseModel):
    """Model for optimization progress WebSocket messages."""
    type: WebSocketMessageType = Field(default=WebSocketMessageType.OPTIMIZATION_PROGRESS, description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Progress timestamp")
    user_id: int = Field(..., description="User who started optimization")

    # Progress details
    optimization_id: str = Field(..., description="Unique optimization session ID")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    current_iteration: int = Field(..., description="Current iteration number")
    total_iterations: int = Field(..., description="Total planned iterations")

    # Performance metrics
    current_score: Optional[float] = Field(None, description="Current solution score")
    best_score: Optional[float] = Field(None, description="Best solution score so far")
    time_elapsed: float = Field(..., description="Time elapsed in seconds")
    estimated_time_remaining: Optional[float] = Field(None, description="Estimated time remaining in seconds")

    # Status
    status: str = Field(..., description="Current optimization status")
    phase: Optional[str] = Field(None, description="Current optimization phase")

    # Metadata
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")


class ConflictNotificationMessage(BaseModel):
    """Model for conflict notification WebSocket messages."""
    type: WebSocketMessageType = Field(default=WebSocketMessageType.CONFLICT_NOTIFICATION, description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Conflict timestamp")
    user_id: Optional[int] = Field(None, description="User who triggered the conflict")

    # Conflict details
    conflict_id: str = Field(..., description="Unique conflict identifier")
    conflict_type: str = Field(..., description="Type of conflict")
    severity: str = Field(..., description="Conflict severity level")
    description: str = Field(..., description="Human-readable conflict description")

    # Affected resources
    affected_surgeries: List[int] = Field(default_factory=list, description="Surgeries involved in conflict")
    affected_rooms: List[int] = Field(default_factory=list, description="Rooms involved in conflict")
    affected_surgeons: List[int] = Field(default_factory=list, description="Surgeons involved in conflict")
    affected_equipment: List[int] = Field(default_factory=list, description="Equipment involved in conflict")

    # Resolution suggestions
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested resolution actions")
    auto_resolution_available: bool = Field(default=False, description="Whether auto-resolution is available")

    # Metadata
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")


class UserPresenceMessage(BaseModel):
    """Model for user presence WebSocket messages."""
    type: WebSocketMessageType = Field(default=WebSocketMessageType.USER_PRESENCE, description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Presence timestamp")
    user_id: int = Field(..., description="User ID")

    # Presence details
    action: str = Field(..., description="Presence action (join, leave, active, idle)")
    username: str = Field(..., description="Username")
    role: Optional[str] = Field(None, description="User role")

    # Activity details
    current_page: Optional[str] = Field(None, description="Current page/view")
    active_schedule_date: Optional[date] = Field(None, description="Currently viewing schedule date")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")

    # Connection info
    connection_id: str = Field(..., description="WebSocket connection ID")

    # Metadata
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")


class EmergencyAlertMessage(BaseModel):
    """Model for emergency alert WebSocket messages."""
    type: WebSocketMessageType = Field(default=WebSocketMessageType.EMERGENCY_ALERT, description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Alert timestamp")
    user_id: int = Field(..., description="User who triggered the alert")

    # Emergency details
    emergency_id: str = Field(..., description="Unique emergency identifier")
    emergency_type: str = Field(..., description="Type of emergency")
    priority: str = Field(..., description="Emergency priority level")
    description: str = Field(..., description="Emergency description")

    # Surgery details
    surgery_id: int = Field(..., description="Emergency surgery ID")
    patient_name: str = Field(..., description="Patient name")
    surgery_type: str = Field(..., description="Surgery type")
    estimated_duration: int = Field(..., description="Estimated duration in minutes")

    # Scheduling details
    requested_time: Optional[datetime] = Field(None, description="Requested surgery time")
    assigned_room: Optional[int] = Field(None, description="Assigned room ID")
    assigned_surgeon: Optional[int] = Field(None, description="Assigned surgeon ID")

    # Impact assessment
    conflicts_detected: bool = Field(default=False, description="Whether conflicts were detected")
    affected_surgeries: List[int] = Field(default_factory=list, description="Surgeries affected by emergency")

    # Metadata
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")


class SystemNotificationMessage(BaseModel):
    """Model for system notification WebSocket messages."""
    type: WebSocketMessageType = Field(default=WebSocketMessageType.SYSTEM_NOTIFICATION, description="Message type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Notification timestamp")

    # Notification details
    notification_type: str = Field(..., description="Type of notification")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    severity: str = Field(default="info", description="Notification severity")

    # Targeting
    target_users: Optional[List[int]] = Field(None, description="Specific users to notify (None = all)")
    target_roles: Optional[List[str]] = Field(None, description="Specific roles to notify")

    # Action details
    action_required: bool = Field(default=False, description="Whether action is required")
    action_url: Optional[str] = Field(None, description="URL for action")
    action_label: Optional[str] = Field(None, description="Label for action button")

    # Expiration
    expires_at: Optional[datetime] = Field(None, description="Notification expiration time")

    # Metadata
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")


class WebSocketConnectionInfo(BaseModel):
    """Model for WebSocket connection information."""
    connection_id: str = Field(..., description="Unique connection identifier")
    user_id: int = Field(..., description="Connected user ID")
    username: str = Field(..., description="Connected username")
    role: Optional[str] = Field(None, description="User role")

    # Connection details
    connected_at: datetime = Field(default_factory=datetime.now, description="Connection timestamp")
    last_heartbeat: datetime = Field(default_factory=datetime.now, description="Last heartbeat timestamp")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")

    # Activity tracking
    current_page: Optional[str] = Field(None, description="Current page/view")
    active_schedule_date: Optional[date] = Field(None, description="Currently viewing schedule date")
    is_active: bool = Field(default=True, description="Whether connection is active")


class WebSocketBroadcastRequest(BaseModel):
    """Model for WebSocket broadcast requests."""
    message_type: WebSocketMessageType = Field(..., description="Type of message to broadcast")
    message_data: Dict[str, Any] = Field(..., description="Message payload")

    # Targeting options
    target_users: Optional[List[int]] = Field(None, description="Specific users to target (None = all)")
    target_roles: Optional[List[str]] = Field(None, description="Specific roles to target")
    exclude_users: Optional[List[int]] = Field(None, description="Users to exclude from broadcast")

    # Delivery options
    require_acknowledgment: bool = Field(default=False, description="Whether to require acknowledgment")
    priority: str = Field(default="normal", description="Message priority")

    # Metadata
    sender_user_id: Optional[int] = Field(None, description="User ID of sender")


# Additional Enhanced Optimization Models
class OptimizationCache(BaseModel):
    """Model for optimization result caching."""
    cache_key: str
    parameters_hash: str
    result: OptimizationResult
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0


class AlgorithmPerformanceMetrics(BaseModel):
    """Model for algorithm performance tracking."""
    algorithm: OptimizationAlgorithm
    average_score: float
    average_execution_time: float
    success_rate: float
    total_runs: int
    best_score_achieved: float
    convergence_rate: float


class OptimizationSession(BaseModel):
    """Model for optimization session tracking."""
    session_id: str
    user_id: int
    created_at: datetime
    parameters: AdvancedOptimizationParameters
    status: OptimizationStatus
    progress: Optional[OptimizationProgress] = None
    result: Optional[OptimizationResult] = None
    error_message: Optional[str] = None


class OptimizationBenchmark(BaseModel):
    """Model for optimization benchmarking."""
    benchmark_id: str
    test_case_name: str
    algorithms_tested: List[OptimizationAlgorithm]
    results: List[OptimizationResult]
    performance_metrics: Dict[str, AlgorithmPerformanceMetrics]
    winner: OptimizationAlgorithm
    execution_summary: str
