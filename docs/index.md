# Начало работы

Библиотека **robokassa** представляет собой легковесное, производительное решение, не использующее посторонних зависимостей. При этом библиотека является асинхронной, это достигается за счёт использования **httpx**.

Эта документация, а также сама библиотека на являются продуктами «Robokassa». Весь функционал, который будет описан далее, разработан на основе официальной [документации](https://docs.robokassa.ru/).



## Установка

Для установки можно использовать любой пакетный менеджер:

* pip

```bash
pip install robokassa
```

* poetry

```bash
poetry add robokassa
```

## Пример использования

```py
from robokassa import HashAlgorithm, Robokassa

robokassa = Robokassa(
    merchant_login="my_login",
    password1="password",
    password2="password",
    is_test=False,
    algorithm=HashAlgorithm.md5,
)

my_link = robokassa.generate_open_payment_link(out_sum=1000, inv_id=0)
```