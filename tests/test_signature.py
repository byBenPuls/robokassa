from hashlib import md5

import pytest

from robokassa.hash import Hash, HashAlgorithm
from robokassa.payment import LinkGenerator
from robokassa.signature import Signature, SignatureChecker
from robokassa.types import RobokassaParams


def test_signature_building():
    my_hash = Hash(HashAlgorithm.md5)

    string = "demo:11:0:Password#1"

    assert (
        Signature(hash_=my_hash)._serialize_string_for_hash("demo", 11, 0, "Password#1")
        == string
    )

    sign = Signature(
        merchant_login="demo",
        out_sum=11,
        inv_id=0,
        password="Password#1",
        hash_=my_hash,
    )

    assert sign.value == md5(bytes(string, "utf8")).hexdigest()


@pytest.fixture
def hash_mock():
    class HashMock:
        def hash_data(self, data):
            return f"mocked_hash_{data}"

    return HashMock()


@pytest.fixture
def link_generator(hash_mock):
    return LinkGenerator(hash_mock, "test_password")


@pytest.fixture
def signature_checker(hash_mock):
    return SignatureChecker(hash_mock, "password1", "password2")


@pytest.fixture
def params():
    return RobokassaParams(
        merchant_login="test_login",
        out_sum=100.50,
        description="Test payment",
        inv_id=123,
        is_test=True,
    )


def test_generate_open_payment_link(link_generator, params):
    response = link_generator.generate_open_payment_link(params)
    assert "mocked_hash" in response.url
    assert response.params.signature_value.startswith("mocked_hash")


def test_generate_subscription_payment_link(link_generator, params):
    response = link_generator.generate_subscription_payment_link(params)
    assert "mocked_hash" in response.url
    assert response.params.signature_value.startswith("mocked_hash")


def test_success_or_fail_url_signature_is_valid(signature_checker):
    assert signature_checker.success_or_fail_url_signature_is_valid(
        "mocked_hash_100.5:123:password1", 100.5, 123
    )


def test_result_url_signature_is_valid(signature_checker):
    assert signature_checker.result_url_signature_is_valid(
        "mocked_hash_100.5:123:password2", 100.5, 123
    )
    assert signature_checker.result_url_signature_is_valid(
        "mocked_hash_100.5:123:password2:shp_id=123", 100.5, 123, shp_id=123
    )
