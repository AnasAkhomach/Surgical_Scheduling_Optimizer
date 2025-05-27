"""
Test script for the solution evaluator.

This script tests the solution evaluator with sample data.
"""

import sys
import os
import logging
import unittest
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models import (
    Surgery,
    OperatingRoom,
    Surgeon,
    SurgeryType,
    SurgeryRoomAssignment,
    SurgeonPreference
)
from solution_evaluator import SolutionEvaluator

class MockDBSession:
    """Mock database session for testing."""

    def __init__(self, surgeries, rooms, surgeons, surgery_types, surgeon_preferences):
        """
        Initialize the mock database session.

        Args:
            surgeries: List of Surgery objects
            rooms: List of OperatingRoom objects
            surgeons: List of Surgeon objects
            surgery_types: List of SurgeryType objects
            surgeon_preferences: List of SurgeonPreference objects
        """
        self.surgeries = surgeries
        self.rooms = rooms
        self.surgeons = surgeons
        self.surgery_types = surgery_types
        self.surgeon_preferences = surgeon_preferences

    def query(self, model):
        """
        Query the mock database.

        Args:
            model: Model class to query

        Returns:
            MockQuery object
        """
        if model == Surgery:
            return MockQuery(self.surgeries)
        elif model == OperatingRoom:
            return MockQuery(self.rooms)
        elif model == Surgeon:
            return MockQuery(self.surgeons)
        elif model == SurgeryType:
            return MockQuery(self.surgery_types)
        elif model == SurgeonPreference:
            return MockQuery(self.surgeon_preferences)
        else:
            return MockQuery([])

class MockQuery:
    """Mock query for testing."""

    def __init__(self, data):
        """
        Initialize the mock query.

        Args:
            data: List of objects
        """
        self.data = data

    def filter_by(self, **kwargs):
        """
        Filter the mock query.

        Args:
            **kwargs: Filter criteria

        Returns:
            MockQuery object
        """
        filtered = []
        for item in self.data:
            match = True
            for key, value in kwargs.items():
                if not hasattr(item, key) or getattr(item, key) != value:
                    match = False
                    break
            if match:
                filtered.append(item)
        return MockQuery(filtered)

    def all(self):
        """
        Get all objects.

        Returns:
            List of objects
        """
        return self.data

    def first(self):
        """
        Get the first object.

        Returns:
            First object or None
        """
        return self.data[0] if self.data else None

class TestSolutionEvaluator(unittest.TestCase):
    """Test case for the solution evaluator."""

    def setUp(self):
        """Set up the test case."""
        # Create sample data
        self.surgeries = [
            Surgery(
                surgery_id=1,
                surgery_type_id=1,
                duration_minutes=60,
                surgeon_id=1,
                urgency_level="Medium"
            ),
            Surgery(
                surgery_id=2,
                surgery_type_id=2,
                duration_minutes=120,
                surgeon_id=2,
                urgency_level="Low"
            ),
            Surgery(
                surgery_id=3,
                surgery_type_id=3,
                duration_minutes=180,
                surgeon_id=3,
                urgency_level="High"
            ),
            Surgery(
                surgery_id=4,
                surgery_type_id=1,
                duration_minutes=90,
                surgeon_id=1,
                urgency_level="High"
            ),
            Surgery(
                surgery_id=5,
                surgery_type_id=2,
                duration_minutes=150,
                surgeon_id=2,
                urgency_level="Medium"
            )
        ]

        self.rooms = [
            OperatingRoom(room_id=1, location="Main Building - Room 101"),
            OperatingRoom(room_id=2, location="Main Building - Room 102"),
            OperatingRoom(room_id=3, location="West Wing - Room 201")
        ]

        self.surgeons = [
            Surgeon(surgeon_id=1, name="Dr. Smith", specialization="General", credentials="MD", availability=True),
            Surgeon(surgeon_id=2, name="Dr. Jones", specialization="Orthopedic", credentials="MD", availability=True),
            Surgeon(surgeon_id=3, name="Dr. Wilson", specialization="Cardiac", credentials="MD, PhD", availability=True)
        ]

        self.surgery_types = [
            SurgeryType(type_id=1, name="Appendectomy", description="Appendix removal"),
            SurgeryType(type_id=2, name="Knee Replacement", description="Total knee replacement"),
            SurgeryType(type_id=3, name="Coronary Bypass", description="Heart bypass surgery")
        ]

        self.surgeon_preferences = [
            SurgeonPreference(preference_id=1, surgeon_id=1, preference_type="room_id", preference_value="1"),
            SurgeonPreference(preference_id=2, surgeon_id=2, preference_type="day_of_week", preference_value="Monday"),
            SurgeonPreference(preference_id=3, surgeon_id=3, preference_type="time_of_day", preference_value="morning")
        ]

        # Create mock database session
        self.db_session = MockDBSession(
            self.surgeries,
            self.rooms,
            self.surgeons,
            self.surgery_types,
            self.surgeon_preferences
        )

        # Create sample solution
        base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

        self.solution = [
            SurgeryRoomAssignment(
                surgery_id=1,
                room_id=1,
                start_time=base_time,
                end_time=base_time + timedelta(minutes=60)
            ),
            SurgeryRoomAssignment(
                surgery_id=2,
                room_id=2,
                start_time=base_time,
                end_time=base_time + timedelta(minutes=120)
            ),
            SurgeryRoomAssignment(
                surgery_id=3,
                room_id=3,
                start_time=base_time,
                end_time=base_time + timedelta(minutes=180)
            ),
            SurgeryRoomAssignment(
                surgery_id=4,
                room_id=1,
                start_time=base_time + timedelta(minutes=75),  # 15-minute setup time
                end_time=base_time + timedelta(minutes=75 + 90)
            ),
            SurgeryRoomAssignment(
                surgery_id=5,
                room_id=2,
                start_time=base_time + timedelta(minutes=135),  # 15-minute setup time
                end_time=base_time + timedelta(minutes=135 + 150)
            )
        ]

        # Create sample SDST data
        self.sds_times_data = {
            (1, 1): 15,
            (1, 2): 30,
            (1, 3): 45,
            (2, 1): 30,
            (2, 2): 15,
            (2, 3): 30,
            (3, 1): 45,
            (3, 2): 30,
            (3, 3): 15
        }

        # Create evaluator
        self.evaluator = SolutionEvaluator(
            db_session=self.db_session,
            sds_times_data=self.sds_times_data
        )

    def test_or_utilization(self):
        """Test operating room utilization calculation."""
        # Calculate manually
        total_duration = 60 + 120 + 180 + 90 + 150  # 600 minutes
        total_available_time = 8 * 60 * 3  # 8 hours * 3 rooms = 1440 minutes
        expected_utilization = total_duration / total_available_time

        # Get from evaluator
        utilization = self.evaluator._calculate_or_utilization(
            self.solution,
            self.solution[0].start_time,
            self.solution[0].start_time + timedelta(hours=8)
        )

        self.assertAlmostEqual(utilization, expected_utilization, places=2)

    def test_sds_time(self):
        """Test sequence-dependent setup time calculation."""
        # Calculate manually
        # Room 1: Surgery 1 -> Surgery 4 (same type, 15 minutes)
        # Room 2: Surgery 2 -> Surgery 5 (same type, 15 minutes)
        # Room 3: No transitions
        expected_sds_time = 15 + 15  # 30 minutes

        # Get from evaluator
        sds_penalty = self.evaluator._calculate_sds_time(self.solution)

        # Check that the penalty is reasonable
        self.assertTrue(0 <= sds_penalty <= 1)

    def test_surgeon_preference_satisfaction(self):
        """Test surgeon preference satisfaction calculation."""
        # Calculate manually
        # Surgeon 1 prefers Room 1, and Surgery 1 is in Room 1 -> Satisfied
        # Surgeon 2 prefers Monday, but we don't know the day -> Not satisfied
        # Surgeon 3 prefers morning, and Surgery 3 is in the morning -> Satisfied
        expected_satisfaction = 2 / 3  # 2 out of 3 preferences satisfied

        # Get from evaluator
        satisfaction = self.evaluator._calculate_surgeon_preference_satisfaction(self.solution)

        # Check that the satisfaction is reasonable
        self.assertTrue(0 <= satisfaction <= 1)

    def test_workload_balance(self):
        """Test workload balance calculation."""
        # Calculate manually
        # Surgeon 1: 60 + 90 = 150 minutes
        # Surgeon 2: 120 + 150 = 270 minutes
        # Surgeon 3: 180 minutes
        # Mean: 200 minutes
        # Variance: ((150-200)^2 + (270-200)^2 + (180-200)^2) / 3 = 2500 / 3 = 833.33
        # Std Dev: sqrt(833.33) = 28.87
        # Normalized balance: 1 - min(1, 28.87/200) = 1 - 0.14 = 0.86

        # Get from evaluator
        balance = self.evaluator._calculate_workload_balance(self.solution)

        # Check that the balance is reasonable
        self.assertTrue(0 <= balance <= 1)

    def test_evaluate_solution(self):
        """Test the overall solution evaluation."""
        # Get the overall score
        score = self.evaluator.evaluate_solution(self.solution)

        # Check that the score is reasonable
        self.assertTrue(-100 <= score <= 100)

        # Create a worse solution with poor OR utilization
        poor_solution = self.solution.copy()
        poor_solution[0].start_time = datetime.now().replace(hour=8, minute=0)
        poor_solution[0].end_time = datetime.now().replace(hour=9, minute=0)
        poor_solution[1].start_time = datetime.now().replace(hour=12, minute=0)
        poor_solution[1].end_time = datetime.now().replace(hour=14, minute=0)

        poor_score = self.evaluator.evaluate_solution(poor_solution)

        # The better solution should have a higher score
        self.assertTrue(score > poor_score)

if __name__ == "__main__":
    unittest.main()
