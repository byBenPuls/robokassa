import json
from typing import Dict, Any, Optional, Union
from urllib.parse import urlencode, quote

from httpx import Response

from robokassa.connection import Requests
from robokassa.hash import Hash
from robokassa.signature import SignaturesChecker
from robokassa.types import Signature, RobokassaParams
from robokassa.utils import HttpResponseValidator


def serialize_receipt(receipt: dict) -> str:
    """
    Returns url serialized receipt

    https://docs.robokassa.ru/fiscalization/
    """
    json_value = json.dumps(receipt, ensure_ascii=False)

    return quote(json_value, safe="")


class PaymentRequests:
    def __init__(self, http: Requests) -> None:
        self.connection = http
        self.payment_url = "https://auth.robokassa.ru/Merchant/Index"

    def _serialize_payment_url(self, invoice_id: str) -> str:
        return f"{self.payment_url}/{invoice_id}"

    def _make_post_request(self, data: dict) -> Response:
        with self.connection as conn:
            response = conn.post("Indexjson.aspx/?", data=data)
            return response

    def create_url_to_payment_page(self, robokassa_params: RobokassaParams) -> str:
        response = self._make_post_request(robokassa_params.as_dict())
        validated_response = HttpResponseValidator(response).validate_http_response()

        invoice_id = validated_response["invoiceID"]
        return self._serialize_payment_url(invoice_id)


class PaymentInterface:
    def __init__(self, http: Requests) -> None:
        self._payment_requests = PaymentRequests(http)

    def create_url_to_payment_page(self, robokassa_params: RobokassaParams) -> str:
        return self._payment_requests.create_url_to_payment_page(robokassa_params)


class PaymentUrlGenerator:
    def __init__(self, merchant_login: str, password: str, is_test: bool, hash_: Hash):
        self._merchant_login = merchant_login
        self._password = password
        self._is_test = is_test
        self._hash = hash_

        self._STATIC_URL = "https://auth.robokassa.ru/Merchant/Index.aspx"

    def _serialize_additional_params(self, default_prefix: str, params: dict) -> dict:
        return {f"{default_prefix}_{k}": v for k, v in params.items()}

    def _get_serialized_link_to_payment_page(self, url_params: Dict[str, Any]) -> str:
        return f"{self._STATIC_URL}?{urlencode(url_params)}"

    def _sort_urls(
        self, urls: Dict[str, str], success_url_method: str, fail_url_method: str
    ) -> Dict[str, str]:
        urls_plus_methods = {}
        for k, v in urls.items():
            if v is not None:
                urls_plus_methods[k] = f"{v}"
                if k == "SuccessUrl2":
                    method = ["SuccessUrl2Method", success_url_method]
                elif k == "FailUrl2":
                    method = ["FailUrl2Method", fail_url_method]
                else:
                    method = None
                if method is not None:
                    urls_plus_methods[method[0]] = method[1]
        return urls_plus_methods

    def generate_by_script(
        self,
        out_sum: float,
        default_prefix: str = "shp",
        receipt: Optional[str] = None,
        result_url: Optional[str] = None,
        success_url: Optional[str] = None,
        success_url_method: Optional[str] = None,
        fail_url: Optional[str] = None,
        fail_url_method: Optional[str] = None,
        inv_id: Optional[int] = 0,
        description: Optional[str] = None,
        **kwargs,
    ):
        params = self._serialize_additional_params(default_prefix, kwargs)
        additional_params_for_url = sorted([f"{k}={v}" for k, v in params.items()])

        signature = Signature(
            merchant_login=self._merchant_login,
            out_sum=out_sum,
            inv_id=inv_id,
            receipt=receipt,
            password=self._password,
            result_url2=quote(result_url, safe="") if result_url else None,
            success_url2=quote(success_url, safe="") if success_url else None,
            success_url2_method=success_url_method,
            fail_url2=quote(fail_url, safe="") if fail_url else None,
            fail_url2_method=fail_url_method,
            hash_=self._hash,
            additional_params=params,
        ).value

        urls_plus_methods = self._sort_urls(
            {
                "ResultUrl2": result_url,
                "SuccessUrl2": success_url,
                "FailUrl2": fail_url,
            },
            success_url_method,
            fail_url_method,
        )
        url_params = {
            k: v
            for k, v in [
                ("MerchantLogin", self._merchant_login),
                ("OutSum", out_sum),
                ("InvId", inv_id),
                ("Receipt", receipt),
                ("Description", description),
                *urls_plus_methods.items(),
                ("SignatureValue", signature),
                ("IsTest", int(self._is_test)),
            ]
            if v is not None
        }
        return (
            f"{self._get_serialized_link_to_payment_page(url_params)}"
            f"&{'&'.join(additional_params_for_url)}"
        )


class PaymentLink:
    def __init__(
        self,
        http: Requests,
        is_test: bool,
        hash_: Hash,
        merchant_login: str,
        password1: str,
    ) -> None:
        self._is_test = is_test
        self._merchant_login = merchant_login
        self._password = password1

        self._hash: Hash = hash_

        self.__http = http
        self._payment_interface = PaymentInterface(http)

        self._payment_generator = PaymentUrlGenerator(
            merchant_login=merchant_login,
            password=password1,
            is_test=is_test,
            hash_=self._hash,
        )

        self._STATIC_URL = "https://auth.robokassa.ru/Merchant/Index.aspx"

    def _create_signature(
        self,
        inv_id: Union[str, int],
        receipt: Union[dict],
        out_sum: Union[str, int, float],
    ) -> Signature:
        return Signature(
            merchant_login=self._merchant_login,
            password=self._password,
            inv_id=inv_id,
            receipt=receipt,
            out_sum=out_sum,
            hash_=self._hash,
        )

    def generate_by_script(
        self,
        out_sum: float,
        receipt: Optional[dict] = None,
        default_prefix: str = "shp",
        result_url: Optional[str] = None,
        success_url: Optional[str] = None,
        success_url_method: Optional[str] = None,
        fail_url: Optional[str] = None,
        fail_url_method: Optional[str] = None,
        inv_id: Optional[int] = 0,
        description: Optional[str] = None,
        **kwargs,
    ) -> str:
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

    def create_link_to_payment_page_by_invoice_id(
        self,
        inv_id: Optional[Union[int, str]],
        out_sum: Union[float, int, str],
        description: str,
        receipt: Optional[dict] = None,
    ) -> str:
        receipt = serialize_receipt(receipt)

        return self._payment_interface.create_url_to_payment_page(
            RobokassaParams(
                inv_id=inv_id,
                out_sum=out_sum,
                receipt=receipt,
                description=description,
                merchant_login=self._merchant_login,
                is_test=self._is_test,
                signature_value=self._create_signature(inv_id, receipt, out_sum).value,
            )
        )


class Payment:
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

        self.__http = http

    @property
    def link(self) -> PaymentLink:
        return PaymentLink(
            http=self.__http,
            is_test=self._is_test,
            hash_=self._hash,
            merchant_login=self._merchant_login,
            password1=self._password1,
        )

    @property
    def check(self) -> SignaturesChecker:
        return SignaturesChecker(
            hash_=self._hash, password1=self._password1, password2=self._password2
        )
