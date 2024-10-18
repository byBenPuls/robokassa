from abc import ABC, abstractmethod
from typing import Any, Dict, Union, Optional
from urllib.parse import urlencode

from robokassa.exceptions import (
    UnusedStrictUrlParameter,
    IncorrectUrlMethod,
)
from robokassa.hash import HashAlgorithm, Hash
from robokassa.types import Signature


class PaymentLink:
    def __init__(
        self, is_test: bool, hash_: Hash, merchant_login: str, password1: str
    ) -> None:
        self.is_test = is_test
        self.merchant_login = merchant_login
        self.password = password1

        self.hash_: Hash = hash_

        self.STATIC_URL = "https://auth.robokassa.ru/Merchant/Index.aspx"

    def _serialize_additional_params(self, default_prefix: str, params: dict) -> dict:
        return {f"{default_prefix}_{k}": v for k, v in params.items()}

    def _get_serialized_link_to_payment_page(self, url_params: Dict[str, Any]) -> str:
        return f"{self.STATIC_URL}?{urlencode(url_params)}"

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

    def generate(
        self,
        out_sum: float,
        default_prefix: str,
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
            merchant_login=self.merchant_login,
            out_sum=out_sum,
            inv_id=inv_id,
            password=self.password,
            result_url2=result_url,
            success_url2=success_url,
            success_url2_method=success_url_method,
            fail_url2=fail_url,
            fail_url2_method=fail_url_method,
            hash_=self.hash_,
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
                ("MerchantLogin", self.merchant_login),
                ("OutSum", out_sum),
                ("InvId", inv_id),
                ("Description", description),
                *urls_plus_methods.items(),
                ("SignatureValue", signature),
                ("IsTest", int(self.is_test)),
            ]
            if v is not None
        }
        return (
            f"{self._get_serialized_link_to_payment_page(url_params)}"
            f"&{"&".join(additional_params_for_url)}"
        )


class RobokassaAbstract:
    pass


class RobokassaAbstractMethods(ABC):
    @abstractmethod
    def generate_link_to_payment_page(
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
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    def success_or_fail_url_signature_is_valid(
        self,
        success_signature: str,
        out_sum: Union[str, float, int],
        inv_id: Optional[Union[str, int]] = None,
        **kwargs: Any,
    ) -> bool:
        pass

    @abstractmethod
    def result_url_signature_is_valid(
        self,
        result_signature: str,
        out_sum: Union[str, float, int],
        inv_id: Optional[Union[str, int]] = None,
        **kwargs: Any,
    ) -> bool:
        pass


class Robokassa(RobokassaAbstract, RobokassaAbstractMethods):
    def __init__(
        self,
        merchant_login: str,
        password1: str,
        password2: str,
        algorithm: HashAlgorithm = HashAlgorithm.md5,
        is_test: bool = False,
        use_standard_naming_of_additional_link_params: bool = True,
    ) -> None:
        self.merchant_login = merchant_login
        self.password1 = password1
        self.password2 = password2
        self.is_test = is_test
        self.use_standard_naming = use_standard_naming_of_additional_link_params

        self._hash = Hash(algorithm)
        self._payment = PaymentLink(
            is_test=self.is_test,
            merchant_login=self.merchant_login,
            password1=self.password1,
            hash_=self._hash,
        )

    def generate_link_to_payment_page(
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
        **kwargs,
    ) -> str:
        available_http_methods = ("GET", "POST", None)

        if (success_url is not None) != (success_url_method is not None):
            raise UnusedStrictUrlParameter(
                "If you use URL, you also need to choose a HTTP method"
            )
        if (
            success_url_method not in available_http_methods
            or fail_url_method not in available_http_methods
        ):
            raise IncorrectUrlMethod("You can use only GET or POST methods")

        payment_link = self._payment.generate(
            default_prefix=default_prefix,
            out_sum=out_sum,
            result_url=result_url,
            success_url=success_url,
            success_url_method=success_url_method,
            fail_url=fail_url,
            fail_url_method=fail_url_method,
            inv_id=inv_id,
            description=description,
            **kwargs,
        )

        return payment_link

    def success_or_fail_url_signature_is_valid(
        self,
        success_signature: str,
        out_sum: Union[str, float, int],
        inv_id: Optional[Union[str, int]] = None,
        **kwargs: Any,
    ) -> bool:
        old_signature = Signature(
            value=success_signature.lower(),
            hash_=self._hash,
        )
        new_signature = Signature(
            out_sum=out_sum,
            inv_id=inv_id,
            additional_params=kwargs,
            password=self.password1,
            hash_=self._hash,
        )

        return old_signature == new_signature

    def result_url_signature_is_valid(
        self,
        result_signature: str,
        out_sum: Union[str, float, int],
        inv_id: Optional[Union[str, int]] = None,
        **kwargs: Any,
    ) -> bool:
        old_signature = Signature(
            value=result_signature.lower(),
            hash_=self._hash,
        )
        new_signature = Signature(
            out_sum=out_sum,
            inv_id=inv_id,
            additional_params=kwargs,
            password=self.password2,
            hash_=self._hash,
        )

        return old_signature == new_signature
