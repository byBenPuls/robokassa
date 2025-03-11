from hashlib import md5, new, sha1, sha256, sha384, sha512
from random import randint

from robokassa.hash import Hash, HashAlgorithm


def get_rand_chars(lenght: int) -> str:
    return "".join(chr(randint(33, 125)) for _ in range(lenght))


def to_bytes(string: str) -> bytes:
    return bytes(string, encoding="utf8")


def test_hash_equality():
    string_to_hash = "MerchantLogin:OutSum::Password#1"

    assert (
        Hash(HashAlgorithm.md5).hash_data(string_to_hash)
        == md5(to_bytes(string_to_hash)).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.ripemd160).hash_data(string_to_hash)
        == new("ripemd160", to_bytes(string_to_hash)).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.sha1).hash_data(string_to_hash)
        == sha1(to_bytes(string_to_hash)).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.sha256).hash_data(string_to_hash)
        == sha256(to_bytes(string_to_hash)).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.sha384).hash_data(string_to_hash)
        == sha384(to_bytes(string_to_hash)).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.sha512).hash_data(string_to_hash)
        == sha512(to_bytes(string_to_hash)).hexdigest()
    )


def test_hash_inequality():
    string_to_hash = "MyLogin:1234:234:secretPa$$word"

    assert (
        Hash(HashAlgorithm.md5).hash_data(string_to_hash)
        != md5(to_bytes(string_to_hash + get_rand_chars(2))).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.ripemd160).hash_data(string_to_hash)
        != new("ripemd160", to_bytes(string_to_hash + get_rand_chars(1))).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.sha1).hash_data(string_to_hash)
        != sha1(to_bytes(string_to_hash + get_rand_chars(13))).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.sha256).hash_data(string_to_hash)
        != sha256(to_bytes(string_to_hash + get_rand_chars(4))).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.sha384).hash_data(string_to_hash)
        != sha384(to_bytes(string_to_hash + get_rand_chars(1))).hexdigest()
    )
    assert (
        Hash(HashAlgorithm.sha512).hash_data(string_to_hash)
        != sha512(to_bytes(string_to_hash + get_rand_chars(4))).hexdigest()
    )
