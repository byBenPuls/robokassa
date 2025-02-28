from typing import Union, Any, Optional

from robokassa import HashAlgorithm
from robokassa.asyncio.connection import Requests
from robokassa.asyncio.merchant import AsyncMerchant
from robokassa.asyncio.payment import AsyncPayment
from robokassa.client import BaseRobokassa
from robokassa.exceptions import IncorrectUrlMethodError, UnusedStrictUrlParameterError
from robokassa.hash import Hash


class Robokassa(BaseRobokassa):
    def __init__(
        self,
        merchant_login: str,
        password1: str,
        password2: str,
        algorithm: HashAlgorithm = HashAlgorithm.md5,
        is_test: bool = False,
        use_standard_naming_of_additional_link_params: bool = True,
    ) -> None:
        super().__init__(
            merchant_login,
            password1,
            password2,
            algorithm,
            is_test,
            use_standard_naming_of_additional_link_params,
        )
        self._merchant_login = merchant_login
        self.__password1 = password1
        self.__password2 = password2
        self._is_test = is_test
        self._use_standard_naming = use_standard_naming_of_additional_link_params

        self.__http = self._init_http_connection()

        self._async_payment = self._init_async_payment(
            self.__http,
            is_test=self._is_test,
            merchant_login=self._merchant_login,
            password1=self.__password1,
            password2=self.__password2,
            hash_=self._hash,
        )
        self._async_merchant = self._init_async_merchant(
            self.__http, self._merchant_login
        )

        self._link = self._async_payment.link
        self._checker = self._async_payment.check

    def _init_http_connection(self):
        return Requests()

    def _init_async_payment(
        self,
        http: Requests,
        is_test: bool,
        merchant_login: str,
        password1: str,
        password2: str,
        hash_: Hash,
    ) -> AsyncPayment:
        return AsyncPayment(
            http=http,
            is_test=is_test,
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            hash_=hash_,
        )

    def _init_async_merchant(
        self,
        http: Requests,
        merchant_login: str,
    ) -> AsyncMerchant:
        return AsyncMerchant(http=http, merchant_login=merchant_login)

    def create_link_to_payment_page_by_script(
        self,
        out_sum: float,
        default_prefix: str = "shp",
        result_url: Optional[str] = None,
        success_url: Optional[str] = None,
        success_url_method: Optional[str] = None,
        fail_url: Optional[str] = None,
        fail_url_method: Optional[str] = None,
        inv_id: Optional[int] = 0,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Create a link to payment page by common params with signature.
        Link of this method will look like:


        `https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin=demo&OutSum=1&SignatureValue=2c113e992e2c985e43e`

        All link params user can see, but cannot edit them.
        If you want to hide these params you need to use by invoice ID method.


        :param out_sum:
        :param default_prefix: `shp` or `Shp` or `SHP` prefix for additional params
        :param result_url: ResultUrl2
        :param success_url: SuccessUrl2
        :param success_url_method: SuccessUrlMethod2
        :param fail_url: FailUrl2
        :param fail_url_method: FailUrlMethod2
        :param inv_id:
        :param description: Shop description
        :param kwargs: any additional params without `shp_` prefix
        :return: link to payment page
        """
        available_http_methods = ("GET", "POST", None)

        if (success_url is not None) != (success_url_method is not None):
            raise UnusedStrictUrlParameterError(
                "If you use URL, you also need to choose a HTTP method"
            )
        if (
            success_url_method not in available_http_methods
            or fail_url_method not in available_http_methods
        ):
            raise IncorrectUrlMethodError("You can use only GET or POST methods")

        return self._link.generate_by_script(
            out_sum=out_sum,
            default_prefix=default_prefix,
            result_url=result_url,
            success_url=success_url,
            success_url_method=success_url_method,
            fail_url=fail_url,
            fail_url_method=fail_url_method,
            inv_id=inv_id,
            description=description,
            **kwargs,
        )

    async def create_link_to_payment_page_by_invoice_id(
        self,
        inv_id: Optional[Union[str, int]],
        out_sum: Union[str, int, float],
        description: str,
        receipt: Optional[dict] = None,
    ) -> str:
        """
        Create a link to payment page by invoice ID.
        It is mean what params will hide.

        Link of this method will look like:

        `https://auth.robokassa.ru/Merchant/Index/41734593-dc97-dc5f-d329-a73158e4cb29`


        :param inv_id:
        :param out_sum:
        :param description: Shop description
        :return: Url to payment page
        """
        return await self._link.create_by_invoice_id(
            inv_id=inv_id,
            receipt=receipt,
            out_sum=out_sum,
            description=description,
        )

    async def get_currencies(self, language: str = "en") -> dict:
        """
        Get available currencies of merchant.

        :param language: `ru` or `en`
        :return: dictionary of currencies
        """
        return await self._async_merchant.get_currencies(language)

    def success_or_fail_signature_is_valid(
        self,
        signature: str,
        out_sum: Union[str, int, float],
        inv_id: Optional[Union[str, int]],
        **kwargs,
    ) -> bool:
        """
        Check success or fail signature is valid.

        :param signature: Output signature
        :param out_sum:
        :param inv_id:
        :param kwargs: Additional params with `shp_` prefix
        :return: True if signature is valid, else False
        """
        return self._checker.success_or_fail_url_signature_is_valid(
            signature=signature, out_sum=out_sum, inv_id=inv_id, **kwargs
        )

    def result_signature_is_valid(
        self,
        signature: str,
        out_sum: Union[str, int, float],
        inv_id: Optional[Union[str, int]],
        **kwargs,
    ) -> bool:
        """
        Check result signature is valid.

        :param signature: Output signature
        :param out_sum:
        :param inv_id:
        :param kwargs: Additional params with `shp_` prefix
        :return: True if signature is valid, else False
        """
        return self._checker.result_url_signature_is_valid(
            result_signature=signature, out_sum=out_sum, inv_id=inv_id, **kwargs
        )
