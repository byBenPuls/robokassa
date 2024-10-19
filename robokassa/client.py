from typing import Optional

from robokassa.exceptions import (
    UnusedStrictUrlParameterError,
    IncorrectUrlMethodError,
)
from robokassa.hash import HashAlgorithm, Hash
from robokassa.payment import PaymentLink, Payment


class RobokassaAbstract:
    pass


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

    @property
    def payment(self) -> Payment:
        return Payment(
            is_test=self.is_test,
            merchant_login=self.merchant_login,
            password1=self.password1,
            password2=self.password2,
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
            raise UnusedStrictUrlParameterError(
                "If you use URL, you also need to choose a HTTP method"
            )
        if (
            success_url_method not in available_http_methods
            or fail_url_method not in available_http_methods
        ):
            raise IncorrectUrlMethodError("You can use only GET or POST methods")

        payment_link = self._payment.generate_by_script(
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
