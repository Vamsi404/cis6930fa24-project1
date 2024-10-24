import unittest
import os

class TestFileExistence(unittest.TestCase):

    def test_censoror_file_exists(self):
        file_path = './Redactor.py'
        self.assertTrue(os.path.exists(file_path), f"File '{file_path}' does not exist.")

    def test_main_file_exists(self):
        # Use an absolute path
        file_path = os.path.abspath('./Redactor.py')
        self.assertTrue(os.path.exists(file_path), f"File '{file_path}' does not exist.")


if __name__ == "__main__":
    unittest.main()