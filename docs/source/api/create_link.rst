Создание ссылки оплаты
*****************************

Библиотека поддерживает 2 способа создания ссылки на оплату:

* Через "скрипт оплаты" (https://docs.robokassa.ru/script-pay/)

.. literalinclude:: ../../examples/link_generator.py


Результат:


``https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin=demo&OutSum=11&Description=Покупка в демо магазине&SignatureValue=2c113e992e2c985e43e348ff3c12f32b``


* Через "интерфейс оплаты" (https://docs.robokassa.ru/pay-interface/?sphrase_id=157007#curl)

.. code-block:: python

    robokassa.create_link_to_payment_page_by_invoice_id(out_sum=1000, inv_id=0)

Результат:

``https://auth.robokassa.ru/Merchant/Index/41734593-dc97-dc5f-d329-a73158e4cb29``

Разница заключается в получающихся ссылках на оплату.

.. note::

  Также документация сервиса сообщает, что ссылка из второго примера должна 
  быть передана пользователю как можно скорее.