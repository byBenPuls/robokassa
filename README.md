<p align="center">
  <img src="assets/banner.png" alt="Robokassa API" width="600">
</p>

# 🚀 Robokassa API

> **Unofficial Python Library for Robokassa Payments**  
> 💳 Fast & Secure Payment Integration with Just a Few Lines of Code!

<p align="center">
  <img src="https://img.shields.io/pypi/v/robokassa?color=blue" alt="PyPI Version">
  <img src="https://img.shields.io/pypi/dm/robokassa?color=green" alt="Downloads">
  <img src="https://img.shields.io/github/license/byBenPuls/robokassa?color=red" alt="License">
</p>

---

## 🎨 Features
✔️ Easy Payment Link Generation  
✔️ Secure Transactions with Hash Algorithms  
✔️ Supports all available Hashes  
✔️ Simple and Fast Integration  

---

## 📦 Installation

```bash
pip install robokassa
```

---

## ⚡ Quick Start

```python
from robokassa import HashAlgorithm, Robokassa

robokassa = Robokassa(
    merchant_login="my_login",
    password1="password",
    password2="password",
    is_test=False,
    algorithm=HashAlgorithm.md5,
)

payment_link = robokassa.generate_open_payment_link(out_sum=1000, inv_id=0)
print(payment_link)
```

---

## 📖 Documentation

📚 **Full Documentation (in Russian):**  
🔗 [Read the Docs](https://robokassa.readthedocs.io/)

---

## 🌟 Contribute & Support
🚀 **Found this project useful?** Show some ❤️ by giving it a star!

---

Made with ❤️ for seamless payment integration.
