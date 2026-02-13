from unittest.mock import AsyncMock, MagicMock

import pytest

from robokassa.exceptions import RobokassaParsingError, RobokassaRequestError
from robokassa.hash import Hash, HashAlgorithm
from robokassa.refund import RefundManager
from robokassa.types import (
    InvoiceItem,
    RefundHashAlgorithm,
    RefundRequest,
    RefundResponse,
    RefundStateResponse,
    RefundStatus,
)


@pytest.fixture
def refund_manager():
    return RefundManager(
        password3="test_password_123",
        jwt_algorithm=RefundHashAlgorithm.HS256,
    )


@pytest.fixture
def refund_manager_hs384():
    return RefundManager(
        password3="test_password_123",
        jwt_algorithm=RefundHashAlgorithm.HS384,
    )


@pytest.fixture
def refund_manager_hs512():
    return RefundManager(
        password3="test_password_123",
        jwt_algorithm=RefundHashAlgorithm.HS512,
    )


@pytest.fixture
def refund_request_simple():
    return RefundRequest(op_key="0005F891-8CCD-434B-8455-816AFFFDBF37-0VOisWikFF")


@pytest.fixture
def refund_request_partial():
    return RefundRequest(
        op_key="0005F891-8CCD-434B-8455-816AFFFDBF37-0VOisWikFF",
        refund_sum=50.5,
    )


@pytest.fixture
def refund_request_with_items():
    items = [
        InvoiceItem(
            name="Тестовый товар-1",
            quantity=1,
            cost=1.0,
            tax="none",
            payment_method="full_payment",
            payment_object="payment",
        ),
        InvoiceItem(
            name="Тестовый товар-2",
            quantity=2,
            cost=2.0,
            tax="vat20",
            payment_method="partial_payment",
            payment_object="commodity",
        ),
    ]
    return RefundRequest(
        op_key="0005F891-8CCD-434B-8455-816AFFFDBF37-0VOisWikFF",
        refund_sum=5.0,
        invoice_items=items,
    )


@pytest.fixture
def success_response():
    return (
        '{"success": true, "message": null, '
        '"requestId": "68cd7fa6-1338-4745-ba5c-28d16cbcdb3d"}'
    )


@pytest.fixture
def error_response():
    return '{"success": false, "message": "NotEnoughOperationFunds", "requestId": null}'


@pytest.fixture
def state_success_response():
    return (
        '{"requestId": "cf15fd52-d2d1-4fc4-b9c0-25310e3bdded", '
        '"amount": 1.000000, "label": "finished"}'
    )


@pytest.fixture
def state_error_response():
    return '{"message": "Id is invalid or request id does not exist"}'


# Test RefundManager initialization


def test_refund_manager_init_success(refund_manager):
    assert refund_manager._password3 == "test_password_123"
    assert refund_manager._jwt_algorithm == RefundHashAlgorithm.HS256
    assert refund_manager._hash is not None


def test_refund_manager_init_without_password():
    with pytest.raises(RobokassaRequestError, match="Password3 is required"):
        RefundManager(password3="")


def test_refund_manager_init_with_none_password():
    with pytest.raises(RobokassaRequestError, match="Password3 is required"):
        RefundManager(password3=None)


def test_refund_manager_init_with_all_algorithms():
    for alg in [RefundHashAlgorithm.HS256, RefundHashAlgorithm.HS384, RefundHashAlgorithm.HS512]:
        manager = RefundManager(password3="test", jwt_algorithm=alg)
        assert manager._jwt_algorithm == alg


# Test JWT creation


def test_create_jwt_token_simple(refund_manager, refund_request_simple):
    token = refund_manager._create_jwt_token(refund_request_simple)
    assert isinstance(token, str)
    assert token.count(".") == 2  # header.payload.signature
    parts = token.split(".")
    assert len(parts) == 3


def test_create_jwt_token_partial(refund_manager, refund_request_partial):
    token = refund_manager._create_jwt_token(refund_request_partial)
    assert isinstance(token, str)
    assert token.count(".") == 2


def test_create_jwt_token_with_items(refund_manager, refund_request_with_items):
    token = refund_manager._create_jwt_token(refund_request_with_items)
    assert isinstance(token, str)
    assert token.count(".") == 2


# Test create_refund


@pytest.mark.asyncio
async def test_create_refund_success(
    refund_manager, refund_request_simple, success_response
):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = success_response
    mock_http.__aenter__.return_value.post.return_value = mock_response

    result = await refund_manager.create_refund(mock_http, refund_request_simple)

    assert isinstance(result, RefundResponse)
    assert result.success is True
    assert result.request_id == "68cd7fa6-1338-4745-ba5c-28d16cbcdb3d"
    assert result.message is None


@pytest.mark.asyncio
async def test_create_refund_with_partial_sum(
    refund_manager, refund_request_partial, success_response
):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = success_response
    mock_http.__aenter__.return_value.post.return_value = mock_response

    result = await refund_manager.create_refund(mock_http, refund_request_partial)

    assert result.success is True


@pytest.mark.asyncio
async def test_create_refund_with_items(
    refund_manager, refund_request_with_items, success_response
):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = success_response
    mock_http.__aenter__.return_value.post.return_value = mock_response

    result = await refund_manager.create_refund(mock_http, refund_request_with_items)

    assert result.success is True


@pytest.mark.asyncio
async def test_create_refund_error(
    refund_manager, refund_request_simple, error_response
):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = error_response
    mock_http.__aenter__.return_value.post.return_value = mock_response

    result = await refund_manager.create_refund(mock_http, refund_request_simple)

    assert result.success is False
    assert result.message == "NotEnoughOperationFunds"
    assert result.request_id is None


@pytest.mark.asyncio
async def test_create_refund_invalid_json(refund_manager, refund_request_simple):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = "<<<>>> this is not json <<<>>>"
    mock_http.__aenter__.return_value.post.return_value = mock_response

    with pytest.raises(RobokassaParsingError, match="Invalid JSON response"):
        await refund_manager.create_refund(mock_http, refund_request_simple)


@pytest.mark.asyncio
async def test_create_refund_malformed_json(refund_manager, refund_request_simple):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = "[]"
    mock_http.__aenter__.return_value.post.return_value = mock_response

    with pytest.raises(RobokassaParsingError, match="Expected dict response"):
        await refund_manager.create_refund(mock_http, refund_request_simple)


# Test get_refund_state


@pytest.mark.asyncio
async def test_get_refund_state_success(
    refund_manager, state_success_response
):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = state_success_response
    mock_http.__aenter__.return_value.get.return_value = mock_response

    request_id = "cf15fd52-d2d1-4fc4-b9c0-25310e3bdded"
    result = await refund_manager.get_refund_state(mock_http, request_id)

    assert isinstance(result, RefundStateResponse)
    assert result.request_id == request_id
    assert result.amount == 1.000000
    assert result.label == RefundStatus.FINISHED
    assert result.message is None


@pytest.mark.asyncio
async def test_get_refund_state_processing(refund_manager):
    response = (
        '{"requestId": "test-id", "amount": 100.0, "label": "processing"}'
    )
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = response
    mock_http.__aenter__.return_value.get.return_value = mock_response

    result = await refund_manager.get_refund_state(mock_http, "test-id")

    assert result.label == RefundStatus.PROCESSING


@pytest.mark.asyncio
async def test_get_refund_state_canceled(refund_manager):
    response = (
        '{"requestId": "test-id", "amount": 100.0, "label": "canceled"}'
    )
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = response
    mock_http.__aenter__.return_value.get.return_value = mock_response

    result = await refund_manager.get_refund_state(mock_http, "test-id")

    assert result.label == RefundStatus.CANCELED


@pytest.mark.asyncio
async def test_get_refund_state_error(
    refund_manager, state_error_response
):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = state_error_response
    mock_http.__aenter__.return_value.get.return_value = mock_response

    request_id = "invalid-id"
    result = await refund_manager.get_refund_state(mock_http, request_id)

    assert result.request_id is None
    assert result.amount is None
    assert result.label is None
    assert result.message == "Id is invalid or request id does not exist"


@pytest.mark.asyncio
async def test_get_refund_state_invalid_json(refund_manager):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = "<<<>>> not json <<<>>>"
    mock_http.__aenter__.return_value.get.return_value = mock_response

    with pytest.raises(RobokassaParsingError, match="Invalid JSON response"):
        await refund_manager.get_refund_state(mock_http, "test-id")


# Test with different JWT algorithms


@pytest.mark.asyncio
async def test_create_refund_with_hs384(
    refund_manager_hs384, refund_request_simple, success_response
):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = success_response
    mock_http.__aenter__.return_value.post.return_value = mock_response

    result = await refund_manager_hs384.create_refund(mock_http, refund_request_simple)
    assert result.success is True


@pytest.mark.asyncio
async def test_create_refund_with_hs512(
    refund_manager_hs512, refund_request_simple, success_response
):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = success_response
    mock_http.__aenter__.return_value.post.return_value = mock_response

    result = await refund_manager_hs512.create_refund(mock_http, refund_request_simple)
    assert result.success is True


# Test InvoiceItem


def test_invoice_item_creation():
    item = InvoiceItem(
        name="Товар",
        quantity=1,
        cost=100.0,
        tax="none",
        payment_method="full_payment",
        payment_object="payment",
    )
    assert item.name == "Товар"
    assert item.quantity == 1
    assert item.cost == 100.0


# Test RefundRequest


def test_refund_request_simple():
    request = RefundRequest(op_key="test-key")
    assert request.op_key == "test-key"
    assert request.refund_sum is None
    assert request.invoice_items is None


def test_refund_request_with_all_fields():
    items = [
        InvoiceItem(
            name="Товар",
            quantity=1,
            cost=100.0,
            tax="none",
            payment_method="full_payment",
            payment_object="payment",
        )
    ]
    request = RefundRequest(op_key="test-key", refund_sum=50.0, invoice_items=items)
    assert request.op_key == "test-key"
    assert request.refund_sum == 50.0
    assert len(request.invoice_items) == 1


# Test RefundResponse


def test_refund_response_success():
    response = RefundResponse(
        success=True,
        message=None,
        request_id="test-request-id",
    )
    assert response.success is True
    assert response.request_id == "test-request-id"


def test_refund_response_error():
    response = RefundResponse(
        success=False,
        message="NotEnoughOperationFunds",
        request_id=None,
    )
    assert response.success is False
    assert response.message == "NotEnoughOperationFunds"


# Test RefundStateResponse


def test_refund_state_response_success():
    response = RefundStateResponse(
        request_id="test-id",
        amount=100.0,
        label=RefundStatus.FINISHED,
    )
    assert response.request_id == "test-id"
    assert response.amount == 100.0
    assert response.label == RefundStatus.FINISHED


def test_refund_state_response_error():
    response = RefundStateResponse(message="Invalid request id")
    assert response.message == "Invalid request id"
    assert response.request_id is None