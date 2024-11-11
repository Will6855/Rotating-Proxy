import random
import requests
from typing import List

class ProxyPool:
    def __init__(self, proxies: List[str] = None, test_url: str = 'https://httpbin.org/ip'):
        self.proxies = proxies or []
        self.blacklist = []
        self.test_url = test_url
        
    def change_test_url(self, test_url: str):
        """Change the URL used to test the proxies."""
        self.test_url = test_url

    def add_proxy(self, proxy: str):
        """Add a proxy to the pool."""
        self.proxies.append(proxy)

    def remove_proxy(self, proxy: str):
        """Remove a proxy from the pool."""
        # self.proxies.remove(proxy)
        self.proxies = [p for p in self.proxies if p != proxy] # List comprehension should be faster than remove()

    def get_proxy(self) -> str:
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

    def is_proxy_working(self, proxy: str) -> bool:
        """Check if a proxy is working by making a test request."""
        try:
            response = requests.get(self.test_url, proxies={"http": proxy, "https": proxy}, timeout=2)
            return response.status_code == 200
        except Exception:
            # print(f"Proxy {proxy} is not working.")
            return False
        
    def filter_working_proxies(self):
        """Move non-working proxies to the blacklist."""
        working_proxies = []
        for proxy in self.proxies:
            if self.is_proxy_working(proxy):
                working_proxies.append(proxy)
            else:
                self.blacklist.append(proxy)
        self.proxies = working_proxies

    def rotate_proxy(self) -> str:
        """Get the next working proxy, rotate if necessary."""
        for _ in range(len(self.proxies)):
            proxy = self.get_proxy()
            if self.is_proxy_working(proxy):
                return proxy
            self.mark_proxy_failed(proxy)
        raise Exception("No working proxies available")
