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
