import unittest
from datetime import datetime, time
import pandas as pd
import os
from typing import List, Tuple, Dict, Set

from find_unoccupied_rooms import (
    find_unoccupied_rooms,
    is_summer,
    class_in_block,
    expand_days,
    parse_time,
)

class TestFindUnoccupiedRooms(unittest.TestCase):
    def setUp(self):
        """Create a sample DataFrame for testing"""
        self.test_data = {
            'building': [5, 5, 5],
            'room_number': [103, 103, 104],
            'term': [20252, 20252, 20252],
            'start_time': ['09:30', '11:00', '09:30'],
            'end_time': ['10:45', '12:15', '10:45'],
            'days': ['MWF', 'TR', 'MWF'],
            'room_cap': [30, 30, 25],
            'start_date': ['2025-01-06', '2025-01-06', '2025-01-06'],
            'end_date': ['2025-05-04', '2025-05-04', '2025-05-04']
        }
        self.df = pd.DataFrame(self.test_data)
        
        # Save test data to a temporary CSV file
        self.test_csv_path = os.path.join("data", "test_data.csv")
        os.makedirs(os.path.dirname(self.test_csv_path), exist_ok=True)
        self.df.to_csv(self.test_csv_path, index=False)

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)

    def test_find_unoccupied_rooms_basic(self):
        """Test basic functionality of find_unoccupied_rooms"""
        selected_rooms = [(5, 103), (5, 104)]
        selected_days = ['M', 'W', 'F']
        selected_time_slots = [
            (time(9, 30), time(10, 45)),
            (time(11, 0), time(12, 15))
        ]
        selected_term = 20252
        selected_session = 1

        unoccupied_slots, room_capacities, semester_blocks = find_unoccupied_rooms(
            selected_days=selected_days,
            selected_rooms=selected_rooms,
            selected_time_slots=selected_time_slots,
            selected_term=selected_term,
            selected_session=selected_session
        )

        # Test room capacities
        self.assertEqual(room_capacities[(5, 103)], 30)
        self.assertEqual(room_capacities[(5, 104)], 25)

        # Test that room 103 is occupied MWF 9:30-10:45
        self.assertNotIn(
            (time(9, 30), time(10, 45)),
            unoccupied_slots[(5, 103)]['M']
        )

        # Test that room 103 is available MWF 11:00-12:15
        self.assertIn(
            (time(11, 0), time(12, 15)),
            unoccupied_slots[(5, 103)]['M']
        )

    def test_find_unoccupied_rooms_empty_selection(self):
        """Test find_unoccupied_rooms with no selections"""
        unoccupied_slots, room_capacities, semester_blocks = find_unoccupied_rooms()
        self.assertIsNotNone(unoccupied_slots)
        self.assertIsNotNone(room_capacities)
        self.assertIsNotNone(semester_blocks)

    def test_find_unoccupied_rooms_session_filtering(self):
        """Test that session dates are properly filtered"""
        selected_term = 20252
        selected_session = 2  # Session 2 ends on 2025-03-02

        unoccupied_slots, _, _ = find_unoccupied_rooms(
            selected_term=selected_term,
            selected_session=selected_session
        )

        # Verify that classes outside session dates are not included
        # This would depend on your test data

    def test_class_in_block(self):
        """Test class_in_block function with various scenarios"""
        # Class fully within block
        self.assertTrue(class_in_block(
            time(9, 30), time(10, 30),  # class time
            time(9, 0), time(11, 0)     # block time
        ))

        # Class overlapping start of block
        self.assertTrue(class_in_block(
            time(9, 0), time(10, 0),    # class time
            time(9, 30), time(10, 30)   # block time
        ))

        # Class overlapping end of block
        self.assertTrue(class_in_block(
            time(10, 0), time(11, 0),   # class time
            time(9, 30), time(10, 30)   # block time
        ))

        # Class completely outside block
        self.assertFalse(class_in_block(
            time(8, 0), time(9, 0),     # class time
            time(9, 30), time(10, 30)   # block time
        ))

    def test_expand_days(self):
        """Test expand_days function with various inputs"""
        # Test MWF
        result = expand_days("MWF")
        expected = pd.Series({
            'M': True, 'T': False, 'W': True,
            'R': False, 'F': True, 'S': False
        })
        pd.testing.assert_series_equal(result, expected)

        # Test empty string
        result = expand_days("")
        expected = pd.Series({
            'M': False, 'T': False, 'W': False,
            'R': False, 'F': False, 'S': False
        })
        pd.testing.assert_series_equal(result, expected)

        # Test None
        result = expand_days(None)
        expected = pd.Series({
            'M': False, 'T': False, 'W': False,
            'R': False, 'F': False, 'S': False
        })
        pd.testing.assert_series_equal(result, expected)

    def test_parse_time(self):
        """Test parse_time function with various inputs"""
        self.assertEqual(parse_time("09:30"), time(9, 30))
        self.assertEqual(parse_time("14:45"), time(14, 45))
        self.assertIsNone(parse_time("invalid"))
        self.assertIsNone(parse_time(None))
        self.assertIsNone(parse_time("25:00"))  # Invalid hour
        self.assertIsNone(parse_time("09:60"))  # Invalid minute

if __name__ == '__main__':
    unittest.main()
