"""
Пример использования API возвратов Robokassa (Refund API).

Для работы с примером необходимо:
1. Запросить доступ к API Refund в личном кабинете Robokassa
2. Сгенерировать Password3 в настройках магазина
3. Иметь успешную операцию оплаты с известным OpKey

Подробнее: https://docs.robokassa.ru/refund-api/
"""

import asyncio

from robokassa import (
    InvoiceItem,
    RefundHashAlgorithm,
    RefundStatus,
    Robokassa, HashAlgorithm,
)


async def main():
    # Инициализация клиента с поддержкой возвратов
    # Password3 обязателен для работы с API возвратов
    robokassa = Robokassa(merchant_login="your_merchant_login", password1="your_password1", password2="your_password2",
                          password3="your_password3", algorithm=HashAlgorithm.md5, refund_algorithm=RefundHashAlgorithm.HS256,
                          is_test=True)

    # Пример 1: Полный возврат без формирования фискального чека
    print("=" * 50)
    print("Пример 1: Полный возврат без чека")
    print("=" * 50)

    op_key = "0005F891-8CCD-434B-8455-816AFFFDBF37-0VOisWikFF"  # Получите из OpStateExt или Result2

    response = await robokassa.refund_op(op_key=op_key)

    if response.success:
        print(f"✅ Заявка на возврат создана успешно!")
        print(f"   Request ID: {response.request_id}")
    else:
        print(f"❌ Ошибка при создании возврата: {response.message}")
        return

    # Проверка статуса возврата
    status = await robokassa.get_refund_status(request_id=response.request_id)
    print(f"   Статус: {status.label}")
    print(f"   Сумма: {status.amount}")

    print()

    # Пример 2: Частичный возврат с формированием фискального чека
    print("=" * 50)
    print("Пример 2: Частичный возврат с чеком")
    print("=" * 50)

    op_key_2 = "ANOTHER-OP-KEY-HERE"  # Получите из OpStateExt или Result2

    # Формируем товарные позиции для чека возврата
    items = [
        InvoiceItem(
            name="Товар 1",
            quantity=2,
            cost=100.0,  # Стоимость единицы
            tax="none",  # Налоговая ставка
            payment_method="full_payment",  # Способ оплаты
            payment_object="payment",  # Объект расчёта
        ),
        InvoiceItem(
            name="Товар 2",
            quantity=1,
            cost=50.0,
            tax="vat20",  # НДС 20%
            payment_method="partial_payment",
            payment_object="commodity",
        ),
    ]

    # Создаём частичный возврат
    response = await robokassa.refund_op(
        op_key=op_key_2,
        refund_sum=250.0,  # Сумма частичного возврата
        invoice_items=items,  # Товарные позиции для чека
    )

    if response.success:
        print(f"✅ Заявка на частичный возврат создана успешно!")
        print(f"   Request ID: {response.request_id}")
    else:
        print(f"❌ Ошибка при создании возврата: {response.message}")
        return

    # Проверка статуса и ожидание завершения
    print("   Ожидание завершения возврата...")
    await asyncio.sleep(2)  # Пауза между запросами

    status = await robokassa.get_refund_status(request_id=response.request_id)
    print(f"   Статус: {status.label}")
    print(f"   Сумма: {status.amount}")

    # Обработка различных статусов
    if status.label == RefundStatus.FINISHED:
        print("   ✅ Возврат успешно выполнен!")
    elif status.label == RefundStatus.PROCESSING:
        print("   ⏳ Возврат в обработке. Попробуйте проверить статус позже.")
    elif status.label == RefundStatus.CANCELED:
        print("   ⚠️ Возврат был отменён через личный кабинет.")

    print()

    # Пример 3: Обработка ошибок
    print("=" * 50)
    print("Пример 3: Обработка ошибок")
    print("=" * 50)

    try:
        # Попытка использовать возвраты без Password3
        robokassa_no_password3 = Robokassa(merchant_login="test", password1="test", password2="test")

        await robokassa_no_password3.refund_op(op_key="test-key")
    except Exception as e:
        print(f"❌ Ошибка (ожидаемо): {e}")

    print()

    # Пример 4: Проверка статуса с ошибкой
    print("=" * 50)
    print("Пример 4: Проверка статуса с ошибкой")
    print("=" * 50)

    # Попытка проверить статус по неверному request_id
    status = await robokassa.get_refund_status(request_id="invalid-request-id")

    if status.message:
        print(f"❌ Ошибка: {status.message}")
    else:
        print(f"   Request ID: {status.request_id}")
        print(f"   Статус: {status.label}")

    print()
    print("=" * 50)
    print("Примеры завершены!")
    print("=" * 50)


if __name__ == "__main__":
    # Запуск асинхронного примера
    asyncio.run(main())