import pytest

from robokassa import Robokassa
from robokassa.hash import HashAlgorithm
from robokassa.types import Culture, HTTPMethod


@pytest.fixture
def robokassa():
    return Robokassa(
        merchant_login="test_login",
        password1="test_pass1",
        password2="test_pass2",
        algorithm=HashAlgorithm.md5,
        is_test=True,
    )


def test_generate_open_payment_link(robokassa):
    response = robokassa.generate_open_payment_link(
        out_sum=100.0,
        inv_id=1,
        description="Test Payment",
        success_url="https://success.ru",
        success_url_method=HTTPMethod.POST,
        fail_url="https://fail.ru",
        fail_url_method=HTTPMethod.POST,
        culture=Culture.RU,
    )
    assert response.url.startswith("https://auth.robokassa.ru/Merchant/Index.aspx")


def test_generate_subscription_link(robokassa):
    response = robokassa.generate_subscription_link(
        inv_id=1, previous_inv_id=0, out_sum=500
    )
    assert response.url.startswith("https://auth.robokassa.ru/Merchant/Index.aspx")


def test_is_redirect_valid(robokassa):
    valid = robokassa.is_redirect_valid(
        signature="test_signature", out_sum=100.0, inv_id=1
    )
    assert isinstance(valid, bool)


def test_is_result_notification_valid(robokassa):
    valid = robokassa.is_result_notification_valid(
        signature="test_signature", out_sum=100.0, inv_id=1
    )
    assert isinstance(valid, bool)
