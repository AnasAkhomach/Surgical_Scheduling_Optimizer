"""
Tests for Emergency Surgery Handler (Task 2.2).

This module tests the emergency surgery handling functionality including:
- Emergency surgery insertion
- Real-time schedule re-optimization
- Priority-based conflict resolution
- Notification integration
- Impact analysis and metrics
"""

import pytest
import logging
from datetime import datetime, timedelta, date
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from emergency_surgery_handler import EmergencySurgeryHandler
from api.models import (
    EmergencySurgeryRequest,
    EmergencyInsertionResult,
    EmergencyMetrics,
    EmergencyType,
    EmergencyPriority,
    UrgencyLevel,
    ConflictResolutionStrategy
)
from models import Surgery, OperatingRoom, Surgeon, Patient, SurgeryType, SurgeryRoomAssignment

logger = logging.getLogger(__name__)


class TestEmergencySurgeryHandler:
    """Test cases for EmergencySurgeryHandler."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = Mock(spec=Session)
        session.query.return_value.filter.return_value.first.return_value = None
        session.query.return_value.filter.return_value.all.return_value = []
        session.query.return_value.all.return_value = []
        session.add = Mock()
        session.commit = Mock()
        session.refresh = Mock()
        return session
    
    @pytest.fixture
    def sample_patient(self):
        """Create a sample patient."""
        patient = Patient()
        patient.patient_id = 1
        patient.name = "John Doe"
        patient.date_of_birth = date(1980, 1, 1)
        patient.contact_info = "555-0123"
        return patient
    
    @pytest.fixture
    def sample_surgeon(self):
        """Create a sample surgeon."""
        surgeon = Surgeon()
        surgeon.surgeon_id = 1
        surgeon.name = "Dr. Smith"
        surgeon.specialization = "General Surgery"
        surgeon.contact_info = "dr.smith@hospital.com"
        return surgeon
    
    @pytest.fixture
    def sample_surgery_type(self):
        """Create a sample surgery type."""
        surgery_type = SurgeryType()
        surgery_type.type_id = 1
        surgery_type.name = "Emergency Appendectomy"
        surgery_type.description = "Emergency appendix removal"
        surgery_type.average_duration = 90
        return surgery_type
    
    @pytest.fixture
    def sample_operating_room(self):
        """Create a sample operating room."""
        room = OperatingRoom()
        room.room_id = 1
        room.location = "OR-1"
        room.capacity = 10
        room.equipment = "Standard surgical equipment"
        return room
    
    @pytest.fixture
    def emergency_request(self):
        """Create a sample emergency surgery request."""
        return EmergencySurgeryRequest(
            patient_id=1,
            surgery_type_id=1,
            emergency_type=EmergencyType.TRAUMA,
            emergency_priority=EmergencyPriority.URGENT,
            urgency_level=UrgencyLevel.EMERGENCY,
            duration_minutes=90,
            arrival_time=datetime.now(),
            max_wait_time_minutes=60,
            required_surgeon_id=1,
            clinical_notes="Emergency appendectomy required",
            allow_bumping=True,
            allow_overtime=True,
            allow_backup_rooms=True
        )
    
    @pytest.fixture
    def handler(self, mock_db_session):
        """Create an emergency surgery handler with mocked dependencies."""
        return EmergencySurgeryHandler(mock_db_session)
    
    def test_handler_initialization(self, mock_db_session):
        """Test emergency surgery handler initialization."""
        handler = EmergencySurgeryHandler(mock_db_session)
        
        assert handler.db_session == mock_db_session
        assert handler.feasibility_checker is not None
        assert handler.solution_evaluator is not None
        assert len(handler.priority_weights) == 4
        assert len(handler.max_wait_times) == 4
        
        # Test priority weights
        assert handler.priority_weights[EmergencyPriority.IMMEDIATE] == 1.0
        assert handler.priority_weights[EmergencyPriority.URGENT] == 0.8
        assert handler.priority_weights[EmergencyPriority.SEMI_URGENT] == 0.6
        assert handler.priority_weights[EmergencyPriority.SCHEDULED] == 0.4
        
        # Test max wait times
        assert handler.max_wait_times[EmergencyPriority.IMMEDIATE] == 15
        assert handler.max_wait_times[EmergencyPriority.URGENT] == 60
        assert handler.max_wait_times[EmergencyPriority.SEMI_URGENT] == 240
        assert handler.max_wait_times[EmergencyPriority.SCHEDULED] == 1440
    
    def test_validate_emergency_request_valid(
        self, 
        handler, 
        emergency_request, 
        sample_patient, 
        sample_surgery_type, 
        sample_surgeon
    ):
        """Test validation of a valid emergency request."""
        # Mock database queries
        handler.db_session.query.return_value.filter.return_value.first.side_effect = [
            sample_patient,  # Patient query
            sample_surgery_type,  # Surgery type query
            sample_surgeon  # Surgeon query
        ]
        
        # Should not raise any exception
        handler._validate_emergency_request(emergency_request)
    
    def test_validate_emergency_request_invalid_patient(self, handler, emergency_request):
        """Test validation with invalid patient."""
        # Mock patient not found
        handler.db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Patient 1 not found"):
            handler._validate_emergency_request(emergency_request)
    
    def test_validate_emergency_request_invalid_surgery_type(
        self, 
        handler, 
        emergency_request, 
        sample_patient
    ):
        """Test validation with invalid surgery type."""
        # Mock patient found, surgery type not found
        handler.db_session.query.return_value.filter.return_value.first.side_effect = [
            sample_patient,  # Patient query
            None  # Surgery type query
        ]
        
        with pytest.raises(ValueError, match="Surgery type 1 not found"):
            handler._validate_emergency_request(emergency_request)
    
    def test_validate_emergency_request_invalid_surgeon(
        self, 
        handler, 
        emergency_request, 
        sample_patient, 
        sample_surgery_type
    ):
        """Test validation with invalid required surgeon."""
        # Mock patient and surgery type found, surgeon not found
        handler.db_session.query.return_value.filter.return_value.first.side_effect = [
            sample_patient,  # Patient query
            sample_surgery_type,  # Surgery type query
            None  # Surgeon query
        ]
        
        with pytest.raises(ValueError, match="Required surgeon 1 not found"):
            handler._validate_emergency_request(emergency_request)
    
    def test_create_emergency_surgery(
        self, 
        handler, 
        emergency_request, 
        sample_patient, 
        sample_surgery_type, 
        sample_surgeon
    ):
        """Test creation of emergency surgery record."""
        # Mock database operations
        created_surgery = Surgery()
        created_surgery.surgery_id = 123
        created_surgery.scheduled_date = emergency_request.arrival_time.date()
        created_surgery.surgery_type_id = emergency_request.surgery_type_id
        created_surgery.urgency_level = emergency_request.urgency_level.value
        created_surgery.duration_minutes = emergency_request.duration_minutes
        created_surgery.patient_id = emergency_request.patient_id
        created_surgery.surgeon_id = emergency_request.required_surgeon_id
        
        handler.db_session.refresh.side_effect = lambda obj: setattr(obj, 'surgery_id', 123)
        
        result = handler._create_emergency_surgery(emergency_request)
        
        # Verify surgery creation
        handler.db_session.add.assert_called_once()
        handler.db_session.commit.assert_called_once()
        handler.db_session.refresh.assert_called_once()
        
        # Verify surgery properties
        added_surgery = handler.db_session.add.call_args[0][0]
        assert added_surgery.scheduled_date == emergency_request.arrival_time.date()
        assert added_surgery.surgery_type_id == emergency_request.surgery_type_id
        assert added_surgery.urgency_level == emergency_request.urgency_level.value
        assert added_surgery.duration_minutes == emergency_request.duration_minutes
        assert added_surgery.patient_id == emergency_request.patient_id
        assert added_surgery.surgeon_id == emergency_request.required_surgeon_id
    
    def test_get_insertion_strategies_immediate(self, handler):
        """Test insertion strategies for immediate priority."""
        strategies = handler._get_insertion_strategies(EmergencyPriority.IMMEDIATE)
        
        expected = [
            ConflictResolutionStrategy.BUMP_LOWER_PRIORITY,
            ConflictResolutionStrategy.USE_BACKUP_ROOM,
            ConflictResolutionStrategy.EXTEND_HOURS
        ]
        
        assert strategies == expected
    
    def test_get_insertion_strategies_urgent(self, handler):
        """Test insertion strategies for urgent priority."""
        strategies = handler._get_insertion_strategies(EmergencyPriority.URGENT)
        
        expected = [
            ConflictResolutionStrategy.USE_BACKUP_ROOM,
            ConflictResolutionStrategy.BUMP_LOWER_PRIORITY,
            ConflictResolutionStrategy.EXTEND_HOURS
        ]
        
        assert strategies == expected
    
    def test_get_insertion_strategies_semi_urgent(self, handler):
        """Test insertion strategies for semi-urgent priority."""
        strategies = handler._get_insertion_strategies(EmergencyPriority.SEMI_URGENT)
        
        expected = [
            ConflictResolutionStrategy.USE_BACKUP_ROOM,
            ConflictResolutionStrategy.EXTEND_HOURS,
            ConflictResolutionStrategy.BUMP_LOWER_PRIORITY
        ]
        
        assert strategies == expected
    
    def test_get_insertion_strategies_scheduled(self, handler):
        """Test insertion strategies for scheduled priority."""
        strategies = handler._get_insertion_strategies(EmergencyPriority.SCHEDULED)
        
        expected = [
            ConflictResolutionStrategy.USE_BACKUP_ROOM,
            ConflictResolutionStrategy.EXTEND_HOURS,
            ConflictResolutionStrategy.MANUAL_REVIEW
        ]
        
        assert strategies == expected
    
    def test_calculate_wait_time(self, handler, emergency_request):
        """Test wait time calculation."""
        # Test with successful insertion
        start_time = emergency_request.arrival_time + timedelta(minutes=30)
        insertion_result = {'start_time': start_time}
        
        wait_time = handler._calculate_wait_time(emergency_request, insertion_result)
        assert wait_time == 30.0
        
        # Test with no start time
        insertion_result = {}
        wait_time = handler._calculate_wait_time(emergency_request, insertion_result)
        assert wait_time is None
        
        # Test with negative wait time (should be clamped to 0)
        start_time = emergency_request.arrival_time - timedelta(minutes=10)
        insertion_result = {'start_time': start_time}
        
        wait_time = handler._calculate_wait_time(emergency_request, insertion_result)
        assert wait_time == 0.0
    
    def test_calculate_disruption_score(self, handler):
        """Test disruption score calculation."""
        # Test minimal disruption
        insertion_result = {
            'bumped_surgeries': [],
            'conflicts_resolved': [],
            'overtime_required': False
        }
        score = handler._calculate_disruption_score(insertion_result)
        assert score == 0.0
        
        # Test moderate disruption
        insertion_result = {
            'bumped_surgeries': [1, 2],
            'conflicts_resolved': [{'type': 'room_conflict'}],
            'overtime_required': False
        }
        score = handler._calculate_disruption_score(insertion_result)
        assert 0.0 < score < 1.0
        
        # Test high disruption
        insertion_result = {
            'bumped_surgeries': [1, 2, 3, 4],
            'conflicts_resolved': [{'type': 'room_conflict'}, {'type': 'surgeon_conflict'}],
            'overtime_required': True
        }
        score = handler._calculate_disruption_score(insertion_result)
        assert score > 0.5
    
    def test_get_emergency_metrics(self, handler):
        """Test emergency metrics calculation."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        # Mock emergency surgeries
        emergency_surgeries = [
            Mock(surgery_id=1, urgency_level="Emergency"),
            Mock(surgery_id=2, urgency_level="Emergency"),
            Mock(surgery_id=3, urgency_level="Emergency")
        ]
        
        handler.db_session.query.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = emergency_surgeries
        
        metrics = handler.get_emergency_metrics(start_date, end_date)
        
        assert isinstance(metrics, EmergencyMetrics)
        assert metrics.date_range_start == start_date.date()
        assert metrics.date_range_end == end_date.date()
        assert metrics.total_emergencies == 3
        assert metrics.average_wait_time_minutes > 0
        assert metrics.successful_insertions_rate > 0
        assert 0 <= metrics.average_disruption_score <= 1
    
    @patch('emergency_surgery_handler.notification_service')
    def test_send_emergency_notifications(self, mock_notification_service, handler, emergency_request):
        """Test emergency notification sending."""
        # Mock database objects
        surgeon = Mock()
        surgeon.surgeon_id = 1
        room = Mock()
        room.room_id = 1
        room.location = "OR-1"
        
        handler.db_session.query.return_value.filter.return_value.first.side_effect = [
            surgeon,  # Surgeon query
            None,     # Bumped surgery query (no bumped surgeries)
            room      # Room query
        ]
        
        emergency_surgery = Mock()
        emergency_surgery.surgery_id = 123
        
        insertion_result = {
            'surgeon_id': 1,
            'room_id': 1,
            'start_time': datetime.now(),
            'bumped_surgeries': [],
            'conflicts_resolved': []
        }
        
        notifications = handler._send_emergency_notifications(
            emergency_surgery, insertion_result, emergency_request
        )
        
        # Verify notifications were sent
        assert len(notifications) >= 2  # At least surgeon and room notifications
        assert any('surgeon_1' in notif for notif in notifications)
        assert any('room_1' in notif for notif in notifications)
    
    def test_is_slot_available_no_conflicts(self, handler):
        """Test slot availability with no conflicts."""
        room_id = 1
        surgeon_id = 1
        start_time = datetime(2024, 1, 1, 9, 0)
        end_time = datetime(2024, 1, 1, 10, 30)
        current_schedule = []
        
        available = handler._is_slot_available(
            room_id, surgeon_id, start_time, end_time, current_schedule
        )
        
        assert available is True
    
    def test_is_slot_available_room_conflict(self, handler):
        """Test slot availability with room conflict."""
        room_id = 1
        surgeon_id = 1
        start_time = datetime(2024, 1, 1, 9, 0)
        end_time = datetime(2024, 1, 1, 10, 30)
        
        # Create conflicting assignment
        conflicting_assignment = Mock()
        conflicting_assignment.room_id = 1
        conflicting_assignment.start_time = datetime(2024, 1, 1, 9, 30)
        conflicting_assignment.end_time = datetime(2024, 1, 1, 11, 0)
        
        current_schedule = [conflicting_assignment]
        
        available = handler._is_slot_available(
            room_id, surgeon_id, start_time, end_time, current_schedule
        )
        
        assert available is False
    
    def test_is_slot_available_surgeon_conflict(self, handler):
        """Test slot availability with surgeon conflict."""
        room_id = 1
        surgeon_id = 1
        start_time = datetime(2024, 1, 1, 9, 0)
        end_time = datetime(2024, 1, 1, 10, 30)
        
        # Create conflicting assignment with different room but same surgeon
        conflicting_assignment = Mock()
        conflicting_assignment.room_id = 2
        conflicting_assignment.surgery_id = 100
        conflicting_assignment.start_time = datetime(2024, 1, 1, 9, 30)
        conflicting_assignment.end_time = datetime(2024, 1, 1, 11, 0)
        
        # Mock surgery with same surgeon
        conflicting_surgery = Mock()
        conflicting_surgery.surgeon_id = 1
        
        handler.db_session.query.return_value.filter.return_value.first.return_value = conflicting_surgery
        
        current_schedule = [conflicting_assignment]
        
        available = handler._is_slot_available(
            room_id, surgeon_id, start_time, end_time, current_schedule
        )
        
        assert available is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
