"""Vigenere cipher (variant 3) with three key schemes.

direct      - the key is repeated cyclically
progressive - on every repeat the key symbols are shifted by one position
autokey     - the plaintext itself continues the key
"""

from typing import List, Sequence

from helpers.alphabet import check, detect

MODES = ("direct", "progressive", "autokey")


def _key_shift(i: int, key: Sequence[int], mode: str,
               plain: Sequence[str], alphabet: str) -> int:
    """Shift for position i; autokey uses the already known text."""
    length = len(key)
    if mode == "autokey":
        return key[i] if i < length else alphabet.index(plain[i - length])
    step = i // length if mode == "progressive" else 0
    return (key[i % length] + step) % len(alphabet)


def _run(text: str, keyword: str, mode: str, decode: bool) -> str:
    if mode not in MODES:
        raise ValueError(f"Key scheme must be one of {MODES}")

    alphabet = detect(text, keyword)
    check(text + keyword, alphabet)
    key = [alphabet.index(symbol) for symbol in keyword]
    if not key:
        raise ValueError("Empty key")

    n = len(alphabet)
    result: List[str] = []
    for i, symbol in enumerate(text):
        # when decrypting, autokey uses the plaintext recovered so far
        shift = _key_shift(i, key, mode, result if decode else text, alphabet)
        index = alphabet.index(symbol)
        result.append(alphabet[(index - shift) % n if decode else (index + shift) % n])
    return "".join(result)


def keystream(text: str, keyword: str, mode: str = "direct") -> str:
    """The key sequence actually applied to the text (for display)."""
    alphabet = detect(text, keyword)
    key = [alphabet.index(symbol) for symbol in keyword]
    return "".join(alphabet[_key_shift(i, key, mode, text, alphabet)]
                   for i in range(len(text)))


def encrypt(text: str, keyword: str, mode: str = "direct") -> str:
    return _run(text, keyword, mode, decode=False)


def decrypt(cipher: str, keyword: str, mode: str = "direct") -> str:
    return _run(cipher, keyword, mode, decode=True)
