# FAQ

## Как создать ссылку оплаты с минимальным количеством оплаты?

```py
from robokassa import Robokassa
from robokassa.hash import HashAlgorithm

robokassa = Robokassa(
    "myMerchantLogin",
    "my_first_secret_password",
    "my_second_secret_password",
    algorithm=HashAlgorithm.md5,
)


response = robokassa.generate_open_payment_link(
    out_sum=1000
)

print(response.url)
print(response.params)
```

Вывод:
```
https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin=myMerchantLogin&OutSum=1000&InvId=0&Culture=ru&Recurring=False&SignatureValue=abd49d48d09a4ad6e373d3bfabc0051e&IsTest=0&
```
```py
RobokassaParams(
    base_url="https://auth.robokassa.ru/Merchant/Index.aspx",
    merchant_login="myMerchantLogin",
    out_sum=1000,
    description=None,
    signature_value="abd49d48d09a4ad6e373d3bfabc0051e",
    receipt=None,
    is_test=False,
    inc_curr_label=None,
    payment_methods=None,
    merchant_comments=None,
    invoice_type=None,
    inv_id=0,
    id=None,
    previous_inv_id=None,
    culture="ru",
    encoding=None,
    user_ip=None,
    email=None,
    recurring=False,
    expiration_date=None,
    default_prefix="shp",
    result_url=None,
    success_url=None,
    success_url_method=None,
    fail_url=None,
    fail_url_method=None,
    additional_params={},
)
```

## Как передать дополнительные параметры в ссылку оплаты?

```py
response = robokassa.generate_open_payment_link(
    out_sum=1000,
    customer_id="s8d92378",
    product_id="a9902187-44f1-4b08-83d0-4944f36c2bfe"
)
```

Переданные параметры через `kwargs` автоматически преобразовываются согласно [документации](https://docs.robokassa.ru/script-parameters/#extra).

Например, если мы передали `customer_id`, то в ссылке это будет `shp_customer_id`.

```
https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin=myMerchantLogin&OutSum=1000&InvId=0&Culture=ru&Recurring=False&SignatureValue=f5ed8acce2768d062817733feaff8b23&IsTest=0&shp_customer_id=s8d92378&shp_product_id=a9902187-44f1-4b08-83d0-4944f36c2bfe
```

Все пользовательские параметры автоматически сортируются, вам не нужно об этом беспокоиться.


## Возможно ли перенаправить пользователя на страницу оплаты через POST запрос?

Да, это возможно. Любой способ создания ссылки возвращает объект `RobokassaResponse`, который содержит готовый URL адрес, а также объект `RobokassaParams`. `RobokassaParams` поддерживает метод `to_dict()`, который преобразует все параметры, чтобы передать их через POST запрос.

На реальном примере это могло бы выглядеть так:

```py
response = robokassa.generate_open_payment_link(
    out_sum=1000,
    customer_id="s8d92378",
    product_id="a9902187-44f1-4b08-83d0-4944f36c2bfe"
)

url = response.url # обычная строка URL
params = response.params # параметры, которые были использованы
json = params.to_dict()

print(json)
```

Мы получаем готовый словарь с параметрами, который мы уже можем дальше использовать, передав через POST запрос:

```python
{
    "MerchantLogin": "myMerchantLogin",
    "OutSum": 1000,
    "InvId": 0,
    "SignatureValue": "f5ed8acce2768d062817733feaff8b23",
    "Culture": "ru",
    "shp_customer_id": "s8d92378",
    "shp_product_id": "a9902187-44f1-4b08-83d0-4944f36c2bfe",
}
```

Например, можно передать эти параметры через форму:

```py
from aiohttp import web
from robokassa.types import RobokassaResponse


def get_payment_link() -> RobokassaResponse:
    return robokassa.generate_open_payment_link(
        out_sum=1000,
        customer_id="s8d92378",
        product_id="a9902187-44f1-4b08-83d0-4944f36c2bfe",
    )


async def redirect_to_payment_page(request: web.Request) -> web.Response:
    response = get_payment_link()
    data = response.params.to_dict()
    target_url = response.params.base_url

    html = f"""
    <html>
    <body onload="document.forms[0].submit()">
        <form action="{target_url}" method="post">
            {"".join(f'<input type="hidden" name="{k}" value="{v}">' for k, v in data.items())}
        </form>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


app = web.Application()
app.router.add_get("/pay", redirect_to_payment_page)
web.run_app(app)
```

Это всего лишь пример, разумеется, требуется более аккуратный и продуманный подход к реализации этого.
