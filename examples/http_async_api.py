import aiohttp
from aiohttp import web

from robokassa.hash import HashAlgorithm
from robokassa import Robokassa


robokassa = Robokassa(
    merchant_login="login",
    password1="<PASSWORD>",
    password2="<PASSWORD>",
    algorithm=HashAlgorithm.md5,
    is_test=True,
)


async def handle_robokassa_request(
    request: aiohttp.web.Request,
) -> aiohttp.web.Response:
    post = await request.post()
    data = post

    result = robokassa.success_or_fail_signature_is_valid(
        signature=data["SignatureValue"].lower(),
        out_sum=data["OutSum"],
        inv_id=data["InvId"],
        **{
            "shp_product_id": data["shp_product_id"],
            "shp_telegram_id": data["shp_telegram_id"],
        },
    )
    if result:
        text = "Thank you for using service!"
    else:
        text = "bad sign"
    return web.Response(text=text)


app = web.Application()
app.router.add_route("*", "/success_notification", handle_robokassa_request)


if __name__ == "__main__":
    web.run_app(app)
