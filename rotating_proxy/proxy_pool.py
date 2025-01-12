import random
import requests
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

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

class ProxyPool:
    def __init__(
        self, 
        proxies: List[str] = None, 
        test_url: str = 'https://httpbin.org/ip',
        max_consecutive_failures: int = 3,
        score_decay_factor: float = 0.9,
        recovery_threshold: float = 0.5
    ):
        """
        Initialize ProxyPool with advanced proxy management features.
        
        :param proxies: Initial list of proxies
        :param test_url: URL to test proxy connectivity
        :param max_consecutive_failures: Maximum consecutive failures before permanent blacklisting
        :param score_decay_factor: Factor to reduce proxy score on failure
        :param recovery_threshold: Minimum score to consider a proxy for recovery
        """
        self.proxies: Dict[str, ProxyMetrics] = {
            proxy: ProxyMetrics(url=proxy) for proxy in (proxies or [])
        }
        self.test_url = test_url
        self.max_consecutive_failures = max_consecutive_failures
        self.score_decay_factor = score_decay_factor
        self.recovery_threshold = recovery_threshold
        self.logger = logging.getLogger(__name__)

    def add_proxy(self, proxy: str):
        """Add a new proxy with initial metrics."""
        if proxy not in self.proxies:
            self.proxies[proxy] = ProxyMetrics(url=proxy)
            self.logger.info(f"Added new proxy: {proxy}")

    def remove_proxy(self, proxy: str):
        """Remove a proxy from the pool."""
        if proxy in self.proxies:
            del self.proxies[proxy]
            self.logger.info(f"Removed proxy: {proxy}")

    def _validate_proxy(self, proxy: str, timeout: float = 5.0) -> bool:
        """
        Advanced proxy validation with detailed metrics tracking.
        
        :param proxy: Proxy to validate
        :param timeout: Request timeout
        :return: Boolean indicating proxy validity
        """
        try:
            response = requests.get(
                self.test_url, 
                proxies={"http": proxy, "https": proxy}, 
                timeout=timeout
            )
            self.logger.info(f"Proxy {proxy} validation succeeded")
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Proxy {proxy} validation failed: {type(e).__name__}")
            # self.logger.warning(f"Proxy {proxy} validation failed: {e}")
            return False

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
            if self._validate_proxy(proxy)
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
            
            if self._validate_proxy(proxy):
                metrics = self.proxies[proxy]
                metrics.success_count += 1
                metrics.last_used = datetime.now()
                metrics.last_success = datetime.now()
                metrics.consecutive_failures = 0
                metrics.score = min(metrics.score * 1.1, 1.0)  # Reward successful proxy
                
                return proxy
            
            # Handle proxy failure
            metrics = self.proxies[proxy]
            metrics.failure_count += 1
            metrics.consecutive_failures += 1
            metrics.score *= self.score_decay_factor
            
            if metrics.consecutive_failures >= self.max_consecutive_failures:
                self.logger.warning(f"Proxy {proxy} permanently blacklisted")
        
        raise Exception("No working proxies available after multiple attempts")

    def get_proxy_stats(self) -> Dict[str, Dict]:
        """
        Retrieve comprehensive proxy statistics.
        
        :return: Dictionary of proxy metrics
        """
        return {
            proxy: {
                "success_rate": metrics.success_count / (metrics.success_count + metrics.failure_count + 1),
                "score": metrics.score,
                "last_used": metrics.last_used,
                "last_success": metrics.last_success
            }
            for proxy, metrics in self.proxies.items()
        }
