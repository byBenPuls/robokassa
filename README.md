# Robokassa API

You can use this simple library for create a link or
use that for checks a signatures.

Example:
* Firstly, create Robokassa instance. If you use this in sandbox mode for test robokassa,
you need to paste a pair of **test keys**.
Also, don't forget check what `is_test` argument equals `True`.
```python
from robokassa import Robokassa, HashAlgorithm

robokassa = Robokassa(
    merchant_login="my_login",
    password1="super_secret_test_password1",
    password2="super_secret_test_password2",
    algorithm=HashAlgorithm.sha512,
    is_test=True
)
```

* After that, you can generate a link to payment page
Write a necessary params for a link. You can use
additional params. Choose default prefix of params.
It can be **shp**, **Shp** or **SHP**. Don't specify
`=` symbol. Method automatically generate additional params.
Next, you can use any params like in example: `user_data`, 
`product_id`.

```python
my_payment_link = robokassa.generate_link_to_payment_page(
    out_sum=1000,
    inv_id=0,
    description="It's my description",
    success_url="https://example.com",
    success_url_method="POST",
    default_prefix="shp",
    user_data="important_user_data",
    product_id="790ec274-20af-4972-b5d6-c8698d64fb52"
)
```

* Check signature when you received robokassa notification
in result, success or fail urls.
```python
signature_is_success = robokassa.result_url_signature_is_valid(
    result_signature=("f31b7e1a669ee8686f14be357e5ed2144"
                      "1aca28893fa5b80032ad7f57af07fca80"
                      "2c5f23abb2628ec2d7826af43c8919d7d"
                      "06b4c6881e774b7dc8a056339a8cf"),
    inv_id=0,
    out_sum=1000,
    shp_user_data="important_user_data",
    shp_product_id="790ec274-20af-4972-b5d6-c8698d64fb52"
)

if signature_is_success:
    print("Nice!")
```