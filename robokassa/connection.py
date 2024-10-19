from typing import Optional

from httpx import Client


class BaseHttpConnection:
    pass


class HttpConnection(BaseHttpConnection):
    def __init__(self, base_url: str = "") -> None:
        self.base_url: str = base_url

        self._sync_client: Optional[Client] = None

    def __enter__(self) -> Client:
        self._sync_client = Client(base_url=self.base_url)
        return self._sync_client

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._sync_client.close()


class Requests:
    _base_url = "https://auth.robokassa.ru/Merchant"
    connection = HttpConnection(base_url=_base_url)
