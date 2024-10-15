import unittest
from datetime import time
from find_unoccupied_rooms import (
    is_summer,
    class_in_block,
    expand_days,
    parse_time,
    find_unoccupied_rooms
)


class TestFindUnoccupiedRooms(unittest.TestCase):
    def setUp(self):
        # This method is called before each test
        # You can use it to set up any common test data
        pass

    def tearDown(self):
        # This method is called after each test
        # You can use it to clean up after tests
        pass

    def test_is_summer(self):
        self.assertTrue(is_summer(20233))
        self.assertFalse(is_summer(20231))
        self.assertFalse(is_summer(20232))

    def test_class_in_block(self):
        class_start = time(9, 0)
        class_end = time(10, 30)
        block_start = time(9, 30)
        block_end = time(10, 45)
        self.assertTrue(class_in_block(class_start, class_end, block_start, block_end))

        class_start = time(11, 0)
        class_end = time(12, 15)
        self.assertFalse(class_in_block(class_start, class_end, block_start, block_end))

    def test_expand_days(self):
        result = expand_days("MWF")
        expected = {"M": True, "T": False, "W": True, "R": False, "F": True, "S": False}
        self.assertEqual(result.to_dict(), expected)

    def test_parse_time(self):
        self.assertEqual(parse_time("09:30"), time(9, 30))
        self.assertEqual(parse_time("14:45"), time(14, 45))
        self.assertIsNone(parse_time("invalid"))

    def test_find_unoccupied_rooms(self):
        # This is a more complex function to test
        # You might want to create a mock CSV file or mock the pandas read_csv function
        # For now, we'll just check if the function runs without errors and returns the expected tuple
        result = find_unoccupied_rooms()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

if __name__ == '__main__':
    unittest.main()
