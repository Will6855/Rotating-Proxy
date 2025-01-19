# Rotating Proxy
![GitHub Release](https://img.shields.io/github/v/release/Will6855/rotating-proxy)
![PyPI Downloads](https://static.pepy.tech/badge/rotating-proxy)

A Python package for managing and utilizing rotating proxies effectively. This module provides a simple and efficient way to handle multiple proxies, automatically switching between them to enhance web scraping or any HTTP requests that require anonymity.

## Features

- Proxy Pool Management: Easily add, remove, and manage a list of proxies.
- Automatic Proxy Rotation: Automatically rotates through working proxies to ensure seamless web requests.
- Proxy Testing: Verifies the functionality of each proxy before use, maintaining a blacklist of failed proxies.
- Support for HTTP and SOCKS proxies: Works with different types of proxies to meet your needs.
- Advanced Proxy Metrics: Track proxy performance with detailed success and failure metrics.
- Proxy Authentication: Support for authenticated proxies
- Background Health Checks: Periodic validation of proxy health
- Exponential Backoff: Intelligent retry mechanism for network requests
- Dynamic Test URL: Ability to change proxy validation URL

## Requirements

- Python 3.9+
- Dependencies:
  - requests
  - typing
  - python-dateutil
  - urllib3
  - dataclasses (for Python < 3.7)

## Installation

You can install the package using pip:

```bash
pip install rotating-proxy
```

## Usage

```python
from rotating_proxy import ProxyPool, ProxySession

class Project:
    def __init__(self):
        # Initialize the proxy pool with proxies, including authentication support
        self.proxy_pool = ProxyPool([
            "http://username:password@proxy1:port",
            "http://proxy2:port"
        ])
        
        # Optional: Change test URL for proxy validation
        self.proxy_pool.change_test_url('https://api.ipify.org')
        
        # Filter and validate working proxies
        self.proxy_pool.filter_working_proxies()

        # Create proxy session with custom configuration
        self.proxy_session = ProxySession(
            self.proxy_pool, 
            timeout=15, 
            max_retries=3,
            default_headers={'User-Agent': 'MyCustomUserAgent'}
        )

    def request_function(self, **kwargs):
        try:
            response = self.proxy_session.request(**kwargs)   
            print(f"IP Address: {response.json()['origin']}")
            
            # Get proxy performance metrics
            metrics = self.proxy_session.get_proxy_performance()
            print(f"Proxy Performance: {metrics}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    project = Project()
    project.request_function(url="https://httpbin.org/ip", method="GET")
```

## Advanced Features

### Proxy Metrics
The `ProxyMetrics` class tracks detailed information about each proxy:
- Success and failure counts
- Last used and last successful timestamps
- Proxy score
- Consecutive failures

### Customization
- Configurable timeout and retry settings
- SSL verification options
- Logging for tracking proxy performance

## Contributing

Contributions are welcome! If you have suggestions for improvements or additional features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Recent Updates

- Added support for advanced proxy metrics
- Improved dependency management
- Enhanced error handling and logging
- Expanded Python version compatibility
