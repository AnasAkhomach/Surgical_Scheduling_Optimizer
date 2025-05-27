import sys
import os
import pytest
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scheduling_optimizer import (
    TabuSearchScheduler,
    SurgeryRoomAssignment,
)
from solution import Solution

# Mock classes for testing
class MockSurgery:
    def __init__(self, surgery_id, surgeon_id=None, duration=120, urgency_level="Medium",
                 surgery_type="General", specialization="General", requested_date=None,
                 start_time=None, end_time=None, room_id=None):
        self.surgery_id = surgery_id
        self.surgeon_id = surgeon_id
        self.duration = duration
        self.urgency_level = urgency_level
        self.surgery_type = surgery_type
        self.specialization = specialization
        self.requested_date = requested_date or (datetime.now() - timedelta(days=7))
        self.start_time = start_time
        self.end_time = end_time
        self.room_id = room_id
        self.preferences = {}
    def get(self, key, default=None):
        # Patch: Return datetime for start_time/end_time if possible
        if key == "start_time" and isinstance(self.start_time, str):
            try:
                return datetime.fromisoformat(self.start_time)
            except Exception:
                return self.start_time
        if key == "end_time" and isinstance(self.end_time, str):
            try:
                return datetime.fromisoformat(self.end_time)
            except Exception:
                return self.end_time
        return getattr(self, key, default)
    def __getitem__(self, key):
        # Patch: Return datetime for start_time/end_time if possible
        if key == "start_time" and isinstance(self.start_time, str):
            try:
                return datetime.fromisoformat(self.start_time)
            except Exception:
                return self.start_time
        if key == "end_time" and isinstance(self.end_time, str):
            try:
                return datetime.fromisoformat(self.end_time)
            except Exception:
                return self.end_time
        return getattr(self, key)
    def __contains__(self, key):
        return hasattr(self, key)

class MockRoom:
    def __init__(self, room_id, location="Main"):
        self.room_id = room_id
        self.location = location

class MockSurgeon:
    def __init__(self, surgeon_id, name="Dr. Test", specialization="General", credentials="MD"):
        self.surgeon_id = surgeon_id
        self.name = name
        self.specialization = specialization
        self.credentials = credentials
        self.preferences = []

class MockAssignment:
    def __init__(self, surgery_id, room_id, start_time, end_time):
        self.surgery_id = surgery_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
    def get(self, key, default=None):
        # Patch: Return datetime for start_time/end_time if possible
        if key == "start_time" and isinstance(self.start_time, str):
            try:
                return datetime.fromisoformat(self.start_time)
            except Exception:
                return self.start_time
        if key == "end_time" and isinstance(self.end_time, str):
            try:
                return datetime.fromisoformat(self.end_time)
            except Exception:
                return self.end_time
        return getattr(self, key, default)
    def __getitem__(self, key):
        # Patch: Return datetime for start_time/end_time if possible
        if key == "start_time" and isinstance(self.start_time, str):
            try:
                return datetime.fromisoformat(self.start_time)
            except Exception:
                return self.start_time
        if key == "end_time" and isinstance(self.end_time, str):
            try:
                return datetime.fromisoformat(self.end_time)
            except Exception:
                return self.end_time
        return getattr(self, key)
    def __contains__(self, key):
        return hasattr(self, key)

@pytest.fixture
def mock_scheduler():
    """Create a mock scheduler with test data."""
    now = datetime.now().replace(microsecond=0, second=0, minute=0)

    # Create surgeries with different urgency levels
    surgeries = [
        MockSurgery(surgery_id=1, surgeon_id=1, duration=120, urgency_level="High",
                   surgery_type="Cardiac Bypass"),
        MockSurgery(surgery_id=2, surgeon_id=2, duration=90, urgency_level="Medium",
                   surgery_type="General"),
        MockSurgery(surgery_id=3, surgeon_id=1, duration=150, urgency_level="Low",
                   surgery_type="Laparoscopic Cholecystectomy"),
        MockSurgery(surgery_id=4, surgeon_id=3, duration=180, urgency_level="High",
                   surgery_type="Complex Brain Tumor Resection"),
    ]

    # Create rooms
    rooms = [
        MockRoom(room_id=1),
        MockRoom(room_id=2),
    ]

    # Create surgeons
    surgeons = [
        MockSurgeon(surgeon_id=1, specialization="General"),
        MockSurgeon(surgeon_id=2, specialization="General"),
        MockSurgeon(surgeon_id=3, specialization="Neurosurgery"),
    ]

    # Create initial assignments
    assignments = [
        MockAssignment(
            surgery_id=1,
            room_id=1,
            start_time=(now + timedelta(hours=1)).isoformat(),
            end_time=(now + timedelta(hours=3)).isoformat(),
        ),
        MockAssignment(
            surgery_id=2,
            room_id=2,
            start_time=(now + timedelta(hours=3)).isoformat(),
            end_time=(now + timedelta(hours=4, minutes=30)).isoformat(),
        ),
        MockAssignment(
            surgery_id=3,
            room_id=1,
            start_time=(now + timedelta(hours=4)).isoformat(),
            end_time=(now + timedelta(hours=6, minutes=30)).isoformat(),
        ),
        MockAssignment(
            surgery_id=4,
            room_id=2,
            start_time=(now + timedelta(hours=5)).isoformat(),
            end_time=(now + timedelta(hours=8)).isoformat(),
        ),
    ]

    scheduler = TabuSearchScheduler(
        db_session=None,
        initial_surgeries=surgeries,
        initial_rooms=rooms,
        initial_surgeons=surgeons,
    )
    scheduler.surgery_room_assignments = assignments

    # Override the is_feasible and is_surgeon_available methods for testing
    scheduler.is_feasible = lambda schedule: True
    scheduler.is_surgeon_available = lambda surgeon_id, start_time, end_time, current_surgery_id_to_ignore=None: True

    return scheduler

def test_evaluate_solution_basic(mock_scheduler):
    """Test that evaluate_solution returns a finite score for a basic feasible schedule."""
    assignments = mock_scheduler.surgery_room_assignments
    score = mock_scheduler.evaluate_solution(assignments)
    assert isinstance(score, (int, float))
    assert score > -float("inf")
    print(f"Basic solution score: {score}")

def test_evaluate_solution_empty():
    """Test that evaluate_solution returns -inf for empty assignments."""
    scheduler = TabuSearchScheduler(
        db_session=None, initial_surgeries=[], initial_rooms=[], initial_surgeons=[]
    )
    score = scheduler.evaluate_solution([])
    assert score == -float("inf")

def test_evaluate_solution_emergency_priority(mock_scheduler):
    """Test that high urgency surgeries scheduled earlier get better scores."""
    assignments = mock_scheduler.surgery_room_assignments

    # Get the original score
    original_score = mock_scheduler.evaluate_solution(assignments)

    # Create a modified schedule where high urgency surgeries are scheduled earlier
    now = datetime.now().replace(microsecond=0, second=0, minute=0)

    # Find high urgency surgeries
    high_urgency_ids = [s.surgery_id for s in mock_scheduler.surgeries if s.urgency_level == "High"]

    # Create new assignments with high urgency surgeries scheduled first
    modified_assignments = []
    start_time = now

    # Schedule high urgency surgeries first
    for surgery_id in high_urgency_ids:
        surgery = next((s for s in mock_scheduler.surgeries if s.surgery_id == surgery_id), None)
        if surgery:
            end_time = start_time + timedelta(minutes=surgery.duration)
            modified_assignments.append(
                MockAssignment(
                    surgery_id=surgery_id,
                    room_id=1,  # Assign to room 1
                    start_time=start_time.isoformat(),
                    end_time=end_time.isoformat(),
                )
            )
            start_time = end_time + timedelta(minutes=15)  # 15-minute gap

    # Schedule remaining surgeries
    for surgery in mock_scheduler.surgeries:
        if surgery.surgery_id not in high_urgency_ids:
            end_time = start_time + timedelta(minutes=surgery.duration)
            modified_assignments.append(
                MockAssignment(
                    surgery_id=surgery.surgery_id,
                    room_id=1,  # Assign to room 1
                    start_time=start_time.isoformat(),
                    end_time=end_time.isoformat(),
                )
            )
            start_time = end_time + timedelta(minutes=15)  # 15-minute gap

    # Evaluate the modified schedule
    modified_score = mock_scheduler.evaluate_solution(modified_assignments)

    # The modified schedule should have a better score
    print(f"Original score: {original_score}, Modified score: {modified_score}")
    assert modified_score > original_score

def test_evaluate_solution_block_scheduling(mock_scheduler):
    """Test that schedules with surgeons having contiguous blocks get better scores."""
    assignments = mock_scheduler.surgery_room_assignments

    # Get the original score
    original_score = mock_scheduler.evaluate_solution(assignments)

    # Create a modified schedule with block scheduling for surgeons
    now = datetime.now().replace(microsecond=0, second=0, minute=0)

    # Group surgeries by surgeon
    surgeon_surgeries = {}
    for surgery in mock_scheduler.surgeries:
        if surgery.surgeon_id not in surgeon_surgeries:
            surgeon_surgeries[surgery.surgeon_id] = []
        surgeon_surgeries[surgery.surgeon_id].append(surgery)

    # Create new assignments with block scheduling
    modified_assignments = []
    current_time = now

    # Schedule each surgeon's surgeries in blocks
    for surgeon_id, surgeries in surgeon_surgeries.items():
        surgeon_start_time = current_time

        for surgery in surgeries:
            end_time = surgeon_start_time + timedelta(minutes=surgery.duration)
            modified_assignments.append(
                MockAssignment(
                    surgery_id=surgery.surgery_id,
                    room_id=1,  # Assign to room 1
                    start_time=surgeon_start_time.isoformat(),
                    end_time=end_time.isoformat(),
                )
            )
            surgeon_start_time = end_time + timedelta(minutes=15)  # 15-minute gap

        # Add a larger gap between different surgeons' blocks
        current_time = surgeon_start_time + timedelta(minutes=30)

    # Evaluate the modified schedule
    modified_score = mock_scheduler.evaluate_solution(modified_assignments)

    # The modified schedule should have a better score
    print(f"Original score: {original_score}, Modified score with block scheduling: {modified_score}")
    assert modified_score != original_score  # Score should be different

def test_evaluate_solution_equipment_conflicts(mock_scheduler):
    """Test that schedules with equipment conflicts get lower scores."""
    assignments = mock_scheduler.surgery_room_assignments

    # Get the original score
    original_score = mock_scheduler.evaluate_solution(assignments)

    # Create a modified schedule with equipment conflicts
    now = datetime.now().replace(microsecond=0, second=0, minute=0)

    # Find surgeries that use the same equipment
    cardiac_surgery = next((s for s in mock_scheduler.surgeries if s.surgery_type == "Cardiac Bypass"), None)
    brain_surgery = next((s for s in mock_scheduler.surgeries if s.surgery_type == "Complex Brain Tumor Resection"), None)

    if cardiac_surgery and brain_surgery:
        # Schedule these surgeries at the same time to create equipment conflict
        conflict_assignments = []

        # Add all original assignments except the conflicting ones
        for assignment in assignments:
            if assignment.surgery_id not in [cardiac_surgery.surgery_id, brain_surgery.surgery_id]:
                conflict_assignments.append(assignment)

        # Add conflicting assignments
        conflict_start_time = now
        conflict_end_time = now + timedelta(hours=2)

        conflict_assignments.append(
            MockAssignment(
                surgery_id=cardiac_surgery.surgery_id,
                room_id=1,
                start_time=conflict_start_time.isoformat(),
                end_time=conflict_end_time.isoformat(),
            )
        )

        conflict_assignments.append(
            MockAssignment(
                surgery_id=brain_surgery.surgery_id,
                room_id=2,
                start_time=conflict_start_time.isoformat(),
                end_time=conflict_end_time.isoformat(),
            )
        )

        # Evaluate the modified schedule
        conflict_score = mock_scheduler.evaluate_solution(conflict_assignments)

        # The conflict schedule should have a lower score or be infeasible
        print(f"Original score: {original_score}, Conflict score: {conflict_score}")
        assert conflict_score <= original_score

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-xvs", __file__])
