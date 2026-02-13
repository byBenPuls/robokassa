import json
from typing import Dict, List, Any

from robokassa.connection import Http
from robokassa.exceptions import RobokassaRequestError, RobokassaParsingError
from robokassa.hash import Hash, HashAlgorithm
from robokassa.jwt import JWT
from robokassa.types import (
    InvoiceItem,
    RefundHashAlgorithm,
    RefundRequest,
    RefundResponse,
    RefundStateResponse,
    RefundStatus,
)


class RefundManager:
    """
    Менеджер для работы с API возвратов Robokassa Refund API.

    Позволяет создавать возвраты по операциям оплаты и проверять их статус.
    Для работы требует Password3 из настроек магазина.

    API документация: https://docs.robokassa.ru/refund-api/
    """

    def __init__(
        self,
        password3: str,
        jwt_algorithm: RefundHashAlgorithm = RefundHashAlgorithm.HS256,
    ) -> None:
        """
        Инициализация менеджера возвратов.

        :param password3: Пароль для подписи JWT токенов (из настроек магазина)
        :param jwt_algorithm: Алгоритм подписи JWT (по умолчанию HS256)
        """
        if not password3:
            raise RobokassaRequestError("Password3 is required for refund operations")

        self._password3 = password3
        self._jwt_algorithm = jwt_algorithm
        self._hash = self._map_refund_hash_algorithm_to_hash(jwt_algorithm)

    def _map_refund_hash_algorithm_to_hash(self, jwt_alg: RefundHashAlgorithm) -> Hash:
        """
        Маппинг RefundHashAlgorithm в Hash для создания подписи.
        
        JWT использует алгоритмы HMAC (HS256 = HMAC-SHA256, HS384 = HMAC-SHA384, HS512 = HMAC-SHA512).
        Это аналогично соответствующим хеш-функциям из HashAlgorithm enum.
        """
        mapping = {
            RefundHashAlgorithm.HS256: HashAlgorithm.sha256,
            RefundHashAlgorithm.HS384: HashAlgorithm.sha384,
            RefundHashAlgorithm.HS512: HashAlgorithm.sha512,
        }
        hash_alg = mapping.get(jwt_alg)
        if not hash_alg:
            raise RobokassaRequestError(f"Unsupported JWT algorithm: {jwt_alg}")
        return Hash(hash_alg)

    def _create_jwt_token(self, request: RefundRequest) -> str:
        """
        Создание JWT токена для запроса возврата.
        
        Заголовок стандартный: {"alg": "HS256", "typ": "JWT"}
        Payload содержит данные о возврате.
        Подпись создаётся с использованием Password3.
        """
        # Формируем заголовок JWT
        header = {"alg": self._jwt_algorithm.value, "typ": "JWT"}
        
        # Формируем payload
        payload: Dict[str, Any] = {"OpKey": request.op_key}
        
        # Добавляем сумму частичного возврата, если указана
        if request.refund_sum is not None:
            payload["RefundSum"] = request.refund_sum
        
        # Добавляем товарные позиции для чека, если указаны
        if request.invoice_items:
            payload["InvoiceItems"] = self._serialize_invoice_items(request.invoice_items)
        
        # Создаём JWT токен
        jwt = JWT(header=header, payload=payload, signature_key=self._password3, hash=self._hash)
        return jwt.create()

    def _serialize_invoice_items(self, items: List[InvoiceItem]) -> List[Dict]:
        """
        Сериализация товарных позиций в формат для API.
        """
        return [
            {
                "Name": item.name,
                "Quantity": item.quantity,
                "Cost": item.cost,
                "Tax": item.tax,
                "PaymentMethod": item.payment_method,
                "PaymentObject": item.payment_object,
            }
            for item in items
        ]

    async def create_refund(
        self,
        http: Http,
        request: RefundRequest,
    ) -> RefundResponse:
        """
        Создать заявку на возврат средств.
        
        POST /RefundService/Refund/Create
        
        :param http: HTTP клиент для выполнения запроса
        :param request: Данные запроса на возврат
        :return: Ответ от API с requestId или ошибкой
        :raises RobokassaRequestError: При ошибке во время запроса
        :raises RobokassaParsingError: При ошибке парсинга ответа
        """
        url = "/Refund/Create"
        
        # Создаём JWT токен
        jwt_token = self._create_jwt_token(request)

        # Отправляем запрос
        async with http as conn:
            # Использовал параметр json, как в примере с robokassa.payment.LinkGenerator.generate_protected_payment_link
            response = await conn.post(url, json=jwt_token)

        # Парсим ответ
        try:
            response_data = json.loads(response.text)
        except json.JSONDecodeError:
            raise RobokassaParsingError("Invalid JSON response from Refund API")
        
        # Проверяем структуру ответа
        if not isinstance(response_data, dict):
            raise RobokassaParsingError("Expected dict response from Refund API")
        
        # Формируем объект ответа
        return RefundResponse(
            success=response_data.get("success", False),
            message=response_data.get("message"),
            request_id=response_data.get("requestId"),
        )

    async def get_refund_state(
        self,
        http: Http,
        request_id: str,
    ) -> RefundStateResponse:
        """
        Получить статус операции возврата.
        
        GET /RefundService/Refund/GetState?id=<request_id>
        
        :param http: HTTP клиент для выполнения запроса
        :param request_id: GUID созданной заявки на возврат
        :return: Статус возврата с суммой и label
        :raises RobokassaRequestError: При ошибке во время запроса
        :raises RobokassaParsingError: При ошибке парсинга ответа
        """
        url = f"/Refund/GetState?id={request_id}"
        
        # Отправляем GET запрос
        async with http as conn:
            response = await conn.get(url)
        
        # Парсим ответ
        try:
            response_data = json.loads(response.text)
        except json.JSONDecodeError:
            raise RobokassaParsingError("Invalid JSON response from Refund API")

        label = None
        if 'label' in response_data:
            try:
                label = RefundStatus(response_data['label'])
            except ValueError:
                raise RobokassaParsingError(f"Unknown refund status received: {response_data['label']}")

        return RefundStateResponse(
            message=response_data.get("message"),
            request_id=response_data.get("requestId"),
            amount=response_data.get("amount"),
            label=label,
        )