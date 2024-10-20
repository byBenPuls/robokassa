from robokassa import HashAlgorithm
from robokassa.connection import HttpConnection
from robokassa.hash import Hash
from robokassa.payment import PaymentRequests
from robokassa.types import RobokassaParams, Signature


def test_http_request():
    conn = HttpConnection()

    with conn as connection:
        request = connection.get(
            "https://httpbin.org/anything",
        )
        assert request.status_code == 200

    with conn as connection:
        request = connection.get("https://example.com")
        assert request.status_code == 200


def test_sync_http_link_generation():
    requests = PaymentRequests()
    robo_data = {
        "merchant_login": "rayspirit",
        "out_sum": 1,
        "inv_id": 0,
        "description": "Hello WORLD",
        "is_test": True,
        "culture": "ru",
    }
    signature = Signature(
        **{
            "merchant_login": "rayspirit",
            "out_sum": 1,
            "inv_id": 0,
        },
        password="VGX70HgoVTiw0R85blhs",
        hash_=Hash(HashAlgorithm.md5),
    )
    link = requests.create_url_to_payment_page(
        RobokassaParams(**robo_data, signature_value=signature.value)
    )
    assert link
    print("\n", link)
