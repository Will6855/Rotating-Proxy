import unittest
import sys
import os

# Add the project root directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rotating_proxy import ProxyPool

class TestProxyPool(unittest.TestCase):
    def test_add_and_remove_proxy(self):
        pool = ProxyPool()
        proxy = 'http://67.43.227.227:9189'
        pool.add_proxy(proxy)
        self.assertEqual(len(pool.proxies), 1)
        pool.remove_proxy(proxy)
        self.assertEqual(len(pool.proxies), 0)

    def test_rotate_proxy(self):
        pool = ProxyPool(['http://67.43.227.227:9189', 'http://131.153.187.5:50689'])
        
        # Test rotation - it should return a proxy that is in the pool
        print(pool.get_proxy())
        proxy = pool.rotate_proxy()
        self.assertIn(proxy, pool.proxies)

    def test_is_proxy_working(self):
        pool = ProxyPool(['http://67.43.227.227:9189', 'http://131.153.187.5:50689'])
        
        # In a real test, you would mock the requests.get call to not rely on actual proxies
        # Here, we will just assume one proxy is working and one is not for demonstration
        # You should use unittest.mock to patch requests.get in real scenarios.
        working_proxy = pool.is_proxy_working('http://67.43.227.227:9189')
        self.assertIsInstance(working_proxy, bool)  # It should return True or False

if __name__ == '__main__':
    unittest.main()
