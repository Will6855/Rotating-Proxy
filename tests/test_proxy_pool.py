import unittest
import sys
import os
import logging

# Add the project root directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rotating_proxy import ProxyPool
from run_tests import TEST_PROXIES

class TestProxyPool(unittest.TestCase):
    def setUp(self):
        # Use a mix of working and non-working proxies for testing
        self.test_proxies = TEST_PROXIES
        
    def test_filter_working_proxies(self):
        """
        Test the filter_working_proxies method
        Checks that only valid proxies are kept in the pool
        """
        proxy_pool = ProxyPool(self.test_proxies)
        
        # Filter working proxies
        filtered_proxies = proxy_pool.filter_working_proxies()
        
        # Validate the filtering process
        self.assertIsInstance(filtered_proxies, dict)
        
        # Verify that only one valid proxy remains
        self.assertTrue(len(filtered_proxies) == 1)
        
        # Verify that the proxy pool is updated
        self.assertEqual(len(proxy_pool.proxies), len(filtered_proxies))

    def test_filter_working_proxies_empty_input(self):
        """
        Test filtering with an empty proxy list
        """
        proxy_pool = ProxyPool([])
        filtered_proxies = proxy_pool.filter_working_proxies()
        
        self.assertEqual(len(filtered_proxies), 0)

    def test_proxy_pool_initialization(self):
        """
        Test ProxyPool initialization with various inputs
        """
        # Empty list
        pool1 = ProxyPool([])
        self.assertEqual(len(pool1.proxies), 0)
        
        # Single proxy
        pool2 = ProxyPool(['http://example.proxy:8080'])
        self.assertEqual(len(pool2.proxies), 1)
        
        # Multiple proxies
        pool3 = ProxyPool(self.test_proxies)
        self.assertEqual(len(pool3.proxies), len(self.test_proxies))

if __name__ == '__main__':
    logging.disable(logging.CRITICAL)
    unittest.main()