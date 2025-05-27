"""
Tests for Advanced Feasibility Checker (Task 2.3).

This module tests the enhanced constraint validation including:
- Equipment availability checking
- Staff availability constraints
- Surgeon specialization matching
- Custom constraint configuration
- Constraint violation reporting
"""

import pytest
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from advanced_feasibility_checker import AdvancedFeasibilityChecker
from api.models import (
    ConstraintType, ConstraintSeverity, ConstraintViolation, ConstraintConfiguration,
    FeasibilityCheckRequest, FeasibilityCheckResult, CustomConstraintRule
)
from models import (
    Surgery, OperatingRoom, Surgeon, SurgeryEquipment, SurgeryRoomAssignment,
    SurgeryEquipmentUsage, SurgeryType, Staff, SurgeryStaffAssignment
)

logger = logging.getLogger(__name__)


class TestAdvancedFeasibilityChecker:
    """Test cases for AdvancedFeasibilityChecker."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_surgery(self):
        """Create a sample surgery for testing."""
        surgery = Mock(spec=Surgery)
        surgery.surgery_id = 1
        surgery.surgery_type_id = 1
        surgery.surgeon_id = 1
        surgery.patient_id = 1
        surgery.duration_minutes = 120
        return surgery

    @pytest.fixture
    def sample_surgeon(self):
        """Create a sample surgeon for testing."""
        surgeon = Mock(spec=Surgeon)
        surgeon.surgeon_id = 1
        surgeon.name = "Dr. Smith"
        surgeon.specialization = "General Surgery"
        surgeon.availability = True
        return surgeon

    @pytest.fixture
    def sample_surgery_type(self):
        """Create a sample surgery type for testing."""
        surgery_type = Mock(spec=SurgeryType)
        surgery_type.type_id = 1
        surgery_type.name = "Appendectomy"
        surgery_type.description = "Appendix removal surgery"
        return surgery_type

    @pytest.fixture
    def sample_equipment(self):
        """Create a sample equipment for testing."""
        equipment = Mock(spec=SurgeryEquipment)
        equipment.equipment_id = 1
        equipment.name = "Surgical Scalpel"
        equipment.type = "Cutting Tool"
        equipment.availability = True
        return equipment

    @pytest.fixture
    def sample_staff(self):
        """Create a sample staff member for testing."""
        staff = Mock(spec=Staff)
        staff.staff_id = 1
        staff.name = "Nurse Johnson"
        staff.role = "Surgical Nurse"
        staff.availability = True
        return staff

    @pytest.fixture
    def feasibility_checker(self, mock_db_session):
        """Create an AdvancedFeasibilityChecker instance."""
        # Mock the cache loading to avoid database calls during initialization
        with patch.object(AdvancedFeasibilityChecker, '_load_cache_data'):
            checker = AdvancedFeasibilityChecker(mock_db_session)
            return checker

    def test_initialization(self, feasibility_checker):
        """Test that the advanced feasibility checker initializes correctly."""
        assert feasibility_checker is not None
        assert len(feasibility_checker.constraint_configurations) > 0
        assert "equipment_availability" in feasibility_checker.constraint_configurations
        assert "staff_availability" in feasibility_checker.constraint_configurations
        assert "surgeon_specialization" in feasibility_checker.constraint_configurations

    def test_check_feasibility_advanced_success(
        self, feasibility_checker, mock_db_session, sample_surgery, sample_surgeon, sample_surgery_type
    ):
        """Test successful advanced feasibility check."""
        # Setup mock database queries
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            sample_surgery,  # Surgery query
            sample_surgeon,  # Surgeon query
            sample_surgery_type  # Surgery type query
        ]
        mock_db_session.query.return_value.filter_by.return_value.all.return_value = []  # No equipment usages
        mock_db_session.query.return_value.filter.return_value.all.return_value = []  # No conflicts

        # Create feasibility check request
        request = FeasibilityCheckRequest(
            surgery_id=1,
            room_id=1,
            start_time=datetime(2024, 1, 15, 9, 0),
            end_time=datetime(2024, 1, 15, 11, 0)
        )

        # Mock the base feasibility check to return True
        with patch.object(feasibility_checker, 'is_feasible', return_value=True):
            with patch.object(feasibility_checker, 'is_room_available', return_value=True):
                result = feasibility_checker.check_feasibility_advanced(request)

        assert isinstance(result, FeasibilityCheckResult)
        assert result.surgery_id == 1
        assert result.room_id == 1
        assert result.check_duration_ms > 0
        assert result.constraints_checked > 0

    def test_equipment_availability_violation(
        self, feasibility_checker, mock_db_session, sample_surgery, sample_equipment
    ):
        """Test equipment availability constraint violation."""
        # Setup equipment that is unavailable
        sample_equipment.availability = False

        # Setup mock database queries
        equipment_usage = Mock(spec=SurgeryEquipmentUsage)
        equipment_usage.equipment_id = 1
        equipment_usage.surgery_id = 1

        # Create separate mock query objects for different query chains
        equipment_usage_query = Mock()
        equipment_query = Mock()

        # Mock the query method to return different objects based on the model
        def mock_query_side_effect(model):
            if model == SurgeryEquipmentUsage:
                return equipment_usage_query
            elif model == SurgeryEquipment:
                return equipment_query
            return Mock()

        mock_db_session.query.side_effect = mock_query_side_effect

        # Setup equipment usage query chain
        equipment_usage_query.filter.return_value.all.return_value = [equipment_usage]

        # Setup equipment query chain
        equipment_query.filter.return_value.first.return_value = sample_equipment

        violations = feasibility_checker._check_equipment_availability_advanced(
            sample_surgery, 1, datetime(2024, 1, 15, 9, 0), datetime(2024, 1, 15, 11, 0)
        )

        assert len(violations) > 0
        assert violations[0].constraint_type == ConstraintType.EQUIPMENT_AVAILABILITY
        assert violations[0].severity == ConstraintSeverity.CRITICAL
        assert "unavailable" in violations[0].description.lower()

    def test_surgeon_specialization_mismatch(
        self, feasibility_checker, mock_db_session, sample_surgeon, sample_surgery_type
    ):
        """Test surgeon specialization constraint violation."""
        # Setup surgeon with wrong specialization
        sample_surgeon.specialization = "Cardiology"
        sample_surgery_type.name = "Appendectomy"  # General surgery procedure

        # Setup mock database queries
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            sample_surgeon,  # Surgeon query
            sample_surgery_type  # Surgery type query
        ]

        violations = feasibility_checker._check_surgeon_specialization_advanced(1, 1)

        assert len(violations) > 0
        assert violations[0].constraint_type == ConstraintType.SURGEON_SPECIALIZATION
        assert violations[0].severity == ConstraintSeverity.HIGH
        assert "not be qualified" in violations[0].description

    def test_surgeon_specialization_match(
        self, feasibility_checker, mock_db_session, sample_surgeon, sample_surgery_type
    ):
        """Test successful surgeon specialization matching."""
        # Setup surgeon with correct specialization
        sample_surgeon.specialization = "General Surgery"
        sample_surgery_type.name = "Appendectomy"

        # Setup mock database queries
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            sample_surgeon,  # Surgeon query
            sample_surgery_type  # Surgery type query
        ]

        violations = feasibility_checker._check_surgeon_specialization_advanced(1, 1)

        assert len(violations) == 0

    def test_staff_availability_violation(
        self, feasibility_checker, mock_db_session, sample_surgery, sample_staff
    ):
        """Test staff availability constraint violation."""
        # Setup staff that is unavailable
        sample_staff.availability = False

        # Setup mock database queries
        staff_assignment = Mock(spec=SurgeryStaffAssignment)
        staff_assignment.staff_id = 1
        staff_assignment.surgery_id = 1

        # Create separate mock query objects for different query chains
        staff_assignment_query = Mock()
        staff_query = Mock()

        # Mock the query method to return different objects based on the model
        def mock_query_side_effect(model):
            if model == SurgeryStaffAssignment:
                return staff_assignment_query
            elif model == Staff:
                return staff_query
            return Mock()

        mock_db_session.query.side_effect = mock_query_side_effect

        # Setup staff assignment query chain
        staff_assignment_query.filter.return_value.all.return_value = [staff_assignment]

        # Setup staff query chain
        staff_query.filter.return_value.first.return_value = sample_staff

        violations = feasibility_checker._check_staff_availability_advanced(
            sample_surgery, 1, datetime(2024, 1, 15, 9, 0), datetime(2024, 1, 15, 11, 0)
        )

        assert len(violations) > 0
        assert violations[0].constraint_type == ConstraintType.STAFF_AVAILABILITY
        assert violations[0].severity == ConstraintSeverity.CRITICAL
        assert "unavailable" in violations[0].description.lower()

    def test_custom_constraint_rule_time_based(self, feasibility_checker, sample_surgery):
        """Test custom time-based constraint rule."""
        # Create a time-based rule that restricts surgeries to business hours
        rule = CustomConstraintRule(
            rule_id="business_hours_only",
            name="Business Hours Only",
            description="Surgeries must be scheduled during business hours",
            rule_type="time_based",
            conditions={
                "allowed_hours": {
                    "start": "08:00",
                    "end": "17:00"
                }
            },
            actions={},
            applies_to={},
            priority=100,
            enabled=True
        )

        feasibility_checker.add_custom_rule(rule)

        # Test violation - surgery scheduled outside business hours
        violation = feasibility_checker._evaluate_time_based_rule(
            rule, sample_surgery,
            datetime(2024, 1, 15, 19, 0),  # 7 PM
            datetime(2024, 1, 15, 21, 0)   # 9 PM
        )

        assert violation is not None
        assert violation.constraint_type == ConstraintType.TIME_WINDOW
        assert "outside allowed time window" in violation.description

    def test_custom_constraint_rule_duration_based(self, feasibility_checker, sample_surgery):
        """Test custom duration-based constraint rule."""
        # Create a duration-based rule that limits surgery duration
        rule = CustomConstraintRule(
            rule_id="max_duration_limit",
            name="Maximum Duration Limit",
            description="Surgeries cannot exceed 4 hours",
            rule_type="duration_based",
            conditions={
                "max_duration_minutes": 240  # 4 hours
            },
            actions={},
            applies_to={},
            priority=100,
            enabled=True
        )

        feasibility_checker.add_custom_rule(rule)

        # Test violation - surgery duration exceeds limit
        violation = feasibility_checker._evaluate_duration_based_rule(
            rule, sample_surgery,
            datetime(2024, 1, 15, 9, 0),
            datetime(2024, 1, 15, 15, 0)  # 6 hours duration
        )

        assert violation is not None
        assert violation.constraint_type == ConstraintType.CUSTOM
        assert "exceeds maximum allowed" in violation.description

    def test_constraint_configuration_management(self, feasibility_checker):
        """Test constraint configuration management."""
        # Test adding a new configuration
        config = ConstraintConfiguration(
            constraint_id="test_constraint",
            constraint_type=ConstraintType.CUSTOM,
            name="Test Constraint",
            description="A test constraint",
            severity=ConstraintSeverity.MEDIUM,
            enabled=True,
            parameters={"test_param": "test_value"}
        )

        feasibility_checker.add_constraint_configuration(config)

        # Verify it was added
        configurations = feasibility_checker.get_constraint_configurations()
        test_config = next((c for c in configurations if c.constraint_id == "test_constraint"), None)
        assert test_config is not None
        assert test_config.name == "Test Constraint"

        # Test removing the configuration
        success = feasibility_checker.remove_constraint_configuration("test_constraint")
        assert success

        # Verify it was removed
        configurations = feasibility_checker.get_constraint_configurations()
        test_config = next((c for c in configurations if c.constraint_id == "test_constraint"), None)
        assert test_config is None

    def test_custom_rule_management(self, feasibility_checker):
        """Test custom rule management."""
        # Test adding a new rule
        rule = CustomConstraintRule(
            rule_id="test_rule",
            name="Test Rule",
            description="A test rule",
            rule_type="test_type",
            conditions={"test": "value"},
            actions={},
            applies_to={},
            priority=100,
            enabled=True
        )

        feasibility_checker.add_custom_rule(rule)

        # Verify it was added
        rules = feasibility_checker.get_custom_rules()
        test_rule = next((r for r in rules if r.rule_id == "test_rule"), None)
        assert test_rule is not None
        assert test_rule.name == "Test Rule"

        # Test removing the rule
        success = feasibility_checker.remove_custom_rule("test_rule")
        assert success

        # Verify it was removed
        rules = feasibility_checker.get_custom_rules()
        test_rule = next((r for r in rules if r.rule_id == "test_rule"), None)
        assert test_rule is None

    def test_generate_recommendations(self, feasibility_checker, sample_surgery):
        """Test recommendation generation based on violations."""
        violations = [
            ConstraintViolation(
                constraint_id="test1",
                constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY,
                severity=ConstraintSeverity.CRITICAL,
                description="Equipment not available"
            ),
            ConstraintViolation(
                constraint_id="test2",
                constraint_type=ConstraintType.STAFF_AVAILABILITY,
                severity=ConstraintSeverity.HIGH,
                description="Staff not available"
            )
        ]

        recommendations = feasibility_checker._generate_recommendations(violations, sample_surgery)

        assert len(recommendations) > 0
        assert any("equipment" in rec.lower() for rec in recommendations)
        assert any("staff" in rec.lower() for rec in recommendations)
        assert any("critical" in rec.lower() for rec in recommendations)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
