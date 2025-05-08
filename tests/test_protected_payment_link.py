from robokassa.hash import Hash, HashAlgorithm
from robokassa.payment import LinkGenerator


def test_generate_open_payment_link():
    mock_hash = Hash(HashAlgorithm.sha256)
    generator = LinkGenerator(mock_hash, "test_password")

    assert generator._to_camel_case("payment_object") == "PaymentObject"
    assert generator._to_camel_case("payment_method") == "PaymentMethod"
    assert generator._to_camel_case("cost") == "Cost"
    assert generator._to_camel_case("quantity") == "Quantity"
    assert generator._to_camel_case("tax") == "Tax"
