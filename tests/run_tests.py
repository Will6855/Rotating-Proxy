import unittest
import sys
import os
import logging

TEST_PROXIES = [
    'http://178.48.68.61:18080',     # Working proxy
    'http://invalid.proxy:8080',     # Definitely invalid proxy
    'http://another.invalid.proxy:3128'  # Another invalid proxy
]

def run_tests():
    logging.disable(logging.CRITICAL)
    # Add the project root directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Create a test loader and test runner
    test_loader = unittest.TestLoader()
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Discover and run all tests in the tests directory
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    
    # Run the tests
    result = test_runner.run(test_suite)
    
    # Return True if tests pass, False otherwise
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)