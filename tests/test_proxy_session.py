# import asyncio
import unittest
import sys
import os

# Add the project root directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rotating_proxy import ProxySession, ProxyPool

class TestProxySession(unittest.TestCase):
    def setUp(self):
        self.proxy_pool = ProxyPool([{'http': '23.94.136.205:80'},
            {'http': '67.43.228.254:14955'},
            {'http': '65.108.207.6:80'}])
        
    def test_init(self):
        proxy_session = ProxySession(self.proxy_pool)
        self.assertIsNotNone(proxy_session)

    def test_request(self):
        proxy_session = ProxySession(self.proxy_pool)
        response = proxy_session.request("https://httpbin.org/ip", "GET")
        self.assertEqual(response.status_code, 200)

    # def test_async_request(self):
    #     async def test_async():
    #         proxy_session = ProxySession(self.proxy_pool)
    #         response = await proxy_session.async_request("https://httpbin.org/ip", "GET")
    #         self.assertEqual(response.status, 200)
    #     asyncio.run(test_async())

if __name__ == '__main__':
    unittest.main()
