# Rotating Proxy

A Python package for managing and utilizing rotating proxies effectively. This module provides a simple and efficient way to handle multiple proxies, automatically switching between them to enhance web scraping or any HTTP requests that require anonymity.
## Features

- Proxy Pool Management: Easily add, remove, and manage a list of proxies.
- Automatic Proxy Rotation: Automatically rotates through working proxies to ensure seamless web requests.
- Proxy Testing: Verifies the functionality of each proxy before use, maintaining a blacklist of failed proxies.
- Support for HTTP and SOCKS proxies: Works with different types of proxies to meet your needs.

## Installation

You can install the package using pip:

```bash
pip install rotating_proxy
```

## Usage

```python
from rotating_proxy import ProxyPool

# Create a ProxyPool instance with your proxies
pool = ProxyPool([{'http': '192.140.42.83:31511'}, {'http': '131.153.187.5:50689'}])

# Get a working proxy
proxy = pool.rotate_proxy()

# Use the proxy for your requests
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or additional features, feel free to open an issue or submit a pull request.

This project is licensed under the MIT License. See the LICENSE file for details.
