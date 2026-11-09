"""Small invariant checks that do not depend on confidential workbook data."""
import unittest
import pandas as pd
from task1_analysis import events


class EventTests(unittest.TestCase):
    def test_boundaries_are_end_exclusive(self):
        idx = pd.date_range("2020-01-01", periods=6, freq="5min")
        result = events(pd.Series([True, True, False, True, False, True], index=idx))
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0].start, idx[0])
        self.assertEqual(result.iloc[0].end, idx[2])
        self.assertAlmostEqual(result.duration_hours.sum(), 4 * 5 / 60)
        self.assertEqual(result.iloc[-1].end, idx[-1] + pd.Timedelta(minutes=5))

    def test_missing_is_not_a_shutdown(self):
        idx = pd.date_range("2020-01-01", periods=3, freq="5min")
        result = events(pd.Series([True, None, True], index=idx, dtype="boolean"))
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
