import unittest
import sys
import os
import logging

# Add the project root directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rotating_proxy import ProxySession, ProxyPool
from run_tests import TEST_PROXIES

class TestProxySession(unittest.TestCase):
    def setUp(self):
        # Fetch some proxies for testing
        proxies = TEST_PROXIES
        self.proxy_pool = ProxyPool(proxies)
        self.proxy_pool.filter_working_proxies()
        
    def test_init(self):
        """
        Test ProxySession initialization
        """
        proxy_session = ProxySession(self.proxy_pool)
        self.assertIsNotNone(proxy_session)
        self.assertIsNotNone(proxy_session.current_proxy)

    def test_request(self):
        """
        Test making a request through the proxy session
        """
        proxy_session = ProxySession(self.proxy_pool)
        response = proxy_session.request("https://httpbin.org/ip", "GET")
        self.assertEqual(response.status_code, 200)
        
        # Verify IP is different (indicating proxy usage)
        ip = response.json().get('origin')
        self.assertIsNotNone(ip)

    def test_proxy_performance(self):
        """
        Test retrieving proxy performance metrics
        """
        proxy_session = ProxySession(self.proxy_pool)
        
        # Make a request to generate some metrics
        proxy_session.request("https://httpbin.org/ip", "GET")
        
        # Get performance metrics
        performance = proxy_session.get_proxy_performance()
        
        # Verify performance metrics
        self.assertIn('success_rate', performance)
        self.assertIn('score', performance)

if __name__ == '__main__':
    logging.disable(logging.CRITICAL)
    unittest.main()