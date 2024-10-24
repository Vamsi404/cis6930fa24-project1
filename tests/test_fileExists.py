import unittest
import os

class TestFileExistence(unittest.TestCase):

    def test_censoror_file_exists(self):
        file_path = './censoror.py'
        self.assertTrue(os.path.exists(file_path), f"File '{file_path}' does not exist.")

    def test_main_file_exists(self):
        file_path = './assignment1/main.py'
        self.assertTrue(os.path.exists(file_path), f"File '{file_path}' does not exist.")


if __name__ == "__main__":
    unittest.main()