import hmac

import pytest

from robokassa.hash import Hash, HashAlgorithm
from robokassa.jwt import JWT
from robokassa import Robokassa
from robokassa.types import (
    Culture,
    HTTPMethod,
    InvoiceType,
    PaymentDetails,
    PaymentMethod,
    RobokassaParams,
    RobokassaResponse,
    RobokassaRefundParams,
    RobokassaRefundResponse,
)


@pytest.fixture
def robokassa():
    return Robokassa(
        merchant_login="test_login",
        password1="test_pass1",
        password2="test_pass2",
        password3="test_pass3",
        algorithm=HashAlgorithm.md5,
        is_test=True,
    )


@pytest.mark.asyncio
async def test_generate_open_payment_link(robokassa: Robokassa):
    response = await robokassa.create_refund(
        params=RobokassaRefundParams(
            opkey='test_opkey',
            refund_sum=1.0,
            invoice_items={

            }
        )
    )

    assert response.message.startswith('BadRequest')
