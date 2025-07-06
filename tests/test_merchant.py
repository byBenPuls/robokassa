from unittest.mock import AsyncMock, MagicMock

import pytest

from robokassa.exceptions import RobokassaParsingError, RobokassaRequestError
from robokassa.hash import Hash, HashAlgorithm
from robokassa.merchant import OperationStateChecker
from robokassa.types import PaymentDetails, PaymentState


@pytest.fixture
def checker():
    return OperationStateChecker(
        merchant_login="demo", hash=Hash(HashAlgorithm.md5), password_2="pass"
    )


@pytest.fixture
def xml_response_ok():
    return """
        <OperationStateResponse xmlns="http://merchant.roboxchange.com/WebService/">
            <Result>
                <Code>0</Code>
                <Description>OK</Description>
            </Result>
            <State>
                <Code>5</Code>
                <RequestDate>2024-01-01T12:00:00</RequestDate>
                <StateDate>2024-01-01T13:00:00</StateDate>
            </State>
            <Info>
                <IncCurrLabel>TestLabel</IncCurrLabel>
                <IncSum>100.5</IncSum>
                <IncAccount>123456</IncAccount>
                <OutCurrLabel>TestOut</OutCurrLabel>
                <OutSum>95.5</OutSum>
                <OpKey>ABC123</OpKey>
                <BankCardRRN>654321</BankCardRRN>
                <PaymentMethod>
                    <Code>VISA</Code>
                    <Description>Visa Card</Description>
                </PaymentMethod>
            </Info>
            <UserField>
                <Field>
                    <Name>custom1</Name>
                    <Value>value1</Value>
                </Field>
            </UserField>
        </OperationStateResponse>
    """


@pytest.mark.asyncio
async def test_get_state_success(checker, xml_response_ok):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = xml_response_ok
    mock_http.__aenter__.return_value.post.return_value = mock_response

    result = await checker.get_state(mock_http, inv_id=123)

    assert isinstance(result, PaymentDetails)
    assert result.state == PaymentState(5)
    assert result.inc_sum == 100.5
    assert result.op_key == "ABC123"
    assert result.user_fields == {"custom1": "value1"}


@pytest.mark.asyncio
async def test_handle_result_error(checker, xml_response_ok):
    xml_with_error_code = xml_response_ok.replace("<Code>0</Code>", "<Code>1</Code>")
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = xml_with_error_code
    mock_http.__aenter__.return_value.post.return_value = mock_response

    with pytest.raises(RobokassaRequestError, match="Wrong digital signature"):
        await checker.get_state(mock_http, inv_id=123)


@pytest.mark.asyncio
async def test_parse_xml_fail(checker):
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = "<<<>>> this is not xml <<<>>>"
    mock_http.__aenter__.return_value.post.return_value = mock_response

    with pytest.raises(RobokassaParsingError):
        await checker.get_state(mock_http, inv_id=123)
