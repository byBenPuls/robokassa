from hashlib import md5

from robokassa.types import Signature
from robokassa.hash import Hash, HashAlgorithm


def test_signature():
    signature = Signature(
        inv_id=0,
        out_sum=123,
        password="my_password",
        additional_params={"shp_telegram_id": 2138912389},
        hash_=Hash(algorithm=HashAlgorithm.md5),
    )
    signature2 = Signature(
        inv_id=0,
        out_sum=123,
        password="my_password",
        additional_params={"shp_telegram_id": 2138912389},
        hash_=Hash(algorithm=HashAlgorithm.md5),
    )
    assert signature.inv_id == 0
    assert signature.value

    assert signature == signature2


def test_hash_comparison():
    signature = Signature(
        inv_id=0, out_sum=1, password="1", hash_=Hash(HashAlgorithm.sha512)
    )

    signature2 = Signature(
        inv_id=0, out_sum=1, password="2", hash_=Hash(HashAlgorithm.sha512)
    )

    assert signature != signature2


def test_hash():
    hashed_data = Hash(algorithm=HashAlgorithm.md5).hash_data("hello world")

    assert hashed_data == md5(b"hello world").hexdigest().lower()
