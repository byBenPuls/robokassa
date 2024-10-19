from typing import Optional

from httpx import AsyncClient

from robokassa.connection import BaseHttpConnection


class AsyncHttpConnection(BaseHttpConnection):
    def __init__(self, base_url: str = "") -> None:
        self.base_url: str = base_url

        self._async_client: Optional[AsyncClient] = None

    async def __aenter__(self) -> AsyncClient:
        self._async_client = AsyncClient(base_url=self.base_url)
        return self._async_client

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._async_client.aclose()


class Requests:
    _base_url = "https://auth.robokassa.ru/Merchant"
    connection = AsyncHttpConnection(base_url=_base_url)
