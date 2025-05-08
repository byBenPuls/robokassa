import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hmac import compare_digest
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

from robokassa.exceptions import UnusedStrictUrlParameterError
from robokassa.hash import Hash


@dataclass
class Signature:
    """ """

    merchant_login: Optional[str] = None

    out_sum: Optional[Union[float, str, int]] = None
    inv_id: Optional[Union[str, int]] = None
    user_ip: Optional[str] = None
    receipt: Optional[dict] = None

    result_url2: Optional[str] = None

    success_url2: Optional[str] = None
    success_url2_method: Optional[str] = None

    fail_url2: Optional[str] = None
    fail_url2_method: Optional[str] = None

    password: Optional[str] = None

    value: Optional[str] = None

    additional_params: Dict[str, Union[int, str, float]] | None = None

    hash_: Optional[Hash] = None

    def __post_init__(self) -> None:
        """
        For create:
        `MerchantLogin:OutSum:InvId:ResultUrl2:SuccessUrl2:SuccessUrl2Method:password1`

        For check:
        `OutSum:InvId:[password 1 or 2]`

        Also, additional params after password if params is containing in Signature.
        """
        if not self._url_data_is_correct(
            self.success_url2, self.success_url2_method
        ) or not self._url_data_is_correct(self.fail_url2, self.fail_url2_method):
            raise UnusedStrictUrlParameterError(
                "If you use success_url2 or fail_url2 don't forget choose"
                "HTTP method for them.\nAvailable HTTP Methods:\n"
                "GET, POST. Use them like a uppercase string"
            )

        if self.value is not None:
            return

        inv_id = "" if self.inv_id is None else self.inv_id
        password = self.password
        hashable_string = self._serialize_string_for_hash(
            self.merchant_login,
            self.out_sum,
            inv_id,
            self.user_ip,
            self.receipt,
            self.result_url2,
            self.success_url2,
            self.success_url2_method,
            self.fail_url2,
            self.fail_url2_method,
            password,
            *self._get_serialized_additional_params(),
        )

        self.value = self._calculate_hash(self.hash_, hashable_string)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Signature):
            raise TypeError("Cannot use this type for signature")

        return compare_digest(other.value, self.value)

    def _get_serialized_additional_params(self) -> list:
        if self.additional_params is None:
            return []
        return sorted(tuple(f"{k}={v}" for k, v in self.additional_params.items()))

    def _serialize_string_for_hash(self, *args) -> str:
        values = tuple(
            str(i) for i in (args) if i is not None and i != "null" and i != -1
        )
        result = ":".join(values)
        return result

    def _calculate_hash(self, hash_: Hash, data: str) -> str:
        return hash_.hash_data(data)

    def _url_data_is_correct(self, url: str, url_method: str) -> bool:
        if (url is not None) or (url_method is not None):
            if (url is None) or (url_method is None):
                return False
        return True


class PaymentMethod(Enum):
    BANK_CARD: str = "BankCard"
    SBP: str = "SBP"


class Culture(Enum):
    RU: str = "ru"
    EN: str = "en"


class HTTPMethod(Enum):
    GET: str = "GET"
    POST: str = "POST"


class InvoiceType(Enum):
    ONE_TIME: str = "OneTime"
    REUSABLE: str = "Reusable"


@dataclass
class RobokassaParams:
    base_url: str = "https://auth.robokassa.ru/Merchant/Index.aspx"
    merchant_login: Optional[str] = None
    out_sum: Optional[Union[float, str, int]] = None
    description: Optional[str] = None
    signature_value: Optional[str] = None
    receipt: Optional[dict] = None
    is_test: bool = False

    inc_curr_label: Optional[str] = None
    payment_methods: Optional[List[PaymentMethod]] = None
    merchant_comments: Optional[str] = None
    invoice_type: Optional[InvoiceType] = None
    inv_id: Optional[Union[int, str]] = None
    id: Optional[int] = None
    previous_inv_id: Optional[int] = None
    culture: Optional[Culture] = None
    encoding: Optional[str] = None
    user_ip: Optional[str] = None
    email: Optional[str] = None
    recurring: bool = False
    expiration_date: Optional[datetime] = None
    default_prefix: str = "shp"

    result_url: Optional[str] = None
    success_url: Optional[str] = None
    success_url_method: Optional[HTTPMethod] = None
    fail_url: Optional[str] = None
    fail_url_method: Optional[HTTPMethod] = None

    additional_params: Optional[Dict[str, Any]] = None

    _serialize_receipt: bool = True

    def _encode_receipt(self) -> None:
        encoded = quote(json.dumps(self.receipt, ensure_ascii=False), safe="")
        self.receipt = encoded if encoded != "null" else None

    def __post_init__(self) -> None:
        if not self.additional_params:
            self.additional_params = {}
        self.additional_params = {
            f"{self.default_prefix}_{k}": v for k, v in self.additional_params.items()
        }

        # -------------
        # SERIALIZATION
        # -------------
        if self._serialize_receipt:
            self._encode_receipt()
        if self.expiration_date:
            self.expiration_date = self.expiration_date.isoformat()
        if self.payment_methods:
            self.payment_methods = [i.value for i in self.payment_methods]
        if self.culture:
            self.culture = self.culture.value
        if self.success_url_method:
            self.success_url_method = self.success_url_method.value
        if self.fail_url_method:
            self.fail_url_method = self.fail_url_method.value
        if self.invoice_type:
            self.invoice_type = self.invoice_type.value

    def to_dict(self) -> dict:
        """
        Returns dict for POST methods.
        """
        params = (
            ("MerchantLogin", self.merchant_login),
            ("OutSum", self.out_sum),
            ("InvId", self.inv_id),
            ("UserIp", self.user_ip),
            ("Email", self.email),
            ("Description", self.description),
            ("SignatureValue", self.signature_value),
            ("Receipt", self.receipt),
            ("Culture", self.culture),
            ("PaymentMethods", self.payment_methods),
            ("Recurring", self.recurring),
            ("PreviousInvoiceID", self.previous_inv_id),
            ("ResultUrl2", self.result_url),
            ("SuccessUrl2", self.success_url),
            ("SuccessUrl2Method", self.success_url_method),
            ("FailUrl2", self.fail_url),
            ("FailUrl2Method", self.fail_url_method),
            ("ExpirationDate", self.expiration_date),
            ("IsTest", self.is_test),
            *self.additional_params.items(),
        )

        return {
            k: v
            for k, v in params
            if v or (isinstance(v, int) and not isinstance(v, bool) and v == 0)
        }


class PaymentState(Enum):
    INITIATED: int = 5
    CANCELLED: int = 10
    ON_HOLD: int = 20
    PENDING: int = 50
    FAILED: int = 60
    SUSPENDED: int = 80
    COMPLETED: int = 100


@dataclass
class RobokassaResponse:
    url: Optional[str] = None
    params: Optional[RobokassaParams] = None


@dataclass
class PaymentDetails:
    state: Optional[PaymentState] = None
    description: Optional[str] = None
    request_date: Optional[datetime] = None
    state_date: Optional[datetime] = None
    inc_curr_label: Optional[str] = None
    inc_sum: Optional[float] = None
    inc_account: Optional[str] = None
    out_curr_label: Optional[str] = None
    out_sum: Optional[float] = None
    op_key: Optional[str] = None
    bank_card_rrn: Optional[str] = None
    user_fields: Optional[Dict[Any, Any]] = None
