"""Столбцовый метод перестановки и его двойной вариант.

Текст пишется в таблицу построчно, читается по столбцам в порядке,
заданном ключевым словом.
"""

from typing import List

from helpers.keyword import read_order


def _columns(text: str, width: int) -> List[str]:
    """Столбцы таблицы: столбец c — символы с шагом width, начиная с c."""
    return ["".join(text[i] for i in range(c, len(text), width)) for c in range(width)]


def encrypt(text: str, keyword: str) -> str:
    order = read_order(keyword)
    columns = _columns(text, len(order))
    return "".join(columns[c] for c in order)


def decrypt(cipher: str, keyword: str) -> str:
    order = read_order(keyword)
    width = len(order)
    full, tail = divmod(len(cipher), width)

    # Длина столбца: первые `tail` столбцов таблицы длиннее на один символ
    lengths = [full + (1 if c < tail else 0) for c in range(width)]

    columns = [""] * width
    pos = 0
    for c in order:                       # столбцы нарезаются в порядке чтения
        columns[c] = cipher[pos:pos + lengths[c]]
        pos += lengths[c]

    rows = max(lengths) if lengths else 0
    return "".join(columns[c][r] for r in range(rows)
                   for c in range(width) if r < lengths[c])


def encrypt_double(text: str, keyword1: str, keyword2: str) -> str:
    """Двойная перестановка: шифрование первым ключом, затем вторым."""
    return encrypt(encrypt(text, keyword1), keyword2)


def decrypt_double(cipher: str, keyword1: str, keyword2: str) -> str:
    return decrypt(decrypt(cipher, keyword2), keyword1)
