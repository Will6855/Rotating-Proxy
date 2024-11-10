import requests
from rotating_proxy import ProxyPool

import requests
# import aiohttp

class ProxySession:
    def __init__(self, pool: ProxyPool):
        self.pool = pool
        self.current_proxy = self.pool.rotate_proxy()
        self.session = requests.Session()

    def request(self, url: str, method: str = 'GET', tries: int = 3, **kwargs) -> requests.Response:
        """
        Make an HTTP request using a rotating proxy from the pool.

        Args:
            url (str): The URL to send the request to.
            method (str): The HTTP method to use for the request (default is 'GET').
            tries (int): The number of attempts to make the request with different proxies (default is 3).
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            requests.Response: The response object resulting from the request.

        Raises:
            Exception: If all attempts to make the request fail.
        """
        for _ in range(tries):
            self.session.proxies.update(self.current_proxy)
            try:
                response = self.session.request(method, url, **kwargs)
                return response
            except requests.RequestException as e:
                print(f"Try {_+1}: Error making request with proxy {self.current_proxy}: {e}")
                self.current_proxy = self.pool.rotate_proxy()
        raise Exception("All attempts to make the request failed.")


    # async def async_request(self, url: str, method: str = 'GET', tries: int = 3, **kwargs) -> requests.Response:
    #     """
    #     Make an asynchronous HTTP request using a rotating proxy from the pool.

    #     Args:
    #         url (str): The URL to send the request to.
    #         method (str): The HTTP method to use for the request (default is 'GET').
    #         tries (int): The number of attempts to make the request with different proxies (default is 3).
    #         **kwargs: Additional keyword arguments to pass to the request.

    #     Returns:
    #         aiohttp.ClientResponse: The response object resulting from the request.

    #     Raises:
    #         Exception: If all attempts to make the request fail.
    #     """
    #     async with aiohttp.ClientSession() as session:
    #         for _ in range(tries):
    #             protocol, ip = next(iter(self.current_proxy.items()))
    #             proxy_str = f"{protocol}://{ip}"
    #             try:
    #                 async with session.request(method, url, proxy=proxy_str, **kwargs) as response:
    #                     return response
    #             except aiohttp.ClientError as e:
    #                 print(f"Try {_+1}: Error making request with proxy {self.current_proxy}: {e}")
    #                 self.current_proxy = self.pool.rotate_proxy()
    #     raise Exception("All attempts to make the request failed.")
