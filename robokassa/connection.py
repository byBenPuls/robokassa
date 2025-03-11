from httpx import AsyncClient


class Http(AsyncClient):
    def __init__(self, base_url: str, *args, **kwargs):
        super().__init__(base_url=base_url, *args, **kwargs)


AUTH_BASE_URL = "https://auth.robokassa.ru/Merchant"
SERVICES_BASE_URL = "https://services.robokassa.ru/InvoiceServiceWebApi/api"
