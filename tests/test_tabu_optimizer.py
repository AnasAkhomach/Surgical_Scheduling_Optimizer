import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from simple_models import Surgery, OperatingRoom, SurgeryRoomAssignment
from scheduler_utils import SchedulerUtils, DatetimeWrapper
from tabu_optimizer import TabuOptimizer
from simple_feasibility_checker import FeasibilityChecker

class TestTabuOptimizer(unittest.TestCase):
    def setUp(self):
        # Set a fixed time for testing
        DatetimeWrapper.set_fixed_now(datetime(2025, 5, 16, 7, 0, 0))

        # Create test surgeries
        self.surgeries = [
            Surgery(surgery_id=1, surgery_type_id=1, duration_minutes=60, surgeon_id=101),
            Surgery(surgery_id=2, surgery_type_id=2, duration_minutes=90, surgeon_id=102),
            Surgery(surgery_id=3, surgery_type_id=1, duration_minutes=120, surgeon_id=103)
        ]

        # Create test operating rooms
        self.operating_rooms = [
            OperatingRoom(room_id=1, operational_start_time=datetime(2025, 5, 16, 8, 0, 0).time()),
            OperatingRoom(room_id=2, operational_start_time=datetime(2025, 5, 16, 9, 0, 0).time())
        ]

        # Create sequence-dependent setup times
        self.sds_times = {
            (1, 1): 15,  # From type 1 to type 1: 15 minutes
            (1, 2): 30,  # From type 1 to type 2: 30 minutes
            (2, 1): 25,  # From type 2 to type 1: 25 minutes
            (2, 2): 15   # From type 2 to type 2: 15 minutes
        }

        # Create mock feasibility checker
        self.feasibility_checker = MagicMock(spec=FeasibilityChecker)
        self.feasibility_checker.is_surgeon_available.return_value = True
        self.feasibility_checker.is_equipment_available.return_value = True

        # Create scheduler utils
        self.scheduler_utils = SchedulerUtils(
            db_session=None,
            surgeries=self.surgeries,
            operating_rooms=self.operating_rooms,
            feasibility_checker=self.feasibility_checker,
            surgery_equipments=None,
            surgery_equipment_usages=None,
            sds_times_data=self.sds_times
        )

        # Create initial solution
        self.initial_solution = [
            SurgeryRoomAssignment(
                surgery_id=1,
                room_id=1,
                start_time=datetime(2025, 5, 16, 8, 30, 0),
                end_time=datetime(2025, 5, 16, 9, 30, 0)
            ),
            SurgeryRoomAssignment(
                surgery_id=2,
                room_id=1,
                start_time=datetime(2025, 5, 16, 10, 15, 0),
                end_time=datetime(2025, 5, 16, 11, 45, 0)
            ),
            SurgeryRoomAssignment(
                surgery_id=3,
                room_id=2,
                start_time=datetime(2025, 5, 16, 9, 30, 0),
                end_time=datetime(2025, 5, 16, 11, 30, 0)
            )
        ]

        # Create Tabu Optimizer
        self.optimizer = TabuOptimizer(
            scheduler_utils=self.scheduler_utils,
            tabu_list_size=5,
            max_iterations=10,
            max_no_improvement=5
        )

    def test_calculate_cost(self):
        """Test the cost calculation function."""
        cost = self.optimizer.calculate_cost(self.initial_solution)

        # The cost should be a positive number
        self.assertGreater(cost, 0)

        # Empty solution should have infinite cost
        self.assertEqual(self.optimizer.calculate_cost([]), float('inf'))

    def test_generate_neighbors(self):
        """Test the neighbor generation function."""
        neighbors = self.optimizer.generate_neighbors(self.initial_solution)

        # Should generate some neighbors
        self.assertGreater(len(neighbors), 0)

        # Each neighbor should be a tuple (solution, move)
        for neighbor in neighbors:
            self.assertEqual(len(neighbor), 2)
            self.assertIsInstance(neighbor[0], list)  # solution is a list
            self.assertIsInstance(neighbor[1], tuple)  # move is a tuple

    def test_optimize(self):
        """Test the optimization process."""
        # Run the optimizer with a small number of iterations
        self.optimizer.max_iterations = 2
        solution = self.optimizer.optimize(self.initial_solution)

        # Should return a solution
        self.assertIsInstance(solution, list)
        self.assertGreater(len(solution), 0)

    def test_optimize_with_real_functions(self):
        """Test the optimization process with real functions."""
        # Run the optimizer with a small number of iterations
        self.optimizer.max_iterations = 3
        solution = self.optimizer.optimize(self.initial_solution)

        # Should return a solution
        self.assertIsInstance(solution, list)
        self.assertGreater(len(solution), 0)

        # Each assignment should have the required attributes
        for assignment in solution:
            self.assertTrue(hasattr(assignment, 'surgery_id'))
            self.assertTrue(hasattr(assignment, 'room_id'))
            self.assertTrue(hasattr(assignment, 'start_time'))
            self.assertTrue(hasattr(assignment, 'end_time'))

if __name__ == '__main__':
    unittest.main()
