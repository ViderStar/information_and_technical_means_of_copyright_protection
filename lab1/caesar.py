"""Caesar cipher and its generalizations (variant 1).

Ek(i) = (i + k) mod n              - shift (Caesar)
Ek(i) = (i * k1 + k2) mod n        - affine transformation
                                     (k1 = 1 - Caesar, k2 = 0 - decimation)
"""

from math import gcd

from helpers.alphabet import check, detect


def _transform(text: str, add: int, mul: int, decode: bool) -> str:
    alphabet = detect(text)
    check(text, alphabet)
    n = len(alphabet)

    if gcd(mul, n) != 1:
        raise ValueError(f"Multiplier {mul} and alphabet size {n} are not coprime")

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
