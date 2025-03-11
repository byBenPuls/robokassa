# Robokassa

Экземпляр `Robokassa` (`from robokassa import Robokassa`) требует введённых данных для работы с API.

Для работы с библиотекой требуется пара ключей, это может быть [тестовая](https://docs.robokassa.ru/testing-mode/) или продовая пара. Если вы используете тестовую пару, не забудьте указать аргумент ``is_test``, который должен быть равен ``True``.

В настоящий момент библиотека поддерживает работу со всеми алгоритмами, которые доступны в личном кабинете Robokassa:

* MD5
* RIPEMD160
* SHA1
* SHA256
* SHA384
* SHA512

Для выбора алгоритма используется `HashAlgorithm`.

Пример создания экземпляра класса:

```python
from robokassa import Robokassa, HashAlgorithm

robokassa = Robokassa(
    merchant_login="my_login",
    password1="password",
    password2="password",
    is_test=False,
    algorithm=HashAlgorithm.md5,
)
```
