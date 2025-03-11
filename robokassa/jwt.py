import base64
import hmac
import json

from robokassa.types import Hash


class JWT:
    def __init__(
        self, header: dict, payload: dict, signature_key: str, hash: Hash
    ) -> None:
        self._header = header
        self._payload = payload
        self._signature_key = signature_key
        self._hash = hash

    def _encode_to_base64(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode().rstrip("=")

    def _dict_to_json_string(self, obj: dict) -> str:
        return json.dumps(obj, separators=(",", ":"))

    def _assemble_parts(self, *args) -> str:
        return ".".join(args)

    def _get_hmac(self, message: str) -> hmac.HMAC:
        return hmac.new(
            key=self._signature_key.encode(),
            msg=message.encode(),
            digestmod=self._hash.encrypt(),
        )

    def _encrypt_data(self, message: str) -> str:
        return self._get_hmac(message).digest()

    def create(self) -> str:
        formatted_parts = tuple(
            self._dict_to_json_string(i) for i in (self._header, self._payload)
        )
        encoded_parts = tuple(
            self._encode_to_base64(i.encode()) for i in formatted_parts
        )
        message = self._assemble_parts(*encoded_parts)
        signature = self._encode_to_base64(self._encrypt_data(message))

        return self._assemble_parts(message, signature)

    def __str__(self) -> str:
        return self.create()

    def __repr__(self) -> str:
        return "JWT()"
