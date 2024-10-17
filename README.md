# Rotating Proxy

A Python package for managing and using rotating proxies.

## Installation

You can install the package using pip:

```bash
pip install rotating_proxy
```

## Usage
```python
from rotating_proxy import ProxyPool

# Example usage
pool = ProxyPool()
proxy = pool.rotate_proxy()
```
