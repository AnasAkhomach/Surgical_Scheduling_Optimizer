import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pytest
from datetime import datetime, timedelta
from utils.equipment_utilization_calculator import EquipmentUtilizationCalculator
from utils.equipment_utilization_efficiency_calculator import (
    EquipmentUtilizationEfficiencyCalculator,
)
from utils.operational_cost_calculator import OperationalCostCalculator
from utils.preference_satisfaction_calculator import PreferenceSatisfactionCalculator
from utils.resource_utilization_efficiency_calculator import (
    ResourceUtilizationEfficiencyCalculator,
)
from utils.room_utilization_calculator import RoomUtilizationCalculator
from utils.workload_balance_calculator import WorkloadBalanceCalculator
import types
import requests
from utils import utils


def test_equipment_utilization_calculator_basic():
    calc = EquipmentUtilizationCalculator()
    # Should handle empty input gracefully
    # The correct method is calculate_equipment_utilization_efficiency
    result = calc.calculate_equipment_utilization_efficiency(
        start_date=datetime.now(),
        end_date=datetime.now(),
        surgeries_data=[],
        equipment_data=[],
    )
    assert result == {}


def test_equipment_utilization_calculator_realistic():
    calc = EquipmentUtilizationCalculator()
    now = datetime(2025, 5, 16, 8, 0, 0)
    # Simulate two pieces of equipment, one used, one unused
    equipment_data = [
        {"equipment_id": 1},
        {"equipment_id": 2},
    ]
    surgeries_data = [
        {"equipment_id": 1, "start_time": now, "end_time": now + timedelta(hours=2)},
        {
            "equipment_id": 1,
            "start_time": now + timedelta(hours=3),
            "end_time": now + timedelta(hours=5),
        },
    ]
    result = calc.calculate_equipment_utilization_efficiency(
        start_date=now,
        end_date=now + timedelta(hours=8),
        surgeries_data=surgeries_data,
        equipment_data=equipment_data,
    )
    assert 1 in result and 2 in result
    assert result[2] == 0  # Unused equipment should have 0% utilization


def test_equipment_utilization_efficiency_calculator_basic():
    calc = EquipmentUtilizationEfficiencyCalculator()
    # Should handle empty input gracefully
    result = calc.calculate(
        start_date=datetime.now(),
        end_date=datetime.now(),
        equipments_data=[],
        surgeries_data=[],
    )
    assert isinstance(result, dict)


def test_equipment_utilization_efficiency_calculator_invalid_data():
    calc = EquipmentUtilizationEfficiencyCalculator()
    now = datetime.now()
    # Equipments with missing IDs, surgeries with invalid fields
    equipments = [
        {},  # missing id
        {"id": None},
        {"_id": "EQ1"},
    ]
    surgeries = [
        {},  # completely empty
        {"equipment_used": ["EQ1"], "start_time": "not-a-date", "end_time": now},
        {"equipment_used": ["EQ1"], "start_time": now, "end_time": None},
        {"equipment_used": None, "start_time": now, "end_time": now},
    ]
    result = calc.calculate(
        start_date=now,
        end_date=now + timedelta(days=1),
        equipments_data=equipments,
        surgeries_data=surgeries,
    )
    assert isinstance(result, dict)
    # Only EQ1 is valid, but no valid surgery, so utilization should be 0
    assert result.get("EQ1", 0) == 0


def test_operational_cost_calculator_average_duration():
    calc = OperationalCostCalculator()
    # Should return 0 for empty input
    assert calc.calculate_average_duration([]) == 0
    # Should compute average duration for valid input
    now = datetime.now()
    assignments = [
        {"start_time": now, "end_time": now + timedelta(hours=2)},
        {"start_time": now + timedelta(hours=3), "end_time": now + timedelta(hours=5)},
    ]
    avg = calc.calculate_average_duration(assignments)
    assert abs(avg - 2.0) < 0.01


def test_operational_cost_calculator_invalid():
    calc = OperationalCostCalculator()
    # Should handle missing or invalid time fields gracefully
    assignments = [
        {"start_time": "not-a-date", "end_time": "not-a-date"},
        {"start_time": None, "end_time": None},
    ]
    avg = calc.calculate_average_duration(assignments)
    assert avg == 0


def test_preference_satisfaction_calculator_empty():
    calc = PreferenceSatisfactionCalculator()
    # Should handle empty input gracefully
    assert calc.calculate([]) == 0


def test_resource_utilization_efficiency_calculator_empty():
    calc = ResourceUtilizationEfficiencyCalculator()
    # Should handle empty input gracefully
    result = calc.calculate(
        start_date=datetime.now(), end_date=datetime.now(), surgeries_data=[]
    )
    assert isinstance(result, dict)


def test_room_utilization_calculator_empty():
    calc = RoomUtilizationCalculator()
    # Should handle empty input gracefully
    assert calc.calculate([], []) == {}


def test_room_utilization_calculator_invalid_data():
    calc = RoomUtilizationCalculator()
    now = datetime.now()
    # Assignments with missing or invalid fields
    assignments = [
        {},  # completely empty
        {"room_id": None, "start_time": now, "end_time": now},  # missing room_id
        {
            "room_id": "OR1",
            "start_time": "not-a-date",
            "end_time": now,
        },  # invalid start_time
        {"room_id": "OR1", "start_time": now, "end_time": None},  # missing end_time
    ]
    result = calc.calculate(
        now, now + timedelta(days=1), room_assignments_data=assignments
    )
    assert isinstance(result, dict)
    assert result == {}  # No valid assignments, so no utilization


def test_workload_balance_calculator_empty():
    calc = WorkloadBalanceCalculator()
    # Should handle empty input gracefully
    assert calc.calculate_workload_balance([]) == 0


def test_workload_balance_calculator_realistic():
    calc = WorkloadBalanceCalculator()
    # Simulate 3 surgeons with different workloads
    surgeries = [
        {"surgeon_id": 1},
        {"surgeon_id": 1},
        {"surgeon_id": 2},
        {"surgeon_id": 3},
        {"surgeon_id": 3},
        {"surgeon_id": 3},
    ]
    stddev = calc.calculate_workload_balance(surgeries)
    assert stddev > 0


def test_workload_balance_calculator_all_same_surgeon():
    calc = WorkloadBalanceCalculator()
    # All surgeries assigned to the same surgeon (stddev should be 0)
    surgeries = [{"surgeon_id": 1} for _ in range(5)]
    stddev = calc.calculate_workload_balance(surgeries)
    assert stddev == 0


def test_workload_balance_calculator_missing_surgeon_id():
    calc = WorkloadBalanceCalculator()
    # Some surgeries missing surgeon_id (should be ignored, not crash)
    surgeries = [
        {"surgeon_id": 1},
        {},  # missing surgeon_id
        {"surgeon_id": 2},
        {"surgeon_id": None},
    ]
    stddev = calc.calculate_workload_balance(surgeries)
    assert stddev >= 0  # Should not error, and should be a valid stddev


def test_workload_balance_calculator_non_numeric_surgeon_id():
    calc = WorkloadBalanceCalculator()
    # Surgeon IDs as strings or mixed types should not cause errors
    surgeries = [
        {"surgeon_id": "A"},
        {"surgeon_id": "B"},
        {"surgeon_id": "A"},
        {"surgeon_id": 3},
    ]
    stddev = calc.calculate_workload_balance(surgeries)
    assert stddev >= 0


def test_workload_balance_calculator_large_input():
    calc = WorkloadBalanceCalculator()
    # Large number of surgeries, should not crash or be too slow
    surgeries = [{"surgeon_id": i % 10} for i in range(1000)]
    stddev = calc.calculate_workload_balance(surgeries)
    assert stddev >= 0


def test_make_api_call_with_retry_success(monkeypatch):
    # Simulate a successful API call on first try
    class DummyResponse:
        def raise_for_status(self):
            pass

    def dummy_post(url, headers, json):
        return DummyResponse()

    monkeypatch.setattr(requests, "post", dummy_post)
    response = utils.make_api_call_with_retry("http://fake", {}, {})
    assert isinstance(response, DummyResponse)


def test_make_api_call_with_retry_http_error(monkeypatch):
    # Simulate an HTTPError (should not retry, should raise)
    class DummyResponse:
        def raise_for_status(self):
            raise requests.exceptions.HTTPError("404 Not Found")

    def dummy_post(url, headers, json):
        return DummyResponse()

    monkeypatch.setattr(requests, "post", dummy_post)
    try:
        utils.make_api_call_with_retry("http://fake", {}, {})
    except requests.exceptions.HTTPError:
        assert True
    else:
        assert False, "Should have raised HTTPError"


def test_make_api_call_with_retry_retries(monkeypatch):
    # Simulate transient RequestException, then success
    call_count = {"count": 0}

    class DummyResponse:
        def raise_for_status(self):
            pass

    def dummy_post(url, headers, json):
        if call_count["count"] < 2:
            call_count["count"] += 1
            raise requests.exceptions.RequestException("Temporary error")
        return DummyResponse()

    monkeypatch.setattr(requests, "post", dummy_post)
    # Patch time.sleep to avoid real delay
    monkeypatch.setattr(utils.time, "sleep", lambda s: None)
    response = utils.make_api_call_with_retry("http://fake", {}, {}, max_retries=3)
    assert isinstance(response, DummyResponse)
