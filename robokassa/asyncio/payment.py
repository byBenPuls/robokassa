from typing import Union, Optional

from httpx import Response

from robokassa.asyncio.connection import Requests
from robokassa.hash import Hash
from robokassa.payment import PaymentUrlGenerator, serialize_receipt
from robokassa.signature import SignaturesChecker
from robokassa.types import RobokassaParams, Signature
from robokassa.utils import HttpResponseValidator


class AsyncPaymentRequests:
    def __init__(self, http: Requests) -> None:
        self._http = http.connection
        self.payment_url = "https://auth.robokassa.ru/Merchant/Index"

    async def _make_post_request(self, data: dict) -> Response:
        async with self._http as conn:
            response = await conn.post("Indexjson.aspx?", data=data)
            return response

    def _serialize_payment_url(self, invoice_id: str) -> str:
        return f"{self.payment_url}/{invoice_id}"

    async def create_url_to_payment_page(
        self, robokassa_params: RobokassaParams
    ) -> str:
        response = await self._make_post_request(robokassa_params.as_dict())
        validated_response = HttpResponseValidator(response).validate_http_response()
        invoice_id = validated_response["invoiceID"]

        return self._serialize_payment_url(invoice_id)


class AsyncPaymentInterface:
    def __init__(self, http: Requests) -> None:
        self._requests = AsyncPaymentRequests(http)

    async def create_url_to_payment_page(
        self, robokassa_params: RobokassaParams
    ) -> str:
        return await self._requests.create_url_to_payment_page(robokassa_params)


class AsyncPaymentLink:
    def __init__(
        self,
        http: Requests,
        is_test: bool,
        hash_: Hash,
        merchant_login: str,
        password1: str,
    ) -> None:
        self._is_test = is_test
        self._hash_ = hash_
        self._merchant_login = merchant_login
        self._password1 = password1

        self._payment_interface = AsyncPaymentInterface(http)

        self._payment_generator = PaymentUrlGenerator(
            is_test=self._is_test,
            hash_=self._hash_,
            merchant_login=self._merchant_login,
            password=password1,
        )

        self.robokassa_params: RobokassaParams = RobokassaParams(
            is_test=self._is_test,
            merchant_login=self._merchant_login,
        )

    def _create_signature(
        self,
        inv_id: Union[str, int],
        out_sum: Union[str, int, float],
        receipt: Optional[str],
    ) -> Signature:
        return Signature(
            merchant_login=self._merchant_login,
            password=self._password1,
            inv_id=inv_id,
            receipt=receipt,
            out_sum=out_sum,
            hash_=self._hash_,
        )

    def generate_by_script(
        self,
        out_sum: float,
        default_prefix: str = "shp",
        result_url: Optional[str] = None,
        success_url: Optional[str] = None,
        success_url_method: Optional[str] = None,
        fail_url: Optional[str] = None,
        fail_url_method: Optional[str] = None,
        inv_id: Optional[int] = 0,
        receipt: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ) -> str:
        if receipt:
            receipt = serialize_receipt(receipt)

        return self._payment_generator.generate_by_script(
            out_sum=out_sum,
            default_prefix=default_prefix,
            receipt=receipt,
            result_url=result_url,
            success_url=success_url,
            success_url_method=success_url_method,
            fail_url=fail_url,
            fail_url_method=fail_url_method,
            inv_id=inv_id,
            description=description,
            **kwargs,
        )

    async def create_by_invoice_id(
        self,
        inv_id: Optional[Union[str, int]],
        out_sum: Union[str, int, float],
        description: str,
        receipt: Optional[dict] = None,
    ) -> str:
        if receipt:
            receipt = serialize_receipt(receipt)

        return await self._payment_interface.create_url_to_payment_page(
            RobokassaParams(
                is_test=self._is_test,
                merchant_login=self._merchant_login,
                inv_id=inv_id,
                receipt=receipt,
                out_sum=out_sum,
                description=description,
                signature_value=self._create_signature(inv_id, out_sum, receipt).value,
            )
        )


class AsyncPayment:
    def __init__(
        self,
        http: Requests,
        is_test: bool,
        hash_: Hash,
        merchant_login: str,
        password1: str,
        password2: str,
    ) -> None:
        self._is_test = is_test
        self._hash = hash_
        self._merchant_login = merchant_login
        self._password1 = password1
        self._password2 = password2

        self._http = http

    @property
    def link(self) -> AsyncPaymentLink:
        return AsyncPaymentLink(
            self._http, self._is_test, self._hash, self._merchant_login, self._password1
        )

    @property
    def check(self) -> SignaturesChecker:
        return SignaturesChecker(
            hash_=self._hash,
            password1=self._password1,
            password2=self._password2,
        )
