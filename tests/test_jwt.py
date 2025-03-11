import hmac

import pytest

from robokassa.hash import Hash, HashAlgorithm
from robokassa.jwt import JWT


@pytest.fixture
def jwt_instance():
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"user_id": 123, "exp": 1710000000}
    signature_key = "secret"
    hash_instance = Hash(HashAlgorithm.sha256)
    return JWT(header, payload, signature_key, hash_instance)


def test_encode_to_base64(jwt_instance):
    assert jwt_instance._encode_to_base64(b'{"test":1}') == "eyJ0ZXN0IjoxfQ"


def test_dict_to_json_string(jwt_instance):
    assert jwt_instance._dict_to_json_string({"a": 1, "b": 2}) == '{"a":1,"b":2}'


def test_assemble_parts(jwt_instance):
    assert jwt_instance._assemble_parts("part1", "part2") == "part1.part2"


def test_get_hmac(jwt_instance):
    message = "test_message"
    hmac_result = jwt_instance._get_hmac(message)
    assert isinstance(hmac_result, hmac.HMAC)


def test_encrypt_data(jwt_instance):
    message = "test_message"
    encrypted = jwt_instance._encrypt_data(message)
    assert isinstance(encrypted, bytes)


def test_create(jwt_instance):
    token = jwt_instance.create()
    assert token.count(".") == 2
    parts = token.split(".")
    assert all(isinstance(part, str) for part in parts)


def test_str_repr(jwt_instance):
    assert isinstance(str(jwt_instance), str)
    assert isinstance(repr(jwt_instance), str)
