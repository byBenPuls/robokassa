import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional

from robokassa.connection import Http
from robokassa.exceptions import RobokassaParsingError, RobokassaRequestError
from robokassa.hash import Hash
from robokassa.types import PaymentDetails, PaymentState, Signature


class OperationStateChecker:
    def __init__(self, merchant_login: str, hash: Hash, password_2: str) -> None:
        self._url = "/WebService/Service.asmx/OpStateExt"
        self._merchant_login = merchant_login
        self._hash = hash
        self.__password = password_2

        self._ns = {"ns": "http://merchant.roboxchange.com/WebService/"}

    def _parse_xml(self, text: str) -> ET.Element:
        return ET.fromstring(text.strip())

    def _find_el(self, xml: ET.Element, name: str) -> Optional[ET.Element]:
        return xml.find(name, self._ns)

    def _serialize_xml(self, xml: ET.Element) -> dict:
        return {
            "result": {
                "code": int(self._find_el(xml, "ns:Result/ns:Code").text)
                if self._find_el(xml, "ns:Result/ns:Code") is not None
                else None,
                "description": self._find_el(xml, "ns:Result/ns:Description").text
                if self._find_el(xml, "ns:Result/ns:Description") is not None
                else None,
            },
            "state": {
                "code": int(self._find_el(xml, "ns:State/ns:Code").text)
                if self._find_el(xml, "ns:State/ns:Code") is not None
                else None,
                "request_date": self._find_el(xml, "ns:State/ns:RequestDate").text
                if self._find_el(xml, "ns:State/ns:RequestDate") is not None
                else None,
                "state_date": self._find_el(xml, "ns:State/ns:StateDate").text
                if self._find_el(xml, "ns:State/ns:StateDate") is not None
                else None,
            },
            "info": {
                "inc_curr_label": self._find_el(xml, "ns:Info/ns:IncCurrLabel").text
                if self._find_el(xml, "ns:Info/ns:IncCurrLabel") is not None
                else None,
                "inc_sum": float(self._find_el(xml, "ns:Info/ns:IncSum").text)
                if self._find_el(xml, "ns:Info/ns:IncSum") is not None
                else None,
                "inc_account": self._find_el(xml, "ns:Info/ns:IncAccount").text
                if self._find_el(xml, "ns:Info/ns:IncAccount") is not None
                else None,
                "payment_method": {
                    "code": self._find_el(xml, "ns:Info/ns:PaymentMethod/ns:Code").text
                    if self._find_el(xml, "ns:Info/ns:PaymentMethod/ns:Code")
                    is not None
                    else None,
                    "description": self._find_el(
                        xml, "ns:Info/ns:PaymentMethod/ns:Description"
                    ).text
                    if self._find_el(xml, "ns:Info/ns:PaymentMethod/ns:Description")
                    is not None
                    else None,
                },
                "out_curr_label": self._find_el(xml, "ns:Info/ns:OutCurrLabel").text
                if self._find_el(xml, "ns:Info/ns:OutCurrLabel") is not None
                else None,
                "out_sum": float(self._find_el(xml, "ns:Info/ns:OutSum").text)
                if self._find_el(xml, "ns:Info/ns:OutSum") is not None
                else None,
                "op_key": self._find_el(xml, "ns:Info/ns:OpKey").text
                if self._find_el(xml, "ns:Info/ns:OpKey") is not None
                else None,
                "bank_card_rrn": self._find_el(xml, "ns:Info/ns:BankCardRRN").text
                if self._find_el(xml, "ns:Info/ns:BankCardRRN") is not None
                else None,
            },
            "user_field": [
                {
                    "name": field.find("ns:Name", self._ns).text
                    if field.find("ns:Name", self._ns) is not None
                    else None,
                    "value": field.find("ns:Value", self._ns).text
                    if field.find("ns:Value", self._ns) is not None
                    else None,
                }
                for field in xml.findall("ns:UserField/ns:Field", self._ns)
            ],
        }

    def _handle_result_data(self, code: int) -> None:
        if code == 0:
            return
        elif code == 1:
            raise RobokassaRequestError("Wrong digital signature of request")
        elif code == 2:
            raise RobokassaRequestError("MerchantLogin not found or not activated")
        elif code == 3:
            raise RobokassaRequestError(
                "Information about a spicified InvoiceId not found"
            )
        elif code == 4:
            raise RobokassaRequestError("Found 2 operations with same InvoiceId")
        elif code == 1000:
            raise RobokassaRequestError("Internal Robokassa servers error")
        else:
            raise RobokassaParsingError("Unexpected response code")

    async def get_state(self, http: Http, inv_id: int) -> PaymentDetails:
        request_data = {
            "MerchantLogin": self._merchant_login,
            "InvoiceId": inv_id,
            "Signature": Signature(
                merchant_login=self._merchant_login,
                password=self.__password,
                hash_=self._hash,
                inv_id=inv_id,
            ).value,
        }
        async with http as conn:
            response = await conn.post(self._url, data=request_data)
        try:
            serialized = self._serialize_xml(self._parse_xml(response.text))
        except Exception:
            raise RobokassaParsingError(
                "Cannot parse response from Robokassa servers"
            ) from None

        self._handle_result_data(serialized["result"]["code"])

        state = serialized.get("state")
        info = serialized.get("info")

        return PaymentDetails(
            state=PaymentState(serialized["state"]["code"]),
            description=state.get("description") if state else None,
            request_date=datetime.fromisoformat(state.get("request_date"))
            if state and state.get("request_date")
            else None,
            state_date=datetime.fromisoformat(state.get("state_date"))
            if state and state.get("state_date")
            else None,
            inc_curr_label=info.get("inc_curr_label") if info else None,
            inc_sum=info.get("inc_sum") if info else None,
            inc_account=info.get("inc_account") if info else None,
            out_curr_label=info.get("out_curr_label") if info else None,
            out_sum=info.get("out_sum") if info else None,
            op_key=info.get("op_key") if info else None,
            bank_card_rrn=info.get("ban_card_rrn") if info else None,
            user_fields={k: v for k, v in serialized.get("user_field")}
            if serialized.get("user_field")
            else None,
        )
