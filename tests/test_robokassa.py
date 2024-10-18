

from robokassa import Robokassa, HashAlgorithm


class TestRobokassaClient:
    robokassa = Robokassa(
        merchant_login="test_login",
        password1="password",
        password2="password",
        algorithm=HashAlgorithm.sha384,
    )

    result_url = "https://example.com"

    def test_client(self) -> None:
        assert self.robokassa.merchant_login == "test_login"

    def test_link_generator(self) -> None:
        link = self.robokassa.generate_link_to_payment_page(out_sum=1, inv_id=0)
        assert link
