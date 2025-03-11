import _hashlib
import hashlib
from enum import Enum

from robokassa.exceptions import UnresolvedAlgorithmTypeError


class HashAlgorithm(Enum):
    md5 = "md5"
    ripemd160 = "ripemd160"
    sha1 = "sha1"
    sha256 = "sha256"
    sha384 = "sha384"
    sha512 = "sha512"


class Hash:
    def __init__(self, algorithm: HashAlgorithm) -> None:
        self.algorithm = algorithm

        if not isinstance(self.algorithm, HashAlgorithm):
            raise UnresolvedAlgorithmTypeError("Use HashAlgorithm class for that")

    def _encrypt_ripemd160(self, *args, **kwargs) -> _hashlib.HASH:
        h = hashlib.new("ripemd160")
        h.update(*args, **kwargs)
        return h

    def encrypt(self) -> _hashlib.HASH:
        if self.algorithm == HashAlgorithm.md5:
            result = hashlib.md5
        elif self.algorithm == HashAlgorithm.ripemd160:
            result = self._encrypt_ripemd160
        elif self.algorithm == HashAlgorithm.sha1:
            result = hashlib.sha1
        elif self.algorithm == HashAlgorithm.sha256:
            result = hashlib.sha256
        elif self.algorithm == HashAlgorithm.sha384:
            result = hashlib.sha384
        elif self.algorithm == HashAlgorithm.sha512:
            result = hashlib.sha512
        else:
            raise UnresolvedAlgorithmTypeError("Cannot define algorithm for hashing")

        return result

    def hash_data(self, data: str) -> str:
        data = data.encode()
        # str to bytes for hash

        hash = self.encrypt()

        return hash(data).hexdigest()
