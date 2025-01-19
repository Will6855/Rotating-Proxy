import random
import requests
import logging
import threading
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class ProxyMetrics:
    """Tracks detailed metrics for each proxy."""
    url: str
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    score: float = 1.0
    consecutive_failures: int = 0
    authentication: Optional[Tuple[str, str]] = None  # username, password
    last_health_check: Optional[datetime] = None

class ProxyPool:
    def __init__(
        self, 
        proxies: List[str] = None, 
        test_url: str = 'https://httpbin.org/ip',
        max_consecutive_failures: int = 3,
        score_decay_factor: float = 0.9,
        recovery_threshold: float = 0.5,
        health_check_interval: int = 300  # 5 minutes
    ):
        """
        Initialize ProxyPool with advanced proxy management features.
        
        :param proxies: Initial list of proxies with optional authentication
        :param test_url: URL to test proxy connectivity
        :param max_consecutive_failures: Maximum consecutive failures before permanent blacklisting
        :param score_decay_factor: Factor to reduce proxy score on failure
        :param recovery_threshold: Minimum score to consider a proxy for recovery
        :param health_check_interval: Interval between health checks in seconds
        """
        # Initialize logger BEFORE using it
        self.logger = logging.getLogger(__name__)

        self.proxies: Dict[str, ProxyMetrics] = {}
        
        # Support proxies with authentication
        for proxy in (proxies or []):
            if '@' in proxy:
                auth, proxy_url = proxy.split('@')
                username, password = auth.split(':')
                self.add_proxy(proxy_url, authentication=(username, password))
            else:
                self.add_proxy(proxy)
        
        self.test_url = test_url
        self.max_consecutive_failures = max_consecutive_failures
        self.score_decay_factor = score_decay_factor
        self.recovery_threshold = recovery_threshold
        self.health_check_interval = health_check_interval
        
        # Start periodic health check thread
        self.health_check_thread = threading.Thread(target=self._periodic_health_check, daemon=True)
        self.health_check_thread.start()

    def add_proxy(self, proxy: str, authentication: Optional[Tuple[str, str]] = None):
        """
        Add a new proxy with initial metrics and optional authentication.
        
        :param proxy: Proxy URL
        :param authentication: Optional (username, password) tuple
        """
        if proxy not in self.proxies:
            metrics = ProxyMetrics(url=proxy, authentication=authentication)
            self.proxies[proxy] = metrics
            self.logger.info(f"Added new proxy: {proxy}")

    def _periodic_health_check(self):
        """
        Periodically check and update proxy health in the background.
        """
        while True:
            try:
                current_time = datetime.now()
                for proxy, metrics in list(self.proxies.items()):
                    # Only check proxies not recently checked
                    if (not metrics.last_health_check or 
                        current_time - metrics.last_health_check > timedelta(seconds=self.health_check_interval)):
                        
                        # Validate proxy and update metrics
                        proxies_dict = {"http": proxy, "https": proxy}
                        if metrics.authentication:
                            username, password = metrics.authentication
                            proxies_dict = {
                                "http": f"http://{username}:{password}@{proxy}",
                                "https": f"https://{username}:{password}@{proxy}"
                            }
                        
                        self._validate_proxy(proxy, proxies_dict)
                        metrics.last_health_check = current_time
            
            except Exception as e:
                self.logger.error(f"Error in periodic health check: {e}")
            
            time.sleep(self.health_check_interval)

    def _validate_proxy(self, proxy: str, proxies_dict: Dict[str, str], timeout: float = 5.0) -> bool:
        """
        Advanced proxy validation with detailed metrics tracking.
        
        :param proxy: Proxy to validate
        :param proxies_dict: Proxy dictionary with optional authentication
        :param timeout: Request timeout
        :return: Boolean indicating proxy validity
        """
        metrics = self.proxies[proxy]
        try:
            response = requests.get(
                self.test_url, 
                proxies=proxies_dict, 
                timeout=timeout
            )
            self.logger.info(f"Proxy {proxy} validation succeeded")

            # Metrics update on success
            metrics.success_count += 1
            metrics.last_used = datetime.now()
            metrics.last_success = datetime.now()
            metrics.consecutive_failures = 0
            metrics.score = min(metrics.score * 1.1, 1.0)  # Reward successful proxy

            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Proxy {proxy} validation failed: {type(e).__name__}")

            # Metrics update on failure
            metrics.last_used = datetime.now()
            metrics.score *= self.score_decay_factor
            metrics.failure_count += 1
            metrics.consecutive_failures += 1
            
            if metrics.consecutive_failures >= self.max_consecutive_failures:
                self.logger.warning(f"Proxy {proxy} permanently blacklisted")
                self.remove_proxy(proxy)
            return False

    def remove_proxy(self, proxy: str):
        """Remove a proxy from the pool."""
        if proxy in self.proxies:
            del self.proxies[proxy]
            self.logger.info(f"Removed proxy: {proxy}")

    def filter_working_proxies(self, proxies: Optional[List[str]] = None) -> Dict[str, ProxyMetrics]:
        """
        Validate and filter working proxies.
        
        :param proxies: Optional list of proxies to filter. 
                        If None, uses existing proxies in the pool.
        :return: Dictionary of working proxies with their metrics
        """
        # Use provided proxies or existing pool proxies
        proxy_list = proxies or list(self.proxies.keys())
        
        # Filter working proxies
        working_proxies = {
            proxy: self.proxies[proxy] 
            for proxy in proxy_list 
            if self._validate_proxy(proxy, {"http": proxy, "https": proxy})
        }
        
        # Log the filtering results
        self.logger.info(f"Filtered proxies: {len(working_proxies)} working out of {len(proxy_list)} total")
        
        # Update the proxy pool
        self.proxies = working_proxies
        
        return working_proxies

    def get_best_proxy(self) -> Optional[str]:
        """
        Select the best proxy based on scoring and metrics.
        
        :return: Best available proxy or None
        """
        valid_proxies = [
            proxy for proxy, metrics in self.proxies.items() 
            if metrics.score > self.recovery_threshold and 
               metrics.consecutive_failures < self.max_consecutive_failures
        ]
        
        if not valid_proxies:
            return None
        
        # Weight selection by proxy score
        weighted_proxies = [
            (proxy, self.proxies[proxy].score) for proxy in valid_proxies
        ]
        
        return random.choices(
            [p[0] for p in weighted_proxies], 
            weights=[p[1] for p in weighted_proxies]
        )[0]

    def rotate_proxy(self) -> str:
        """
        Rotate to the next best proxy with advanced selection logic.
        
        :return: Selected proxy
        :raises Exception: If no proxies are available
        """
        for _ in range(len(self.proxies)):
            proxy = self.get_best_proxy()
            
            if not proxy:
                raise Exception("No working proxies available")
            
            if self._validate_proxy(proxy, {"http": proxy, "https": proxy}):
                
                return proxy
            
            if self.proxies[proxy].consecutive_failures >= self.max_consecutive_failures:
                self.logger.warning(f"Proxy {proxy} permanently blacklisted")
        
        raise Exception("No working proxies available after multiple attempts")

    def get_proxy_stats(self) -> Dict[str, Dict]:
        """
        Retrieve comprehensive proxy statistics.
        
        :return: Dictionary of proxy metrics
        """
        return {
            proxy: {
                "success_rate": self.proxies[proxy].success_count / (self.proxies[proxy].success_count + self.proxies[proxy].failure_count + 1),
                "score": self.proxies[proxy].score,
                "last_used": self.proxies[proxy].last_used,
                "last_success": self.proxies[proxy].last_success
            }
            for proxy in self.proxies
        }

    def change_test_url(self, new_test_url: str):
        """
        Change the URL used for proxy validation.
        
        :param new_test_url: New URL to use for testing proxy connectivity
        :raises ValueError: If the new URL is not a valid HTTP/HTTPS URL
        """
        if not new_test_url.startswith(('http://', 'https://')):
            raise ValueError("Test URL must start with http:// or https://")

        self.logger.info(f"Changing test URL from {self.test_url} to {new_test_url}")
        self.test_url = new_test_url
