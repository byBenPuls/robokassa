from typing import Optional, Union, Any

from robokassa.types import Signature
from robokassa.hash import Hash


class SignaturesChecker:
    def __init__(self, hash_: Hash, password1: str, password2: str) -> None:
        self._hash: Hash = hash_
        self._password1 = password1
        self._password2 = password2

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
            password=self._password1,
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
            password=self._password2,
            hash_=self._hash,
        )

        return old_signature == new_signature
