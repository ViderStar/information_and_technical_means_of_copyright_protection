"""Шифр Виженера (вариант №3) с тремя схемами применения ключа.

direct      — ключ повторяется циклически
progressive — при каждом повторе символы ключа сдвигаются на одну позицию
autokey     — продолжением ключа служит сам исходный текст
"""

from typing import List, Sequence

from helpers.alphabet import check, detect

MODES = ("direct", "progressive", "autokey")


def _key_shift(i: int, key: Sequence[int], mode: str,
               plain: Sequence[str], alphabet: str) -> int:
    """Сдвиг для позиции i; для autokey используется уже известный текст."""
    length = len(key)
    if mode == "autokey":
        return key[i] if i < length else alphabet.index(plain[i - length])
    step = i // length if mode == "progressive" else 0
    return (key[i % length] + step) % len(alphabet)


def _run(text: str, keyword: str, mode: str, decode: bool) -> str:
    if mode not in MODES:
        raise ValueError(f"Режим ключа должен быть одним из {MODES}")

    alphabet = detect(text, keyword)
    check(text + keyword, alphabet)
    key = [alphabet.index(symbol) for symbol in keyword]
    if not key:
        raise ValueError("Пустой ключ")

    n = len(alphabet)
    result: List[str] = []
    for i, symbol in enumerate(text):
        # при дешифровании autokey ключом служит уже восстановленный текст
        shift = _key_shift(i, key, mode, result if decode else text, alphabet)
        index = alphabet.index(symbol)
        result.append(alphabet[(index - shift) % n if decode else (index + shift) % n])
    return "".join(result)


def keystream(text: str, keyword: str, mode: str = "direct") -> str:
    """Последовательность ключа, реально применённая к тексту (для наглядности)."""
    alphabet = detect(text, keyword)
    key = [alphabet.index(symbol) for symbol in keyword]
    return "".join(alphabet[_key_shift(i, key, mode, text, alphabet)]
                   for i in range(len(text)))


def encrypt(text: str, keyword: str, mode: str = "direct") -> str:
    return _run(text, keyword, mode, decode=False)


def decrypt(cipher: str, keyword: str, mode: str = "direct") -> str:
    return _run(cipher, keyword, mode, decode=True)
