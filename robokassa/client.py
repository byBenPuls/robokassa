from datetime import datetime
from typing import List, Optional, Union

from robokassa.connection import AUTH_BASE_URL, SERVICES_BASE_URL, Http
from robokassa.exceptions import (
    IncorrectUrlMethodError,
    RobokassaInterfaceError,
    UnusedParameterError,
    UnusedStrictUrlParameterError,
)
from robokassa.hash import Hash, HashAlgorithm
from robokassa.merchant import OperationStateChecker
from robokassa.payment import LinkGenerator
from robokassa.signature import SignatureChecker
from robokassa.types import (
    Culture,
    HTTPMethod,
    InvoiceType,
    PaymentDetails,
    PaymentMethod,
    RobokassaParams,
    RobokassaResponse,
)


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
    ) -> None:
        self._merchant_login = merchant_login
        self._password1 = password1
        self._password2 = password2
        self._algorithm = algorithm
        self._is_test = is_test

        self._hash = self._init_hash(self._algorithm)
        self._link_generator = self._init_link_generator()
        self._signature_checker = self._init_signature_checker()
        self._operation_state_checker = self._init_operation_state_checker()

    def _create_http(self, url: str) -> Http:
        return Http(url)

    def _init_hash(self, algorithm: HashAlgorithm) -> Hash:
        return Hash(algorithm)

    def _init_link_generator(self) -> LinkGenerator:
        return LinkGenerator(hash=self._hash, password_1=self._password1)

    def _init_signature_checker(self) -> SignatureChecker:
        return SignatureChecker(
            hash_=self._hash, password1=self._password1, password2=self._password2
        )

    def _init_operation_state_checker(self) -> OperationStateChecker:
        return OperationStateChecker(
            merchant_login=self._merchant_login,
            hash=self._hash,
            password_2=self._password2,
        )

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
    ) -> None:
        super().__init__(
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            algorithm=algorithm,
            is_test=is_test,
        )

    def generate_open_payment_link(
        self,
        out_sum: Union[float, int],
        default_prefix: str = "shp",
        result_url: Optional[str] = None,
        success_url: Optional[str] = None,
        success_url_method: Optional[HTTPMethod] = None,
        fail_url: Optional[str] = None,
        fail_url_method: Optional[HTTPMethod] = None,
        inv_id: int = 0,
        receipt: Optional[dict] = None,
        description: Optional[str] = None,
        recurring: bool = False,
        culture: Culture = Culture.RU,
        email: Optional[str] = None,
        expiration_date: Optional[datetime] = None,
        user_ip: Optional[str] = None,
        payment_methods: Optional[List[PaymentMethod]] = None,
        **kwargs,
    ) -> RobokassaResponse:
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

        available_http_methods = (HTTPMethod.GET, HTTPMethod.POST, None)

        if (success_url is not None) != (success_url_method is not None):
            raise UnusedStrictUrlParameterError(
                "If you use URL, you also need to choose a HTTP method"
            )
        if (
            success_url_method not in available_http_methods
            or fail_url_method not in available_http_methods
        ):
            raise IncorrectUrlMethodError("You can use only GET or POST methods")

        params = RobokassaParams(
            is_test=self._is_test,
            merchant_login=self._merchant_login,
            out_sum=out_sum,
            inv_id=inv_id,
            receipt=receipt,
            description=description,
            recurring=recurring,
            payment_methods=payment_methods,
            success_url=success_url,
            success_url_method=success_url_method,
            fail_url=fail_url,
            fail_url_method=fail_url_method,
            result_url=result_url,
            default_prefix=default_prefix,
            culture=culture,
            email=email,
            user_ip=user_ip,
            expiration_date=expiration_date,
            additional_params=kwargs,
        )
        return self._link_generator.generate_open_payment_link(params=params)

    def generate_subscription_link(
        self,
        inv_id: int,
        previous_inv_id: int,
        out_sum: int,
        receipt: Optional[dict] = None,
    ) -> RobokassaResponse:
        params = RobokassaParams(
            is_test=self._is_test,
            merchant_login=self._merchant_login,
            out_sum=out_sum,
            inv_id=inv_id,
            previous_inv_id=previous_inv_id,
            receipt=receipt,
        )
        return self._link_generator.generate_subscription_payment_link(params=params)

    async def generate_protected_payment_link(
        self,
        invoice_type: InvoiceType,
        out_sum: float,
        merchant_comments: str,
        default_prefix: str = "shp",
        result_url: Optional[str] = None,
        success_url: Optional[str] = None,
        success_url_method: Optional[HTTPMethod] = None,
        fail_url: Optional[str] = None,
        fail_url_method: Optional[HTTPMethod] = None,
        inv_id: int = 0,
        receipt: Optional[dict] = None,
        description: Optional[str] = None,
        recurring: bool = False,
        culture: Culture = Culture.RU,
        email: Optional[str] = None,
        expiration_date: Optional[datetime] = None,
        **kwargs,
    ) -> RobokassaResponse:
        """
        Generate payment link using JWT
        https://docs.robokassa.ru/pay-interface/#jwt


        :param invoice_type: Type of invoice
        :type invoice_type: InvoiceType
        :param out_sum: Out sum
        :type out_sum: float
        :param merchant_comments: Description for merchant
        :type merchant_comments: str
        :param default_prefix: Prefix: shp, Shp or SHP. Default: shp (use without `_`)
        :type default_prefix: str
        :param result_url: url
        :type result_url:
        :param success_url: url
        :type success_url: str
        :param success_url_method: Method: GET, POST
        :type success_url_method:
        :param fail_url: url
        :type fail_url: str
        :param fail_url_method: Method: GET, POST
        :type fail_url_method:
        :param inv_id: Invoice ID
        :type inv_id: int
        :param receipt: Receipt. See: https://docs.robokassa.ru/fiscalization/
        :type receipt: dict
        :param description: Description of payment page
        :type description: str
        :param recurring: Is recurring payment? See: https://docs.robokassa.ru/recurring/
        :type recurring: bool
        :param culture: Language of payment page
        :type culture: Culture
        :param email: User email
        :type email: str
        :param expiration_date: Datetime obj when link expire
        :type expiration_date:
        :param kwargs: additional payments params without shp_.
        :type kwargs:
        :return: RobokassaResponse
        :rtype: RobokassaResponse
        """

        if self.is_test:
            raise RobokassaInterfaceError(
                "generate_protected_payment_link is unavailable in Test mode"
            )

        available_http_methods = ("GET", "POST", None)

        if (success_url is not None) != (success_url_method is not None):
            raise UnusedStrictUrlParameterError(
                "If you use URL, you also need to choose a HTTP method"
            )

        if (
            success_url_method
            and fail_url_method
            and (
                success_url_method.value not in available_http_methods
                or fail_url_method.value not in available_http_methods
            )
        ):
            raise IncorrectUrlMethodError("You can use only GET or POST methods")

        params = RobokassaParams(
            is_test=self._is_test,
            merchant_login=self._merchant_login,
            out_sum=out_sum,
            inv_id=inv_id,
            receipt=receipt,
            description=description,
            recurring=recurring,
            merchant_comments=merchant_comments,
            invoice_type=invoice_type,
            success_url=success_url,
            success_url_method=success_url_method,
            fail_url=fail_url,
            fail_url_method=fail_url_method,
            result_url=result_url,
            default_prefix=default_prefix,
            culture=culture,
            email=email,
            expiration_date=expiration_date,
            additional_params=kwargs,
            _serialize_receipt=False,
        )

        return await self._link_generator.generate_protected_payment_link(
            http=self._create_http(SERVICES_BASE_URL),
            params=params,
        )

    async def deactivate_invoice(
        self,
        inv_id: Optional[int] = None,
        encoded_id: Optional[str] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        Deactivate invoice using invoiceId, Id or EncodedId

        :param inv_id: The account number specified by the seller when creating the link.
        :type inv_id:
        :param encoded_id: The last part of the invoice link.
        For example: https://auth.robokassa.ru/merchant/Invoice/6hucaX7-BkKNi4lyi-Iu2g.
        :type encoded_id: str
        :param id: The invoice ID is returned in response to an invoice request.
        :type id: str
        """

        if not inv_id and not encoded_id and not id:
            raise UnusedParameterError(
                "Provide inv_id or encoded_id or id of invoice for deactivation"
            )

        return await self._link_generator.deactivate_protected_payment_link(
            http=self._create_http(SERVICES_BASE_URL),
            merchant_login=self._merchant_login,
            inv_id=inv_id,
            encoded_id=encoded_id,
            id=id,
        )

    def is_redirect_valid(
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

        return self._signature_checker.success_or_fail_url_signature_is_valid(
            success_signature=signature, out_sum=out_sum, inv_id=inv_id, **kwargs
        )

    def is_result_notification_valid(
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

        return self._signature_checker.result_url_signature_is_valid(
            result_signature=signature, out_sum=out_sum, inv_id=inv_id, **kwargs
        )

    async def get_payment_details(self, inv_id: int) -> PaymentDetails:
        """
        Get details of operation by invoice ID

        :param inv_id: Invoice ID
        :type inv_id: int
        :return: Details of operation
        :rtype: PaymentDetails
        """

        return await self._operation_state_checker.get_state(
            http=self._create_http(AUTH_BASE_URL), inv_id=inv_id
        )
