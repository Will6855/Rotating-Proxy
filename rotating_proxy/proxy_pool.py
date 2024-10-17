import random
import requests
from typing import Dict, List

class ProxyPool:
    def __init__(self, proxies: List[Dict[str, str]] = None):
        self.proxies = proxies or []
        self.blacklist = []

    def add_proxy(self, proxy: Dict[str, str]):
        """Add a proxy to the pool."""
        self.proxies.append(proxy)

    def remove_proxy(self, proxy: Dict[str, str]):
        """Remove a proxy from the pool."""
        # self.proxies.remove(proxy)
        self.proxies = [p for p in self.proxies if p != proxy] # List comprehension should be faster than remove()

    def get_proxy(self) -> Dict[str, str]:
        """Get a proxy."""
        proxies = [p for p in self.proxies if p not in self.blacklist]
        if proxies:
            return random.choice(proxies)
        raise Exception("No proxies available")

    def mark_proxy_failed(self, proxy: str):
        """Add a proxy to the blacklist."""
        self.blacklist.append(proxy)
        
    def recover_blacklisted_proxies(self):
        """Re-check blacklisted proxies and recover them if they are working."""
        for proxy in self.blacklist:
            if self.is_proxy_working(proxy):
                # self.blacklist.remove(proxy)
                self.blacklist = [p for p in self.blacklist if p != proxy] # List comprehension should be faster than remove()

    def is_proxy_working(self, proxy: Dict[str, str], test_url: str = 'https://httpbin.org/ip') -> bool:
        """Check if a proxy is working by making a test request."""
        try:
            response = requests.get(test_url, proxies=proxy, timeout=2)
            return response.status_code == 200
        except Exception:
            # print(f"Proxy {proxy} is not working.")
            return False

    def rotate_proxy(self) -> Dict[str, str]:
        """Get the next working proxy, rotate if necessary."""
        for _ in range(len(self.proxies)):
            proxy = self.get_proxy()
            if self.is_proxy_working(proxy):
                return proxy
            self.mark_proxy_failed(proxy)
        raise Exception("No working proxies available")
