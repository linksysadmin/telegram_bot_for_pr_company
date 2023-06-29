import os
import unittest

from services.file_handler import find_files


class TestFileHandler(unittest.TestCase):
    def test_find_files(self):
        abs_path = os.path.abspath('.')
        result = find_files(abs_path)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
