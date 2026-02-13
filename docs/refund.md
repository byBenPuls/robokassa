# Возвраты (Refund API)

API возвратов позволяет создавать заявки на полный или частичный возврат средств по успешно проведённым операциям оплаты.

> **Важно:** Перед началом работы запросите доступ к API Refund в личном кабинете Robokassa и сгенерируйте `Password3` в настройках магазина.

## Инициализация клиента

```python
from robokassa import RefundHashAlgorithm, Robokassa

robokassa = Robokassa(
    merchant_login="your_merchant_login",
    password1="your_password1",
    password2="your_password2",
    password3="your_password3",  # Обязательно для возвратов
    refund_algorithm=RefundHashAlgorithm.HS256,  # Алгоритм подписи JWT для токенов возвратов
)
```

### Поддерживаемые алгоритмы подписи

Для работы с API возвратов используются HMAC-алгоритмы для подписи JWT токенов:

* `HS256` - HMAC-SHA256 (по умолчанию)
* `HS384` - HMAC-SHA384
* `HS512` - HMAC-SHA512

## Создание возврата

### Полный возврат

```python
response = await robokassa.refund_op(
    op_key="0005F891-8CCD-434B-8455-816AFFFDBF37-0VOisWikFF"
)

if response.success:
    print(f"Request ID: {response.request_id}")
else:
    print(f"Error: {response.message}")
```

### Частичный возврат

```python
response = await robokassa.refund_op(
    op_key="0005F891-8CCD-434B-8455-816AFFFDBF37-0VOisWikFF",
    refund_sum=50.0  # Сумма частичного возврата
)
```

### Возврат с формированием фискального чека

```python
from robokassa import InvoiceItem

items = [
    InvoiceItem(
        name="Товар 1",
        quantity=2,
        cost=100.0,
        tax="none",
        payment_method="full_payment",
        payment_object="payment",
    ),
    InvoiceItem(
        name="Товар 2",
        quantity=1,
        cost=50.0,
        tax="vat20",
        payment_method="partial_payment",
        payment_object="commodity",
    ),
]

response = await robokassa.refund_op(
    op_key="0005F891-8CCD-434B-8455-816AFFFDBF37-0VOisWikFF",
    refund_sum=250.0,
    invoice_items=items,
)
```

## Проверка статуса возврата

```python
from robokassa import RefundStatus

status = await robokassa.get_refund_status(request_id=response.request_id)

if status.message:
    print(f"Error: {status.message}")
else:
    print(f"Amount: {status.amount}")
    print(f"Status: {status.label}")

    if status.label == RefundStatus.FINISHED:
        print("Возврат успешно выполнен")
    elif status.label == RefundStatus.PROCESSING:
        print("Возврат в обработке")
    elif status.label == RefundStatus.CANCELED:
        print("Возврат отменён")
```

## Статусы возврата

| Статус | Описание |
|--------|----------|
| `finished` | Успешный полный или частичный возврат |
| `processing` | Возврат находящийся в процессе выполнения |
| `canceled` | Возврат отмененный через личный кабинет |

## Ошибки

### При создании возврата

- `NotEnoughOperationFunds` - Недостаточно средств на операции

### При проверке статуса

- `Id is invalid or request id does not exist` - Неверный requestId или заявка не найдена

## Дополнительная документация

Полная документация API: [docs.robokassa.ru/refund-api/](https://docs.robokassa.ru/refund-api/)