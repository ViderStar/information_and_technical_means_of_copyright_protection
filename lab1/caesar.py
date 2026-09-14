"""Шифр Цезаря и его обобщения (вариант №1).

Ek(i) = (i + k) mod n              — сдвиг (Цезарь)
Ek(i) = (i * k1 + k2) mod n        — аффинное преобразование
                                     (k1 = 1 — Цезарь, k2 = 0 — децимация)
"""

from math import gcd

from helpers.alphabet import check, detect


def _transform(text: str, add: int, mul: int, decode: bool) -> str:
    alphabet = detect(text)
    check(text, alphabet)
    n = len(alphabet)

    if gcd(mul, n) != 1:
        raise ValueError(f"Множитель {mul} и мощность алфавита {n} не взаимно просты")

    if decode:
        inverse = pow(mul, -1, n)
        code = lambda i: (inverse * (i - add)) % n
    else:
        code = lambda i: (i * mul + add) % n

    return "".join(alphabet[code(alphabet.index(symbol))] for symbol in text)


def encrypt(text: str, key: int, mul: int = 1) -> str:
    return _transform(text, key, mul, decode=False)


def decrypt(cipher: str, key: int, mul: int = 1) -> str:
    return _transform(cipher, key, mul, decode=True)
