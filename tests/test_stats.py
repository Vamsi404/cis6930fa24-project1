import unittest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Add parent directory to Python path
from assignment1.main import generate_statistics

class TestGenerateStatistics(unittest.TestCase):
    
    def test_generate_statistics(self):
        #initial values test
        statistics = generate_statistics()

        # Assert that statistics are generated correctly
        self.assertTrue(statistics["Names"] >= 0)
        self.assertTrue(statistics["Address and Country"] >= 0)
        self.assertTrue(statistics["Date"] >= 0)
        self.assertTrue(statistics["Phone Numbers or Important Numbers"] >= 0)

    # Additional test cases can be added here

if __name__ == '__main__':
    unittest.main()