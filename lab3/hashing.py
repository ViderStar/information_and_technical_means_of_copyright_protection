"""Quadratic hash function from the lab manual (formula 3.2).

H_i = (H_{i-1} + m_i)^2 mod n,   h(M) = H_k

Letter codes follow the manual: А = 1, Б = 2, ..., Я = 33 (Ё included).
English letters and digits continue the table so any text can be signed;
spaces and punctuation carry no code and are skipped.
"""

from typing import List, NamedTuple, Optional

RUSSIAN = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ENGLISH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
CODES = {symbol: i for i, symbol in enumerate(RUSSIAN + ENGLISH + DIGITS, start=1)}


class HashStep(NamedTuple):
    symbol: str
    m: int
    h: int


def encode(text: str) -> List[int]:
    return [CODES[ch] for ch in text.upper() if ch in CODES]


def quad_hash(text: str, n: int, h0: int, trace: Optional[List[HashStep]] = None) -> int:
    if n < 2:
        raise ValueError("The hash modulus must be at least 2")
    h = h0 % n
    for symbol in (ch for ch in text.upper() if ch in CODES):
        m = CODES[symbol]
        h = (h + m) ** 2 % n
        if trace is not None:
            trace.append(HashStep(symbol, m, h))
    return h
