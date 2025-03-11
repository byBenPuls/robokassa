import xml.etree.ElementTree as Et
from json import JSONDecodeError

import httpx

from robokassa.exceptions import RobokassaInterfaceError

correct_keys = {
    "merchant_login": "MerchantLogin",
    "description": "Description",
    "out_sum": "OutSum",
    "signature_value": "SignatureValue",
    "inc_current_label": "IncCurrentLabel",
    "payment_methods": "PaymentMethods",
    "inv_id": "InvId",
    "culture": "Culture",
    "encoding": "Encoding",
    "email": "Email",
    "expiration_data": "ExpirationDate",
    "is_test": "IsTest",
}


def flatten_dict(data, serialize_to_http_naming: bool = False):
    items = {}

    def recurse(current_dict):
        for key, value in current_dict.items():
            if isinstance(value, dict):
                recurse(value)
            else:
                if value is not None:
                    if serialize_to_http_naming:
                        key = correct_keys.get(key, key)
                    items[key] = value

    recurse(data)
    return items


class HttpResponseValidator:
    def __init__(self, response: httpx.Response, in_json: bool = True) -> None:
        self.response = response
        self.in_json = in_json

        if response.status_code != 200:
            raise RobokassaInterfaceError(
                "RobokassaInterface servers are unavailable. Please try again later."
            )

    def xml_to_dict(self, element):
        if len(element) == 0:
            return element.text.strip() if element.text else None
        result = {}
        for child in element:
            tag = child.tag.split("}")[-1]
            child_dict = self.xml_to_dict(child)
            if child.attrib:
                if tag in result:
                    if not isinstance(result[tag], list):
                        result[tag] = [result[tag]]
                    result[tag].append(
                        {**child.attrib, **(child_dict if child_dict else {})}
                    )
                else:
                    result[tag] = {**child.attrib, **(child_dict if child_dict else {})}
            else:
                if tag in result:
                    if not isinstance(result[tag], list):
                        result[tag] = [result[tag]]
                    result[tag].append(child_dict)
                else:
                    result[tag] = child_dict
        return result

    def validate_http_response(self) -> dict:
        if not self.in_json:
            data = self.response.text
            root = Et.fromstring(data)
            return self.xml_to_dict(root)

        try:
            data = self.response.json()
        except JSONDecodeError:
            raise RobokassaInterfaceError("Internal Robokassa server error")
        if data.get("errorCode") == 0:
            return data
        else:
            if data.get("errorCode") is None:
                return data
        raise RobokassaInterfaceError(
            f"Error code: {data.get('errorCode')}, error message: {data.get('errorMessage')}"
        )
