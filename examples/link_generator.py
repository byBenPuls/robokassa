from robokassa import HashAlgorithm, Robokassa

robokassa = Robokassa(
    merchant_login="my_login",
    password1="password",
    password2="password",
    is_test=False,
    algorithm=HashAlgorithm.md5,
)

my_link = robokassa.generate_open_payment_link(out_sum=1000, inv_id=0)
