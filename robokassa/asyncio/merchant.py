from robokassa.asyncio.connection import Requests
from robokassa.utils import HttpResponseValidator


class AsyncMerchant:
    def __init__(self, http: Requests, merchant_login: str) -> None:
        self._http = http.connection

        self._merchant_login = merchant_login
        print(merchant_login)

    async def get_currencies(self, language: str) -> dict:
        async with self._http as conn:
            response = await conn.post(
                url="WebService/Service.asmx/GetCurrencies",
                data={
                    "MerchantLogin": self._merchant_login,
                    "Language": language,
                },
            )
            print(response.url)
            validated_response = HttpResponseValidator(
                response, False
            ).validate_http_response()
            return validated_response
