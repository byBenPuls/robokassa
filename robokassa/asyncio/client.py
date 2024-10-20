from robokassa import HashAlgorithm
from robokassa.asyncio.connection import Requests
from robokassa.asyncio.merchant import AsyncMerchant
from robokassa.asyncio.payment import AsyncPayment
from robokassa.client import RobokassaAbstract
from robokassa.hash import Hash


class Robokassa(RobokassaAbstract):
    def __init__(
        self,
        merchant_login: str,
        password1: str,
        password2: str,
        algorithm: HashAlgorithm = HashAlgorithm.md5,
        is_test: bool = False,
        use_standard_naming_of_additional_link_params: bool = True,
    ) -> None:
        self._merchant_login = merchant_login
        self._password1 = password1
        self._password2 = password2
        self._is_test = is_test
        self._use_standard_naming = use_standard_naming_of_additional_link_params

        self._hash = Hash(algorithm)

        self.__http = Requests()

    @property
    def payments(self) -> AsyncPayment:
        return AsyncPayment(
            self.__http,
            is_test=self._is_test,
            merchant_login=self._merchant_login,
            password1=self._password1,
            password2=self._password2,
            hash_=self._hash,
        )

    async def get_currencies(self, language: str = "en") -> dict:
        return await AsyncMerchant(self.__http, self._merchant_login).get_currencies(language)
