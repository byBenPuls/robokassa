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

    def hash_data(self, data: str) -> str:
        data = data.encode()
        # str to bytes for hash

        if self.algorithm == HashAlgorithm.md5:
            result = hashlib.md5(data).hexdigest()
        elif self.algorithm == HashAlgorithm.ripemd160:
            h = hashlib.new("ripemd160")
            h.update(data)
            result = h.hexdigest()
        elif self.algorithm == HashAlgorithm.sha1:
            result = hashlib.sha1(data).hexdigest()
        elif self.algorithm == HashAlgorithm.sha256:
            result = hashlib.sha256(data).hexdigest()
        elif self.algorithm == HashAlgorithm.sha384:
            result = hashlib.sha384(data).hexdigest()
        elif self.algorithm == HashAlgorithm.sha512:
            result = hashlib.sha512(data).hexdigest()
        else:
            raise UnresolvedAlgorithmTypeError("Cannot define algorithm for hashing")

        return result
