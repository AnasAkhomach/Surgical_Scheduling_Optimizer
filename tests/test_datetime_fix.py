import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import sys

# Create a wrapper class for datetime
class DatetimeWrapper:
    _fixed_now = None

    @classmethod
    def set_fixed_now(cls, fixed_now):
        cls._fixed_now = fixed_now

    @classmethod
    def now(cls, tz=None):
        if cls._fixed_now is not None:
            return cls._fixed_now
        return datetime.now(tz)

    # Delegate all other methods to the original datetime
    @classmethod
    def fromisoformat(cls, date_string):
        return datetime.fromisoformat(date_string)

    # Add other methods as needed

class TestDatetimeMocking(unittest.TestCase):
    def test_datetime_wrapper(self):
        # Set a fixed time for testing
        fixed_time = datetime(2025, 5, 16, 7, 0, 0)
        DatetimeWrapper.set_fixed_now(fixed_time)

        # Test that DatetimeWrapper.now() returns the fixed time
        self.assertEqual(DatetimeWrapper.now(), fixed_time)

        # Test that other datetime methods still work
        test_date_str = "2025-05-16T08:00:00"
        parsed_date = DatetimeWrapper.fromisoformat(test_date_str)
        self.assertEqual(parsed_date.isoformat(), test_date_str)

        # Test that timedelta works with the mocked datetime
        one_hour_later = DatetimeWrapper.now() + timedelta(hours=1)
        expected = datetime(2025, 5, 16, 8, 0, 0)
        self.assertEqual(one_hour_later, expected)

if __name__ == '__main__':
    unittest.main()
