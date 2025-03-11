from robokassa.hash import Hash, HashAlgorithm
from robokassa.payment import LinkGenerator
from robokassa.types import RobokassaParams


def test_generate_open_payment_link():
    mock_hash = Hash(HashAlgorithm.sha256)
    generator = LinkGenerator(mock_hash, "test_password")

    params = RobokassaParams(
        merchant_login="test_login",
        out_sum=100.0,
        inv_id=1,
        description="Test payment",
        is_test=True,
    )

    response = generator.generate_open_payment_link(params)

    assert response.url.startswith("https://auth.robokassa.ru/Merchant/Index.aspx?")
    assert "MerchantLogin=test_login" in response.url
    assert "OutSum=100.0" in response.url
    assert "InvId=1" in response.url
    assert "IsTest=1" in response.url
    assert params.signature_value is not None


def test_generate_subscription_payment_link():
    mock_hash = Hash(HashAlgorithm.sha256)
    generator = LinkGenerator(mock_hash, "test_password")

    params = RobokassaParams(
        out_sum=200.0, inv_id=2, description="Subscription payment", is_test=False
    )

    response = generator.generate_subscription_payment_link(params)

    assert response.url.startswith("https://auth.robokassa.ru/Merchant/Index.aspx?")
    assert "OutSum=200.0" in response.url
    assert "InvId=2" in response.url
    assert "IsTest=0" in response.url
    assert params.signature_value is not None
