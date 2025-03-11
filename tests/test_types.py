from datetime import datetime

import pytest

from robokassa.hash import Hash, HashAlgorithm
from robokassa.types import PaymentState, RobokassaParams, Signature


@pytest.fixture
def mock_hash():
    class MockHash(Hash):
        def hash_data(self, data: str) -> str:
            return "mocked_hash"

    return MockHash(algorithm=HashAlgorithm.md5)


def test_signature_init(mock_hash):
    sig = Signature(
        merchant_login="test_login",
        out_sum=100.50,
        inv_id=123,
        password="test_pass",
        hash_=mock_hash,
    )
    assert sig.value == "mocked_hash"


def test_signature_equality(mock_hash):
    sig1 = Signature("test_login", 100.50, 123, "test_pass", hash_=mock_hash)
    sig2 = Signature("test_login", 100.50, 123, "test_pass", hash_=mock_hash)
    assert sig1 == sig2


def test_signature_additional_params(mock_hash):
    sig = Signature(
        merchant_login="test_login",
        out_sum=100.50,
        inv_id=123,
        password="test_pass",
        additional_params={"custom": "value"},
        hash_=mock_hash,
    )
    assert "custom=value" in sig._get_serialized_additional_params()


def test_robokassa_params_init():
    params = RobokassaParams(
        merchant_login="test_login",
        out_sum=100.50,
        inv_id=123,
        description="Test payment",
        expiration_date=datetime(2025, 1, 1),
    )
    assert params.merchant_login == "test_login"
    assert params.expiration_date == "2025-01-01T00:00:00"


def test_robokassa_params_to_dict():
    params = RobokassaParams(
        merchant_login="test_login",
        out_sum=100.50,
        inv_id=123,
        description="Test payment",
        expiration_date=datetime(2025, 1, 1),
    )
    params_dict = params.to_dict()
    assert params_dict["MerchantLogin"] == "test_login"
    assert params_dict["OutSum"] == 100.50
    assert params_dict["InvId"] == 123
    assert params_dict["Description"] == "Test payment"


def test_payment_state_enum():
    assert PaymentState.COMPLETED.value == 100
