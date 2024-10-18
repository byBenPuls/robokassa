import hashlib

from robokassa.hash import HashAlgorithm, Hash


def test_algorithm():
    assert HashAlgorithm.md5 != HashAlgorithm.sha256
    assert HashAlgorithm.md5 == HashAlgorithm("md5")


def test_hash():
    assert (
        Hash(algorithm=HashAlgorithm.md5).hash_data("Hello World")
        == hashlib.md5(b"Hello World").hexdigest()
    )
