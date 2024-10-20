from dataclasses import dataclass, asdict
from typing import Optional, Union, Dict, Any

from robokassa.exceptions import UnusedStrictUrlParameterError
from robokassa.hash import Hash
from robokassa.utils import flatten_dict


@dataclass
class Signature:
    """ """

    merchant_login: Optional[str] = None

    out_sum: Optional[Union[float, str, int]] = None
    inv_id: Optional[Union[str, int]] = None

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

        return other.value == self.value

    def _get_serialized_additional_params(self) -> list:
        if self.additional_params is None:
            return []
        return sorted(tuple(f"{k}={v}" for k, v in self.additional_params.items()))

    def _serialize_string_for_hash(self, *args) -> str:
        values = tuple(str(i) for i in (args) if i is not None)
        return ":".join(values)

    def _calculate_hash(self, hash_: Hash, data: str) -> str:
        return hash_.hash_data(data)

    def _url_data_is_correct(self, url: str, url_method: str) -> bool:
        if (url is not None) or (url_method is not None):
            if (url is None) or (url_method is None):
                return False
        return True


@dataclass
class RobokassaParams:
    merchant_login: Optional[str] = None
    out_sum: Optional[Union[float, str, int]] = None
    description: Optional[str] = None
    signature_value: Optional[str] = None
    is_test: bool = False

    # additional params

    inc_curr_label: Optional[str] = None
    payment_methods: Optional[str] = None
    inv_id: Optional[Union[int, str]] = None
    culture: Optional[str] = None
    encoding: Optional[str] = None
    email: Optional[str] = None
    expiration_date: Optional[str] = None

    additional_params: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        return flatten_dict(asdict(self), True)
