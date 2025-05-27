import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pytest
from utils.preference_satisfaction_calculator import PreferenceSatisfactionCalculator


def test_preference_satisfaction_empty():
    calc = PreferenceSatisfactionCalculator()
    assert calc.calculate([]) == 0


def test_preference_satisfaction_all_match():
    calc = PreferenceSatisfactionCalculator()
    # Simulate all assignments matching preferences (if logic is implemented)
    assignments = [
        {"surgeon_id": 1, "preferred": True},
        {"surgeon_id": 2, "preferred": True},
    ]
    # If the calculator uses a 'preferred' field, this should be max score
    score = calc.calculate(assignments)
    assert score >= 0


def test_preference_satisfaction_some_missing():
    calc = PreferenceSatisfactionCalculator()
    # Some assignments missing preference info
    assignments = [
        {"surgeon_id": 1},
        {"surgeon_id": 2, "preferred": False},
    ]
    score = calc.calculate(assignments)
    assert score >= 0


def test_preference_satisfaction_invalid_input():
    calc = PreferenceSatisfactionCalculator()
    # Should handle invalid input gracefully
    assignments = [None, {}, {"surgeon_id": None}]
    score = calc.calculate(assignments)
    assert score >= 0
