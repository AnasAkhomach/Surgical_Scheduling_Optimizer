"""
Tests for Emergency Surgery API Endpoints (Task 2.2).

This module tests the emergency surgery API endpoints including:
- Emergency surgery insertion endpoint
- Emergency metrics endpoint
- Emergency re-optimization endpoint
- Emergency conflicts endpoint
- Emergency simulation endpoint
"""

import pytest
import json
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from main import app
from api.models import (
    EmergencySurgeryRequest,
    EmergencyInsertionResult,
    EmergencyMetrics,
    EmergencyType,
    EmergencyPriority,
    UrgencyLevel
)

client = TestClient(app)


class TestEmergencySurgeryAPI:
    """Test cases for emergency surgery API endpoints."""
    
    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers for API requests."""
        # Mock authentication - in real tests, you'd get a valid token
        return {"Authorization": "Bearer mock_token"}
    
    @pytest.fixture
    def emergency_request_data(self):
        """Create sample emergency surgery request data."""
        return {
            "patient_id": 1,
            "surgery_type_id": 1,
            "emergency_type": "Trauma",
            "emergency_priority": "Urgent",
            "urgency_level": "Emergency",
            "duration_minutes": 90,
            "arrival_time": datetime.now().isoformat(),
            "max_wait_time_minutes": 60,
            "required_surgeon_id": 1,
            "clinical_notes": "Emergency appendectomy required",
            "allow_bumping": True,
            "allow_overtime": True,
            "allow_backup_rooms": True
        }
    
    @pytest.fixture
    def mock_emergency_insertion_result(self):
        """Create a mock emergency insertion result."""
        return EmergencyInsertionResult(
            success=True,
            emergency_surgery_id=123,
            assigned_room_id=1,
            assigned_surgeon_id=1,
            scheduled_start_time=datetime.now() + timedelta(minutes=30),
            scheduled_end_time=datetime.now() + timedelta(minutes=120),
            bumped_surgeries=[],
            conflicts_resolved=[],
            notifications_sent=["surgeon_1", "room_1"],
            affected_staff=[1],
            insertion_time_seconds=2.5,
            wait_time_minutes=30.0,
            schedule_disruption_score=0.2
        )
    
    @pytest.fixture
    def mock_emergency_metrics(self):
        """Create mock emergency metrics."""
        return EmergencyMetrics(
            date_range_start=date(2024, 1, 1),
            date_range_end=date(2024, 1, 31),
            total_emergencies=10,
            emergencies_by_type={"Trauma": 5, "Cardiac": 3, "General": 2},
            emergencies_by_priority={"Immediate": 2, "Urgent": 6, "Semi-Urgent": 2},
            average_wait_time_minutes=45.0,
            average_insertion_time_seconds=3.2,
            successful_insertions_rate=0.95,
            surgeries_bumped=3,
            overtime_hours_generated=12.5,
            average_disruption_score=0.25,
            rooms_used_for_emergencies={"OR-1": 4, "OR-2": 3, "OR-3": 3},
            surgeons_involved={"Dr. Smith": 4, "Dr. Johnson": 3, "Dr. Brown": 3}
        )
    
    @patch('api.routers.schedules.EmergencySurgeryHandler')
    @patch('api.routers.schedules.get_current_active_user')
    def test_insert_emergency_surgery_success(
        self, 
        mock_get_user, 
        mock_handler_class, 
        auth_headers, 
        emergency_request_data, 
        mock_emergency_insertion_result
    ):
        """Test successful emergency surgery insertion."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.user_id = 1
        mock_get_user.return_value = mock_user
        
        # Mock emergency handler
        mock_handler = Mock()
        mock_handler.insert_emergency_surgery.return_value = mock_emergency_insertion_result
        mock_handler_class.return_value = mock_handler
        
        # Make API request
        response = client.post(
            "/api/schedules/emergency/insert",
            json=emergency_request_data,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        
        result_data = response.json()
        assert result_data["success"] is True
        assert result_data["emergency_surgery_id"] == 123
        assert result_data["assigned_room_id"] == 1
        assert result_data["assigned_surgeon_id"] == 1
        assert result_data["wait_time_minutes"] == 30.0
        assert result_data["schedule_disruption_score"] == 0.2
        
        # Verify handler was called
        mock_handler.insert_emergency_surgery.assert_called_once()
    
    @patch('api.routers.schedules.EmergencySurgeryHandler')
    @patch('api.routers.schedules.get_current_active_user')
    def test_insert_emergency_surgery_validation_error(
        self, 
        mock_get_user, 
        mock_handler_class, 
        auth_headers, 
        emergency_request_data
    ):
        """Test emergency surgery insertion with validation error."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.user_id = 1
        mock_get_user.return_value = mock_user
        
        # Mock emergency handler to raise validation error
        mock_handler = Mock()
        mock_handler.insert_emergency_surgery.side_effect = ValueError("Patient not found")
        mock_handler_class.return_value = mock_handler
        
        # Make API request
        response = client.post(
            "/api/schedules/emergency/insert",
            json=emergency_request_data,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Patient not found" in response.json()["detail"]
    
    @patch('api.routers.schedules.EmergencySurgeryHandler')
    @patch('api.routers.schedules.get_current_active_user')
    def test_insert_emergency_surgery_server_error(
        self, 
        mock_get_user, 
        mock_handler_class, 
        auth_headers, 
        emergency_request_data
    ):
        """Test emergency surgery insertion with server error."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.user_id = 1
        mock_get_user.return_value = mock_user
        
        # Mock emergency handler to raise general error
        mock_handler = Mock()
        mock_handler.insert_emergency_surgery.side_effect = Exception("Database error")
        mock_handler_class.return_value = mock_handler
        
        # Make API request
        response = client.post(
            "/api/schedules/emergency/insert",
            json=emergency_request_data,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database error" in response.json()["detail"]
    
    def test_insert_emergency_surgery_invalid_data(self, auth_headers):
        """Test emergency surgery insertion with invalid request data."""
        invalid_data = {
            "patient_id": "invalid",  # Should be integer
            "surgery_type_id": 1,
            "emergency_type": "InvalidType",  # Invalid enum value
            "duration_minutes": -10  # Should be positive
        }
        
        response = client.post(
            "/api/schedules/emergency/insert",
            json=invalid_data,
            headers=auth_headers
        )
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('api.routers.schedules.EmergencySurgeryHandler')
    @patch('api.routers.schedules.get_current_active_user')
    def test_get_emergency_metrics_success(
        self, 
        mock_get_user, 
        mock_handler_class, 
        auth_headers, 
        mock_emergency_metrics
    ):
        """Test successful emergency metrics retrieval."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.user_id = 1
        mock_get_user.return_value = mock_user
        
        # Mock emergency handler
        mock_handler = Mock()
        mock_handler.get_emergency_metrics.return_value = mock_emergency_metrics
        mock_handler_class.return_value = mock_handler
        
        # Make API request
        response = client.get(
            "/api/schedules/emergency/metrics",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        
        metrics_data = response.json()
        assert metrics_data["total_emergencies"] == 10
        assert metrics_data["average_wait_time_minutes"] == 45.0
        assert metrics_data["successful_insertions_rate"] == 0.95
        assert metrics_data["surgeries_bumped"] == 3
        assert metrics_data["average_disruption_score"] == 0.25
        
        # Verify handler was called with correct parameters
        mock_handler.get_emergency_metrics.assert_called_once()
    
    @patch('api.routers.schedules.EmergencySurgeryHandler')
    @patch('api.routers.schedules.get_current_active_user')
    def test_re_optimize_for_emergency_success(
        self, 
        mock_get_user, 
        mock_handler_class, 
        auth_headers
    ):
        """Test successful emergency re-optimization."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.user_id = 1
        mock_get_user.return_value = mock_user
        
        # Mock emergency handler
        mock_handler = Mock()
        mock_optimization_result = {
            "optimization_result": {"score": 0.85, "assignments": []},
            "emergency_surgery_id": 123,
            "schedule_date": date(2024, 1, 15),
            "total_surgeries": 8
        }
        mock_handler.re_optimize_schedule_for_emergency.return_value = mock_optimization_result
        mock_handler_class.return_value = mock_handler
        
        # Make API request
        response = client.post(
            "/api/schedules/emergency/re-optimize/123",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        
        result_data = response.json()
        assert result_data["message"] == "Schedule re-optimization completed"
        assert result_data["emergency_surgery_id"] == 123
        assert "optimization_result" in result_data
        
        # Verify handler was called
        mock_handler.re_optimize_schedule_for_emergency.assert_called_once_with(123, None)
    
    @patch('api.routers.schedules.EmergencySurgeryHandler')
    @patch('api.routers.schedules.get_current_active_user')
    def test_re_optimize_for_emergency_not_found(
        self, 
        mock_get_user, 
        mock_handler_class, 
        auth_headers
    ):
        """Test re-optimization with non-existent emergency surgery."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.user_id = 1
        mock_get_user.return_value = mock_user
        
        # Mock emergency handler to raise ValueError
        mock_handler = Mock()
        mock_handler.re_optimize_schedule_for_emergency.side_effect = ValueError(
            "Emergency surgery 999 not found"
        )
        mock_handler_class.return_value = mock_handler
        
        # Make API request
        response = client.post(
            "/api/schedules/emergency/re-optimize/999",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Emergency surgery 999 not found" in response.json()["detail"]
    
    @patch('api.routers.schedules._detect_schedule_conflicts')
    @patch('api.routers.schedules.get_current_active_user')
    def test_get_emergency_conflicts_success(
        self, 
        mock_get_user, 
        mock_detect_conflicts, 
        auth_headers
    ):
        """Test successful emergency conflicts retrieval."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.user_id = 1
        mock_get_user.return_value = mock_user
        
        # Mock emergency surgery
        mock_surgery = Mock()
        mock_surgery.surgery_id = 123
        mock_surgery.urgency_level = "Emergency"
        mock_surgery.scheduled_date = date(2024, 1, 15)
        
        # Mock database query
        with patch('api.routers.schedules.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.query.return_value.filter.return_value.first.return_value = mock_surgery
            mock_get_db.return_value = mock_db
            
            # Mock conflicts
            mock_conflicts = [
                Mock(surgery_id=123, conflicting_surgery_id=124, conflict_type="room_overlap"),
                Mock(surgery_id=125, conflicting_surgery_id=123, conflict_type="surgeon_overlap")
            ]
            mock_detect_conflicts.return_value = mock_conflicts
            
            # Make API request
            response = client.get(
                "/api/schedules/emergency/conflicts/123",
                headers=auth_headers
            )
            
            # Verify response
            assert response.status_code == status.HTTP_200_OK
            
            result_data = response.json()
            assert result_data["emergency_surgery_id"] == 123
            assert result_data["total_conflicts"] == 2
            assert len(result_data["resolution_suggestions"]) > 0
    
    @patch('api.routers.schedules.EmergencySurgeryHandler')
    @patch('api.routers.schedules.get_current_active_user')
    def test_simulate_emergency_insertion_success(
        self, 
        mock_get_user, 
        mock_handler_class, 
        auth_headers, 
        emergency_request_data
    ):
        """Test successful emergency surgery simulation."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.user_id = 1
        mock_get_user.return_value = mock_user
        
        # Mock emergency handler
        mock_handler = Mock()
        mock_insertion_result = {
            'success': True,
            'strategy': 'use_backup_room',
            'bumped_surgeries': [],
            'conflicts_resolved': [],
            'overtime_required': False
        }
        mock_handler._find_optimal_insertion.return_value = mock_insertion_result
        mock_handler._calculate_disruption_score.return_value = 0.2
        mock_handler._calculate_wait_time.return_value = 25.0
        mock_handler_class.return_value = mock_handler
        
        # Make API request
        response = client.post(
            "/api/schedules/emergency/simulate",
            json=emergency_request_data,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        
        result_data = response.json()
        assert result_data["simulation_successful"] is True
        assert result_data["insertion_strategy"] == "use_backup_room"
        assert result_data["estimated_wait_time_minutes"] == 25.0
        assert result_data["schedule_disruption_score"] == 0.2
        assert result_data["bumped_surgeries_count"] == 0
        assert result_data["overtime_required"] is False
        assert len(result_data["recommendations"]) > 0
    
    @patch('api.routers.schedules.EmergencySurgeryHandler')
    @patch('api.routers.schedules.get_current_active_user')
    def test_simulate_emergency_insertion_failure(
        self, 
        mock_get_user, 
        mock_handler_class, 
        auth_headers, 
        emergency_request_data
    ):
        """Test emergency surgery simulation failure."""
        # Mock user authentication
        mock_user = Mock()
        mock_user.user_id = 1
        mock_get_user.return_value = mock_user
        
        # Mock emergency handler
        mock_handler = Mock()
        mock_insertion_result = {
            'success': False,
            'reason': 'No available operating rooms',
            'bumped_surgeries': [],
            'conflicts_resolved': []
        }
        mock_handler._find_optimal_insertion.return_value = mock_insertion_result
        mock_handler._calculate_disruption_score.return_value = 1.0
        mock_handler._calculate_wait_time.return_value = None
        mock_handler_class.return_value = mock_handler
        
        # Make API request
        response = client.post(
            "/api/schedules/emergency/simulate",
            json=emergency_request_data,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        
        result_data = response.json()
        assert result_data["simulation_successful"] is False
        assert result_data["reason"] == "No available operating rooms"
        assert result_data["schedule_disruption_score"] == 1.0
        assert result_data["estimated_wait_time_minutes"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
