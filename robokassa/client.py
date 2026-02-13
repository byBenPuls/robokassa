from datetime import datetime
from typing import List, Optional, Union

from robokassa.connection import AUTH_BASE_URL, REFUND_BASE_URL, SERVICES_BASE_URL, Http
from robokassa.exceptions import (
    IncorrectUrlMethodError,
    RobokassaInterfaceError,
    RobokassaRequestError,
    UnusedParameterError,
    UnusedStrictUrlParameterError,
)
from robokassa.hash import Hash, HashAlgorithm
from robokassa.merchant import OperationStateChecker
from robokassa.payment import LinkGenerator
from robokassa.refund import RefundManager
from robokassa.signature import SignatureChecker
from robokassa.types import (
    Culture,
    HTTPMethod,
    InvoiceItem,
    InvoiceType,
    PaymentDetails,
    PaymentMethod,
    RefundHashAlgorithm,
    RefundRequest,
    RefundResponse,
    RefundStateResponse,
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

    def _init_refund_manager(self) -> Optional[RefundManager]:
        """
        Инициализация менеджера возврата, если настроен Password3.
        
        :return: RefundManager или None если Password3 не настроен
        """
        if not self._password3:
            return None
        return RefundManager(password3=self._password3, jwt_algorithm=self._jwt_algorithm)

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
        password3: Optional[str] = None,
        algorithm: HashAlgorithm = HashAlgorithm.md5,
        refund_algorithm: RefundHashAlgorithm = RefundHashAlgorithm.HS256,
        is_test: bool = False,
    ) -> None:
        super().__init__(
            merchant_login=merchant_login,
            password1=password1,
            password2=password2,
            algorithm=algorithm,
            is_test=is_test,
        )
        self._password3 = password3
        self._refund_algorithm = refund_algorithm
        self._refund_manager = self._init_refund_manager() if password3 else None

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

    async def refund_op(
        self,
        op_key: str,
        refund_sum: Optional[float] = None,
        invoice_items: Optional[List[InvoiceItem]] = None,
    ) -> RefundResponse:
        """
        Инициировать возврат по операции.

        Этот метод позволяет создать запрос на полный или частичный возврат средств
        по успешно прошедшей операции оплаты.

        Для работы этого метода необходимо:
        1. Запросить доступ к API Refund в личном кабинете Robokassa
        2. Сгенерировать Password3 в настройках магазина
        3. Предоставить password3 при инициализации Robokassa клиента

        :param op_key: Уникальный идентификатор операции (получается из OpStateExt или Result2)
        :param refund_sum: Сумма частичного возврата (не указывать при полном возврате)
        :param invoice_items: Товарные позиции для формирования фискального чека возврата
        :return: Ответ от API создания возврата
        :raises RobokassaRequestError: Если не настроен Password3

        Example:
            ```python
            from robokassa import Robokassa, InvoiceItem

            robokassa = Robokassa(
                merchant_login="demo",
                password1="pass1",
                password2="pass2",
                password3="pass3"  # Обязательно для возвратов
            )

            # Полный возврат без чека
            response = await robokassa.refund_op(op_key="12345-ABC-123")

            # Частичный возврат с чеком
            items = [
                InvoiceItem(
                    name="Товар",
                    quantity=1,
                    cost=100.0,
                    tax="none",
                    payment_method="full_payment",
                    payment_object="payment"
                )
            ]
            response = await robokassa.refund_op(
                op_key="12345-ABC-123",
                refund_sum=50.0,
                invoice_items=items
            )
            ```
        """
        if not self._refund_manager:
            raise RobokassaRequestError(
                "Password3 is required for refund operations. "
                "Please provide password3 when initializing Robokassa client."
            )

        request = RefundRequest(
            op_key=op_key, refund_sum=refund_sum, invoice_items=invoice_items
        )

        return await self._refund_manager.create_refund(
            http=self._create_http(REFUND_BASE_URL), request=request
        )

    async def get_refund_status(self, request_id: str) -> RefundStateResponse:
        """
        Получить статус операции возврата.

        Позволяет проверить текущий статус заявки на возврат,
        созданной через метод refund_op.

        :param request_id: GUID созданной заявки на возврат (получается в RefundResponse)
        :return: Статус возврата с суммой и label
        :raises RobokassaRequestError: Если не настроен Password3

        Example:
            ```python
            # Создаем возврат
            response = await robokassa.refund_op(op_key="12345-ABC-123")
            request_id = response.request_id  # "68cd7fa6-1338-4745-ba5c-28d16cbcdb3d"

            # Проверяем статус
            status = await robokassa.get_refund_status(request_id=request_id)
            print(f"Status: {status.label}")  # "finished", "processing" or "canceled"
            print(f"Amount: {status.amount}")
            ```
        """
        if not self._refund_manager:
            raise RobokassaRequestError(
                "Password3 is required for refund operations. "
                "Please provide password3 when initializing Robokassa client."
            )

        return await self._refund_manager.get_refund_state(
            http=self._create_http(REFUND_BASE_URL), request_id=request_id
        )
