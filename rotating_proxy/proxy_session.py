import logging
import requests
import time
from typing import Dict, Any, Optional
from requests.exceptions import RequestException, ConnectionError, Timeout
from rotating_proxy import ProxyPool
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProxySession:
    def __init__(
        self, 
        pool: ProxyPool, 
        timeout: int = 10, 
        max_retries: int = 3,
        verify_ssl: bool = True,
        default_headers: Optional[Dict[str, str]] = None,
        retry_backoff_factor: float = 0.3,
    ):
        """
        Initialize a ProxySession with advanced configuration.

        :param pool: ProxyPool instance for managing proxies
        :param timeout: Request timeout in seconds
        :param max_retries: Maximum number of retry attempts
        :param verify_ssl: Whether to verify SSL certificates
        :param default_headers: Default headers to use for all requests
        :param retry_backoff_factor: Exponential backoff factor for retries
        """
        self.pool = pool
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self.default_headers = default_headers or {}
        self.retry_backoff_factor = retry_backoff_factor
        
        self.logger = logging.getLogger(__name__)
        
        # Configure retry strategy
        self.retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Initialize session and first proxy
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update(self.default_headers)
        
        # Adapter with retry strategy
        adapter = requests.adapters.HTTPAdapter(max_retries=self.retry_strategy)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.current_proxy = self._get_initial_proxy()

    def _get_initial_proxy(self) -> str:
        """
        Get the initial proxy, with robust error handling.
        
        :return: A valid proxy from the pool
        :raises Exception: If no proxy is available
        """
        try:
            return self.pool.rotate_proxy()
        except Exception as e:
            self.logger.error(f"Failed to get initial proxy: {e}")
            raise

    def _update_proxy_settings(self, proxy: str):
        """
        Update session proxy settings with protocol support.
        
        :param proxy: Proxy URL to use
        """
        proxies = {}
        for protocol in self.proxy_protocols:
            proxies[protocol] = proxy
        
        self.session.proxies.update(proxies)
        self.current_proxy = proxy

    def request(
        self, 
        url: str, 
        method: str = 'GET', 
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request using a rotating proxy with advanced error handling.

        :param url: The URL to send the request to
        :param method: HTTP method to use (default is 'GET')
        :param headers: Optional headers for this specific request
        :param kwargs: Additional keyword arguments for requests
        :return: Response object
        :raises RequestException: If all attempts fail
        """
        # Merge default and request-specific headers
        request_headers = {**self.default_headers, **(headers or {})}
        
        # Merge default parameters with user-provided kwargs
        request_kwargs = {
            'timeout': self.timeout,
            'verify': self.verify_ssl,
            'headers': request_headers,
            **kwargs
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Request attempt {attempt} using proxy: {self.current_proxy}")
                
                proxies = {"http": self.current_proxy, "https": self.current_proxy}
                request_kwargs['proxies'] = proxies
                
                response = self.session.request(method, url, **request_kwargs)
                
                # Ensure the response is fully read and the connection is closed
                response.content
                
                # Log successful request
                self.logger.info(f"Successful request to {url} with proxy {self.current_proxy}")
                
                return response

            except (RequestException, ConnectionError, Timeout) as e:
                self.logger.warning(
                    f"Request failed (Attempt {attempt}/{self.max_retries}): "
                    f"Proxy {self.current_proxy}, Error: {e}"
                )
                
                # Exponential backoff
                if attempt < self.max_retries:
                    time.sleep(self.retry_backoff_factor * (2 ** (attempt - 1)))
                
                # Rotate to a new proxy on failure
                try:
                    self.current_proxy = self.pool.rotate_proxy()
                except Exception:
                    if attempt == self.max_retries:
                        raise RequestException(f"All proxy attempts failed")

    def get_proxy_performance(self, proxy: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve performance metrics for a specific proxy or the current proxy.
        
        :param proxy: Optional proxy to get stats for. If None, uses current proxy.
        :return: Dictionary of proxy performance metrics
        """
        stats = self.pool.get_proxy_stats()
        
        # If no proxy specified, use current proxy
        if proxy is None:
            proxy = self.current_proxy
        
        return stats.get(proxy, {})

    def __del__(self):
        """Ensure session is closed when the object is deleted"""
        if hasattr(self, 'session'):
            self.session.close()

    def close(self):
        """Close the current session and release resources."""
        self.session.close()
        self.logger.info("ProxySession closed")

    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point, ensures session is closed."""
        self.close()
