from typing import Optional, Union

from robokassa.connection import Requests
from robokassa.exceptions import (
    UnusedStrictUrlParameterError,
    IncorrectUrlMethodError,
)
from robokassa.hash import HashAlgorithm, Hash
from robokassa.merchant import Merchant
from robokassa.payment import Payment


class RobokassaAbstract:
    pass


class BaseRobokassa(RobokassaAbstract):
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
        self._algorithm = algorithm
        self._is_test = is_test

        self._use_standard_naming_of_additional_link_params = (
            use_standard_naming_of_additional_link_params
        )

        self._hash = self._init_hash(self._algorithm)

    def _init_hash(self, algorithm: HashAlgorithm) -> Hash:
        return Hash(algorithm)

    @property
    def merchant_login(self) -> str:
        return self._merchant_login

    @property
    def algorithm(self) -> HashAlgorithm:
        return self._algorithm

    @property
    def is_test(self) -> bool:
        return self._is_test

    def __repr__(self):
        return f"{self.__class__.__name__}(is_test={self.is_test})"


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
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            algorithm=algorithm,
            is_test=is_test,
            use_standard_naming_of_additional_link_params=use_standard_naming_of_additional_link_params,
        )

        self.__http = self._init_http_connection()

        self._payment = self._init_payment(
            http=self.__http,
            is_test=is_test,
            merchant_login=self.merchant_login,
            password1=self._password1,
            password2=self._password2,
            hash_=self._hash,
        )
        self._merchant = self._init_merchant(
            self.__http,
            self._merchant_login,
        )

        self._link = self._payment.link
        self._checker = self._payment.check

    def _init_merchant(
        self,
        http: Requests,
        merchant_login: str,
    ) -> Merchant:
        return Merchant(
            http=http,
            merchant_login=merchant_login,
        )

    def _init_payment(
        self,
        http: Requests,
        is_test: bool,
        merchant_login: str,
        password1: str,
        password2: str,
        hash_: Hash,
    ) -> Payment:
        return Payment(
            http=http,
            is_test=is_test,
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            hash_=hash_,
        )

    def _init_http_connection(self) -> Requests:
        return Requests()

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
        receipt: Optional[dict] = None,
        description: Optional[str] = None,
        recurring: bool = False,
        **kwargs,
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
        :param kwargs: Any additional params without `shp_` prefix
        :return: Link to payment page
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

        payment_link = self._link.generate_by_script(
            default_prefix=default_prefix,
            out_sum=out_sum,
            result_url=result_url,
            success_url=success_url,
            success_url_method=success_url_method,
            fail_url=fail_url,
            fail_url_method=fail_url_method,
            inv_id=inv_id,
            receipt=receipt,
            recurrent=recurring,
            description=description,
            **kwargs,
        )
        return payment_link

    def create_link_to_payment_page_by_invoice_id(
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
        return self._link.create_link_to_payment_page_by_invoice_id(
            inv_id=inv_id,
            out_sum=out_sum,
            receipt=receipt,
            description=description,
        )

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
            success_signature=signature, out_sum=out_sum, inv_id=inv_id, **kwargs
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
            signature=signature, out_sum=out_sum, inv_id=inv_id, **kwargs
        )

    def get_currencies(self, language: str = "en") -> dict:
        """
        Get available currencies of merchant.

        :param language: `ru` or `en`
        :return: dictionary of currencies
        """
        return self._merchant.get_currencies(language=language)

    # def get_operation_state(self, invoice_id: Union[str, int]) -> dict:
    #     signature = Signature(
    #         merchant_login=self._merchant_login,
    #         inv_id=invoice_id,
    #         password=self._password2,
    #         hash_=self._hash,
    #     )
    #     return self._merchant.get_operation_state(
    #         invoice_id=invoice_id, signature_value=signature.value
    #     )
